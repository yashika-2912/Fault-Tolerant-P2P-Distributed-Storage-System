"""Day-4 direct-run verification of coordinator.node_client against three processes.

Start N1, N2, and N3 separately before running this script. It is not a pytest test.
"""

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from coordinator.node_client import ChunkNotFoundError, NodeCommunicationError, fetch_chunk, store_chunk


__test__ = False

NODES = [("N1", 6001), ("N2", 6002), ("N3", 6003)]
HOST = "127.0.0.1"


def main() -> None:
    """Verify coordinator STORE/FETCH calls over separate node processes."""
    for node_id, port in NODES:
        chunk_id = f"day4_{node_id.lower()}_chunk"
        original_data = f"Day 4 data for {node_id}".encode("utf-8")
        try:
            assert store_chunk(HOST, port, chunk_id, original_data)
            print(f"{node_id} STORE: PASS")
            assert fetch_chunk(HOST, port, chunk_id) == original_data
            print(f"{node_id} FETCH: PASS")
        except (AssertionError, NodeCommunicationError, ChunkNotFoundError) as error:
            print(f"{node_id} round trip: FAIL ({error})")
            raise

    try:
        fetch_chunk(HOST, 6001, "day4_chunk_that_was_never_stored")
    except ChunkNotFoundError:
        print("Missing chunk response: PASS")
    else:
        print("Missing chunk response: FAIL")
        raise AssertionError("missing chunk did not raise ChunkNotFoundError")

    try:
        store_chunk(HOST, 6099, "day4_unreachable_node", b"unreachable")
    except NodeCommunicationError:
        print("Unreachable node response: PASS")
    else:
        print("Unreachable node response: FAIL")
        raise AssertionError("unreachable node did not raise NodeCommunicationError")

    print("Day-4 manual verification: PASS")


if __name__ == "__main__":
    main()
