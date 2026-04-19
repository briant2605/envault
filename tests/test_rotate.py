"""Tests for envault.rotate module."""

import pytest
from pathlib import Path
from envault.vault import seal
from envault.rotate import rotate_key, vault_exists


ENV_CONTENT = b"API_KEY=secret\nDB_URL=postgres://localhost/mydb\n"


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_bytes(ENV_CONTENT)
    return p


def test_vault_exists_false_before_lock(env_file):
    assert vault_exists(env_file) is False


def test_vault_exists_true_after_lock(env_file):
    seal(env_file, "password123")
    assert vault_exists(env_file) is True


def test_rotate_key_roundtrip(env_file):
    seal(env_file, "old_pass")
    rotate_key(env_file, "old_pass", "new_pass")

    from envault.vault import unseal
    result = unseal(env_file, "new_pass")
    assert result == ENV_CONTENT


def test_rotate_key_old_password_no_longer_works(env_file):
    seal(env_file, "old_pass")
    rotate_key(env_file, "old_pass", "new_pass")

    from envault.vault import unseal
    with pytest.raises(Exception):
        unseal(env_file, "old_pass")


def test_rotate_key_wrong_old_password_raises(env_file):
    seal(env_file, "correct_pass")
    with pytest.raises(Exception):
        rotate_key(env_file, "wrong_pass", "new_pass")


def test_rotate_key_no_vault_raises(env_file):
    with pytest.raises(FileNotFoundError, match="No vault found"):
        rotate_key(env_file, "any", "new")


def test_rotate_records_audit_event(env_file, tmp_path):
    seal(env_file, "pass1")
    rotate_key(env_file, "pass1", "pass2")

    from envault.audit import read_events
    events = read_events()
    assert any(e["action"] == "rotate" for e in events)
