"""Tests for envault.cli_chain CLI commands."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_chain import chain_cli


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def env_files(tmp_path: Path):
    base = tmp_path / ".env.base"
    base.write_text("A=1\nB=base\n")
    local = tmp_path / ".env.local"
    local.write_text("B=local\nC=3\n")
    return base, local


def test_chain_run_stdout(runner: CliRunner, env_files):
    base, local = env_files
    result = runner.invoke(chain_cli, ["run", str(base), str(local)])
    assert result.exit_code == 0
    assert "A=1" in result.output
    assert "B=local" in result.output
    assert "C=3" in result.output


def test_chain_run_output_file(runner: CliRunner, env_files, tmp_path: Path):
    base, local = env_files
    out = tmp_path / "merged.env"
    result = runner.invoke(chain_cli, ["run", str(base), str(local), "-o", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    content = out.read_text()
    assert "B=local" in content


def test_chain_preview_shows_source(runner: CliRunner, env_files):
    base, local = env_files
    result = runner.invoke(chain_cli, ["preview", str(base), str(local)])
    assert result.exit_code == 0
    assert "←" in result.output
    assert ".env.local" in result.output


def test_chain_count(runner: CliRunner, env_files):
    base, local = env_files
    result = runner.invoke(chain_cli, ["count", str(base), str(local)])
    assert result.exit_code == 0
    assert result.output.strip() == "3"  # A, B, C


def test_chain_run_missing_file_still_works(runner: CliRunner, env_files, tmp_path):
    base, _ = env_files
    ghost = tmp_path / "ghost.env"
    result = runner.invoke(chain_cli, ["run", str(base), str(ghost)])
    assert result.exit_code == 0
    assert "A=1" in result.output


def test_chain_preview_no_keys(runner: CliRunner, tmp_path: Path):
    empty = tmp_path / "empty.env"
    empty.write_text("# just a comment\n")
    result = runner.invoke(chain_cli, ["preview", str(empty)])
    assert result.exit_code == 0
    assert "No keys" in result.output
