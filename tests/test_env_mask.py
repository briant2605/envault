"""Tests for envault.env_mask."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_mask import (
    is_sensitive_key,
    mask_value,
    mask_env_text,
    mask_env_file,
    MaskedEntry,
)


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "APP_NAME=myapp\n"
        "DB_PASSWORD=supersecret\n"
        "API_KEY=abc123xyz\n"
        "PORT=8080\n"
        "SECRET_TOKEN=tok-abcdef\n"
    )
    return p


def test_is_sensitive_key_password():
    assert is_sensitive_key("DB_PASSWORD") is True


def test_is_sensitive_key_token():
    assert is_sensitive_key("SECRET_TOKEN") is True


def test_is_sensitive_key_api_key():
    assert is_sensitive_key("API_KEY") is True


def test_is_sensitive_key_plain():
    assert is_sensitive_key("APP_NAME") is False
    assert is_sensitive_key("PORT") is False


def test_is_sensitive_key_extra_pattern():
    assert is_sensitive_key("MY_PIN", extra_patterns=[r"(?i)pin"]) is True


def test_mask_value_long():
    result = mask_value("supersecret", visible=4)
    assert result.endswith("cret")
    assert result.startswith("*")
    assert len(result) == len("supersecret")


def test_mask_value_short():
    result = mask_value("ab", visible=4)
    assert result == "**"


def test_mask_value_empty():
    assert mask_value("") == ""


def test_mask_env_text_sensitive_masked():
    text = "DB_PASSWORD=mysecret\nAPP_NAME=myapp\n"
    entries = mask_env_text(text)
    pw = next(e for e in entries if e.key == "DB_PASSWORD")
    assert pw.is_sensitive is True
    assert pw.masked_value != pw.raw_value
    assert pw.masked_value.endswith(pw.raw_value[-4:])


def test_mask_env_text_non_sensitive_unchanged():
    text = "APP_NAME=myapp\nPORT=8080\n"
    entries = mask_env_text(text)
    for e in entries:
        assert e.masked_value == e.raw_value
        assert e.is_sensitive is False


def test_mask_env_text_returns_all_keys():
    text = "A=1\nB=2\nC=3\n"
    entries = mask_env_text(text)
    assert [e.key for e in entries] == ["A", "B", "C"]


def test_mask_env_file_roundtrip(env_file: Path):
    entries = mask_env_file(env_file)
    keys = [e.key for e in entries]
    assert "APP_NAME" in keys
    assert "DB_PASSWORD" in keys
    pw = next(e for e in entries if e.key == "DB_PASSWORD")
    assert pw.is_sensitive
    assert "*" in pw.masked_value


def test_mask_env_file_missing_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        mask_env_file(tmp_path / "nonexistent.env")


def test_mask_env_text_custom_visible():
    text = "API_KEY=abcdefgh\n"
    entries = mask_env_text(text, visible=2)
    e = entries[0]
    assert e.masked_value.endswith("gh")
    assert e.masked_value.count("*") == len("abcdefgh") - 2
