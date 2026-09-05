"""Day-2 TCP storage node supporting one-request STORE and FETCH connections."""

import argparse
import base64
import json
import socket
import struct
import threading
from pathlib import Path


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


def run_server(port: int, node_id: str) -> None:
    """Run the Day-2 local STORE/FETCH TCP server until interrupted."""
    storage_dir = Path(__file__).resolve().parent.parent / "node_data" / node_id
    storage_dir.mkdir(parents=True, exist_ok=True)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, port))
    server.listen()
    print(f"Node {node_id} listening on {HOST}:{port}; storing chunks in {storage_dir}")

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
        server.close()


def parse_args() -> argparse.Namespace:
    """Parse the local node identity and listening port."""
    parser = argparse.ArgumentParser(description="Day-2 P2P storage node")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--node-id", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    run_server(arguments.port, arguments.node_id)
