# Design Document

## Scope

This project demonstrates encrypted replicated file storage and recovery from one storage-node failure on one host. It does not implement peer discovery, consensus, authentication/authorization, key management, erasure coding, deletion/garbage collection, Byzantine fault tolerance, multi-coordinator high availability, or production-grade transport security.

## Components and data path

The CLI sends a multipart upload to the Flask coordinator. The coordinator splits plaintext into fixed 1 MiB chunks, AES-256-GCM encrypts every chunk, chooses two nodes deterministically, and sends framed `STORE` requests to TCP nodes. Only after every `STORE_ACK` does it write file, chunk, replica, and audit metadata to SQLite. This prevents a partial upload from appearing complete.

For a download, the coordinator reads chunks in index order, tries each non-DOWN replica, verifies the encrypted-chunk SHA-256 hash, verifies the final Merkle root, decrypts AES-GCM, and joins plaintext chunks. An unavailable, missing, or hash-mismatched replica is skipped for the other replica.

```
CLI -> HTTP coordinator -> STORE/FETCH TCP -> N1, N2 (replicas)
                  |                         -> N3 (standby)
                  +-> SQLite metadata + hash-linked audit log
```

## Storage protocol

Each TCP message is UTF-8 JSON preceded by a four-byte big-endian length. `STORE` carries `chunk_id` and base64 `data_b64`; a node returns `STORE_ACK`. `FETCH` carries `chunk_id`; a node returns `FETCH_RESULT` with data or `not_found`. Each connection serves one request. Chunk IDs are validated before a node writes under `node_data/<node-id>/`.

## Metadata and integrity

SQLite has `files`, `chunks`, `replicas`, `nodes`, and `audit_log`, with foreign keys enabled. A file records original size, chunk count, and Merkle root. A chunk stores the SHA-256 hash of encrypted bytes, so a retrieved payload is validated before decryption. The Merkle tree hashes pairs of hexadecimal child hashes and duplicates the final leaf at odd levels. Empty files use no chunks and a NULL root.

The audit log is append-only in normal operation. Each row hashes canonical JSON of its event, predecessor hash, and timestamp; verification recomputes every link from an all-zero genesis hash. This detects database tampering but is not an external immutable ledger.

## Placement and availability

For a sorted ACTIVE node list, the first eight bytes of `SHA256(chunk_id)` modulo node count choose primary placement and the next circular position is secondary. With N1 and N2 ACTIVE, every chunk has both replicas. N3 starts STANDBY. Upload requires at least two ACTIVE nodes.

Nodes send coordinator-side timestamped heartbeats every second. An ACTIVE node missing heartbeats for more than four seconds becomes DOWN. The coordinator selects one STANDBY node, fetches every affected chunk from a surviving non-DOWN replica, stores it on the standby, changes the mapping only after acknowledgement, and then promotes the standby. If no standby or source is available, it does not claim repair.

## Operational notes and limitations

The demo uses loopback addresses, fixed ports, and the static 32-byte development key in `coordinator/config.py`; never use that key or unauthenticated protocol with sensitive data. Set `P2P_DB_PATH` to isolate a run. Benchmark scripts do this automatically, validate returned bytes, and use Matplotlib's non-interactive `Agg` backend.

Failure recovery assumes at most one failed data replica per chunk and an available standby. Restarting a DOWN node does not automatically reintegrate it. A crash during metadata writes can leave harmless orphaned node files; they are not garbage-collected.
