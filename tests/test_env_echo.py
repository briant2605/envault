"""Tests for envault/env_echo.py."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.env_echo import echo_env
from envault.cli_echo import echo_cli


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "APP_NAME=myapp\n"
        "DB_PASSWORD=s3cr3t\n"
        "API_KEY=abc123\n"
        "# a comment\n"
        "\n"
        "DEBUG=true\n",
        encoding="utf-8",
    )
    return p


def test_echo_env_returns_all_keys(env_file: Path) -> None:
    lines = echo_env(env_file)
    assert len(lines) == 4


def test_echo_env_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        echo_env(tmp_path / "missing.env")


def test_echo_env_mask_redacts_sensitive(env_file: Path) -> None:
    lines = echo_env(env_file, mask=True)
    masked = {line.split("=", 1)[0]: line.split("=", 1)[1] for line in lines}
    assert masked["DB_PASSWORD"] != "s3cr3t"
    assert masked["API_KEY"] != "abc123"
    assert masked["APP_NAME"] == "myapp"


def test_echo_env_prefix_filters(env_file: Path) -> None:
    lines = echo_env(env_file, prefix="DB_")
    assert len(lines) == 1
    assert lines[0].startswith("DB_PASSWORD=")


def test_echo_env_export_flag(env_file: Path) -> None:
    lines = echo_env(env_file, export=True)
    assert all(line.startswith("export ") for line in lines)


def test_echo_env_skips_comments_and_blanks(env_file: Path) -> None:
    lines = echo_env(env_file)
    assert not any(line.startswith("#") for line in lines)
    assert not any(line.strip() == "" for line in lines)


# --- CLI tests ---


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_cli_echo_show(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(echo_cli, ["show", str(env_file)])
    assert result.exit_code == 0
    assert "APP_NAME=myapp" in result.output


def test_cli_echo_show_missing_file(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(echo_cli, ["show", str(tmp_path / "nope.env")])
    assert result.exit_code != 0


def test_cli_echo_count(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(echo_cli, ["count", str(env_file)])
    assert result.exit_code == 0
    assert result.output.strip() == "4"


def test_cli_echo_count_with_prefix(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(echo_cli, ["count", str(env_file), "--prefix", "API_"])
    assert result.exit_code == 0
    assert result.output.strip() == "1"
