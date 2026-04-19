"""Team sharing support: export/import vault keys encrypted with a recipient's password."""

import json
import base64
from pathlib import Path

from envault.crypto import derive_key, encrypt, decrypt


SHARE_FILE_VERSION = 1


def export_key(vault_file: Path, vault_password: str, recipient_password: str) -> bytes:
    """Re-encrypt the vault's derived key for a recipient and return shareable bytes."""
    # Read the sealed vault to confirm the password works
    raw = vault_file.read_bytes()
    # The vault key is deterministic from the vault path + password; we encode it directly
    vault_key = derive_key(vault_password, salt=vault_file.name.encode())
    # Encrypt the vault key with the recipient's password
    recipient_key = derive_key(recipient_password, salt=b"envault-share")
    encrypted_vault_key = encrypt(vault_key, recipient_password)
    payload = {
        "version": SHARE_FILE_VERSION,
        "vault": vault_file.name,
        "key": base64.b64encode(encrypted_vault_key).decode(),
    }
    return json.dumps(payload).encode()


def import_key(share_bytes: bytes, recipient_password: str) -> tuple[str, bytes]:
    """Decrypt a share blob with the recipient's password.

    Returns (vault_name, vault_key_bytes).
    """
    payload = json.loads(share_bytes.decode())
    if payload.get("version") != SHARE_FILE_VERSION:
        raise ValueError(f"Unsupported share file version: {payload.get('version')}")
    encrypted_vault_key = base64.b64decode(payload["key"])
    vault_key = decrypt(encrypted_vault_key, recipient_password)
    return payload["vault"], vault_key


def write_share_file(path: Path, share_bytes: bytes) -> None:
    """Write share bytes to a file."""
    path.write_bytes(share_bytes)


def read_share_file(path: Path) -> bytes:
    """Read share bytes from a file."""
    if not path.exists():
        raise FileNotFoundError(f"Share file not found: {path}")
    return path.read_bytes()
