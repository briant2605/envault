"""Tests for envault.env_required."""
from __future__ import annotations

import json
import pytest
from pathlib import Path

from envault.env_required import (
    MissingKeyReport,
    check_required,
    load_required_keys,
    save_required_keys,
    _required_path,
)


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc123\n")
    return f


def test_required_path_naming(env_file: Path) -> None:
    rp = _required_path(env_file)
    assert rp.name == ".env.required.json"
    assert rp.parent == env_file.parent


def test_load_required_keys_missing_file(env_file: Path) -> None:
    keys = load_required_keys(env_file)
    assert keys == []


def test_save_and_load_required_keys(env_file: Path) -> None:
    save_required_keys(env_file, ["DB_HOST", "SECRET_KEY", "API_KEY"])
    keys = load_required_keys(env_file)
    assert sorted(keys) == ["API_KEY", "DB_HOST", "SECRET_KEY"]


def test_save_deduplicates(env_file: Path) -> None:
    save_required_keys(env_file, ["DB_HOST", "DB_HOST", "API_KEY"])
    keys = load_required_keys(env_file)
    assert keys.count("DB_HOST") == 1


def test_check_required_all_present(env_file: Path) -> None:
    report = check_required(env_file, required=["DB_HOST", "DB_PORT"])
    assert report.ok
    assert set(report.present) == {"DB_HOST", "DB_PORT"}
    assert report.missing == []


def test_check_required_some_missing(env_file: Path) -> None:
    report = check_required(env_file, required=["DB_HOST", "API_KEY"])
    assert not report.ok
    assert "DB_HOST" in report.present
    assert "API_KEY" in report.missing


def test_check_required_uses_saved_keys(env_file: Path) -> None:
    save_required_keys(env_file, ["DB_HOST", "MISSING_KEY"])
    report = check_required(env_file)
    assert "DB_HOST" in report.present
    assert "MISSING_KEY" in report.missing


def test_check_required_missing_env_file(tmp_path: Path) -> None:
    missing = tmp_path / ".env"
    report = check_required(missing, required=["DB_HOST"])
    assert not report.ok
    assert "DB_HOST" in report.missing


def test_missing_key_report_summary_shows_both(env_file: Path) -> None:
    report = MissingKeyReport(present=["DB_HOST"], missing=["API_KEY"])
    summary = report.summary()
    assert "Present" in summary
    assert "Missing" in summary
    assert "DB_HOST" in summary
    assert "API_KEY" in summary


def test_missing_key_report_summary_empty() -> None:
    report = MissingKeyReport()
    assert "No required keys" in report.summary()
