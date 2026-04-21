"""Tests for envault.env_merge."""
from pathlib import Path

import pytest

from envault.env_merge import (
    MergeStrategy,
    merge_env_files,
    merge_env_texts,
)

BASE = """DB_HOST=localhost
DB_PORT=5432
SECRET=abc
"""

OTHER = """DB_HOST=remotehost
DB_PORT=5432
NEW_KEY=hello
"""


def test_merge_no_conflict_adds_new_key():
    merged, conflicts = merge_env_texts(BASE, OTHER)
    assert "NEW_KEY" in merged
    assert merged["NEW_KEY"] == "hello"


def test_merge_ours_keeps_base_on_conflict():
    merged, conflicts = merge_env_texts(BASE, OTHER, MergeStrategy.OURS)
    assert merged["DB_HOST"] == "localhost"
    assert len(conflicts) == 1
    assert conflicts[0] == ("DB_HOST", "localhost", "remotehost")


def test_merge_theirs_takes_other_on_conflict():
    merged, conflicts = merge_env_texts(BASE, OTHER, MergeStrategy.THEIRS)
    assert merged["DB_HOST"] == "remotehost"
    assert len(conflicts) == 1


def test_merge_union_keeps_all_keys():
    merged, _ = merge_env_texts(BASE, OTHER, MergeStrategy.UNION)
    assert "SECRET" in merged
    assert "NEW_KEY" in merged
    assert "DB_HOST" in merged


def test_merge_no_conflict_when_identical():
    _, conflicts = merge_env_texts(BASE, BASE)
    assert conflicts == []


def test_merge_empty_base():
    merged, conflicts = merge_env_texts("", OTHER)
    assert merged == {"DB_HOST": "remotehost", "DB_PORT": "5432", "NEW_KEY": "hello"}
    assert conflicts == []


def test_merge_empty_other():
    merged, conflicts = merge_env_texts(BASE, "")
    assert "SECRET" in merged
    assert conflicts == []


def test_merge_env_files_writes_output(tmp_path: Path):
    base_file = tmp_path / ".env.base"
    other_file = tmp_path / ".env.other"
    out_file = tmp_path / ".env.merged"
    base_file.write_text(BASE)
    other_file.write_text(OTHER)
    conflicts = merge_env_files(base_file, other_file, out_file)
    assert out_file.exists()
    content = out_file.read_text()
    assert "NEW_KEY=hello" in content
    assert len(conflicts) == 1


def test_merge_env_files_default_strategy_ours(tmp_path: Path):
    base_file = tmp_path / ".env.base"
    other_file = tmp_path / ".env.other"
    out_file = tmp_path / ".env.out"
    base_file.write_text(BASE)
    other_file.write_text(OTHER)
    merge_env_files(base_file, other_file, out_file, MergeStrategy.OURS)
    content = out_file.read_text()
    assert "DB_HOST=localhost" in content


def test_merge_ignores_comments_and_blanks():
    text = "# comment\n\nFOO=bar\n"
    merged, _ = merge_env_texts(text, "FOO=baz")
    assert "# comment" not in merged
