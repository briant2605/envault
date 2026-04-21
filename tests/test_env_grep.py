"""Tests for envault.env_grep."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.vault import seal
from envault.env_grep import grep_values, grep_keys_and_values, GrepMatch


PASSWORD = "hunter2"


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text(
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "API_KEY=secret_abc123\n"
        "DEBUG=true\n"
        "# a comment\n"
        "EMPTY=\n"
    )
    seal(f, PASSWORD)
    return f


# --- grep_values ---

def test_grep_values_glob_wildcard(env_file: Path):
    matches = grep_values(env_file, PASSWORD, "secret*")
    assert len(matches) == 1
    assert matches[0].key == "API_KEY"
    assert matches[0].value == "secret_abc123"


def test_grep_values_exact_glob(env_file: Path):
    matches = grep_values(env_file, PASSWORD, "true")
    assert len(matches) == 1
    assert matches[0].key == "DEBUG"


def test_grep_values_no_match(env_file: Path):
    matches = grep_values(env_file, PASSWORD, "nonexistent*")
    assert matches == []


def test_grep_values_regex(env_file: Path):
    matches = grep_values(env_file, PASSWORD, r"\d{4}", use_regex=True)
    assert any(m.key == "DB_PORT" for m in matches)


def test_grep_values_case_insensitive(env_file: Path):
    matches = grep_values(env_file, PASSWORD, "TRUE", case_sensitive=False)
    assert len(matches) == 1
    assert matches[0].key == "DEBUG"


def test_grep_values_case_sensitive_no_match(env_file: Path):
    matches = grep_values(env_file, PASSWORD, "TRUE", case_sensitive=True)
    assert matches == []


def test_grep_values_wrong_password_raises(env_file: Path):
    with pytest.raises(Exception):
        grep_values(env_file, "wrongpass", "*")


def test_grep_values_match_has_line_number(env_file: Path):
    matches = grep_values(env_file, PASSWORD, "localhost")
    assert len(matches) == 1
    assert isinstance(matches[0].line_number, int)
    assert matches[0].line_number >= 1


# --- grep_keys_and_values ---

def test_grep_keys_and_values_matches_key(env_file: Path):
    # pattern matches the full "KEY=value" string
    matches = grep_keys_and_values(env_file, PASSWORD, "DB_*", case_sensitive=True)
    keys = {m.key for m in matches}
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys


def test_grep_keys_and_values_regex_key(env_file: Path):
    matches = grep_keys_and_values(
        env_file, PASSWORD, r"^API_KEY=", use_regex=True
    )
    assert len(matches) == 1
    assert matches[0].key == "API_KEY"


def test_grep_match_str_representation(env_file: Path):
    matches = grep_values(env_file, PASSWORD, "localhost")
    assert "DB_HOST" in str(matches[0])
    assert "localhost" in str(matches[0])
