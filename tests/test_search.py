"""Tests for envault.search module."""

from __future__ import annotations

import pytest

from envault.vault import seal
from envault.search import search_keys, list_keys


PASSWORD = "test-password"

ENV_CONTENT = """# sample env
DB_HOST=localhost
DB_PORT=5432
DB_PASSWORD=secret
APP_ENV=production
APP_DEBUG=false
"""


@pytest.fixture()
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text(ENV_CONTENT)
    seal(str(f), PASSWORD)
    return str(f)


def test_list_keys_returns_all(env_file):
    keys = list_keys(env_file, PASSWORD)
    assert set(keys) == {"DB_HOST", "DB_PORT", "DB_PASSWORD", "APP_ENV", "APP_DEBUG"}


def test_list_keys_returns_list_type(env_file):
    """Ensure list_keys returns a list, not some other iterable."""
    keys = list_keys(env_file, PASSWORD)
    assert isinstance(keys, list)


def test_search_keys_glob_prefix(env_file):
    result = search_keys(env_file, PASSWORD, "DB_*")
    assert set(result.keys()) == {"DB_HOST", "DB_PORT", "DB_PASSWORD"}


def test_search_keys_exact(env_file):
    result = search_keys(env_file, PASSWORD, "APP_ENV")
    assert result == {"APP_ENV": "production"}


def test_search_keys_no_match(env_file):
    result = search_keys(env_file, PASSWORD, "REDIS_*")
    assert result == {}


def test_search_keys_value_contains(env_file):
    result = search_keys(env_file, PASSWORD, "*", value_contains="local")
    assert result == {"DB_HOST": "localhost"}


def test_search_keys_value_contains_no_match(env_file):
    """Ensure value_contains filter returns empty dict when nothing matches."""
    result = search_keys(env_file, PASSWORD, "*", value_contains="nonexistent")
    assert result == {}


def test_search_keys_missing_vault(tmp_path):
    missing = str(tmp_path / ".env")
    with pytest.raises(FileNotFoundError):
        search_keys(missing, PASSWORD, "*")


def test_search_keys_wrong_password(env_file):
    with pytest.raises(Exception):
        search_keys(env_file, "wrong-password", "*")
