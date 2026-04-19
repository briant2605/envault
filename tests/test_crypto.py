"""Tests for envault.crypto encryption/decryption."""

import pytest
from envault.crypto import encrypt, decrypt


PASSWORD = "super-secret-passphrase"
PLAINTEXT = "DATABASE_URL=postgres://localhost/mydb\nSECRET_KEY=abc123\n"


def test_encrypt_returns_bytes():
    result = encrypt(PLAINTEXT, PASSWORD)
    assert isinstance(result, bytes)


def test_encrypt_decrypt_roundtrip():
    cipherdata = encrypt(PLAINTEXT, PASSWORD)
    recovered = decrypt(cipherdata, PASSWORD)
    assert recovered == PLAINTEXT


def test_different_encryptions_produce_different_output():
    c1 = encrypt(PLAINTEXT, PASSWORD)
    c2 = encrypt(PLAINTEXT, PASSWORD)
    assert c1 != c2  # random salt ensures uniqueness


def test_decrypt_wrong_password_raises():
    cipherdata = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(cipherdata, "wrong-password")


def test_decrypt_corrupted_data_raises():
    cipherdata = bytearray(encrypt(PLAINTEXT, PASSWORD))
    cipherdata[20] ^= 0xFF  # flip a byte in the token area
    with pytest.raises(ValueError):
        decrypt(bytes(cipherdata), PASSWORD)
