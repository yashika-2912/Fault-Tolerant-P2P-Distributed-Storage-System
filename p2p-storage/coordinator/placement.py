"""Pure deterministic chunk placement across the current active node set."""

import hashlib


def placement_index(chunk_id: str, active_set_size: int) -> int:
    """Map chunk_id to an index using SHA256(chunk_id)'s first eight bytes."""
    if active_set_size <= 0:
        raise ValueError("active_set_size must be positive")
    if not isinstance(chunk_id, str):
        raise TypeError("chunk_id must be a string")

    digest_prefix = hashlib.sha256(chunk_id.encode("utf-8")).digest()[:8]
    return int.from_bytes(digest_prefix, byteorder="big", signed=False) % active_set_size


def replica_set(chunk_id: str, active_nodes: list[str]) -> tuple[str, str]:
    """Return the deterministic primary and secondary nodes for chunk_id."""
    if len(active_nodes) < 2:
        raise ValueError("replication factor R=2 requires at least two active nodes")

    index = placement_index(chunk_id, len(active_nodes))
    primary = active_nodes[index]
    # With two active nodes this always returns both; determinism, not balancing, is the value.
    secondary = active_nodes[(index + 1) % len(active_nodes)]
    return primary, secondary
