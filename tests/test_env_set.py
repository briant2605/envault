"""Tests for envault.env_set (set_key, unset_key, get_key)."""

import pytest
from pathlib import Path
from envault.env_set import set_key, unset_key, get_key


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("FOO=bar\nBAZ=qux\n")
    return f


# --- get_key ---

def test_get_key_existing(env_file: Path) -> None:
    assert get_key(env_file, "FOO") == "bar"


def test_get_key_second_key(env_file: Path) -> None:
    assert get_key(env_file, "BAZ") == "qux"


def test_get_key_missing_returns_none(env_file: Path) -> None:
    assert get_key(env_file, "NOPE") is None


def test_get_key_missing_file_returns_none(tmp_path: Path) -> None:
    assert get_key(tmp_path / ".env", "KEY") is None


# --- set_key ---

def test_set_key_updates_existing(env_file: Path) -> None:
    set_key(env_file, "FOO", "newval")
    assert get_key(env_file, "FOO") == "newval"


def test_set_key_adds_new_key(env_file: Path) -> None:
    set_key(env_file, "NEW", "123")
    assert get_key(env_file, "NEW") == "123"


def test_set_key_preserves_other_keys(env_file: Path) -> None:
    set_key(env_file, "FOO", "changed")
    assert get_key(env_file, "BAZ") == "qux"


def test_set_key_creates_file_if_missing(tmp_path: Path) -> None:
    path = tmp_path / ".env"
    set_key(path, "A", "1")
    assert path.exists()
    assert get_key(path, "A") == "1"


def test_set_key_file_ends_with_newline(env_file: Path) -> None:
    set_key(env_file, "FOO", "val")
    assert env_file.read_text().endswith("\n")


# --- unset_key ---

def test_unset_key_removes_key(env_file: Path) -> None:
    unset_key(env_file, "FOO")
    assert get_key(env_file, "FOO") is None


def test_unset_key_preserves_other_keys(env_file: Path) -> None:
    unset_key(env_file, "FOO")
    assert get_key(env_file, "BAZ") == "qux"


def test_unset_key_missing_key_raises(env_file: Path) -> None:
    with pytest.raises(KeyError, match="NOPE"):
        unset_key(env_file, "NOPE")


def test_unset_key_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(KeyError):
        unset_key(tmp_path / ".env", "KEY")
