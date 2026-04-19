"""Tests for envault.sharing — team key export/import."""

import json
import pytest
from pathlib import Path

from envault.sharing import export_key, import_key, write_share_file, read_share_file
from envault.crypto import derive_key


VAULT_PASSWORD = "owner-secret"
RECIPIENT_PASSWORD = "recipient-secret"
WRONG_PASSWORD = "wrong-password"


@pytest.fixture()
def fake_vault(tmp_path):
    """Create a minimal fake vault file."""
    vault_file = tmp_path / "project.env.vault"
    vault_file.write_bytes(b"fake-sealed-content")
    return vault_file


def test_export_key_returns_bytes(fake_vault):
    result = export_key(fake_vault, VAULT_PASSWORD, RECIPIENT_PASSWORD)
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_export_key_valid_json(fake_vault):
    result = export_key(fake_vault, VAULT_PASSWORD, RECIPIENT_PASSWORD)
    payload = json.loads(result)
    assert payload["version"] == 1
    assert payload["vault"] == fake_vault.name
    assert "key" in payload


def test_import_key_roundtrip(fake_vault):
    share_bytes = export_key(fake_vault, VAULT_PASSWORD, RECIPIENT_PASSWORD)
    vault_name, vault_key = import_key(share_bytes, RECIPIENT_PASSWORD)
    assert vault_name == fake_vault.name
    expected_key = derive_key(VAULT_PASSWORD, salt=fake_vault.name.encode())
    assert vault_key == expected_key


def test_import_key_wrong_password_raises(fake_vault):
    share_bytes = export_key(fake_vault, VAULT_PASSWORD, RECIPIENT_PASSWORD)
    with pytest.raises(Exception):
        import_key(share_bytes, WRONG_PASSWORD)


def test_import_key_bad_version_raises(fake_vault):
    share_bytes = export_key(fake_vault, VAULT_PASSWORD, RECIPIENT_PASSWORD)
    payload = json.loads(share_bytes)
    payload["version"] = 99
    bad_bytes = json.dumps(payload).encode()
    with pytest.raises(ValueError, match="Unsupported share file version"):
        import_key(bad_bytes, RECIPIENT_PASSWORD)


def test_write_and_read_share_file(tmp_path, fake_vault):
    share_bytes = export_key(fake_vault, VAULT_PASSWORD, RECIPIENT_PASSWORD)
    share_path = tmp_path / "team.share"
    write_share_file(share_path, share_bytes)
    loaded = read_share_file(share_path)
    assert loaded == share_bytes


def test_read_share_file_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_share_file(tmp_path / "nonexistent.share")
