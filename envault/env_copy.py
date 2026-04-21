"""Copy or clone variables between .env files with optional key filtering."""

from __future__ import annotations

from pathlib import Path
from typing import Optional


def _parse_env(text: str) -> dict[str, str]:
    """Parse .env text into a key-value dict, skipping comments and blanks."""
    result: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        result[key] = value
    return result


def _to_dotenv(pairs: dict[str, str]) -> str:
    """Serialize key-value pairs back to .env format."""
    return "\n".join(f"{k}={v}" for k, v in sorted(pairs.items())) + "\n"


def copy_keys(
    src_path: Path,
    dst_path: Path,
    keys: Optional[list[str]] = None,
    overwrite: bool = True,
) -> dict[str, str]:
    """Copy variables from src_path to dst_path.

    Args:
        src_path: Source .env file.
        dst_path: Destination .env file (created if missing).
        keys: If provided, only copy these keys; otherwise copy all.
        overwrite: If False, skip keys already present in destination.

    Returns:
        Mapping of keys that were actually written.
    """
    if not src_path.exists():
        raise FileNotFoundError(f"Source file not found: {src_path}")

    src = _parse_env(src_path.read_text())
    dst = _parse_env(dst_path.read_text()) if dst_path.exists() else {}

    candidates = {k: v for k, v in src.items() if keys is None or k in keys}

    if keys:
        missing = set(keys) - set(src)
        if missing:
            raise KeyError(f"Keys not found in source: {sorted(missing)}")

    written: dict[str, str] = {}
    for k, v in candidates.items():
        if not overwrite and k in dst:
            continue
        dst[k] = v
        written[k] = v

    dst_path.write_text(_to_dotenv(dst))
    return written
