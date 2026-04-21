"""Tests for envault.env_pin."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_pin import (
    clear_pins,
    get_pinned,
    is_pinned,
    pin_key,
    unpin_key,
)


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("FOO=bar\nBAZ=qux\n")
    return f


def test_get_pinned_empty(env_file: Path) -> None:
    assert get_pinned(env_file) == []


def test_pin_key_creates_entry(env_file: Path) -> None:
    pin_key(env_file, "FOO")
    assert "FOO" in get_pinned(env_file)


def test_pin_key_no_duplicates(env_file: Path) -> None:
    pin_key(env_file, "FOO")
    pin_key(env_file, "FOO")
    assert get_pinned(env_file).count("FOO") == 1


def test_pin_multiple_keys(env_file: Path) -> None:
    pin_key(env_file, "FOO")
    pin_key(env_file, "BAZ")
    pinned = get_pinned(env_file)
    assert "FOO" in pinned
    assert "BAZ" in pinned


def test_is_pinned_true(env_file: Path) -> None:
    pin_key(env_file, "FOO")
    assert is_pinned(env_file, "FOO") is True


def test_is_pinned_false(env_file: Path) -> None:
    assert is_pinned(env_file, "FOO") is False


def test_unpin_key_removes_entry(env_file: Path) -> None:
    pin_key(env_file, "FOO")
    unpin_key(env_file, "FOO")
    assert "FOO" not in get_pinned(env_file)


def test_unpin_key_not_pinned_raises(env_file: Path) -> None:
    with pytest.raises(KeyError, match="FOO"):
        unpin_key(env_file, "FOO")


def test_clear_pins_removes_all(env_file: Path) -> None:
    pin_key(env_file, "FOO")
    pin_key(env_file, "BAZ")
    clear_pins(env_file)
    assert get_pinned(env_file) == []


def test_pins_are_isolated_per_file(tmp_path: Path) -> None:
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("FOO=1\n")
    b.write_text("FOO=2\n")
    pin_key(a, "FOO")
    assert is_pinned(a, "FOO") is True
    assert is_pinned(b, "FOO") is False
