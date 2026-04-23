"""Namespace support: group env keys under logical namespaces (e.g. DB_*, AWS_*)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _namespaces_path(env_file: Path) -> Path:
    return env_file.parent / f".{env_file.name}.namespaces.json"


def _load_namespaces(env_file: Path) -> Dict[str, List[str]]:
    path = _namespaces_path(env_file)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_namespaces(env_file: Path, data: Dict[str, List[str]]) -> None:
    _namespaces_path(env_file).write_text(json.dumps(data, indent=2))


def assign_namespace(env_file: Path, key: str, namespace: str) -> None:
    """Assign *key* to *namespace*. A key may belong to multiple namespaces."""
    data = _load_namespaces(env_file)
    members = data.setdefault(namespace, [])
    if key not in members:
        members.append(key)
    _save_namespaces(env_file, data)


def remove_from_namespace(env_file: Path, key: str, namespace: str) -> None:
    """Remove *key* from *namespace*. Raises KeyError if not present."""
    data = _load_namespaces(env_file)
    if namespace not in data or key not in data[namespace]:
        raise KeyError(f"Key '{key}' not in namespace '{namespace}'")
    data[namespace].remove(key)
    if not data[namespace]:
        del data[namespace]
    _save_namespaces(env_file, data)


def get_namespace_keys(env_file: Path, namespace: str) -> List[str]:
    """Return all keys assigned to *namespace*."""
    return list(_load_namespaces(env_file).get(namespace, []))


def list_namespaces(env_file: Path) -> List[str]:
    """Return all namespace names defined for *env_file*."""
    return list(_load_namespaces(env_file).keys())


def find_namespaces_for_key(env_file: Path, key: str) -> List[str]:
    """Return every namespace that contains *key*."""
    data = _load_namespaces(env_file)
    return [ns for ns, keys in data.items() if key in keys]


def delete_namespace(env_file: Path, namespace: str) -> None:
    """Delete an entire namespace. Raises KeyError if it does not exist."""
    data = _load_namespaces(env_file)
    if namespace not in data:
        raise KeyError(f"Namespace '{namespace}' does not exist")
    del data[namespace]
    _save_namespaces(env_file, data)
