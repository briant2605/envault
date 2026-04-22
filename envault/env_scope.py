"""Scope support: tag .env keys with named scopes (e.g. dev, prod, test)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


def _scopes_path(env_file: Path) -> Path:
    return env_file.parent / f".{env_file.name}.scopes.json"


def _load_scopes(env_file: Path) -> Dict[str, List[str]]:
    path = _scopes_path(env_file)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_scopes(env_file: Path, data: Dict[str, List[str]]) -> None:
    _scopes_path(env_file).write_text(json.dumps(data, indent=2))


def assign_scope(env_file: Path, key: str, scope: str) -> None:
    """Assign a scope to a key. No-op if already assigned."""
    data = _load_scopes(env_file)
    scopes = data.setdefault(key, [])
    if scope not in scopes:
        scopes.append(scope)
    _save_scopes(env_file, data)


def remove_scope(env_file: Path, key: str, scope: str) -> None:
    """Remove a scope from a key. Raises KeyError if key/scope not found."""
    data = _load_scopes(env_file)
    if key not in data or scope not in data[key]:
        raise KeyError(f"Scope '{scope}' not assigned to key '{key}'")
    data[key].remove(scope)
    if not data[key]:
        del data[key]
    _save_scopes(env_file, data)


def get_scopes(env_file: Path, key: str) -> List[str]:
    """Return all scopes assigned to a key."""
    return _load_scopes(env_file).get(key, [])


def keys_in_scope(env_file: Path, scope: str) -> List[str]:
    """Return all keys assigned to a given scope."""
    data = _load_scopes(env_file)
    return [k for k, scopes in data.items() if scope in scopes]


def list_scopes(env_file: Path) -> Dict[str, List[str]]:
    """Return full scope mapping for the env file."""
    return dict(_load_scopes(env_file))
