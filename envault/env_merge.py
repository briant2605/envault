"""Merge two .env files with conflict resolution strategies."""
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Dict, List, Tuple


class MergeStrategy(str, Enum):
    OURS = "ours"       # keep values from base file on conflict
    THEIRS = "theirs"   # take values from other file on conflict
    UNION = "union"     # include all keys; base wins on conflict


MergeConflict = Tuple[str, str, str]  # (key, base_val, other_val)


def _parse_env(text: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip().strip('"').strip("'")
        result[key.strip()] = value
    return result


def merge_env_texts(
    base: str,
    other: str,
    strategy: MergeStrategy = MergeStrategy.OURS,
) -> Tuple[Dict[str, str], List[MergeConflict]]:
    """Merge two env texts. Returns (merged_dict, conflicts)."""
    base_map = _parse_env(base)
    other_map = _parse_env(other)
    conflicts: List[MergeConflict] = []
    merged: Dict[str, str] = dict(base_map)

    for key, other_val in other_map.items():
        if key not in merged:
            merged[key] = other_val
        elif merged[key] != other_val:
            conflicts.append((key, merged[key], other_val))
            if strategy == MergeStrategy.THEIRS:
                merged[key] = other_val
            # OURS and UNION both keep base value

    return merged, conflicts


def merge_env_files(
    base_path: Path,
    other_path: Path,
    output_path: Path,
    strategy: MergeStrategy = MergeStrategy.OURS,
) -> List[MergeConflict]:
    """Merge two .env files and write result to output_path."""
    base_text = base_path.read_text() if base_path.exists() else ""
    other_text = other_path.read_text() if other_path.exists() else ""
    merged, conflicts = merge_env_texts(base_text, other_text, strategy)
    lines = [f"{k}={v}" for k, v in sorted(merged.items())]
    output_path.write_text("\n".join(lines) + ("\n" if lines else ""))
    return conflicts
