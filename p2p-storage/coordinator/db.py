"""SQLite schema initialization and minimal Day-5 metadata query helpers."""

import sqlite3
from pathlib import Path

from coordinator.config import DB_PATH


def init_db(db_path: str | None = None) -> sqlite3.Connection:
    """Open a database, enable foreign keys, and create all Day-5 tables."""
    resolved_path = db_path if db_path is not None else DB_PATH
    if resolved_path != ":memory:":
        Path(resolved_path).parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(resolved_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS files (
            file_id TEXT PRIMARY KEY,
            filename TEXT,
            size_bytes INTEGER,
            chunk_count INTEGER,
            merkle_root TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id TEXT PRIMARY KEY,
            file_id TEXT,
            chunk_index INTEGER,
            chunk_hash TEXT,
            FOREIGN KEY (file_id) REFERENCES files(file_id)
        );

        CREATE TABLE IF NOT EXISTS nodes (
            node_id TEXT PRIMARY KEY,
            host TEXT,
            port INTEGER,
            status TEXT,
            last_heartbeat TEXT
        );

        CREATE TABLE IF NOT EXISTS replicas (
            chunk_id TEXT,
            node_id TEXT,
            role TEXT,
            PRIMARY KEY (chunk_id, node_id),
            FOREIGN KEY (chunk_id) REFERENCES chunks(chunk_id),
            FOREIGN KEY (node_id) REFERENCES nodes(node_id)
        );

        CREATE TABLE IF NOT EXISTS audit_log (
            entry_index INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            prev_hash TEXT,
            entry_hash TEXT,
            created_at TEXT
        );
        """
    )
    connection.commit()
    return connection


def insert_node(conn: sqlite3.Connection, node_id: str, host: str, port: int, status: str) -> None:
    """Insert or refresh a node's basic metadata."""
    conn.execute(
        """
        INSERT INTO nodes (node_id, host, port, status)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(node_id) DO UPDATE SET
            host = excluded.host,
            port = excluded.port,
            status = excluded.status
        """,
        (node_id, host, port, status),
    )
    conn.commit()


def get_all_nodes(conn: sqlite3.Connection) -> list[dict]:
    """Return all nodes as dictionaries ordered by node identifier."""
    rows = conn.execute(
        "SELECT node_id, host, port, status, last_heartbeat FROM nodes ORDER BY node_id"
    ).fetchall()
    return [dict(row) for row in rows]


def update_last_heartbeat(conn: sqlite3.Connection, node_id: str, received_at: float) -> None:
    """Persist the coordinator receipt timestamp for one node heartbeat."""
    conn.execute("UPDATE nodes SET last_heartbeat = ? WHERE node_id = ?", (str(received_at), node_id))
    conn.commit()


def update_node_status(conn: sqlite3.Connection, node_id: str, new_status: str) -> None:
    """Set a node's lifecycle status."""
    conn.execute("UPDATE nodes SET status = ? WHERE node_id = ?", (new_status, node_id))
    conn.commit()


def insert_replica(conn: sqlite3.Connection, chunk_id: str, node_id: str, role: str) -> None:
    """Insert or refresh one chunk replica's assigned node and role."""
    conn.execute(
        """
        INSERT INTO replicas (chunk_id, node_id, role)
        VALUES (?, ?, ?)
        ON CONFLICT(chunk_id, node_id) DO UPDATE SET role = excluded.role
        """,
        (chunk_id, node_id, role),
    )
    conn.commit()


def get_replicas_for_chunk(conn: sqlite3.Connection, chunk_id: str) -> list[dict]:
    """Return a chunk's replicas as dictionaries, ordered by role then node ID."""
    rows = conn.execute(
        "SELECT chunk_id, node_id, role FROM replicas WHERE chunk_id = ? ORDER BY role, node_id",
        (chunk_id,),
    ).fetchall()
    return [dict(row) for row in rows]
