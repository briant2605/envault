"""Tests for envault.env_flatten."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_flatten import (
    flatten_to_dict,
    expand_from_dict,
    flatten_env_file,
)


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "DB__HOST=localhost\n"
        "DB__PORT=5432\n"
        "APP__NAME=myapp\n"
        "APP__DEBUG=true\n"
        "SIMPLE=value\n"
        "# comment line\n"
        "\n"
    )
    return p


def test_flatten_to_dict_groups_by_prefix():
    text = "DB__HOST=localhost\nDB__PORT=5432\n"
    result = flatten_to_dict(text)
    assert result == {"DB": {"HOST": "localhost", "PORT": "5432"}}


def test_flatten_to_dict_no_prefix_goes_to_empty_key():
    text = "SIMPLE=value\n"
    result = flatten_to_dict(text)
    assert result == {"": {"SIMPLE": "value"}}


def test_flatten_to_dict_mixed_keys():
    text = "DB__HOST=localhost\nSIMPLE=value\n"
    result = flatten_to_dict(text)
    assert "DB" in result
    assert "" in result
    assert result["DB"]["HOST"] == "localhost"
    assert result[""]["SIMPLE"] == "value"


def test_flatten_to_dict_ignores_comments_and_blanks():
    text = "# comment\n\nDB__HOST=localhost\n"
    result = flatten_to_dict(text)
    assert result == {"DB": {"HOST": "localhost"}}


def test_flatten_to_dict_custom_separator():
    text = "DB.HOST=localhost\nDB.PORT=5432\n"
    result = flatten_to_dict(text, separator=".")
    assert result == {"DB": {"HOST": "localhost", "PORT": "5432"}}


def test_expand_from_dict_basic():
    nested = {"DB": {"HOST": "localhost", "PORT": "5432"}}
    text = expand_from_dict(nested)
    assert "DB__HOST=localhost" in text
    assert "DB__PORT=5432" in text


def test_expand_from_dict_no_prefix():
    nested = {"": {"SIMPLE": "value"}}
    text = expand_from_dict(nested)
    assert "SIMPLE=value" in text


def test_expand_roundtrip():
    original = "APP__DEBUG=true\nAPP__NAME=myapp\nDB__HOST=localhost\nDB__PORT=5432\n"
    grouped = flatten_to_dict(original)
    restored = expand_from_dict(grouped)
    # All key=value pairs must be present
    for line in original.strip().splitlines():
        assert line in restored


def test_flatten_env_file(env_file: Path):
    result = flatten_env_file(env_file)
    assert "DB" in result
    assert result["DB"]["HOST"] == "localhost"
    assert result["APP"]["NAME"] == "myapp"


def test_flatten_env_file_missing_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        flatten_env_file(tmp_path / "nonexistent.env")
