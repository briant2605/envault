"""Tests for envault.env_namespace."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_namespace import (
    assign_namespace,
    delete_namespace,
    find_namespaces_for_key,
    get_namespace_keys,
    list_namespaces,
    remove_from_namespace,
)


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDB_PORT=5432\nAWS_KEY=abc\n")
    return f


def test_list_namespaces_empty(env_file: Path) -> None:
    assert list_namespaces(env_file) == []


def test_assign_namespace_creates_entry(env_file: Path) -> None:
    assign_namespace(env_file, "DB_HOST", "database")
    assert "database" in list_namespaces(env_file)


def test_assign_namespace_no_duplicates(env_file: Path) -> None:
    assign_namespace(env_file, "DB_HOST", "database")
    assign_namespace(env_file, "DB_HOST", "database")
    assert get_namespace_keys(env_file, "database").count("DB_HOST") == 1


def test_assign_multiple_keys_to_namespace(env_file: Path) -> None:
    assign_namespace(env_file, "DB_HOST", "database")
    assign_namespace(env_file, "DB_PORT", "database")
    keys = get_namespace_keys(env_file, "database")
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys


def test_get_namespace_keys_empty(env_file: Path) -> None:
    assert get_namespace_keys(env_file, "nonexistent") == []


def test_remove_from_namespace(env_file: Path) -> None:
    assign_namespace(env_file, "DB_HOST", "database")
    remove_from_namespace(env_file, "DB_HOST", "database")
    assert get_namespace_keys(env_file, "database") == []


def test_remove_from_namespace_missing_key_raises(env_file: Path) -> None:
    assign_namespace(env_file, "DB_HOST", "database")
    with pytest.raises(KeyError):
        remove_from_namespace(env_file, "DB_PORT", "database")


def test_remove_last_key_removes_namespace(env_file: Path) -> None:
    assign_namespace(env_file, "DB_HOST", "database")
    remove_from_namespace(env_file, "DB_HOST", "database")
    assert "database" not in list_namespaces(env_file)


def test_find_namespaces_for_key(env_file: Path) -> None:
    assign_namespace(env_file, "AWS_KEY", "cloud")
    assign_namespace(env_file, "AWS_KEY", "secrets")
    namespaces = find_namespaces_for_key(env_file, "AWS_KEY")
    assert "cloud" in namespaces
    assert "secrets" in namespaces


def test_find_namespaces_for_key_not_assigned(env_file: Path) -> None:
    assert find_namespaces_for_key(env_file, "DB_HOST") == []


def test_delete_namespace(env_file: Path) -> None:
    assign_namespace(env_file, "DB_HOST", "database")
    delete_namespace(env_file, "database")
    assert "database" not in list_namespaces(env_file)


def test_delete_namespace_missing_raises(env_file: Path) -> None:
    with pytest.raises(KeyError):
        delete_namespace(env_file, "ghost")
