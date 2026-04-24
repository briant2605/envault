"""Tests for envault.env_truncate."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_truncate import (
    DEFAULT_MAX_LENGTH,
    TruncatedEntry,
    truncate_env_file,
    truncate_env_text,
    truncate_value,
)


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    short_val = "short"
    long_val = "x" * 100
    p.write_text(f"SHORT_KEY={short_val}\nLONG_KEY={long_val}\n", encoding="utf-8")
    return p


def test_truncate_value_short_unchanged() -> None:
    assert truncate_value("hello", max_length=10) == "hello"


def test_truncate_value_exact_length_unchanged() -> None:
    value = "a" * 10
    assert truncate_value(value, max_length=10) == value


def test_truncate_value_long_adds_suffix() -> None:
    value = "a" * 20
    result = truncate_value(value, max_length=10)
    assert result == "a" * 10 + "..."


def test_truncate_env_text_returns_entries() -> None:
    text = "FOO=bar\nBAZ=qux\n"
    entries = truncate_env_text(text, max_length=64)
    assert len(entries) == 2
    assert all(isinstance(e, TruncatedEntry) for e in entries)


def test_truncate_env_text_short_not_truncated() -> None:
    text = "KEY=short_value\n"
    entries = truncate_env_text(text, max_length=64)
    assert entries[0].was_truncated is False
    assert entries[0].truncated_value == "short_value"


def test_truncate_env_text_long_is_truncated() -> None:
    long_val = "z" * 100
    text = f"KEY={long_val}\n"
    entries = truncate_env_text(text, max_length=DEFAULT_MAX_LENGTH)
    assert entries[0].was_truncated is True
    assert entries[0].truncated_value.endswith("...")
    assert len(entries[0].truncated_value) == DEFAULT_MAX_LENGTH + 3


def test_truncate_env_text_ignores_comments() -> None:
    text = "# comment\nKEY=val\n"
    entries = truncate_env_text(text)
    assert len(entries) == 1
    assert entries[0].key == "KEY"


def test_truncate_env_text_ignores_blank_lines() -> None:
    text = "\nKEY=val\n\n"
    entries = truncate_env_text(text)
    assert len(entries) == 1


def test_truncate_env_file_roundtrip(env_file: Path) -> None:
    entries = truncate_env_file(env_file, max_length=DEFAULT_MAX_LENGTH)
    keys = [e.key for e in entries]
    assert "SHORT_KEY" in keys
    assert "LONG_KEY" in keys


def test_truncate_env_file_long_key_truncated(env_file: Path) -> None:
    entries = truncate_env_file(env_file, max_length=DEFAULT_MAX_LENGTH)
    long_entry = next(e for e in entries if e.key == "LONG_KEY")
    assert long_entry.was_truncated is True


def test_truncate_env_file_short_key_not_truncated(env_file: Path) -> None:
    entries = truncate_env_file(env_file, max_length=DEFAULT_MAX_LENGTH)
    short_entry = next(e for e in entries if e.key == "SHORT_KEY")
    assert short_entry.was_truncated is False


def test_truncate_env_file_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        truncate_env_file(tmp_path / "nonexistent.env")


def test_truncated_entry_str_format() -> None:
    entry = TruncatedEntry(
        key="MY_KEY",
        original_value="original",
        truncated_value="orig...",
        was_truncated=True,
    )
    assert str(entry) == "MY_KEY=orig... [truncated]"


def test_truncated_entry_str_not_truncated() -> None:
    entry = TruncatedEntry(
        key="MY_KEY",
        original_value="short",
        truncated_value="short",
        was_truncated=False,
    )
    assert str(entry) == "MY_KEY=short"
