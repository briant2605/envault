"""Detect and remove duplicate keys in .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple


@dataclass
class DuplicateReport:
    duplicates: dict[str, List[int]] = field(default_factory=dict)  # key -> list of line numbers (1-based)

    @property
    def has_duplicates(self) -> bool:
        return bool(self.duplicates)

    def summary(self) -> str:
        if not self.has_duplicates:
            return "No duplicate keys found."
        lines = ["Duplicate keys detected:"]
        for key, linenos in self.duplicates.items():
            lines.append(f"  {key}: lines {', '.join(str(n) for n in linenos)}")
        return "\n".join(lines)


def find_duplicates(env_text: str) -> DuplicateReport:
    """Scan env_text and return a DuplicateReport listing keys that appear more than once."""
    seen: dict[str, List[int]] = {}
    for lineno, raw in enumerate(env_text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key = line.split("=", 1)[0].strip()
        seen.setdefault(key, []).append(lineno)
    duplicates = {k: v for k, v in seen.items() if len(v) > 1}
    return DuplicateReport(duplicates=duplicates)


def dedup_env_text(env_text: str, keep: str = "last") -> str:
    """Return env_text with duplicate keys removed.

    Args:
        env_text: Raw .env file content.
        keep: 'first' keeps the first occurrence; 'last' keeps the final one.
    """
    if keep not in ("first", "last"):
        raise ValueError("keep must be 'first' or 'last'")

    lines = env_text.splitlines(keepends=True)
    key_positions: dict[str, List[int]] = {}

    for idx, raw in enumerate(lines):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key = line.split("=", 1)[0].strip()
        key_positions.setdefault(key, []).append(idx)

    drop: set[int] = set()
    for positions in key_positions.values():
        if len(positions) < 2:
            continue
        to_drop = positions[:-1] if keep == "last" else positions[1:]
        drop.update(to_drop)

    return "".join(line for idx, line in enumerate(lines) if idx not in drop)


def dedup_env_file(env_file: Path, keep: str = "last") -> Tuple[bool, DuplicateReport]:
    """Deduplicate keys in *env_file* in-place.

    Returns (changed, report) where changed is True if the file was rewritten.
    """
    text = env_file.read_text(encoding="utf-8")
    report = find_duplicates(text)
    if not report.has_duplicates:
        return False, report
    cleaned = dedup_env_text(text, keep=keep)
    env_file.write_text(cleaned, encoding="utf-8")
    return True, report
