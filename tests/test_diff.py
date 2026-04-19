"""Tests for envault.diff."""

from __future__ import annotations

from pathlib import Path

import pytest

from envault.vault import seal
from envault.diff import diff_env, load_env_text, vault_text


ENV_CONTENT = "API_KEY=secret\nDEBUG=true\n"
PASSWORD = "testpass"


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(ENV_CONTENT, encoding="utf-8")
    seal(p, PASSWORD)
    return p


def test_load_env_text_existing(env_file: Path) -> None:
    assert load_env_text(env_file) == ENV_CONTENT


def test_load_env_text_missing(tmp_path: Path) -> None:
    assert load_env_text(tmp_path / ".env") == ""


def test_vault_text_roundtrip(env_file: Path) -> None:
    assert vault_text(env_file, PASSWORD) == ENV_CONTENT


def test_vault_text_no_vault(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text(ENV_CONTENT)
    with pytest.raises(FileNotFoundError):
        vault_text(env, PASSWORD)


def test_diff_env_identical(env_file: Path) -> None:
    """When .env matches vault, diff returns None."""
    result = diff_env(env_file, PASSWORD)
    assert result is None


def test_diff_env_detects_changes(env_file: Path) -> None:
    """When .env is modified after sealing, diff returns a non-empty string."""
    env_file.write_text(ENV_CONTENT + "NEW_VAR=1\n", encoding="utf-8")
    result = diff_env(env_file, PASSWORD)
    assert result is not None
    assert "NEW_VAR" in result
    assert "+++" in result


def test_diff_env_wrong_password(env_file: Path) -> None:
    from envault.crypto import InvalidToken
    with pytest.raises(Exception):
        diff_env(env_file, "wrongpass")
