"""Tests for CLI tag commands."""
import pytest
from click.testing import CliRunner
from envault.cli_tags import tags_cli
import envault.tags as tags_mod


@pytest.fixture(autouse=True)
def isolated_tags(tmp_path, monkeypatch):
    monkeypatch.setattr(tags_mod, "_TAGS_FILE", tmp_path / "tags.json")


@pytest.fixture
def runner():
    return CliRunner()


def test_tag_add(runner):
    result = runner.invoke(tags_cli, ["add", ".env", "prod"])
    assert result.exit_code == 0
    assert "prod" in result.output


def test_tag_add_duplicate(runner):
    """Adding the same tag twice should not result in duplicates in the list."""
    runner.invoke(tags_cli, ["add", ".env", "prod"])
    runner.invoke(tags_cli, ["add", ".env", "prod"])
    result = runner.invoke(tags_cli, ["list", ".env"])
    assert result.output.count("prod") == 1


def test_tag_list(runner):
    runner.invoke(tags_cli, ["add", ".env", "alpha"])
    result = runner.invoke(tags_cli, ["list", ".env"])
    assert "alpha" in result.output


def test_tag_list_empty(runner):
    result = runner.invoke(tags_cli, ["list", ".env"])
    assert "No tags" in result.output


def test_tag_remove(runner):
    runner.invoke(tags_cli, ["add", ".env", "beta"])
    result = runner.invoke(tags_cli, ["remove", ".env", "beta"])
    assert result.exit_code == 0


def test_tag_remove_missing(runner):
    result = runner.invoke(tags_cli, ["remove", ".env", "ghost"])
    assert result.exit_code != 0


def test_tag_find(runner):
    runner.invoke(tags_cli, ["add", ".env.prod", "live"])
    result = runner.invoke(tags_cli, ["find", "live"])
    assert ".env.prod" in result.output


def test_tag_find_no_match(runner):
    result = runner.invoke(tags_cli, ["find", "nothing"])
    assert "No entries" in result.output


def test_tag_clear(runner):
    runner.invoke(tags_cli, ["add", ".env", "x"])
    result = runner.invoke(tags_cli, ["clear", ".env"])
    assert result.exit_code == 0
    list_result = runner.invoke(tags_cli, ["list", ".env"])
    assert "No tags" in list_result.output
