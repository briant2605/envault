"""Vault file read/write operations for envault."""

import os
from pathlib import Path
from envault.crypto import encrypt, decrypt

DEFAULT_VAULT_EXT = ".vault"


def vault_path_for(env_file: str) -> Path:
    """Return the vault file path corresponding to an env file."""
    p = Path(env_file)
    return p.with_suffix(DEFAULT_VAULT_EXT)


def seal(env_file: str, password: str, vault_file: str | None = None) -> Path:
    """
    Encrypt an .env file and write it to a vault file.
    Returns the path of the created vault file.
    """
    env_path = Path(env_file)
    if not env_path.exists():
        raise FileNotFoundError(f"Env file not found: {env_file}")

    plaintext = env_path.read_text(encoding="utf-8")
    cipherdata = encrypt(plaintext, password)

    out_path = Path(vault_file) if vault_file else vault_path_for(env_file)
    out_path.write_bytes(cipherdata)
    return out_path


def unseal(vault_file: str, password: str, env_file: str | None = None) -> Path:
    """
    Decrypt a vault file and write the plaintext to an .env file.
    Returns the path of the written env file.
    """
    vault_path = Path(vault_file)
    if not vault_path.exists():
        raise FileNotFoundError(f"Vault file not found: {vault_file}")

    cipherdata = vault_path.read_bytes()
    plaintext = decrypt(cipherdata, password)

    out_path = Path(env_file) if env_file else vault_path.with_suffix(".env")
    out_path.write_text(plaintext, encoding="utf-8")
    return out_path
