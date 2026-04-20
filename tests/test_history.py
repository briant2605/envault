"""Tests for envault.history module."""

import pytest
from pathlib import Path
from unittest.mock import patch
from envault.history import record, get_history, clear_history, _history_path


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\n")
    return f


@pytest.fixture(autouse=True)
def isolated_history(tmp_path, monkeypatch):
    history_dir = tmp_path / "history"
    import envault.history as h
    monkeypatch.setattr(h, "_HISTORY_DIR", history_dir)
    yield history_dir


def test_get_history_empty(env_file):
    entries = get_history(env_file)
    assert entries == []


def test_record_creates_entry(env_file):
    record(env_file, "lock")
    entries = get_history(env_file)
    assert len(entries) == 1
    assert entries[0]["action"] == "lock"


def test_record_stores_env_file_path(env_file):
    record(env_file, "unlock")
    entries = get_history(env_file)
    assert str(env_file.resolve()) in entries[0]["env_file"]


def test_record_stores_timestamp(env_file):
    record(env_file, "lock")
    entries = get_history(env_file)
    assert "timestamp" in entries[0]
    assert entries[0]["timestamp"].endswith("+00:00")


def test_record_with_note(env_file):
    record(env_file, "lock", note="pre-deploy")
    entries = get_history(env_file)
    assert entries[0]["note"] == "pre-deploy"


def test_multiple_records(env_file):
    record(env_file, "lock")
    record(env_file, "unlock")
    record(env_file, "lock")
    entries = get_history(env_file)
    assert len(entries) == 3
    assert [e["action"] for e in entries] == ["lock", "unlock", "lock"]


def test_clear_history(env_file):
    record(env_file, "lock")
    clear_history(env_file)
    assert get_history(env_file) == []


def test_clear_history_no_file_does_not_raise(env_file):
    clear_history(env_file)  # no history file exists yet
    assert get_history(env_file) == []
