"""Group management for .env keys — tag keys into named groups and retrieve them."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


def _groups_path(env_file: Path) -> Path:
    return env_file.parent / f".{env_file.name}.groups.json"


def _load_groups(env_file: Path) -> Dict[str, List[str]]:
    p = _groups_path(env_file)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_groups(env_file: Path, data: Dict[str, List[str]]) -> None:
    _groups_path(env_file).write_text(json.dumps(data, indent=2))


def add_to_group(env_file: Path, group: str, key: str) -> None:
    """Add *key* to *group*. No-op if already present."""
    data = _load_groups(env_file)
    members = data.setdefault(group, [])
    if key not in members:
        members.append(key)
    _save_groups(env_file, data)


def remove_from_group(env_file: Path, group: str, key: str) -> None:
    """Remove *key* from *group*. Raises KeyError if group or key is absent."""
    data = _load_groups(env_file)
    if group not in data or key not in data[group]:
        raise KeyError(f"Key '{key}' not found in group '{group}'")
    data[group].remove(key)
    if not data[group]:
        del data[group]
    _save_groups(env_file, data)


def get_group(env_file: Path, group: str) -> List[str]:
    """Return list of keys in *group*. Returns empty list if group doesn't exist."""
    return _load_groups(env_file).get(group, [])


def list_groups(env_file: Path) -> List[str]:
    """Return all group names defined for *env_file*."""
    return list(_load_groups(env_file).keys())


def delete_group(env_file: Path, group: str) -> None:
    """Delete an entire group. Raises KeyError if not found."""
    data = _load_groups(env_file)
    if group not in data:
        raise KeyError(f"Group '{group}' not found")
    del data[group]
    _save_groups(env_file, data)
