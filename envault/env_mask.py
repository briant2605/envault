"""Masking/redacting sensitive .env values for safe display."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

# Keys matching these patterns are considered sensitive by default
_SENSITIVE_PATTERNS: List[re.Pattern] = [
    re.compile(r"(?i)(password|passwd|secret|token|api[_-]?key|private[_-]?key|auth|credential|access[_-]?key)"),
]

_MASK_CHAR = "*"
_VISIBLE_CHARS = 4


@dataclass
class MaskedEntry:
    key: str
    raw_value: str
    masked_value: str
    is_sensitive: bool


def is_sensitive_key(key: str, extra_patterns: Optional[List[str]] = None) -> bool:
    """Return True if the key name looks sensitive."""
    patterns = list(_SENSITIVE_PATTERNS)
    if extra_patterns:
        patterns.extend(re.compile(p) for p in extra_patterns)
    return any(p.search(key) for p in patterns)


def mask_value(value: str, visible: int = _VISIBLE_CHARS) -> str:
    """Partially mask a string, showing only the last `visible` characters."""
    if not value:
        return value
    if len(value) <= visible:
        return _MASK_CHAR * len(value)
    return _MASK_CHAR * (len(value) - visible) + value[-visible:]


def _parse_env(text: str) -> List[tuple[str, str]]:
    pairs: List[tuple[str, str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        pairs.append((key, value))
    return pairs


def mask_env_text(
    text: str,
    extra_patterns: Optional[List[str]] = None,
    visible: int = _VISIBLE_CHARS,
) -> List[MaskedEntry]:
    """Parse env text and return MaskedEntry list with sensitive values masked."""
    entries: List[MaskedEntry] = []
    for key, value in _parse_env(text):
        sensitive = is_sensitive_key(key, extra_patterns)
        masked = mask_value(value, visible) if sensitive else value
        entries.append(MaskedEntry(key=key, raw_value=value, masked_value=masked, is_sensitive=sensitive))
    return entries


def mask_env_file(
    env_path: Path,
    extra_patterns: Optional[List[str]] = None,
    visible: int = _VISIBLE_CHARS,
) -> List[MaskedEntry]:
    """Read an .env file and return masked entries."""
    if not env_path.exists():
        raise FileNotFoundError(f".env file not found: {env_path}")
    return mask_env_text(env_path.read_text(), extra_patterns=extra_patterns, visible=visible)
