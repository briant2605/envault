"""Tests for envault.audit module."""

import pytest
from pathlib import Path
from envault.audit import record_event, read_events, clear_events, audit_log_path


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("SECRET=abc\n")
    return f


def test_audit_log_path(env_file):
    log = audit_log_path(env_file)
    assert log.parent == env_file.parent
    assert log.name == ".envault_audit.log"


def test_record_event_creates_log(env_file):
    record_event(env_file, "lock")
    log = audit_log_path(env_file)
    assert log.exists()


def test_record_event_content(env_file):
    record_event(env_file, "lock", user="alice")
    events = read_events(env_file)
    assert len(events) == 1
    assert events[0]["action"] == "lock"
    assert events[0]["user"] == "alice"
    assert "timestamp" in events[0]
    assert str(env_file.resolve()) == events[0]["env_file"]


def test_multiple_events(env_file):
    record_event(env_file, "lock", user="alice")
    record_event(env_file, "unlock", user="bob")
    events = read_events(env_file)
    assert len(events) == 2
    assert events[0]["action"] == "lock"
    assert events[1]["action"] == "unlock"


def test_read_events_no_log(env_file):
    events = read_events(env_file)
    assert events == []


def test_clear_events(env_file):
    record_event(env_file, "lock")
    clear_events(env_file)
    assert read_events(env_file) == []
    assert not audit_log_path(env_file).exists()


def test_clear_events_no_log(env_file):
    # Should not raise even if log doesn't exist
    clear_events(env_file)
