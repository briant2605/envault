"""Tests for envault.env_sort."""
from pathlib import Path
import pytest

from envault.env_sort import sort_env_text, sort_env_file


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("ZEBRA=1\nAPPLE=2\nMANGO=3\n")
    return p


def test_sort_env_text_basic():
    text = "ZEBRA=1\nAPPLE=2\nMANGO=3\n"
    result = sort_env_text(text)
    lines = [l for l in result.splitlines() if l.strip()]
    assert lines == ["APPLE=2", "MANGO=3", "ZEBRA=1"]


def test_sort_env_text_reverse():
    text = "APPLE=2\nMANGO=3\nZEBRA=1\n"
    result = sort_env_text(text, reverse=True)
    lines = [l for l in result.splitlines() if l.strip()]
    assert lines == ["ZEBRA=1", "MANGO=3", "APPLE=2"]


def test_sort_env_text_preserves_comments_at_top():
    text = "# config file\nZEBRA=1\nAPPLE=2\n"
    result = sort_env_text(text)
    assert result.startswith("# config file\n")


def test_sort_env_text_attached_comment_moves_with_key():
    text = "# zebra comment\nZEBRA=1\n# apple comment\nAPPLE=2\n"
    result = sort_env_text(text, keep_comments_attached=True)
    assert result.index("# apple comment") < result.index("# zebra comment")


def test_sort_env_text_blank_lines_attached():
    text = "ZEBRA=1\n\nAPPLE=2\n"
    result = sort_env_text(text, keep_comments_attached=True)
    # APPLE should come first
    assert result.index("APPLE") < result.index("ZEBRA")


def test_sort_env_text_case_insensitive():
    text = "b_KEY=1\nA_KEY=2\nC_KEY=3\n"
    result = sort_env_text(text)
    lines = [l for l in result.splitlines() if l.strip()]
    assert lines[0].startswith("A_KEY")
    assert lines[1].startswith("b_KEY")
    assert lines[2].startswith("C_KEY")


def test_sort_env_text_already_sorted_unchanged():
    text = "ALPHA=1\nBETA=2\nGAMMA=3\n"
    result = sort_env_text(text)
    assert result == text


def test_sort_env_file_modifies_file(env_file: Path):
    sort_env_file(env_file)
    lines = [l for l in env_file.read_text().splitlines() if l.strip()]
    assert lines == ["APPLE=2", "MANGO=3", "ZEBRA=1"]


def test_sort_env_file_returns_new_content(env_file: Path):
    result = sort_env_file(env_file)
    assert "APPLE=2" in result
    assert result == env_file.read_text()


def test_sort_env_file_missing_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        sort_env_file(tmp_path / "nonexistent.env")


def test_sort_env_text_values_with_equals():
    text = "Z_KEY=a=b\nA_KEY=x=y\n"
    result = sort_env_text(text)
    lines = [l for l in result.splitlines() if l.strip()]
    assert lines[0] == "A_KEY=x=y"
    assert lines[1] == "Z_KEY=a=b"
