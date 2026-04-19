"""Tag management for vault entries — attach searchable labels to .env files."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List

_TAGS_FILE = Path.home() / ".envault" / "tags.json"


def _load_tags() -> Dict[str, List[str]]:
    if not _TAGS_FILE.exists():
        return {}
    return json.loads(_TAGS_FILE.read_text())


def _save_tags(data: Dict[str, List[str]]) -> None:
    _TAGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _TAGS_FILE.write_text(json.dumps(data, indent=2))


def add_tag(env_path: str, tag: str) -> None:
    """Add a tag to an env file entry."""
    data = _load_tags()
    tags = data.setdefault(env_path, [])
    if tag not in tags:
        tags.append(tag)
    _save_tags(data)


def remove_tag(env_path: str, tag: str) -> None:
    """Remove a tag from an env file entry."""
    data = _load_tags()
    tags = data.get(env_path, [])
    if tag not in tags:
        raise KeyError(f"Tag '{tag}' not found for '{env_path}'")
    tags.remove(tag)
    if not tags:
        del data[env_path]
    _save_tags(data)


def get_tags(env_path: str) -> List[str]:
    """Return all tags for an env file entry."""
    return _load_tags().get(env_path, [])


def find_by_tag(tag: str) -> List[str]:
    """Return all env paths that have the given tag."""
    return [path for path, tags in _load_tags().items() if tag in tags]


def clear_tags(env_path: str) -> None:
    """Remove all tags for an env file entry."""
    data = _load_tags()
    data.pop(env_path, None)
    _save_tags(data)
