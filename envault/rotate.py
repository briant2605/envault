"""Key rotation support for envault vaults."""

from pathlib import Path
from envault.vault import vault_path_for, seal, unseal
from envault.audit import record_event


def rotate_key(env_path: str | Path, old_password: str, new_password: str) -> None:
    """Re-encrypt a vault with a new password.

    Decrypts the existing vault using old_password, then re-encrypts the
    plaintext with new_password. The original .env file is not modified.

    Args:
        env_path: Path to the .env file whose vault should be rotated.
        old_password: Current encryption password.
        new_password: New encryption password to use.

    Raises:
        FileNotFoundError: If the vault file does not exist.
        ValueError: If old_password is incorrect (propagated from unseal).
    """
    env_path = Path(env_path)
    vault = vault_path_for(env_path)

    if not vault.exists():
        raise FileNotFoundError(f"No vault found for {env_path}. Run 'envault lock' first.")

    plaintext = unseal(env_path, old_password)
    seal(env_path, new_password, source=None, plaintext=plaintext)

    record_event("rotate", str(env_path))


def vault_exists(env_path: str | Path) -> bool:
    """Return True if a vault file exists for the given .env path."""
    return vault_path_for(Path(env_path)).exists()
