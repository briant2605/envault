"""Manage key aliases — map a short alias to a canonical .env key."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_ALIASES_FILE = ".envault_aliases.json"


def _aliases_path(env_file: Path) -> Path:
    return env_file.parent / _ALIASES_FILE


def _load_aliases(env_file: Path) -> Dict[str, str]:
    p = _aliases_path(env_file)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_aliases(env_file: Path, aliases: Dict[str, str]) -> None:
    _aliases_path(env_file).write_text(json.dumps(aliases, indent=2))


def add_alias(env_file: Path, alias: str, key: str) -> None:
    """Register *alias* as a shorthand for *key*."""
    aliases = _load_aliases(env_file)
    if alias in aliases:
        raise ValueError(f"Alias '{alias}' already exists (points to '{aliases[alias]}'). Remove it first.")
    aliases[alias] = key
    _save_aliases(env_file, aliases)


def remove_alias(env_file: Path, alias: str) -> None:
    """Delete an existing alias."""
    aliases = _load_aliases(env_file)
    if alias not in aliases:
        raise KeyError(f"Alias '{alias}' not found.")
    del aliases[alias]
    _save_aliases(env_file, aliases)


def resolve_alias(env_file: Path, alias: str) -> Optional[str]:
    """Return the canonical key for *alias*, or None if unknown."""
    return _load_aliases(env_file).get(alias)


def list_aliases(env_file: Path) -> List[Dict[str, str]]:
    """Return all aliases as a list of {alias, key} dicts, sorted by alias."""
    aliases = _load_aliases(env_file)
    return [{"alias": a, "key": k} for a, k in sorted(aliases.items())]
