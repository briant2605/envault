"""env_run.py — Run a subprocess with decrypted .env variables injected into its environment.

This module provides functionality to decrypt a vault, inject the key-value
pairs into a subprocess environment, and execute a given command — without
ever writing the secrets to disk in plaintext.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional

from envault.vault import vault_path_for, unseal


def _parse_env(text: str) -> dict[str, str]:
    """Parse a .env-formatted string into a dictionary.

    Skips blank lines and comments. Strips optional surrounding quotes
    from values.
    """
    result: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        # Strip surrounding quotes (single or double)
        if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
            value = value[1:-1]
        if key:
            result[key] = value
    return result


def build_env(
    env_file: Path,
    password: str,
    override: bool = True,
) -> dict[str, str]:
    """Decrypt the vault for *env_file* and return a merged environment dict.

    Args:
        env_file: Path to the .env file whose vault should be decrypted.
        password: Password used to decrypt the vault.
        override: If True, vault values overwrite existing OS environment
                  variables with the same name.  If False, existing variables
                  are preserved.

    Returns:
        A copy of the current OS environment with vault variables merged in.

    Raises:
        FileNotFoundError: If no vault exists for the given env_file.
        ValueError: If the password is incorrect or the vault is corrupted.
    """
    vault = vault_path_for(env_file)
    if not vault.exists():
        raise FileNotFoundError(
            f"No vault found for '{env_file}'. Run 'envault lock' first."
        )

    plaintext = unseal(env_file, password)
    vault_vars = _parse_env(plaintext)

    merged = dict(os.environ)
    for key, value in vault_vars.items():
        if override or key not in merged:
            merged[key] = value

    return merged


def run_with_env(
    env_file: Path,
    password: str,
    command: list[str],
    override: bool = True,
    cwd: Optional[Path] = None,
) -> int:
    """Execute *command* with decrypted vault variables injected into its env.

    Args:
        env_file: Path to the .env file whose vault should be decrypted.
        password: Password used to decrypt the vault.
        command: The command and its arguments to execute, e.g. ``['python', 'app.py']``.
        override: Whether vault values should override existing env variables.
        cwd: Working directory for the subprocess.  Defaults to the current
             directory.

    Returns:
        The exit code of the subprocess.

    Raises:
        FileNotFoundError: If the vault does not exist or the command is not found.
        ValueError: If the password is incorrect or the vault is corrupted.
    """
    if not command:
        raise ValueError("No command provided to run_with_env.")

    env = build_env(env_file, password, override=override)

    result = subprocess.run(
        command,
        env=env,
        cwd=str(cwd) if cwd else None,
    )
    return result.returncode
