"""Day-2 manual verification script; it is not part of the pytest suite.

Start node/node_process.py separately before running this script.
"""

import base64
import json
import socket
import struct


__test__ = False  # This client is run directly, not collected as a pytest test module.

HOST = "127.0.0.1"
PORT = 6001
SOCKET_TIMEOUT_SECONDS = 2


def receive_exact(connection: socket.socket, byte_count: int) -> bytes:
    """Receive exactly byte_count bytes."""
    chunks = bytearray()
    while len(chunks) < byte_count:
        chunk = connection.recv(byte_count - len(chunks))
        if not chunk:
            raise ConnectionError("connection_closed")
        chunks.extend(chunk)
    return bytes(chunks)


def send_request(message: dict) -> dict:
    """Send one framed request through a fresh connection and return its response."""
    payload = json.dumps(message).encode("utf-8")
    with socket.create_connection((HOST, PORT), timeout=SOCKET_TIMEOUT_SECONDS) as connection:
        connection.settimeout(SOCKET_TIMEOUT_SECONDS)
        connection.sendall(struct.pack("!I", len(payload)) + payload)
        response_length = struct.unpack("!I", receive_exact(connection, 4))[0]
        return json.loads(receive_exact(connection, response_length).decode("utf-8"))


def main() -> None:
    """Exercise STORE, FETCH, and missing-chunk behavior against a running node."""
    chunk_id = "chunk_test_1"
    original_data = b"hello world" * 3

    store_response = send_request(
        {"type": "STORE", "chunk_id": chunk_id, "data_b64": base64.b64encode(original_data).decode("ascii")}
    )
    print("STORE_ACK:", store_response)
    assert store_response == {"type": "STORE_ACK", "chunk_id": chunk_id, "status": "OK"}

    fetch_response = send_request({"type": "FETCH", "chunk_id": chunk_id})
    fetched_data = base64.b64decode(fetch_response.get("data_b64", ""))
    if fetch_response.get("status") == "OK" and fetched_data == original_data:
        print("FETCH existing chunk: PASS")
    else:
        print("FETCH existing chunk: FAIL", fetch_response)
        raise AssertionError("fetched data did not match stored data")

    missing_response = send_request({"type": "FETCH", "chunk_id": "chunk_nonexistent"})
    if missing_response.get("status") == "ERROR" and missing_response.get("error") == "not_found":
        print("FETCH missing chunk: PASS")
    else:
        print("FETCH missing chunk: FAIL", missing_response)
        raise AssertionError("missing chunk did not return not_found")

    print("Day-2 manual verification: PASS")


if __name__ == "__main__":
    main()
