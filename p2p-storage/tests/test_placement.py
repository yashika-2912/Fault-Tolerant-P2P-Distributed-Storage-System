"""Tests for Day-5 placement and SQLite schema initialization."""

import hashlib

import pytest

from coordinator.db import init_db
from coordinator.placement import placement_index, replica_set


def test_replica_set_is_deterministic():
    """The same chunk and active set always choose the same ordered pair."""
    active_nodes = ["N1", "N2"]
    first_result = replica_set("stable-chunk-id", active_nodes)
    assert all(replica_set("stable-chunk-id", active_nodes) == first_result for _ in range(10))


def test_two_node_active_set_uses_both_indices():
    """A sample of independent IDs exercises both possible hash indices."""
    indices = {placement_index(f"chunk-{number}", 2) for number in range(100)}
    assert indices == {0, 1}


def test_two_node_replica_set_always_contains_both_nodes():
    """At replication factor two, either primary still has the other as secondary."""
    active_nodes = ["N1", "N2"]
    for chunk_id in ("chunk-a", "chunk-b", "chunk-c", "chunk-d"):
        assert set(replica_set(chunk_id, active_nodes)) == {"N1", "N2"}


def test_placement_index_generalizes_to_three_active_nodes():
    """The computed index is the specified SHA-256 prefix modulo active-set size."""
    chunk_id = "promoted-active-set-chunk"
    expected = int.from_bytes(hashlib.sha256(chunk_id.encode("utf-8")).digest()[:8], "big") % 3
    assert placement_index(chunk_id, 3) == expected
    assert placement_index(chunk_id, 3) in {0, 1, 2}


def test_replica_set_requires_two_active_nodes():
    """Replication factor two cannot be satisfied by zero or one active node."""
    with pytest.raises(ValueError, match="at least two"):
        replica_set("chunk", [])
    with pytest.raises(ValueError, match="at least two"):
        replica_set("chunk", ["N1"])


def test_init_db_creates_all_expected_tables_and_columns(tmp_path):
    """A throwaway database contains exactly the required Day-5 schema columns."""
    db_path = tmp_path / "schema_check.db"
    conn = init_db(str(db_path))
    try:
        tables = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        }
        assert {"files", "chunks", "replicas", "nodes", "audit_log"}.issubset(tables)

        expected_columns = {
            "files": {"file_id", "filename", "size_bytes", "chunk_count", "merkle_root", "created_at"},
            "chunks": {"chunk_id", "file_id", "chunk_index", "chunk_hash"},
            "replicas": {"chunk_id", "node_id", "role"},
            "nodes": {"node_id", "host", "port", "status", "last_heartbeat"},
            "audit_log": {"entry_index", "event", "prev_hash", "entry_hash", "created_at"},
        }
        for table_name, expected in expected_columns.items():
            actual = {row[1] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()}
            assert actual == expected
        assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    finally:
        conn.close()
        db_path.unlink()
