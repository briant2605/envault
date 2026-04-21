"""Backup and restore .env files with timestamped archives."""

from __future__ import annotations

import shutil
import time
from pathlib import Path
from typing import List

BACKUP_DIR_NAME = ".envault_backups"


def _backup_dir(env_file: Path) -> Path:
    return env_file.parent / BACKUP_DIR_NAME


def backup_path(env_file: Path, timestamp: int | None = None) -> Path:
    """Return the path for a backup of *env_file* at *timestamp* (epoch seconds)."""
    ts = timestamp if timestamp is not None else int(time.time())
    stem = env_file.name  # e.g. ".env"
    return _backup_dir(env_file) / f"{stem}.{ts}.bak"


def create_backup(env_file: Path) -> Path:
    """Copy *env_file* into the backup directory and return the backup path."""
    if not env_file.exists():
        raise FileNotFoundError(f"env file not found: {env_file}")
    dest = backup_path(env_file)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(env_file, dest)
    return dest


def list_backups(env_file: Path) -> List[Path]:
    """Return all backups for *env_file*, sorted oldest-first."""
    bdir = _backup_dir(env_file)
    if not bdir.exists():
        return []
    prefix = env_file.name + "."
    suffix = ".bak"
    backups = sorted(
        p for p in bdir.iterdir()
        if p.name.startswith(prefix) and p.name.endswith(suffix)
    )
    return backups


def restore_backup(env_file: Path, backup: Path) -> None:
    """Overwrite *env_file* with the contents of *backup*."""
    if not backup.exists():
        raise FileNotFoundError(f"backup not found: {backup}")
    shutil.copy2(backup, env_file)


def delete_backup(backup: Path) -> None:
    """Delete a single backup file."""
    if not backup.exists():
        raise FileNotFoundError(f"backup not found: {backup}")
    backup.unlink()


def purge_backups(env_file: Path) -> int:
    """Delete all backups for *env_file*. Returns count of deleted files."""
    backups = list_backups(env_file)
    for b in backups:
        b.unlink()
    return len(backups)
