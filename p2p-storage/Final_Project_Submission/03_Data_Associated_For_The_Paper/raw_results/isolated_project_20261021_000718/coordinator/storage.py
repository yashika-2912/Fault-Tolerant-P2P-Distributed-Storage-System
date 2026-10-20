"""Coordinator upload/download workflow over the existing node protocol."""

from pathlib import Path
import uuid

from coordinator.audit import append_audit_entry
from coordinator.chunking import reassemble, split_file
from coordinator.crypto import aes_decrypt, aes_encrypt, sha256_hash
from coordinator.db import (get_active_nodes, get_chunks_for_file, get_file, get_node,
                            get_replicas_for_chunk, init_db, insert_chunk, insert_file,
                            insert_replica)
from coordinator.merkle import build_merkle_root
from coordinator.node_client import ChunkNotFoundError, NodeCommunicationError, fetch_chunk, store_chunk
from coordinator.placement import replica_set


class StorageError(RuntimeError):
    """A file could not be stored or reconstructed safely."""


def upload_bytes(data: bytes, filename: str = "upload.bin", db_path: str | None = None) -> str:
    """Encrypt, replicate, and record bytes; return a newly allocated file ID."""
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")
    conn = init_db(db_path)
    try:
        nodes = get_active_nodes(conn)
        if len(nodes) < 2:
            raise StorageError("upload requires at least two ACTIVE nodes")
        by_id = {node["node_id"]: node for node in nodes}
        file_id = uuid.uuid4().hex
        plain_chunks = split_file(data)
        encrypted_chunks = [aes_encrypt(chunk) for chunk in plain_chunks]
        root = build_merkle_root(encrypted_chunks)
        # Do not create metadata until every replica ACKs: failed uploads are invisible.
        planned = []
        for index, encrypted in enumerate(encrypted_chunks):
            chunk_id = f"{file_id}-{index}"
            primary, secondary = replica_set(chunk_id, sorted(by_id))
            for node_id in (primary, secondary):
                node = by_id[node_id]
                try:
                    if not store_chunk(node["host"], node["port"], chunk_id, encrypted):
                        raise StorageError(f"node {node_id} rejected chunk {index}")
                except NodeCommunicationError as error:
                    raise StorageError(f"could not store chunk {index} on {node_id}: {error}") from error
            planned.append((chunk_id, index, sha256_hash(encrypted), primary, secondary))
        insert_file(conn, file_id, Path(filename).name, len(data), len(plain_chunks), root)
        for chunk_id, index, digest, primary, secondary in planned:
            insert_chunk(conn, chunk_id, file_id, index, digest)
            insert_replica(conn, chunk_id, primary, "PRIMARY")
            insert_replica(conn, chunk_id, secondary, "SECONDARY")
        append_audit_entry(conn, f"UPLOAD file_id={file_id} chunks={len(planned)}")
        return file_id
    finally:
        conn.close()


def download_bytes(file_id: str, db_path: str | None = None) -> bytes:
    """Fetch any healthy replica per chunk, verify it, then decrypt and join."""
    conn = init_db(db_path)
    try:
        metadata = get_file(conn, file_id)
        if metadata is None:
            raise StorageError(f"unknown file ID: {file_id}")
        plaintext = []
        encrypted = []
        for chunk in get_chunks_for_file(conn, file_id):
            data = None
            for replica in get_replicas_for_chunk(conn, chunk["chunk_id"]):
                node = get_node(conn, replica["node_id"])
                if not node or node["status"] == "DOWN":
                    continue
                try:
                    candidate = fetch_chunk(node["host"], node["port"], chunk["chunk_id"])
                    if sha256_hash(candidate) != chunk["chunk_hash"]:
                        continue
                    data = candidate
                    break
                except (NodeCommunicationError, ChunkNotFoundError):
                    continue
            if data is None:
                raise StorageError(f"no valid replica available for chunk {chunk['chunk_index']}")
            encrypted.append(data)
            plaintext.append(aes_decrypt(data))
        if build_merkle_root(encrypted) != metadata["merkle_root"]:
            raise StorageError("Merkle-root verification failed")
        result = reassemble(plaintext)
        if len(result) != metadata["size_bytes"]:
            raise StorageError("reconstructed size does not match metadata")
        append_audit_entry(conn, f"DOWNLOAD file_id={file_id}")
        return result
    finally:
        conn.close()
