"""Pure fixed-size byte chunking helpers.

An empty input is represented by an empty chunk list; no empty chunk is emitted.
"""

from pathlib import Path

from coordinator.config import CHUNK_SIZE


def split_file(file_path_or_bytes: str | Path | bytes, chunk_size: int = CHUNK_SIZE) -> list[bytes]:
    """Split bytes or a file's bytes into ordered, unpadded fixed-size chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if isinstance(file_path_or_bytes, bytes):
        data = file_path_or_bytes
    elif isinstance(file_path_or_bytes, (str, Path)):
        data = Path(file_path_or_bytes).read_bytes()
    else:
        raise TypeError("file_path_or_bytes must be bytes, str, or pathlib.Path")

    return [data[offset : offset + chunk_size] for offset in range(0, len(data), chunk_size)]


def reassemble(chunks: list[bytes]) -> bytes:
    """Concatenate ordered chunks to recover the original bytes exactly."""
    return b"".join(chunks)
