"""Diff support: compare decrypted vault contents against current .env file."""

from __future__ import annotations

import difflib
from pathlib import Path
from typing import Optional

from envault.vault import vault_path_for, unseal


def load_env_text(env_path: Path) -> str:
    """Read raw text from a .env file, or return empty string if missing."""
    if not env_path.exists():
        return ""
    return env_path.read_text(encoding="utf-8")


def vault_text(env_path: Path, password: str) -> str:
    """Decrypt vault for *env_path* and return its text content."""
    vault = vault_path_for(env_path)
    if not vault.exists():
        raise FileNotFoundError(f"No vault found for {env_path}")
    data = unseal(env_path, password)
    return data.decode("utf-8")


def diff_env(
    env_path: Path,
    password: str,
    context_lines: int = 3,
) -> Optional[str]:
    """Return a unified diff string between the vault snapshot and the current
    .env file, or *None* when the files are identical."""
    sealed = vault_text(env_path, password)
    current = load_env_text(env_path)

    if sealed == current:
        return None

    lines_a = sealed.splitlines(keepends=True)
    lines_b = current.splitlines(keepends=True)

    diff = difflib.unified_diff(
        lines_a,
        lines_b,
        fromfile="vault (sealed)",
        tofile=str(env_path),
        n=context_lines,
    )
    return "".join(diff)
