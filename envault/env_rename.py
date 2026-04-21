"""Rename or alias keys within a .env file or vault."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple


def _parse_env(text: str) -> List[Tuple[str, str, str]]:
    """Parse env text into list of (key, value, raw_line) tuples.
    Comments and blank lines are preserved as (None, None, raw_line)."""
    result = []
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            result.append((None, None, line))
            continue
        if "=" in stripped:
            key, _, value = stripped.partition("=")
            result.append((key.strip(), value.strip(), line))
        else:
            result.append((None, None, line))
    return result


def _to_dotenv(entries: List[Tuple[str, str, str]]) -> str:
    """Reconstruct .env text from parsed entries."""
    lines = []
    for key, value, raw in entries:
        if key is None:
            lines.append(raw if raw.endswith("\n") else raw + "\n")
        else:
            lines.append(f"{key}={value}\n")
    return "".join(lines)


def rename_key(
    env_text: str,
    old_key: str,
    new_key: str,
    overwrite: bool = False,
) -> str:
    """Rename *old_key* to *new_key* in *env_text*.

    Raises KeyError if old_key is not found.
    Raises ValueError if new_key already exists and overwrite is False.
    """
    entries = _parse_env(env_text)
    keys_present = {e[0] for e in entries if e[0] is not None}

    if old_key not in keys_present:
        raise KeyError(f"Key '{old_key}' not found in env text.")
    if new_key in keys_present and not overwrite:
        raise ValueError(
            f"Key '{new_key}' already exists. Use overwrite=True to replace it."
        )

    updated: List[Tuple[str, str, str]] = []
    for key, value, raw in entries:
        if key == new_key and new_key in keys_present and overwrite:
            # Drop the existing new_key entry so the renamed one takes its place
            continue
        if key == old_key:
            updated.append((new_key, value, raw))
        else:
            updated.append((key, value, raw))

    return _to_dotenv(updated)


def rename_key_in_file(
    env_file: Path,
    old_key: str,
    new_key: str,
    overwrite: bool = False,
) -> None:
    """Rename a key directly in *env_file* (in-place)."""
    text = env_file.read_text()
    updated = rename_key(text, old_key, new_key, overwrite=overwrite)
    env_file.write_text(updated)
