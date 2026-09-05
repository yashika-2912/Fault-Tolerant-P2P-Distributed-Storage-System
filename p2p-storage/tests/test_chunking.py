"""Tests for coordinator.chunking."""

from coordinator.chunking import reassemble, split_file


def test_split_and_reassemble_round_trip_with_partial_last_chunk():
    """A non-multiple input preserves its shorter final chunk exactly."""
    chunk_size = 1024
    original = (b"chunk-data-" * 300) + b"final"

    chunks = split_file(original, chunk_size=chunk_size)

    assert len(original) % chunk_size != 0
    assert len(chunks[-1]) == len(original) % chunk_size
    assert reassemble(chunks) == original


def test_small_chunk_size_has_expected_chunk_boundaries():
    """Chunk boundaries are deterministic and do not pad the final chunk."""
    chunks = split_file(b"abcdefghijklmnopqrstuvwxyz", chunk_size=16)

    assert chunks == [b"abcdefghijklmnop", b"qrstuvwxyz"]


def test_empty_input_returns_no_chunks():
    """The documented empty-input representation is an empty list."""
    assert split_file(b"") == []
    assert reassemble([]) == b""


def test_splitting_same_input_is_deterministic():
    """Identical input yields identical ordered chunks on every call."""
    original = b"deterministic bytes" * 20
    assert split_file(original, chunk_size=16) == split_file(original, chunk_size=16)
