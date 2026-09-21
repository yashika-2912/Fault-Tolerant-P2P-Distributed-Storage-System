"""Append-only, hash-linked audit entries."""

from datetime import datetime, timezone
import json
import sqlite3

from coordinator.crypto import sha256_hash

GENESIS_HASH = "0" * 64


def _entry_hash(event: str, prev_hash: str, created_at: str) -> str:
    return sha256_hash(json.dumps({"event": event, "prev_hash": prev_hash, "created_at": created_at}, sort_keys=True, separators=(",", ":")).encode())


def append_audit_entry(conn: sqlite3.Connection, event: str, created_at: str | None = None) -> str:
    """Persist one event and return its tamper-evident chain hash."""
    if not isinstance(event, str) or not event:
        raise ValueError("event must be a non-empty string")
    timestamp = created_at or datetime.now(timezone.utc).isoformat()
    row = conn.execute("SELECT entry_hash FROM audit_log ORDER BY entry_index DESC LIMIT 1").fetchone()
    previous = row[0] if row else GENESIS_HASH
    digest = _entry_hash(event, previous, timestamp)
    conn.execute("INSERT INTO audit_log (event, prev_hash, entry_hash, created_at) VALUES (?, ?, ?, ?)", (event, previous, digest, timestamp))
    conn.commit()
    return digest


def verify_audit_log(conn: sqlite3.Connection) -> bool:
    """Verify all links and hashes in insertion order."""
    previous = GENESIS_HASH
    for row in conn.execute("SELECT event, prev_hash, entry_hash, created_at FROM audit_log ORDER BY entry_index"):
        if row[1] != previous or row[2] != _entry_hash(row[0], row[1], row[3]):
            return False
        previous = row[2]
    return True
