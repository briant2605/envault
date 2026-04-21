"""Tests for envault.cli_comment CLI commands."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_comment import comment_cli


SAMPLE = "DB_HOST=localhost\nDB_PORT=5432  # old comment\n"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(SAMPLE)
    return p


def test_comment_set(runner, env_file):
    result = runner.invoke(
        comment_cli, ["set", "DB_HOST", "main host", "--env", str(env_file)]
    )
    assert result.exit_code == 0
    assert "Comment set" in result.output
    assert "# main host" in env_file.read_text()


def test_comment_set_replaces(runner, env_file):
    result = runner.invoke(
        comment_cli, ["set", "DB_PORT", "new comment", "--env", str(env_file)]
    )
    assert result.exit_code == 0
    text = env_file.read_text()
    assert "new comment" in text
    assert "old comment" not in text


def test_comment_get_existing(runner, env_file):
    result = runner.invoke(comment_cli, ["get", "DB_PORT", "--env", str(env_file)])
    assert result.exit_code == 0
    assert "old comment" in result.output


def test_comment_get_absent(runner, env_file):
    result = runner.invoke(comment_cli, ["get", "DB_HOST", "--env", str(env_file)])
    assert result.exit_code == 0
    assert "No comment" in result.output


def test_comment_remove(runner, env_file):
    result = runner.invoke(
        comment_cli, ["remove", "DB_PORT", "--env", str(env_file)]
    )
    assert result.exit_code == 0
    assert "#" not in env_file.read_text().split("DB_PORT")[1].split("\n")[0]


def test_comment_set_missing_key(runner, env_file):
    result = runner.invoke(
        comment_cli, ["set", "GHOST", "nope", "--env", str(env_file)]
    )
    assert result.exit_code != 0


def test_comment_missing_file(runner, tmp_path):
    result = runner.invoke(
        comment_cli, ["get", "KEY", "--env", str(tmp_path / ".env")]
    )
    assert result.exit_code != 0
