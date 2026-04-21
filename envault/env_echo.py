"""env_echo.py — print resolved env vars with optional masking and filtering."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from envault.env_mask import is_sensitive_key, mask_value


def _parse_env(text: str) -> list[tuple[str, str]]:
    """Return (key, value) pairs from env text, skipping comments and blanks."""
    pairs: list[tuple[str, str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            pairs.append((key, value))
    return pairs


def echo_env(
    env_file: Path,
    *,
    mask: bool = False,
    prefix: Optional[str] = None,
    export: bool = False,
) -> list[str]:
    """Return lines representing the resolved env vars.

    Args:
        env_file: Path to the .env file.
        mask: If True, redact sensitive values.
        prefix: If given, only include keys starting with this prefix.
        export: If True, prepend each line with 'export '.

    Returns:
        List of formatted KEY=VALUE strings.
    """
    if not env_file.exists():
        raise FileNotFoundError(f".env file not found: {env_file}")

    text = env_file.read_text(encoding="utf-8")
    pairs = _parse_env(text)

    lines: list[str] = []
    for key, value in pairs:
        if prefix and not key.startswith(prefix):
            continue
        if mask and is_sensitive_key(key):
            value = mask_value(value)
        line = f"{key}={value}"
        if export:
            line = f"export {line}"
        lines.append(line)
    return lines
