"""Tests for envault.snapshot."""

import pytest
from pathlib import Path

from envault.vault import seal
from envault.snapshot import (
    save_snapshot,
    restore_snapshot,
    list_snapshots,
    delete_snapshot,
    snapshot_path,
)


PASSWORD = "snapshotpass"


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=original\nSECRET=abc\n")
    seal(f, PASSWORD)
    return f


def test_save_snapshot_creates_file(env_file):
    dest = save_snapshot(env_file, "v1")
    assert dest.exists()


def test_save_snapshot_no_vault_raises(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("X=1\n")
    with pytest.raises(FileNotFoundError):
        save_snapshot(env_file, "v1")


def test_list_snapshots_empty(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("X=1\n")
    assert list_snapshots(env_file) == []


def test_list_snapshots_after_save(env_file):
    save_snapshot(env_file, "v1")
    save_snapshot(env_file, "v2")
    names = [s["name"] for s in list_snapshots(env_file)]
    assert "v1" in names
    assert "v2" in names


def test_restore_snapshot_roundtrip(env_file, tmp_path):
    from envault.vault import vault_path_for, unseal

    save_snapshot(env_file, "before")

    # overwrite vault with new content
    new_env = tmp_path / ".env2"
    new_env.write_text("KEY=changed\n")
    seal(new_env, PASSWORD)
    import shutil
    shutil.copy2(vault_path_for(new_env), vault_path_for(env_file))

    restore_snapshot(env_file, "before")
    result = unseal(env_file, PASSWORD)
    assert b"original" in result


def test_restore_snapshot_missing_raises(env_file):
    with pytest.raises(FileNotFoundError):
        restore_snapshot(env_file, "nonexistent")


def test_delete_snapshot(env_file):
    save_snapshot(env_file, "to_delete")
    delete_snapshot(env_file, "to_delete")
    names = [s["name"] for s in list_snapshots(env_file)]
    assert "to_delete" not in names
    assert not snapshot_path(env_file, "to_delete").exists()


def test_delete_snapshot_missing_raises(env_file):
    with pytest.raises(FileNotFoundError):
        delete_snapshot(env_file, "ghost")
