"""Tests for envault.cli_pin CLI commands."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_pin import pin_cli
from envault.env_pin import get_pinned


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("FOO=bar\nBAZ=qux\n")
    return f


def test_pin_add(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(pin_cli, ["add", "FOO", "--env", str(env_file)])
    assert result.exit_code == 0
    assert "Pinned" in result.output
    assert "FOO" in get_pinned(env_file)


def test_pin_list_empty(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(pin_cli, ["list", "--env", str(env_file)])
    assert result.exit_code == 0
    assert "No pinned keys" in result.output


def test_pin_list_shows_keys(runner: CliRunner, env_file: Path) -> None:
    runner.invoke(pin_cli, ["add", "FOO", "--env", str(env_file)])
    runner.invoke(pin_cli, ["add", "BAZ", "--env", str(env_file)])
    result = runner.invoke(pin_cli, ["list", "--env", str(env_file)])
    assert "FOO" in result.output
    assert "BAZ" in result.output


def test_pin_remove(runner: CliRunner, env_file: Path) -> None:
    runner.invoke(pin_cli, ["add", "FOO", "--env", str(env_file)])
    result = runner.invoke(pin_cli, ["remove", "FOO", "--env", str(env_file)])
    assert result.exit_code == 0
    assert "Unpinned" in result.output


def test_pin_remove_not_pinned_fails(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(pin_cli, ["remove", "FOO", "--env", str(env_file)])
    assert result.exit_code != 0


def test_pin_check_pinned(runner: CliRunner, env_file: Path) -> None:
    runner.invoke(pin_cli, ["add", "FOO", "--env", str(env_file)])
    result = runner.invoke(pin_cli, ["check", "FOO", "--env", str(env_file)])
    assert "is pinned" in result.output


def test_pin_check_not_pinned(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(pin_cli, ["check", "FOO", "--env", str(env_file)])
    assert "NOT pinned" in result.output


def test_pin_clear(runner: CliRunner, env_file: Path) -> None:
    runner.invoke(pin_cli, ["add", "FOO", "--env", str(env_file)])
    result = runner.invoke(pin_cli, ["clear", "--env", str(env_file)])
    assert result.exit_code == 0
    assert get_pinned(env_file) == []
