"""Tests for envault.env_stats."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_stats import EnvStats, compute_stats, compute_stats_file


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "# database config\n"
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "DB_PASSWORD=supersecret\n"
        "API_KEY=abc123\n"
        "EMPTY_VAL=\n"
        "\n"
        "# another comment\n"
        "DB_HOST=duplicate\n"
    )
    return p


# ---------------------------------------------------------------------------
# compute_stats
# ---------------------------------------------------------------------------

def test_total_keys(env_file: Path) -> None:
    stats = compute_stats_file(env_file)
    assert stats.total_keys == 6  # DB_HOST×2, DB_PORT, DB_PASSWORD, API_KEY, EMPTY_VAL


def test_empty_values(env_file: Path) -> None:
    stats = compute_stats_file(env_file)
    assert stats.empty_values == 1


def test_commented_lines(env_file: Path) -> None:
    stats = compute_stats_file(env_file)
    assert stats.commented_lines == 2


def test_blank_lines(env_file: Path) -> None:
    stats = compute_stats_file(env_file)
    assert stats.blank_lines == 1


def test_duplicate_keys(env_file: Path) -> None:
    stats = compute_stats_file(env_file)
    assert stats.duplicate_keys == 1  # DB_HOST appears twice


def test_sensitive_keys(env_file: Path) -> None:
    stats = compute_stats_file(env_file)
    # DB_PASSWORD and API_KEY are sensitive
    assert stats.sensitive_keys == 2


def test_avg_key_length_nonzero(env_file: Path) -> None:
    stats = compute_stats_file(env_file)
    assert stats.avg_key_length() > 0


def test_avg_value_length_nonzero(env_file: Path) -> None:
    stats = compute_stats_file(env_file)
    assert stats.avg_value_length() > 0


def test_longest_key_set(env_file: Path) -> None:
    stats = compute_stats_file(env_file)
    assert stats.longest_key != ""


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        compute_stats_file(tmp_path / "nonexistent.env")


def test_empty_file_returns_zero_keys() -> None:
    stats = compute_stats("")
    assert stats.total_keys == 0
    assert stats.avg_key_length() == 0.0
    assert stats.avg_value_length() == 0.0


def test_summary_contains_total_keys(env_file: Path) -> None:
    stats = compute_stats_file(env_file)
    assert "Total keys" in stats.summary()
    assert str(stats.total_keys) in stats.summary()


def test_stats_sensitive_key_with_secret() -> None:
    text = "MY_SECRET_TOKEN=abc\nPLAIN=hello\n"
    stats = compute_stats(text)
    assert stats.sensitive_keys == 1
