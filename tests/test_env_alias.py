"""Tests for envault.env_alias."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_alias import (
    add_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
    _aliases_path,
)


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\n")
    return p


def test_list_aliases_empty(env_file: Path) -> None:
    assert list_aliases(env_file) == []


def test_add_alias_creates_entry(env_file: Path) -> None:
    add_alias(env_file, "host", "DB_HOST")
    entries = list_aliases(env_file)
    assert len(entries) == 1
    assert entries[0] == {"alias": "host", "key": "DB_HOST"}


def test_add_alias_no_duplicates(env_file: Path) -> None:
    add_alias(env_file, "host", "DB_HOST")
    with pytest.raises(ValueError, match="already exists"):
        add_alias(env_file, "host", "DB_PORT")


def test_add_multiple_aliases(env_file: Path) -> None:
    add_alias(env_file, "host", "DB_HOST")
    add_alias(env_file, "port", "DB_PORT")
    entries = list_aliases(env_file)
    assert len(entries) == 2


def test_resolve_alias_returns_key(env_file: Path) -> None:
    add_alias(env_file, "host", "DB_HOST")
    assert resolve_alias(env_file, "host") == "DB_HOST"


def test_resolve_alias_unknown_returns_none(env_file: Path) -> None:
    assert resolve_alias(env_file, "nonexistent") is None


def test_remove_alias(env_file: Path) -> None:
    add_alias(env_file, "host", "DB_HOST")
    remove_alias(env_file, "host")
    assert list_aliases(env_file) == []


def test_remove_alias_missing_raises(env_file: Path) -> None:
    with pytest.raises(KeyError, match="not found"):
        remove_alias(env_file, "ghost")


def test_aliases_persisted_to_disk(env_file: Path) -> None:
    add_alias(env_file, "db", "DB_HOST")
    # Re-read from disk by calling list_aliases again
    result = list_aliases(env_file)
    assert result[0]["alias"] == "db"


def test_aliases_file_location(env_file: Path) -> None:
    p = _aliases_path(env_file)
    assert p.parent == env_file.parent
    assert p.name == ".envault_aliases.json"
