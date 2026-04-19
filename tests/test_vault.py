"""Tests for envault.vault seal/unseal operations."""

import pytest
from pathlib import Path
from envault.vault import seal, unseal, vault_path_for


PASSWORD = "vault-test-password"
ENV_CONTENT = "API_KEY=test123\nDEBUG=true\n"


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(ENV_CONTENT, encoding="utf-8")
    return str(p)


def test_vault_path_for():
    assert vault_path_for(".env") == Path(".vault")
    assert vault_path_for("config.env") == Path("config.vault")


def test_seal_creates_vault_file(env_file, tmp_path):
    vault_out = str(tmp_path / ".env.vault")
    result = seal(env_file, PASSWORD, vault_out)
    assert Path(result).exists()
    assert Path(result).stat().st_size > 0


def test_seal_unseal_roundtrip(env_file, tmp_path):
    vault_out = str(tmp_path / ".env.vault")
    env_out = str(tmp_path / "recovered.env")
    seal(env_file, PASSWORD, vault_out)
    unseal(vault_out, PASSWORD, env_out)
    assert Path(env_out).read_text(encoding="utf-8") == ENV_CONTENT


def test_seal_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        seal(str(tmp_path / "nonexistent.env"), PASSWORD)


def test_unseal_wrong_password_raises(env_file, tmp_path):
    vault_out = str(tmp_path / ".env.vault")
    seal(env_file, PASSWORD, vault_out)
    with pytest.raises(ValueError):
        unseal(vault_out, "wrong-password")
