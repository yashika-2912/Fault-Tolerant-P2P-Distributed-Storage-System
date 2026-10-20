"""AES-256-GCM encryption and SHA-256 hashing helpers.

Encrypted blobs use the self-contained layout ``nonce(12) || ciphertext || tag(16)``.
"""

import hashlib

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from coordinator.config import AES_KEY


NONCE_LENGTH = 12
TAG_LENGTH = 16
AES_256_KEY_LENGTH = 32


def _validate_key(key: bytes) -> None:
    """Require an AES-256 key rather than allowing weaker AES key sizes."""
    if not isinstance(key, bytes) or len(key) != AES_256_KEY_LENGTH:
        raise ValueError("AES-256-GCM requires a 32-byte key")


def aes_encrypt(plaintext: bytes, key: bytes = AES_KEY) -> bytes:
    """Encrypt plaintext as ``nonce(12) || ciphertext || tag(16)`` using AES-256-GCM."""
    _validate_key(key)
    if not isinstance(plaintext, bytes):
        raise TypeError("plaintext must be bytes")

    nonce = get_random_bytes(NONCE_LENGTH)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce, mac_len=TAG_LENGTH)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return nonce + ciphertext + tag


def aes_decrypt(blob: bytes, key: bytes = AES_KEY) -> bytes:
    """Decrypt and authenticate a ``nonce(12) || ciphertext || tag(16)`` blob."""
    _validate_key(key)
    if not isinstance(blob, bytes):
        raise TypeError("blob must be bytes")
    if len(blob) < NONCE_LENGTH + TAG_LENGTH:
        raise ValueError("invalid AES-GCM blob: too short for nonce and authentication tag")

    nonce = blob[:NONCE_LENGTH]
    tag = blob[-TAG_LENGTH:]
    ciphertext = blob[NONCE_LENGTH:-TAG_LENGTH]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce, mac_len=TAG_LENGTH)
    try:
        return cipher.decrypt_and_verify(ciphertext, tag)
    except ValueError as error:
        raise ValueError("AES-GCM authentication failed") from error


def sha256_hash(data: bytes) -> str:
    """Return the lowercase hexadecimal SHA-256 digest of data."""
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")
    return hashlib.sha256(data).hexdigest()
