"""Merkle and tamper-evident audit-log unit tests."""

from coordinator.audit import append_audit_entry, verify_audit_log
from coordinator.db import init_db
from coordinator.merkle import build_merkle_root, verify_merkle_root


def test_merkle_root_is_deterministic_and_detects_a_changed_chunk():
    chunks = [b"one", b"two", b"three"]
    root = build_merkle_root(chunks)
    assert root == build_merkle_root(chunks)
    assert verify_merkle_root(chunks, root)
    assert not verify_merkle_root([b"one", b"changed", b"three"], root)


def test_empty_merkle_root_is_explicitly_none():
    assert build_merkle_root([]) is None


def test_audit_chain_identifies_tampering(tmp_path):
    conn = init_db(str(tmp_path / "audit.db"))
    try:
        append_audit_entry(conn, "uploaded", "2020-01-01T00:00:00+00:00")
        append_audit_entry(conn, "downloaded", "2020-01-01T00:00:01+00:00")
        assert verify_audit_log(conn)
        conn.execute("UPDATE audit_log SET event = 'altered' WHERE entry_index = 1")
        conn.commit()
        assert not verify_audit_log(conn)
    finally:
        conn.close()
