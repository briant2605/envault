"""Flatten nested/prefixed env keys into a structured dict or expand a structured dict back."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple


def _parse_env(text: str) -> List[Tuple[str, str]]:
    """Return (key, value) pairs, skipping comments and blank lines."""
    pairs: List[Tuple[str, str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip().strip("'\"")
        if key:
            pairs.append((key, value))
    return pairs


def flatten_to_dict(text: str, separator: str = "__") -> Dict[str, Dict]:
    """Group keys sharing a common prefix into nested dicts.

    E.g. DB__HOST=localhost, DB__PORT=5432 -> {"DB": {"HOST": "localhost", "PORT": "5432"}}
    Keys without the separator are placed under the empty-string top-level group.
    """
    result: Dict[str, Dict] = {}
    for key, value in _parse_env(text):
        if separator in key:
            prefix, _, rest = key.partition(separator)
            result.setdefault(prefix, {})[rest] = value
        else:
            result.setdefault("", {})[key] = value
    return result


def expand_from_dict(nested: Dict[str, Dict], separator: str = "__") -> str:
    """Reverse of flatten_to_dict — produce .env text from nested dict."""
    lines: List[str] = []
    # top-level (no prefix) first
    for key, value in sorted(nested.get("", {}).items()):
        lines.append(f"{key}={value}")
    for prefix, sub in sorted(nested.items()):
        if prefix == "":
            continue
        for key, value in sorted(sub.items()):
            lines.append(f"{prefix}{separator}{key}={value}")
    return "\n".join(lines)


def flatten_env_file(path: Path, separator: str = "__") -> Dict[str, Dict]:
    """Read a .env file and return its flattened representation."""
    if not path.exists():
        raise FileNotFoundError(f".env file not found: {path}")
    return flatten_to_dict(path.read_text(), separator=separator)
