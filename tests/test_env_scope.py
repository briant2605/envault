"""Tests for envault.env_scope."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_scope import (
    assign_scope,
    get_scopes,
    keys_in_scope,
    list_scopes,
    remove_scope,
)


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("DB_URL=postgres://localhost/db\nSECRET_KEY=abc\n")
    return f


def test_get_scopes_empty(env_file: Path) -> None:
    assert get_scopes(env_file, "DB_URL") == []


def test_assign_scope_creates_entry(env_file: Path) -> None:
    assign_scope(env_file, "DB_URL", "prod")
    assert "prod" in get_scopes(env_file, "DB_URL")


def test_assign_scope_no_duplicates(env_file: Path) -> None:
    assign_scope(env_file, "DB_URL", "dev")
    assign_scope(env_file, "DB_URL", "dev")
    assert get_scopes(env_file, "DB_URL").count("dev") == 1


def test_assign_multiple_scopes(env_file: Path) -> None:
    assign_scope(env_file, "SECRET_KEY", "dev")
    assign_scope(env_file, "SECRET_KEY", "prod")
    scopes = get_scopes(env_file, "SECRET_KEY")
    assert "dev" in scopes
    assert "prod" in scopes


def test_remove_scope(env_file: Path) -> None:
    assign_scope(env_file, "DB_URL", "staging")
    remove_scope(env_file, "DB_URL", "staging")
    assert "staging" not in get_scopes(env_file, "DB_URL")


def test_remove_scope_cleans_empty_key(env_file: Path) -> None:
    assign_scope(env_file, "DB_URL", "test")
    remove_scope(env_file, "DB_URL", "test")
    assert "DB_URL" not in list_scopes(env_file)


def test_remove_scope_missing_raises(env_file: Path) -> None:
    with pytest.raises(KeyError):
        remove_scope(env_file, "DB_URL", "nonexistent")


def test_keys_in_scope(env_file: Path) -> None:
    assign_scope(env_file, "DB_URL", "prod")
    assign_scope(env_file, "SECRET_KEY", "prod")
    assign_scope(env_file, "DB_URL", "dev")
    keys = keys_in_scope(env_file, "prod")
    assert "DB_URL" in keys
    assert "SECRET_KEY" in keys


def test_keys_in_scope_empty(env_file: Path) -> None:
    assert keys_in_scope(env_file, "unknown") == []


def test_list_scopes_returns_all(env_file: Path) -> None:
    assign_scope(env_file, "DB_URL", "dev")
    assign_scope(env_file, "SECRET_KEY", "prod")
    mapping = list_scopes(env_file)
    assert "DB_URL" in mapping
    assert "SECRET_KEY" in mapping


def test_list_scopes_empty(env_file: Path) -> None:
    assert list_scopes(env_file) == {}


def test_scopes_persisted_across_calls(env_file: Path) -> None:
    assign_scope(env_file, "DB_URL", "ci")
    assert "ci" in get_scopes(env_file, "DB_URL")
