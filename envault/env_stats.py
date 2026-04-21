"""Statistics and summary reporting for .env files."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class EnvStats:
    total_keys: int = 0
    empty_values: int = 0
    commented_lines: int = 0
    blank_lines: int = 0
    duplicate_keys: int = 0
    sensitive_keys: int = 0
    longest_key: str = ""
    longest_value_key: str = ""
    key_lengths: List[int] = field(default_factory=list)
    value_lengths: List[int] = field(default_factory=list)

    def avg_key_length(self) -> float:
        if not self.key_lengths:
            return 0.0
        return sum(self.key_lengths) / len(self.key_lengths)

    def avg_value_length(self) -> float:
        if not self.value_lengths:
            return 0.0
        return sum(self.value_lengths) / len(self.value_lengths)

    def summary(self) -> str:
        lines = [
            f"Total keys      : {self.total_keys}",
            f"Empty values    : {self.empty_values}",
            f"Sensitive keys  : {self.sensitive_keys}",
            f"Duplicate keys  : {self.duplicate_keys}",
            f"Commented lines : {self.commented_lines}",
            f"Blank lines     : {self.blank_lines}",
            f"Avg key length  : {self.avg_key_length():.1f}",
            f"Avg value length: {self.avg_value_length():.1f}",
        ]
        if self.longest_key:
            lines.append(f"Longest key     : {self.longest_key}")
        if self.longest_value_key:
            lines.append(f"Longest value in: {self.longest_value_key}")
        return "\n".join(lines)


_SENSITIVE_RE = re.compile(
    r"(password|passwd|secret|token|api_?key|private|auth|credential)",
    re.IGNORECASE,
)


def _is_sensitive(key: str) -> bool:
    return bool(_SENSITIVE_RE.search(key))


def compute_stats(text: str) -> EnvStats:
    """Compute statistics from raw .env file text."""
    stats = EnvStats()
    seen_keys: Dict[str, int] = {}
    max_key_len = 0
    max_val_len = 0

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            stats.blank_lines += 1
            continue
        if line.startswith("#"):
            stats.commented_lines += 1
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        stats.total_keys += 1
        seen_keys[key] = seen_keys.get(key, 0) + 1
        if not value:
            stats.empty_values += 1
        if _is_sensitive(key):
            stats.sensitive_keys += 1
        stats.key_lengths.append(len(key))
        stats.value_lengths.append(len(value))
        if len(key) > max_key_len:
            max_key_len = len(key)
            stats.longest_key = key
        if len(value) > max_val_len:
            max_val_len = len(value)
            stats.longest_value_key = key

    stats.duplicate_keys = sum(1 for v in seen_keys.values() if v > 1)
    return stats


def compute_stats_file(env_file: Path) -> EnvStats:
    """Compute statistics from a .env file on disk."""
    if not env_file.exists():
        raise FileNotFoundError(f"{env_file} not found")
    return compute_stats(env_file.read_text())
