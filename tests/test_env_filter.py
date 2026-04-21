"""Tests for envault.env_filter."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_filter import (
    filter_by_prefix,
    filter_by_suffix,
    filter_by_glob,
    filter_by_regex,
    filter_env_text,
    filter_env_file,
    _parse_env,
)

SAMPLE = """
DB_HOST=localhost
DB_PORT=5432
DB_PASSWORD=secret
APP_NAME=myapp
APP_ENV=production
SECRET_KEY=abc123
# a comment
EMPTY=
"""


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(SAMPLE)
    return p


def test_parse_env_basic():
    result = _parse_env("KEY=value\nOTHER=123")
    assert result == {"KEY": "value", "OTHER": "123"}


def test_parse_env_ignores_comments():
    result = _parse_env("# comment\nKEY=val")
    assert "# comment" not in result
    assert result["KEY"] == "val"


def test_filter_by_prefix():
    env = _parse_env(SAMPLE)
    result = filter_by_prefix(env, "DB_")
    assert set(result.keys()) == {"DB_HOST", "DB_PORT", "DB_PASSWORD"}


def test_filter_by_suffix():
    env = _parse_env(SAMPLE)
    result = filter_by_suffix(env, "_NAME")
    assert set(result.keys()) == {"APP_NAME"}


def test_filter_by_glob():
    env = _parse_env(SAMPLE)
    result = filter_by_glob(env, "APP_*")
    assert set(result.keys()) == {"APP_NAME", "APP_ENV"}


def test_filter_by_glob_no_match():
    env = _parse_env(SAMPLE)
    result = filter_by_glob(env, "NOPE_*")
    assert result == {}


def test_filter_by_regex():
    env = _parse_env(SAMPLE)
    result = filter_by_regex(env, r"^DB_")
    assert all(k.startswith("DB_") for k in result)


def test_filter_env_text_prefix_and_suffix():
    result = filter_env_text(SAMPLE, prefix="DB_", suffix="_PASSWORD")
    assert set(result.keys()) == {"DB_PASSWORD"}


def test_filter_env_text_no_criteria_returns_all():
    result = filter_env_text(SAMPLE)
    assert "DB_HOST" in result
    assert "APP_NAME" in result


def test_filter_env_file_existing(env_file: Path):
    result = filter_env_file(env_file, prefix="APP_")
    assert "APP_NAME" in result
    assert "APP_ENV" in result
    assert "DB_HOST" not in result


def test_filter_env_file_missing(tmp_path: Path):
    result = filter_env_file(tmp_path / "nonexistent.env", prefix="X")
    assert result == {}


def test_filter_env_text_glob_and_regex():
    result = filter_env_text(SAMPLE, glob="*_KEY", regex=r"SECRET")
    assert "SECRET_KEY" in result
