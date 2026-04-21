"""Tests for envault.env_comment."""
from __future__ import annotations

import pytest

from envault.env_comment import (
    set_comment,
    remove_comment,
    get_comment,
    set_comment_in_file,
    remove_comment_in_file,
    get_comment_from_file,
)


SAMPLE = """# config
DB_HOST=localhost
DB_PORT=5432  # default port
SECRET_KEY=abc123
"""


def test_get_comment_existing():
    assert get_comment(SAMPLE, "DB_PORT") == "default port"


def test_get_comment_none_when_absent():
    assert get_comment(SAMPLE, "DB_HOST") is None


def test_get_comment_missing_key_raises():
    with pytest.raises(KeyError, match="MISSING"):
        get_comment(SAMPLE, "MISSING")


def test_set_comment_adds_new():
    result = set_comment(SAMPLE, "DB_HOST", "database host")
    assert "# database host" in result
    assert "DB_HOST=localhost  # database host" in result


def test_set_comment_replaces_existing():
    result = set_comment(SAMPLE, "DB_PORT", "custom port")
    assert "# custom port" in result
    assert "default port" not in result


def test_set_comment_missing_key_raises():
    with pytest.raises(KeyError):
        set_comment(SAMPLE, "NOPE", "hi")


def test_remove_comment_clears_inline():
    result = remove_comment(SAMPLE, "DB_PORT")
    assert "#" not in result.split("DB_PORT")[1].split("\n")[0]


def test_remove_comment_no_op_when_absent():
    result = remove_comment(SAMPLE, "DB_HOST")
    assert "DB_HOST=localhost" in result


def test_remove_comment_missing_key_raises():
    with pytest.raises(KeyError):
        remove_comment(SAMPLE, "GHOST")


def test_set_and_get_roundtrip():
    updated = set_comment(SAMPLE, "SECRET_KEY", "keep this safe")
    assert get_comment(updated, "SECRET_KEY") == "keep this safe"


def test_file_helpers(tmp_path):
    env = tmp_path / ".env"
    env.write_text(SAMPLE)

    set_comment_in_file(env, "DB_HOST", "primary host")
    assert get_comment_from_file(env, "DB_HOST") == "primary host"

    remove_comment_in_file(env, "DB_HOST")
    assert get_comment_from_file(env, "DB_HOST") is None
