"""Tests for envault.env_rename."""

from pathlib import Path

import pytest

from envault.env_rename import rename_key, rename_key_in_file


ENV_TEXT = """# Sample env file
DB_HOST=localhost
DB_PORT=5432
APP_SECRET=hunter2
"""


# ---------------------------------------------------------------------------
# rename_key (pure text)
# ---------------------------------------------------------------------------

def test_rename_key_basic():
    result = rename_key(ENV_TEXT, "DB_HOST", "DATABASE_HOST")
    assert "DATABASE_HOST=localhost" in result
    assert "DB_HOST" not in result


def test_rename_key_preserves_other_keys():
    result = rename_key(ENV_TEXT, "DB_HOST", "DATABASE_HOST")
    assert "DB_PORT=5432" in result
    assert "APP_SECRET=hunter2" in result


def test_rename_key_preserves_comments():
    result = rename_key(ENV_TEXT, "DB_HOST", "DATABASE_HOST")
    assert "# Sample env file" in result


def test_rename_key_missing_old_key_raises():
    with pytest.raises(KeyError, match="MISSING"):
        rename_key(ENV_TEXT, "MISSING", "NEW_KEY")


def test_rename_key_new_key_exists_raises():
    with pytest.raises(ValueError, match="already exists"):
        rename_key(ENV_TEXT, "DB_HOST", "DB_PORT")


def test_rename_key_overwrite_existing():
    result = rename_key(ENV_TEXT, "DB_HOST", "DB_PORT", overwrite=True)
    # DB_PORT should now hold the old DB_HOST value
    assert "DB_PORT=localhost" in result
    # Original DB_PORT entry should be gone
    assert "DB_PORT=5432" not in result
    assert "DB_HOST" not in result


def test_rename_key_roundtrip_line_count():
    """Number of non-blank, non-comment lines must stay the same."""
    original_keys = [l for l in ENV_TEXT.splitlines() if l and not l.startswith("#")]
    result = rename_key(ENV_TEXT, "APP_SECRET", "APP_TOKEN")
    result_keys = [l for l in result.splitlines() if l and not l.startswith("#")]
    assert len(original_keys) == len(result_keys)


# ---------------------------------------------------------------------------
# rename_key_in_file
# ---------------------------------------------------------------------------

@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text(ENV_TEXT)
    return f


def test_rename_key_in_file_modifies_file(env_file: Path):
    rename_key_in_file(env_file, "DB_HOST", "DATABASE_HOST")
    content = env_file.read_text()
    assert "DATABASE_HOST=localhost" in content
    assert "DB_HOST" not in content


def test_rename_key_in_file_missing_key_raises(env_file: Path):
    with pytest.raises(KeyError):
        rename_key_in_file(env_file, "NONEXISTENT", "NEW_KEY")


def test_rename_key_in_file_no_change_on_error(env_file: Path):
    original = env_file.read_text()
    with pytest.raises(ValueError):
        rename_key_in_file(env_file, "DB_HOST", "DB_PORT")
    # File must be untouched because the error is raised before writing
    assert env_file.read_text() == original
