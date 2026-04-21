"""Compare two .env files or vault snapshots side by side."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from envault.diff import load_env_text
from envault.snapshot import snapshot_path, restore_snapshot
from envault.vault import unseal


@dataclass
class CompareResult:
    only_in_left: List[str]
    only_in_right: List[str]
    changed: List[Tuple[str, str, str]]   # (key, left_val, right_val)
    same: List[str]

    @property
    def has_differences(self) -> bool:
        return bool(self.only_in_left or self.only_in_right or self.changed)


def _parse_env(text: str) -> Dict[str, str]:
    """Parse env text into a dict, ignoring comments and blank lines."""
    result: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def compare_env_texts(left: str, right: str) -> CompareResult:
    """Compare two env file texts and return a CompareResult."""
    left_map = _parse_env(left)
    right_map = _parse_env(right)

    left_keys = set(left_map)
    right_keys = set(right_map)

    only_in_left = sorted(left_keys - right_keys)
    only_in_right = sorted(right_keys - left_keys)

    changed: List[Tuple[str, str, str]] = []
    same: List[str] = []

    for key in sorted(left_keys & right_keys):
        if left_map[key] != right_map[key]:
            changed.append((key, left_map[key], right_map[key]))
        else:
            same.append(key)

    return CompareResult(
        only_in_left=only_in_left,
        only_in_right=only_in_right,
        changed=changed,
        same=same,
    )


def compare_env_files(left_path: Path, right_path: Path) -> CompareResult:
    """Compare two env files on disk."""
    left_text = load_env_text(left_path)
    right_text = load_env_text(right_path)
    return compare_env_texts(left_text, right_text)


def compare_vault_with_snapshot(
    env_file: Path,
    password: str,
    snapshot_name: str,
    snapshot_password: Optional[str] = None,
) -> CompareResult:
    """Compare the current vault contents with a named snapshot."""
    current_text = unseal(env_file, password)
    snap_path = snapshot_path(env_file, snapshot_name)
    if not snap_path.exists():
        raise FileNotFoundError(f"Snapshot '{snapshot_name}' not found for {env_file}")
    snap_text = restore_snapshot(env_file, snapshot_name, snapshot_password or password)
    return compare_env_texts(current_text, snap_text)
