"""Search and filter keys across vault files."""

from __future__ import annotations

import fnmatch
from typing import Optional

from envault.vault import vault_path_for, unseal


def search_keys(
    env_file: str,
    password: str,
    pattern: str,
    value_contains: Optional[str] = None,
) -> dict[str, str]:
    """Return key-value pairs from a vault whose keys match *pattern*.

    Args:
        env_file: Path to the original .env file (used to locate the vault).
        password: Decryption password.
        pattern: Shell-style glob pattern matched against key names.
        value_contains: Optional substring that must appear in the value.

    Returns:
        Filtered dict of matching key-value pairs.

    Raises:
        FileNotFoundError: If the vault does not exist.
        ValueError: If decryption fails.
    """
    vault = vault_path_for(env_file)
    if not vault.exists():
        raise FileNotFoundError(f"No vault found for {env_file}")

    plaintext = unseal(env_file, password)
    results: dict[str, str] = {}

    for line in plaintext.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if fnmatch.fnmatch(key, pattern):
            if value_contains is None or value_contains in value:
                results[key] = value

    return results


def list_keys(env_file: str, password: str) -> list[str]:
    """Return all key names stored in the vault."""
    return list(search_keys(env_file, password, pattern="*").keys())
