"""Tests for coordinator.crypto."""

import pytest

from coordinator.crypto import aes_decrypt, aes_encrypt, sha256_hash


TEST_KEY = b"0123456789abcdef0123456789abcdef"


def test_aes_gcm_encrypt_decrypt_round_trip():
    """Authenticated encryption recovers the original plaintext."""
    plaintext = b"confidential chunk payload"
    assert aes_decrypt(aes_encrypt(plaintext, TEST_KEY), TEST_KEY) == plaintext


def test_same_plaintext_encrypts_to_different_blobs():
    """A fresh random nonce makes repeated encryptions distinct."""
    plaintext = b"same input"
    assert aes_encrypt(plaintext, TEST_KEY) != aes_encrypt(plaintext, TEST_KEY)


def test_wrong_key_cannot_decrypt_blob():
    """GCM authentication rejects a ciphertext decrypted with another key."""
    blob = aes_encrypt(b"protected", TEST_KEY)
    wrong_key = b"fedcba9876543210fedcba9876543210"
    with pytest.raises(ValueError, match="authentication failed"):
        aes_decrypt(blob, wrong_key)


def test_tampered_blob_is_rejected():
    """Changing any encrypted byte invalidates the GCM authentication tag."""
    blob = bytearray(aes_encrypt(b"protected", TEST_KEY))
    blob[-1] ^= 1
    with pytest.raises(ValueError, match="authentication failed"):
        aes_decrypt(bytes(blob), TEST_KEY)


def test_sha256_hash_matches_known_abc_vector():
    """The SHA-256 helper matches the published digest for b'abc'."""
    assert sha256_hash(b"abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
