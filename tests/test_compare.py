"""Tests for envault.compare module."""

from pathlib import Path

import pytest

from envault.compare import (
    CompareResult,
    _parse_env,
    compare_env_files,
    compare_env_texts,
    compare_vault_with_snapshot,
)
from envault.vault import seal
from envault.snapshot import save_snapshot


LEFT = """KEY_A=alpha
KEY_B=beta
KEY_C=common
"""

RIGHT = """KEY_B=changed
KEY_C=common
KEY_D=delta
"""


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text(LEFT)
    return f


# --- _parse_env ---

def test_parse_env_basic():
    result = _parse_env("FOO=bar\nBAZ=qux\n")
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_parse_env_ignores_comments_and_blanks():
    text = "# comment\n\nFOO=bar\n"
    assert _parse_env(text) == {"FOO": "bar"}


def test_parse_env_strips_quotes():
    assert _parse_env('KEY="value"') == {"KEY": "value"}
    assert _parse_env("KEY='value'") == {"KEY": "value"}


# --- compare_env_texts ---

def test_compare_only_in_left():
    result = compare_env_texts(LEFT, RIGHT)
    assert "KEY_A" in result.only_in_left


def test_compare_only_in_right():
    result = compare_env_texts(LEFT, RIGHT)
    assert "KEY_D" in result.only_in_right


def test_compare_changed():
    result = compare_env_texts(LEFT, RIGHT)
    keys = [k for k, _, _ in result.changed]
    assert "KEY_B" in keys


def test_compare_same():
    result = compare_env_texts(LEFT, RIGHT)
    assert "KEY_C" in result.same


def test_compare_has_differences_true():
    assert compare_env_texts(LEFT, RIGHT).has_differences is True


def test_compare_has_differences_false():
    assert compare_env_texts(LEFT, LEFT).has_differences is False


# --- compare_env_files ---

def test_compare_env_files(tmp_path: Path):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text(LEFT)
    b.write_text(RIGHT)
    result = compare_env_files(a, b)
    assert isinstance(result, CompareResult)
    assert result.has_differences


# --- compare_vault_with_snapshot ---

def test_compare_vault_with_snapshot_same(env_file: Path):
    password = "secret"
    seal(env_file, password)
    save_snapshot(env_file, "snap1", password)
    result = compare_vault_with_snapshot(env_file, password, "snap1")
    assert not result.has_differences


def test_compare_vault_with_snapshot_missing_raises(env_file: Path):
    password = "secret"
    seal(env_file, password)
    with pytest.raises(FileNotFoundError, match="no_such_snap"):
        compare_vault_with_snapshot(env_file, password, "no_such_snap")
