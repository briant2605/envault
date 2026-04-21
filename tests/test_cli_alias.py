"""Tests for envault.cli_alias CLI commands."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_alias import alias_cli
from envault.env_alias import add_alias


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\n")
    return p


def test_alias_add(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(alias_cli, ["add", "host", "DB_HOST", "--env-file", str(env_file)])
    assert result.exit_code == 0
    assert "added" in result.output


def test_alias_add_duplicate_fails(runner: CliRunner, env_file: Path) -> None:
    add_alias(env_file, "host", "DB_HOST")
    result = runner.invoke(alias_cli, ["add", "host", "DB_HOST", "--env-file", str(env_file)])
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_alias_list_empty(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(alias_cli, ["list", "--env-file", str(env_file)])
    assert result.exit_code == 0
    assert "No aliases" in result.output


def test_alias_list_shows_entries(runner: CliRunner, env_file: Path) -> None:
    add_alias(env_file, "host", "DB_HOST")
    result = runner.invoke(alias_cli, ["list", "--env-file", str(env_file)])
    assert result.exit_code == 0
    assert "host" in result.output
    assert "DB_HOST" in result.output


def test_alias_resolve(runner: CliRunner, env_file: Path) -> None:
    add_alias(env_file, "host", "DB_HOST")
    result = runner.invoke(alias_cli, ["resolve", "host", "--env-file", str(env_file)])
    assert result.exit_code == 0
    assert "DB_HOST" in result.output


def test_alias_resolve_unknown_fails(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(alias_cli, ["resolve", "ghost", "--env-file", str(env_file)])
    assert result.exit_code != 0


def test_alias_remove(runner: CliRunner, env_file: Path) -> None:
    add_alias(env_file, "host", "DB_HOST")
    result = runner.invoke(alias_cli, ["remove", "host", "--env-file", str(env_file)])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_alias_remove_missing_fails(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(alias_cli, ["remove", "ghost", "--env-file", str(env_file)])
    assert result.exit_code != 0
