"""Replica repair after a failed node, using a promoted standby node."""

from coordinator.audit import append_audit_entry
from coordinator.db import (get_all_nodes, get_node, get_replicas_for_chunk, init_db,
                            update_node_status)
from coordinator.node_client import ChunkNotFoundError, NodeCommunicationError, fetch_chunk, store_chunk


def recover_failed_node(failed_node_id: str, db_path: str | None = None) -> int:
    """Promote one STANDBY, copy affected chunks, and return repaired count.

    A replica mapping changes only after its copy was acknowledged.  If no
    standby exists, data remains readable from the surviving replica but is
    intentionally reported as unrepaired rather than claiming durability.
    """
    conn = init_db(db_path)
    try:
        standby = next((node for node in get_all_nodes(conn) if node["status"] == "STANDBY"), None)
        if standby is None:
            return 0
        affected = conn.execute("SELECT chunk_id FROM replicas WHERE node_id = ? ORDER BY chunk_id", (failed_node_id,)).fetchall()
        if not affected:
            update_node_status(conn, standby["node_id"], "ACTIVE")
            append_audit_entry(conn, f"PROMOTE node_id={standby['node_id']} no_repairs")
            return 0
        repaired = 0
        for row in affected:
            chunk_id = row[0]
            source_data = None
            for replica in get_replicas_for_chunk(conn, chunk_id):
                if replica["node_id"] == failed_node_id:
                    continue
                source = get_node(conn, replica["node_id"])
                if not source or source["status"] == "DOWN":
                    continue
                try:
                    source_data = fetch_chunk(source["host"], source["port"], chunk_id)
                    break
                except (NodeCommunicationError, ChunkNotFoundError):
                    continue
            if source_data is None:
                continue
            try:
                if not store_chunk(standby["host"], standby["port"], chunk_id, source_data):
                    continue
            except NodeCommunicationError:
                continue
            conn.execute("DELETE FROM replicas WHERE chunk_id = ? AND node_id = ?", (chunk_id, failed_node_id))
            conn.execute("INSERT OR REPLACE INTO replicas (chunk_id, node_id, role) VALUES (?, ?, 'SECONDARY')", (chunk_id, standby["node_id"]))
            conn.commit()
            repaired += 1
        update_node_status(conn, standby["node_id"], "ACTIVE")
        append_audit_entry(conn, f"RECOVERY failed_node={failed_node_id} promoted={standby['node_id']} repaired={repaired}")
        return repaired
    finally:
        conn.close()
