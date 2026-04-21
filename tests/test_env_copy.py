"""Tests for envault.env_copy."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_copy import copy_keys, _parse_env, _to_dotenv


@pytest.fixture()
def src_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env.src"
    p.write_text("FOO=foo\nBAR=bar\nBAZ=baz\n")
    return p


@pytest.fixture()
def dst_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env.dst"
    p.write_text("EXISTING=yes\n")
    return p


def test_parse_env_basic():
    text = "KEY=value\n# comment\n\nOTHER='quoted'\n"
    result = _parse_env(text)
    assert result == {"KEY": "value", "OTHER": "quoted"}


def test_to_dotenv_sorted():
    pairs = {"B": "2", "A": "1"}
    assert _to_dotenv(pairs) == "A=1\nB=2\n"


def test_copy_all_keys(src_file: Path, tmp_path: Path):
    dst = tmp_path / ".env.new"
    written = copy_keys(src_file, dst)
    assert set(written.keys()) == {"FOO", "BAR", "BAZ"}
    assert dst.exists()
    result = _parse_env(dst.read_text())
    assert result["FOO"] == "foo"


def test_copy_specific_keys(src_file: Path, tmp_path: Path):
    dst = tmp_path / ".env.new"
    written = copy_keys(src_file, dst, keys=["FOO", "BAZ"])
    assert set(written.keys()) == {"FOO", "BAZ"}
    result = _parse_env(dst.read_text())
    assert "BAR" not in result


def test_copy_preserves_existing_keys(src_file: Path, dst_file: Path):
    copy_keys(src_file, dst_file)
    result = _parse_env(dst_file.read_text())
    assert result["EXISTING"] == "yes"
    assert result["FOO"] == "foo"


def test_no_overwrite_skips_present_keys(src_file: Path, dst_file: Path):
    dst_file.write_text("FOO=original\n")
    written = copy_keys(src_file, dst_file, keys=["FOO", "BAR"], overwrite=False)
    assert "FOO" not in written
    assert "BAR" in written
    result = _parse_env(dst_file.read_text())
    assert result["FOO"] == "original"


def test_copy_missing_src_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        copy_keys(tmp_path / "nope.env", tmp_path / "dst.env")


def test_copy_missing_keys_raises(src_file: Path, tmp_path: Path):
    dst = tmp_path / ".env.new"
    with pytest.raises(KeyError, match="GHOST"):
        copy_keys(src_file, dst, keys=["FOO", "GHOST"])


def test_copy_creates_dst_if_missing(src_file: Path, tmp_path: Path):
    dst = tmp_path / "brand_new.env"
    assert not dst.exists()
    copy_keys(src_file, dst, keys=["BAR"])
    assert dst.exists()
