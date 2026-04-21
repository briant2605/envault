"""Tests for envault.env_import."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.env_import import (
    export_env,
    import_env,
    write_env,
    _parse_env,
    _to_dotenv,
    _to_json,
    _to_yaml,
)


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text('DB_HOST="localhost"\nDB_PORT="5432"\nSECRET="abc123"\n')
    return p


def test_parse_env_basic():
    data = _parse_env('FOO="bar"\nBAZ=qux\n')
    assert data == {"FOO": "bar", "BAZ": "qux"}


def test_parse_env_ignores_comments_and_blanks():
    data = _parse_env("# comment\n\nKEY=val\n")
    assert "KEY" in data
    assert len(data) == 1


def test_to_dotenv_sorted():
    result = _to_dotenv({"Z": "1", "A": "2"})
    assert result.index("A") < result.index("Z")


def test_to_json_valid():
    result = _to_json({"KEY": "value"})
    parsed = json.loads(result)
    assert parsed["KEY"] == "value"


def test_to_yaml_basic():
    result = _to_yaml({"KEY": "value"})
    assert "KEY: value" in result


def test_export_env_dotenv(env_file: Path):
    result = export_env(env_file, "dotenv")
    assert "DB_HOST" in result
    assert "DB_PORT" in result


def test_export_env_json(env_file: Path):
    result = export_env(env_file, "json")
    data = json.loads(result)
    assert data["DB_HOST"] == "localhost"
    assert data["DB_PORT"] == "5432"


def test_export_env_yaml(env_file: Path):
    result = export_env(env_file, "yaml")
    assert "DB_HOST: localhost" in result


def test_export_env_missing_file(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        export_env(tmp_path / "nonexistent.env", "json")


def test_export_env_bad_format(env_file: Path):
    with pytest.raises(ValueError, match="Unsupported format"):
        export_env(env_file, "toml")


def test_import_env_json_roundtrip(env_file: Path):
    exported = export_env(env_file, "json")
    data = import_env(exported, "json")
    assert data["DB_HOST"] == "localhost"


def test_import_env_yaml_roundtrip(env_file: Path):
    exported = export_env(env_file, "yaml")
    data = import_env(exported, "yaml")
    assert "DB_HOST" in data


def test_import_env_dotenv_roundtrip(env_file: Path):
    exported = export_env(env_file, "dotenv")
    data = import_env(exported, "dotenv")
    assert data["SECRET"] == "abc123"


def test_import_env_json_not_object():
    with pytest.raises(ValueError, match="top-level object"):
        import_env("[1, 2, 3]", "json")


def test_write_env(tmp_path: Path):
    dest = tmp_path / ".env.out"
    write_env({"FOO": "bar", "BAZ": "qux"}, dest)
    assert dest.exists()
    content = dest.read_text()
    assert 'BAZ="qux"' in content
    assert 'FOO="bar"' in content
