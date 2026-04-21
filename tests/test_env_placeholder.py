"""Tests for envault.env_placeholder."""

import pytest
from pathlib import Path

from envault.env_placeholder import (
    find_placeholders,
    find_placeholders_in_file,
    has_placeholders,
    summary,
    PlaceholderMatch,
)


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        'DB_HOST=localhost\n'
        'DB_PASS=${DB_PASSWORD}\n'
        'API_KEY={{API_KEY_VALUE}}\n'
        'REGION=us-east-1\n'
        'CERT=<CERT_PATH>\n'
    )
    return p


def test_find_placeholders_dollar_brace():
    text = "DB_PASS=${DB_PASSWORD}\n"
    matches = find_placeholders(text)
    assert len(matches) == 1
    assert matches[0].key == "DB_PASS"
    assert "${DB_PASSWORD}" in matches[0].placeholders


def test_find_placeholders_double_brace():
    text = "API_KEY={{API_KEY_VALUE}}\n"
    matches = find_placeholders(text)
    assert len(matches) == 1
    assert "{{API_KEY_VALUE}}" in matches[0].placeholders


def test_find_placeholders_angle_bracket():
    text = "CERT=<CERT_PATH>\n"
    matches = find_placeholders(text)
    assert len(matches) == 1
    assert "<CERT_PATH>" in matches[0].placeholders


def test_find_placeholders_no_match():
    text = "HOST=localhost\nPORT=5432\n"
    assert find_placeholders(text) == []


def test_find_placeholders_ignores_comments():
    text = "# DB_PASS=${DB_PASSWORD}\nHOST=localhost\n"
    assert find_placeholders(text) == []


def test_find_placeholders_multiple_in_value():
    text = "URL=${SCHEME}://${HOST}\n"
    matches = find_placeholders(text)
    assert len(matches) == 1
    assert len(matches[0].placeholders) == 2


def test_has_placeholders_true():
    assert has_placeholders("TOKEN=${SECRET}\n") is True


def test_has_placeholders_false():
    assert has_placeholders("TOKEN=abc123\n") is False


def test_find_placeholders_in_file(env_file: Path):
    matches = find_placeholders_in_file(env_file)
    keys = [m.key for m in matches]
    assert "DB_PASS" in keys
    assert "API_KEY" in keys
    assert "CERT" in keys
    assert "DB_HOST" not in keys
    assert "REGION" not in keys


def test_find_placeholders_in_file_missing_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        find_placeholders_in_file(tmp_path / "nonexistent.env")


def test_summary_no_matches():
    assert summary([]) == "No unresolved placeholders found."


def test_summary_with_matches():
    m = PlaceholderMatch(key="TOKEN", value="${SECRET}", placeholders=["${SECRET}"])
    result = summary([m])
    assert "1 key(s)" in result
    assert "TOKEN" in result
