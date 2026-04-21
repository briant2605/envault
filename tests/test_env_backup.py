"""Tests for envault.env_backup."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envault.env_backup import (
    backup_path,
    create_backup,
    delete_backup,
    list_backups,
    purge_backups,
    restore_backup,
)


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("KEY=value\nSECRET=abc\n")
    return f


def test_backup_path_contains_timestamp(env_file: Path) -> None:
    ts = 1700000000
    p = backup_path(env_file, timestamp=ts)
    assert str(ts) in p.name
    assert p.name.endswith(".bak")


def test_create_backup_creates_file(env_file: Path) -> None:
    dest = create_backup(env_file)
    assert dest.exists()
    assert dest.read_text() == env_file.read_text()


def test_create_backup_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        create_backup(tmp_path / "missing.env")


def test_list_backups_empty(env_file: Path) -> None:
    assert list_backups(env_file) == []


def test_list_backups_after_create(env_file: Path) -> None:
    create_backup(env_file)
    backups = list_backups(env_file)
    assert len(backups) == 1


def test_list_backups_sorted_oldest_first(env_file: Path) -> None:
    b1 = create_backup(env_file)
    time.sleep(0.01)
    b2 = create_backup(env_file)
    backups = list_backups(env_file)
    assert backups[0] == b1 or backups[0].name <= backups[1].name
    assert len(backups) == 2


def test_restore_backup_overwrites_file(env_file: Path) -> None:
    backup = create_backup(env_file)
    env_file.write_text("CHANGED=yes\n")
    restore_backup(env_file, backup)
    assert env_file.read_text() == "KEY=value\nSECRET=abc\n"


def test_restore_backup_missing_raises(env_file: Path) -> None:
    with pytest.raises(FileNotFoundError):
        restore_backup(env_file, env_file.parent / "ghost.bak")


def test_delete_backup_removes_file(env_file: Path) -> None:
    backup = create_backup(env_file)
    delete_backup(backup)
    assert not backup.exists()


def test_delete_backup_missing_raises(env_file: Path) -> None:
    with pytest.raises(FileNotFoundError):
        delete_backup(env_file.parent / "nope.bak")


def test_purge_backups_removes_all(env_file: Path) -> None:
    create_backup(env_file)
    create_backup(env_file)
    count = purge_backups(env_file)
    assert count == 2
    assert list_backups(env_file) == []


def test_purge_backups_empty_returns_zero(env_file: Path) -> None:
    assert purge_backups(env_file) == 0
