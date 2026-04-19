"""Tests for envault.tags module."""
import pytest
from pathlib import Path
from unittest.mock import patch
import json

from envault.tags import add_tag, remove_tag, get_tags, find_by_tag, clear_tags


@pytest.fixture(autouse=True)
def isolated_tags(tmp_path, monkeypatch):
    tags_file = tmp_path / "tags.json"
    import envault.tags as tags_mod
    monkeypatch.setattr(tags_mod, "_TAGS_FILE", tags_file)
    yield tags_file


def test_get_tags_empty():
    assert get_tags(".env") == []


def test_add_tag_creates_entry():
    add_tag(".env", "production")
    assert "production" in get_tags(".env")


def test_add_tag_no_duplicates():
    add_tag(".env", "staging")
    add_tag(".env", "staging")
    assert get_tags(".env").count("staging") == 1


def test_add_multiple_tags():
    add_tag(".env", "a")
    add_tag(".env", "b")
    assert set(get_tags(".env")) == {"a", "b"}


def test_remove_tag():
    add_tag(".env", "old")
    remove_tag(".env", "old")
    assert "old" not in get_tags(".env")


def test_remove_tag_missing_raises():
    with pytest.raises(KeyError):
        remove_tag(".env", "nonexistent")


def test_remove_last_tag_cleans_entry(isolated_tags):
    add_tag(".env", "solo")
    remove_tag(".env", "solo")
    data = json.loads(isolated_tags.read_text())
    assert ".env" not in data


def test_find_by_tag():
    add_tag(".env.prod", "production")
    add_tag(".env.dev", "development")
    add_tag(".env.staging", "production")
    result = find_by_tag("production")
    assert set(result) == {".env.prod", ".env.staging"}


def test_find_by_tag_no_match():
    assert find_by_tag("ghost") == []


def test_clear_tags():
    add_tag(".env", "x")
    add_tag(".env", "y")
    clear_tags(".env")
    assert get_tags(".env") == []


def test_clear_tags_nonexistent_no_error():
    clear_tags(".env.missing")  # should not raise
