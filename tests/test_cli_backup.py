"""CLI integration tests for the backup command group."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_backup import backup_cli


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("A=1\nB=2\n")
    return f


def test_backup_create(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(backup_cli, ["create", str(env_file)])
    assert result.exit_code == 0
    assert "Backup created" in result.output


def test_backup_create_missing_file(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(backup_cli, ["create", str(tmp_path / "missing.env")])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_backup_list_empty(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(backup_cli, ["list", str(env_file)])
    assert result.exit_code == 0
    assert "No backups" in result.output


def test_backup_list_after_create(runner: CliRunner, env_file: Path) -> None:
    runner.invoke(backup_cli, ["create", str(env_file)])
    result = runner.invoke(backup_cli, ["list", str(env_file)])
    assert result.exit_code == 0
    assert ".bak" in result.output


def test_backup_restore(runner: CliRunner, env_file: Path) -> None:
    create_result = runner.invoke(backup_cli, ["create", str(env_file)])
    backup_path = create_result.output.split(":", 1)[1].strip()
    env_file.write_text("CHANGED=yes\n")
    result = runner.invoke(backup_cli, ["restore", backup_path, str(env_file)])
    assert result.exit_code == 0
    assert "Restored" in result.output
    assert env_file.read_text() == "A=1\nB=2\n"


def test_backup_delete(runner: CliRunner, env_file: Path) -> None:
    create_result = runner.invoke(backup_cli, ["create", str(env_file)])
    backup_path = create_result.output.split(":", 1)[1].strip()
    result = runner.invoke(backup_cli, ["delete", backup_path])
    assert result.exit_code == 0
    assert "Deleted" in result.output


def test_backup_purge(runner: CliRunner, env_file: Path) -> None:
    runner.invoke(backup_cli, ["create", str(env_file)])
    runner.invoke(backup_cli, ["create", str(env_file)])
    result = runner.invoke(
        backup_cli, ["purge", str(env_file)], input="y\n"
    )
    assert result.exit_code == 0
    assert "Purged" in result.output
