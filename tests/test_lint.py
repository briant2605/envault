"""Tests for envault.lint and envault.cli_lint."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_lint import lint_cli
from envault.lint import LintIssue, lint_env


@pytest.fixture()
def env_file(tmp_path: Path):
    """Return a factory that writes content to a temp .env file."""

    def _make(content: str) -> Path:
        p = tmp_path / ".env"
        p.write_text(content)
        return p

    return _make


def test_lint_clean_file(env_file):
    p = env_file("FOO=bar\nBAZ=qux\n")
    issues = lint_env(p)
    assert issues == []


def test_lint_empty_value_warning(env_file):
    p = env_file("FOO=\n")
    codes = [i.code for i in lint_env(p)]
    assert "W001" in codes


def test_lint_empty_quoted_value_warning(env_file):
    p = env_file('FOO=""\n')
    codes = [i.code for i in lint_env(p)]
    assert "W001" in codes


def test_lint_duplicate_key_error(env_file):
    p = env_file("FOO=bar\nFOO=baz\n")
    issues = lint_env(p)
    codes = [i.code for i in issues]
    assert "E002" in codes


def test_lint_invalid_line_error(env_file):
    p = env_file("THIS IS NOT VALID\n")
    issues = lint_env(p)
    codes = [i.code for i in issues]
    assert "E001" in codes


def test_lint_comments_and_blanks_ignored(env_file):
    p = env_file("# comment\n\nFOO=bar\n")
    assert lint_env(p) == []


def test_lint_missing_file_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        lint_env(tmp_path / "nonexistent.env")


def test_lint_issue_namedtuple(env_file):
    p = env_file("FOO=\n")
    issue = lint_env(p)[0]
    assert isinstance(issue, LintIssue)
    assert issue.line == 1
    assert issue.key == "FOO"


# --- CLI tests ---


@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_lint_check_clean(runner, env_file):
    p = env_file("FOO=bar\n")
    result = runner.invoke(lint_cli, ["check", str(p)])
    assert result.exit_code == 0
    assert "No issues" in result.output


def test_cli_lint_check_error_exits_nonzero(runner, env_file):
    p = env_file("NOT VALID\n")
    result = runner.invoke(lint_cli, ["check", str(p)])
    assert result.exit_code != 0


def test_cli_lint_check_warning_strict_exits_nonzero(runner, env_file):
    p = env_file("FOO=\n")
    result = runner.invoke(lint_cli, ["check", "--strict", str(p)])
    assert result.exit_code != 0


def test_cli_lint_summary(runner, env_file):
    p = env_file("FOO=bar\nFOO=baz\n")
    result = runner.invoke(lint_cli, ["summary", str(p)])
    assert "1 error" in result.output
