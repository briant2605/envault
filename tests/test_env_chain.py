"""Tests for envault.env_chain."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_chain import (
    _parse_env,
    _to_dotenv,
    chain_env_texts,
    chain_env_files,
    chain_sources,
)


# ---------------------------------------------------------------------------
# _parse_env
# ---------------------------------------------------------------------------

def test_parse_env_basic():
    text = "A=1\nB=2\n"
    assert _parse_env(text) == {"A": "1", "B": "2"}


def test_parse_env_ignores_comments_and_blanks():
    text = "# comment\n\nA=hello\n"
    assert _parse_env(text) == {"A": "hello"}


def test_parse_env_strips_quotes():
    text = 'KEY="quoted value"\n'
    assert _parse_env(text) == {"KEY": "quoted value"}


# ---------------------------------------------------------------------------
# chain_env_texts
# ---------------------------------------------------------------------------

def test_chain_env_texts_later_overrides():
    base = "A=1\nB=2\n"
    override = "B=99\nC=3\n"
    result = chain_env_texts([base, override])
    assert result == {"A": "1", "B": "99", "C": "3"}


def test_chain_env_texts_single_file():
    text = "X=10\n"
    assert chain_env_texts([text]) == {"X": "10"}


def test_chain_env_texts_empty_list():
    assert chain_env_texts([]) == {}


def test_chain_env_texts_all_empty_strings():
    assert chain_env_texts(["", ""]) == {}


# ---------------------------------------------------------------------------
# chain_env_files
# ---------------------------------------------------------------------------

def test_chain_env_files_missing_file_skipped(tmp_path: Path):
    existing = tmp_path / ".env"
    existing.write_text("A=1\n")
    missing = tmp_path / ".env.missing"
    result = chain_env_files([existing, missing])
    assert result == {"A": "1"}


def test_chain_env_files_override(tmp_path: Path):
    f1 = tmp_path / ".env.base"
    f1.write_text("A=base\nB=base\n")
    f2 = tmp_path / ".env.local"
    f2.write_text("B=local\nC=local\n")
    result = chain_env_files([f1, f2])
    assert result["A"] == "base"
    assert result["B"] == "local"
    assert result["C"] == "local"


# ---------------------------------------------------------------------------
# chain_sources (provenance)
# ---------------------------------------------------------------------------

def test_chain_sources_provenance(tmp_path: Path):
    f1 = tmp_path / "a.env"
    f1.write_text("A=1\nB=1\n")
    f2 = tmp_path / "b.env"
    f2.write_text("B=2\nC=2\n")
    merged, provenance = chain_sources([f1, f2])
    assert provenance["A"] == str(f1)
    assert provenance["B"] == str(f2)  # last-wins
    assert provenance["C"] == str(f2)


def test_chain_sources_missing_file_skipped(tmp_path: Path):
    f1 = tmp_path / "a.env"
    f1.write_text("A=1\n")
    merged, _ = chain_sources([f1, tmp_path / "ghost.env"])
    assert "A" in merged
