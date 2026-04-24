"""Truncate long values in .env files for display or storage purposes."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

DEFAULT_MAX_LENGTH = 64
TRUNCATE_SUFFIX = "..."


@dataclass
class TruncatedEntry:
    key: str
    original_value: str
    truncated_value: str
    was_truncated: bool

    def __str__(self) -> str:
        marker = " [truncated]" if self.was_truncated else ""
        return f"{self.key}={self.truncated_value}{marker}"


def _parse_env(text: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        value = value.strip().strip('"').strip("'")
        pairs.append((key.strip(), value))
    return pairs


def truncate_value(value: str, max_length: int = DEFAULT_MAX_LENGTH) -> str:
    if len(value) <= max_length:
        return value
    return value[:max_length] + TRUNCATE_SUFFIX


def truncate_env_text(
    text: str, max_length: int = DEFAULT_MAX_LENGTH
) -> list[TruncatedEntry]:
    results: list[TruncatedEntry] = []
    for key, value in _parse_env(text):
        trunc = truncate_value(value, max_length)
        results.append(
            TruncatedEntry(
                key=key,
                original_value=value,
                truncated_value=trunc,
                was_truncated=len(value) > max_length,
            )
        )
    return results


def truncate_env_file(
    path: Path, max_length: int = DEFAULT_MAX_LENGTH
) -> list[TruncatedEntry]:
    if not path.exists():
        raise FileNotFoundError(f".env file not found: {path}")
    return truncate_env_text(path.read_text(encoding="utf-8"), max_length)
