"""Day-7 failure-detection tests; recovery itself is implemented later."""

import time

from coordinator import heartbeat_monitor
from coordinator.db import get_all_nodes, init_db, insert_node


def _status(conn, node_id: str) -> str:
    """Read one test node's persisted status."""
    return next(node["status"] for node in get_all_nodes(conn) if node["node_id"] == node_id)


def test_stale_active_node_is_marked_down_once_while_recent_node_stays_active(tmp_path, capsys):
    """Detection changes only a stale ACTIVE node and is idempotent afterward."""
    conn = init_db(str(tmp_path / "detection.db"))
    try:
        insert_node(conn, "STALE", "127.0.0.1", 7001, "ACTIVE")
        insert_node(conn, "RECENT", "127.0.0.1", 7002, "ACTIVE")
        now = time.time()
        with heartbeat_monitor._t_last_lock:
            heartbeat_monitor.t_last.clear()
            heartbeat_monitor.t_last.update(
                {"STALE": now - heartbeat_monitor.HEARTBEAT_TIMEOUT - 0.1, "RECENT": now}
            )

        assert heartbeat_monitor.check_all_nodes_once(conn, now=now) == ["STALE"]
        assert _status(conn, "STALE") == "DOWN"
        assert _status(conn, "RECENT") == "ACTIVE"
        first_output = capsys.readouterr().out
        assert "[FAILURE DETECTED] STALE" in first_output

        assert heartbeat_monitor.check_all_nodes_once(conn, now=now + 1) == []
        assert _status(conn, "STALE") == "DOWN"
        assert "[FAILURE DETECTED]" not in capsys.readouterr().out
    finally:
        conn.close()
        with heartbeat_monitor._t_last_lock:
            heartbeat_monitor.t_last.clear()
