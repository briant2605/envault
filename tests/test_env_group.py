"""Tests for envault.env_group."""

from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_group import (
    add_to_group,
    delete_group,
    get_group,
    list_groups,
    remove_from_group,
)


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPI_KEY=secret\n")
    return f


def test_get_group_empty(env_file: Path) -> None:
    assert get_group(env_file, "database") == []


def test_list_groups_empty(env_file: Path) -> None:
    assert list_groups(env_file) == []


def test_add_to_group_creates_entry(env_file: Path) -> None:
    add_to_group(env_file, "database", "DB_HOST")
    assert "DB_HOST" in get_group(env_file, "database")


def test_add_to_group_no_duplicates(env_file: Path) -> None:
    add_to_group(env_file, "database", "DB_HOST")
    add_to_group(env_file, "database", "DB_HOST")
    assert get_group(env_file, "database").count("DB_HOST") == 1


def test_add_multiple_keys_to_group(env_file: Path) -> None:
    add_to_group(env_file, "database", "DB_HOST")
    add_to_group(env_file, "database", "DB_PORT")
    members = get_group(env_file, "database")
    assert "DB_HOST" in members
    assert "DB_PORT" in members


def test_list_groups_returns_all(env_file: Path) -> None:
    add_to_group(env_file, "database", "DB_HOST")
    add_to_group(env_file, "api", "API_KEY")
    groups = list_groups(env_file)
    assert "database" in groups
    assert "api" in groups


def test_remove_from_group(env_file: Path) -> None:
    add_to_group(env_file, "database", "DB_HOST")
    add_to_group(env_file, "database", "DB_PORT")
    remove_from_group(env_file, "database", "DB_HOST")
    assert "DB_HOST" not in get_group(env_file, "database")
    assert "DB_PORT" in get_group(env_file, "database")


def test_remove_last_key_deletes_group(env_file: Path) -> None:
    add_to_group(env_file, "database", "DB_HOST")
    remove_from_group(env_file, "database", "DB_HOST")
    assert "database" not in list_groups(env_file)


def test_remove_missing_key_raises(env_file: Path) -> None:
    add_to_group(env_file, "database", "DB_HOST")
    with pytest.raises(KeyError):
        remove_from_group(env_file, "database", "NONEXISTENT")


def test_remove_from_missing_group_raises(env_file: Path) -> None:
    with pytest.raises(KeyError):
        remove_from_group(env_file, "nonexistent", "DB_HOST")


def test_delete_group(env_file: Path) -> None:
    add_to_group(env_file, "database", "DB_HOST")
    add_to_group(env_file, "database", "DB_PORT")
    delete_group(env_file, "database")
    assert "database" not in list_groups(env_file)


def test_delete_missing_group_raises(env_file: Path) -> None:
    with pytest.raises(KeyError):
        delete_group(env_file, "nonexistent")


def test_groups_persist_across_calls(env_file: Path) -> None:
    add_to_group(env_file, "infra", "DB_HOST")
    # Re-read from disk by calling get_group fresh
    result = get_group(env_file, "infra")
    assert result == ["DB_HOST"]
