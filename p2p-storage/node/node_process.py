"""Day-2 TCP storage node supporting one-request STORE and FETCH connections."""

import argparse
import base64
import json
import socket
import struct
import threading
import time
from pathlib import Path

import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from coordinator.config import COORDINATOR_PORT, HEARTBEAT_INTERVAL


HOST = "127.0.0.1"
SOCKET_TIMEOUT_SECONDS = 2


def receive_exact(connection: socket.socket, byte_count: int) -> bytes:
    """Receive exactly byte_count bytes or raise if the client disconnects."""
    chunks = bytearray()
    while len(chunks) < byte_count:
        chunk = connection.recv(byte_count - len(chunks))
        if not chunk:
            raise ConnectionError("connection_closed")
        chunks.extend(chunk)
    return bytes(chunks)


def receive_message(connection: socket.socket) -> dict:
    """Receive one length-prefixed UTF-8 JSON message."""
    payload_length = struct.unpack("!I", receive_exact(connection, 4))[0]
    payload = receive_exact(connection, payload_length)
    return json.loads(payload.decode("utf-8"))


def send_message(connection: socket.socket, message: dict) -> None:
    """Send one length-prefixed UTF-8 JSON message."""
    payload = json.dumps(message).encode("utf-8")
    connection.sendall(struct.pack("!I", len(payload)) + payload)


def heartbeat_loop(node_id: str, coordinator_host: str, coordinator_port: int, stop_event: threading.Event) -> None:
    """Send one framed heartbeat each interval; transient coordinator outages are nonfatal."""
    while not stop_event.is_set():
        try:
            with socket.create_connection((coordinator_host, coordinator_port), timeout=SOCKET_TIMEOUT_SECONDS) as connection:
                connection.settimeout(SOCKET_TIMEOUT_SECONDS)
                send_message(connection, {"type": "HEARTBEAT", "node_id": node_id, "ts": time.time()})
                response = receive_message(connection)
                if response.get("type") == "HEARTBEAT_ACK":
                    print(f"HEARTBEAT acknowledged: {node_id}")
                else:
                    print(f"HEARTBEAT warning: unexpected reply for {node_id}: {response}")
        except (ConnectionError, OSError, socket.timeout, UnicodeDecodeError, json.JSONDecodeError) as error:
            print(f"HEARTBEAT warning: coordinator {coordinator_host}:{coordinator_port} unavailable ({error})")
        stop_event.wait(HEARTBEAT_INTERVAL)


def chunk_path(storage_dir: Path, chunk_id: str) -> Path:
    """Return the local filename for a chunk identifier."""
    if not isinstance(chunk_id, str) or not chunk_id or "/" in chunk_id or "\\" in chunk_id:
        raise ValueError("invalid_chunk_id")
    return storage_dir / f"{chunk_id}.bin"


def handle_store(connection: socket.socket, message: dict, storage_dir: Path) -> None:
    """Persist one base64-encoded chunk and acknowledge the result."""
    chunk_id = message.get("chunk_id")
    print(f"STORE received: {chunk_id}")
    try:
        path = chunk_path(storage_dir, chunk_id)
        data = base64.b64decode(message["data_b64"], validate=True)
        with path.open("wb") as chunk_file:
            chunk_file.write(data)
        send_message(connection, {"type": "STORE_ACK", "chunk_id": chunk_id, "status": "OK"})
    except (KeyError, TypeError, ValueError, OSError) as error:
        send_message(
            connection,
            {"type": "STORE_ACK", "chunk_id": chunk_id, "status": "ERROR", "error": str(error)},
        )


def handle_fetch(connection: socket.socket, message: dict, storage_dir: Path) -> None:
    """Return one stored chunk or a not_found response."""
    chunk_id = message.get("chunk_id")
    print(f"FETCH received: {chunk_id}")
    try:
        path = chunk_path(storage_dir, chunk_id)
        if not path.exists():
            send_message(
                connection,
                {"type": "FETCH_RESULT", "chunk_id": chunk_id, "status": "ERROR", "error": "not_found"},
            )
            return

        data_b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        send_message(
            connection,
            {"type": "FETCH_RESULT", "chunk_id": chunk_id, "data_b64": data_b64, "status": "OK"},
        )
    except (TypeError, ValueError, OSError) as error:
        send_message(
            connection,
            {"type": "FETCH_RESULT", "chunk_id": chunk_id, "status": "ERROR", "error": str(error)},
        )


def handle_connection(connection: socket.socket, address: tuple[str, int], storage_dir: Path) -> None:
    """Serve a single request, then close the short-lived client connection."""
    with connection:
        connection.settimeout(SOCKET_TIMEOUT_SECONDS)
        try:
            message = receive_message(connection)
            message_type = message.get("type")
            if message_type == "STORE":
                handle_store(connection, message, storage_dir)
            elif message_type == "FETCH":
                handle_fetch(connection, message, storage_dir)
            else:
                send_message(connection, {"type": "ERROR", "error": "unknown_type"})
        except (ConnectionError, socket.timeout, UnicodeDecodeError, json.JSONDecodeError, OSError) as error:
            print(f"Connection from {address} ended with error: {error}")


def run_server(port: int, node_id: str, coordinator_host: str, coordinator_port: int) -> None:
    """Run the local STORE/FETCH server and its background heartbeat sender."""
    storage_dir = Path(__file__).resolve().parent.parent / "node_data" / node_id
    storage_dir.mkdir(parents=True, exist_ok=True)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, port))
    server.listen()
    print(f"Node {node_id} listening on {HOST}:{port}; storing chunks in {storage_dir}")
    stop_event = threading.Event()
    threading.Thread(
        target=heartbeat_loop,
        args=(node_id, coordinator_host, coordinator_port, stop_event),
        daemon=True,
    ).start()

    try:
        while True:
            connection, address = server.accept()
            threading.Thread(
                target=handle_connection,
                args=(connection, address, storage_dir),
                daemon=True,
            ).start()
    except KeyboardInterrupt:
        print("Shutting down node server.")
    finally:
        stop_event.set()
        server.close()


def parse_args() -> argparse.Namespace:
    """Parse the local node identity and listening port."""
    parser = argparse.ArgumentParser(description="P2P storage node")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--node-id", required=True)
    parser.add_argument("--coordinator-host", default="127.0.0.1")
    parser.add_argument("--coordinator-port", type=int, default=COORDINATOR_PORT)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    run_server(arguments.port, arguments.node_id, arguments.coordinator_host, arguments.coordinator_port)
