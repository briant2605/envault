"""Snapshot support: save and restore named snapshots of a vault."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from datetime import datetime, timezone

from envault.vault import vault_path_for


def _snapshot_dir(env_file: Path) -> Path:
    return env_file.parent / ".envault_snapshots" / env_file.name


def snapshot_path(env_file: Path, name: str) -> Path:
    return _snapshot_dir(env_file) / f"{name}.vault"


def save_snapshot(env_file: Path, name: str) -> Path:
    """Copy the current vault file to a named snapshot."""
    src = vault_path_for(env_file)
    if not src.exists():
        raise FileNotFoundError(f"No vault found for {env_file}")
    dest = snapshot_path(env_file, name)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    _write_meta(env_file, name)
    return dest


def restore_snapshot(env_file: Path, name: str) -> None:
    """Overwrite the current vault with a named snapshot."""
    src = snapshot_path(env_file, name)
    if not src.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found for {env_file}")
    dest = vault_path_for(env_file)
    shutil.copy2(src, dest)


def list_snapshots(env_file: Path) -> list[dict]:
    """Return metadata for all snapshots of the given env file."""
    meta_file = _snapshot_dir(env_file) / "meta.json"
    if not meta_file.exists():
        return []
    return json.loads(meta_file.read_text())


def delete_snapshot(env_file: Path, name: str) -> None:
    p = snapshot_path(env_file, name)
    if not p.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found")
    p.unlink()
    metas = [m for m in list_snapshots(env_file) if m["name"] != name]
    meta_file = _snapshot_dir(env_file) / "meta.json"
    meta_file.write_text(json.dumps(metas, indent=2))


def _write_meta(env_file: Path, name: str) -> None:
    meta_file = _snapshot_dir(env_file) / "meta.json"
    metas = list_snapshots(env_file)
    metas = [m for m in metas if m["name"] != name]
    metas.append({"name": name, "created_at": datetime.now(timezone.utc).isoformat()})
    meta_file.write_text(json.dumps(metas, indent=2))
