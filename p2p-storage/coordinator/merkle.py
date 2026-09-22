"""Deterministic SHA-256 Merkle-root helpers for encrypted chunks."""

from coordinator.crypto import sha256_hash


def merkle_root(leaves: list[str]) -> str | None:
    """Return the root for hexadecimal leaf hashes, duplicating an odd leaf.

    ``None`` represents the root of an empty file; callers store that value as
    SQL NULL rather than inventing a synthetic chunk.
    """
    if not leaves:
        return None
    if any(not isinstance(item, str) for item in leaves):
        raise TypeError("Merkle leaves must be hexadecimal hash strings")
    level = list(leaves)
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [sha256_hash((level[i] + level[i + 1]).encode("ascii")) for i in range(0, len(level), 2)]
    return level[0]


def build_merkle_root(chunks: list[bytes]) -> str | None:
    """Hash chunks and return their deterministic Merkle root."""
    return merkle_root([sha256_hash(chunk) for chunk in chunks])


def verify_merkle_root(chunks: list[bytes], expected_root: str | None) -> bool:
    """Return whether chunks produce the persisted root."""
    return build_merkle_root(chunks) == expected_root
