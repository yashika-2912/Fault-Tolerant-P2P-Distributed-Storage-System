"""Coordinator-side STORE/FETCH client for Day-2 storage nodes."""

import base64
import json
import socket
import struct


class NodeCommunicationError(Exception):
    """Raised when a node cannot be reached or returns an invalid wire response."""


class ChunkNotFoundError(Exception):
    """Raised when a node reports that a requested chunk is absent."""


def _receive_exact(sock: socket.socket, byte_count: int) -> bytes:
    """Receive exactly byte_count bytes or fail if the node closes the connection."""
    chunks = bytearray()
    while len(chunks) < byte_count:
        chunk = sock.recv(byte_count - len(chunks))
        if not chunk:
            raise ConnectionError("connection_closed")
        chunks.extend(chunk)
    return bytes(chunks)


def _send_message(sock: socket.socket, message: dict) -> None:
    """Send one UTF-8 JSON message with a 4-byte big-endian length prefix."""
    payload = json.dumps(message).encode("utf-8")
    sock.sendall(struct.pack("!I", len(payload)) + payload)


def _recv_message(sock: socket.socket) -> dict:
    """Receive one 4-byte-length-prefixed UTF-8 JSON message."""
    payload_length = struct.unpack("!I", _receive_exact(sock, 4))[0]
    message = json.loads(_receive_exact(sock, payload_length).decode("utf-8"))
    if not isinstance(message, dict):
        raise ValueError("node response is not a JSON object")
    return message


def _request(host: str, port: int, message: dict, timeout: float) -> dict:
    """Send one short-lived request and normalize transport/protocol failures."""
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            sock.settimeout(timeout)
            _send_message(sock, message)
            return _recv_message(sock)
    except (socket.timeout, ConnectionRefusedError, ConnectionError, OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise NodeCommunicationError(f"node {host}:{port} communication failed: {error}") from error


def store_chunk(host: str, port: int, chunk_id: str, data: bytes, timeout: float = 2.0) -> bool:
    """STORE data on one node, returning False for an application-level error ACK."""
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")

    print(f"STORE attempt: chunk {chunk_id} -> {host}:{port}")
    response = _request(
        host,
        port,
        {"type": "STORE", "chunk_id": chunk_id, "data_b64": base64.b64encode(data).decode("ascii")},
        timeout,
    )
    succeeded = response.get("type") == "STORE_ACK" and response.get("status") == "OK"
    print(f"STORE {'succeeded' if succeeded else 'failed'}: chunk {chunk_id} -> {host}:{port}")
    return succeeded


def fetch_chunk(host: str, port: int, chunk_id: str, timeout: float = 2.0) -> bytes:
    """FETCH one chunk, raising ChunkNotFoundError for an application-level miss."""
    print(f"FETCH attempt: chunk {chunk_id} <- {host}:{port}")
    response = _request(host, port, {"type": "FETCH", "chunk_id": chunk_id}, timeout)
    if response.get("type") != "FETCH_RESULT":
        raise NodeCommunicationError(f"node {host}:{port} returned an unexpected response type")
    if response.get("status") != "OK":
        error = response.get("error", "unknown_error")
        if error == "not_found":
            raise ChunkNotFoundError(f"chunk {chunk_id!r} was not found on node {host}:{port}")
        raise NodeCommunicationError(f"node {host}:{port} FETCH failed: {error}")

    try:
        data = base64.b64decode(response["data_b64"], validate=True)
    except (KeyError, TypeError, ValueError) as error:
        raise NodeCommunicationError(f"node {host}:{port} returned invalid chunk data: {error}") from error

    print(f"FETCH succeeded: chunk {chunk_id} <- {host}:{port}")
    return data
