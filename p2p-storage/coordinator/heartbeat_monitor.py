"""Coordinator heartbeat listener and stale-active-node failure detector."""

import json
import socket
import struct
import threading
import time
from pathlib import Path

from coordinator.config import COORDINATOR_PORT, HEARTBEAT_INTERVAL, HEARTBEAT_TIMEOUT, NODE_PORTS
from coordinator.db import get_all_nodes, init_db, insert_node, update_last_heartbeat, update_node_status


HOST = "127.0.0.1"
SOCKET_TIMEOUT_SECONDS = 2
t_last: dict[str, float] = {}
_t_last_lock = threading.Lock()
_listener_started = False
_detector_started = False
_start_lock = threading.Lock()


def _receive_exact(connection: socket.socket, byte_count: int) -> bytes:
    """Receive exactly byte_count bytes from one short-lived connection."""
    chunks = bytearray()
    while len(chunks) < byte_count:
        chunk = connection.recv(byte_count - len(chunks))
        if not chunk:
            raise ConnectionError("connection_closed")
        chunks.extend(chunk)
    return bytes(chunks)


def _receive_message(connection: socket.socket) -> dict:
    """Receive one 4-byte-length-prefixed JSON message."""
    length = struct.unpack("!I", _receive_exact(connection, 4))[0]
    return json.loads(_receive_exact(connection, length).decode("utf-8"))


def _send_message(connection: socket.socket, message: dict) -> None:
    """Send one 4-byte-length-prefixed JSON message."""
    payload = json.dumps(message).encode("utf-8")
    connection.sendall(struct.pack("!I", len(payload)) + payload)


def preregister_expected_nodes(conn) -> None:
    """Create the fixed Day-6 node rows once, preserving later DOWN states."""
    existing = {node["node_id"] for node in get_all_nodes(conn)}
    for node_id, port, status in (("N1", NODE_PORTS[0], "ACTIVE"), ("N2", NODE_PORTS[1], "ACTIVE"), ("N3", NODE_PORTS[2], "STANDBY")):
        if node_id not in existing:
            insert_node(conn, node_id, HOST, port, status)


def record_heartbeat(node_id: str, received_at: float, db_path: str | None = None) -> None:
    """Record coordinator receipt time, avoiding assumptions about node clock skew."""
    with _t_last_lock:
        t_last[node_id] = received_at
    conn = init_db(db_path)
    try:
        update_last_heartbeat(conn, node_id, received_at)
    finally:
        conn.close()


def get_last_heartbeat(node_id: str) -> float | None:
    """Return the most recent coordinator-side heartbeat receipt time."""
    with _t_last_lock:
        return t_last.get(node_id)


def get_all_last_heartbeats() -> dict[str, float]:
    """Return a copy of all coordinator-side heartbeat receipt times."""
    with _t_last_lock:
        return dict(t_last)


def _handle_connection(connection: socket.socket, address: tuple[str, int], db_path: str | None) -> None:
    """Receive one heartbeat, persist it, acknowledge it, and close the connection."""
    with connection:
        connection.settimeout(SOCKET_TIMEOUT_SECONDS)
        try:
            message = _receive_message(connection)
            if message.get("type") != "HEARTBEAT" or not isinstance(message.get("node_id"), str):
                _send_message(connection, {"type": "ERROR", "error": "unknown_type"})
                return
            node_id = message["node_id"]
            received_at = time.time()
            record_heartbeat(node_id, received_at, db_path)
            print(f"HEARTBEAT received: {node_id} at {received_at:.3f}")
            _send_message(connection, {"type": "HEARTBEAT_ACK"})
        except (ConnectionError, OSError, socket.timeout, UnicodeDecodeError, json.JSONDecodeError) as error:
            print(f"Heartbeat connection from {address} ended with error: {error}")


def _listener_loop(host: str, port: int, db_path: str | None) -> None:
    """Run the coordinator heartbeat TCP listener indefinitely."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen()
    print(f"Heartbeat listener running on {host}:{port}")
    while True:
        connection, address = server.accept()
        threading.Thread(target=_handle_connection, args=(connection, address, db_path), daemon=True).start()


def start_heartbeat_listener(host: str = HOST, port: int = COORDINATOR_PORT, db_path: str | None = None) -> None:
    """Pre-register nodes and start the listener once as a daemon thread."""
    global _listener_started
    conn = init_db(db_path)
    try:
        preregister_expected_nodes(conn)
    finally:
        conn.close()
    with _start_lock:
        if _listener_started:
            return
        threading.Thread(target=_listener_loop, args=(host, port, db_path), daemon=True).start()
        _listener_started = True


def check_all_nodes_once(conn, now: float | None = None) -> list[str]:
    """Mark ACTIVE nodes stale beyond tau DOWN once; return newly failed IDs.

    Nodes with no received heartbeat are ignored until their first heartbeat arrives.
    """
    current_time = time.time() if now is None else now
    failed_nodes = []
    with _t_last_lock:
        last_seen = dict(t_last)
    for node in get_all_nodes(conn):
        if node["status"] != "ACTIVE":
            continue
        heartbeat_time = last_seen.get(node["node_id"])
        if heartbeat_time is not None and current_time - heartbeat_time > HEARTBEAT_TIMEOUT:
            update_node_status(conn, node["node_id"], "DOWN")
            failed_nodes.append(node["node_id"])
            print(f"[FAILURE DETECTED] {node['node_id']} missed heartbeat, marked DOWN at {current_time:.3f}")
    return failed_nodes


def _detector_loop(db_path: str | None) -> None:
    """Check active-node liveness every HEARTBEAT_INTERVAL seconds."""
    while True:
        conn = init_db(db_path)
        try:
            check_all_nodes_once(conn)
        finally:
            conn.close()
        time.sleep(HEARTBEAT_INTERVAL)


def start_failure_detector(db_path: str | None = None) -> None:
    """Start the Day-7 failure detector once as a daemon thread."""
    global _detector_started
    with _start_lock:
        if _detector_started:
            return
        threading.Thread(target=_detector_loop, args=(db_path,), daemon=True).start()
        _detector_started = True
