"""Tests for envault.env_expire."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from envault.env_expire import (
    ExpiryReport,
    check_expiry,
    get_expiry,
    remove_expiry,
    set_expiry,
)


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("API_KEY=abc\nDB_PASS=secret\n")
    return f


def test_get_expiry_none_when_absent(env_file: Path) -> None:
    assert get_expiry(env_file, "API_KEY") is None


def test_set_expiry_creates_entry(env_file: Path) -> None:
    d = date(2025, 12, 31)
    set_expiry(env_file, "API_KEY", d)
    assert get_expiry(env_file, "API_KEY") == d


def test_set_expiry_overwrites_existing(env_file: Path) -> None:
    set_expiry(env_file, "API_KEY", date(2025, 1, 1))
    set_expiry(env_file, "API_KEY", date(2026, 6, 15))
    assert get_expiry(env_file, "API_KEY") == date(2026, 6, 15)


def test_remove_expiry_clears_entry(env_file: Path) -> None:
    set_expiry(env_file, "API_KEY", date(2025, 12, 31))
    remove_expiry(env_file, "API_KEY")
    assert get_expiry(env_file, "API_KEY") is None


def test_remove_expiry_missing_key_no_error(env_file: Path) -> None:
    remove_expiry(env_file, "NONEXISTENT")  # should not raise


def test_check_expiry_empty_when_no_entries(env_file: Path) -> None:
    assert check_expiry(env_file) == []


def test_check_expiry_not_expired(env_file: Path) -> None:
    set_expiry(env_file, "API_KEY", date(2099, 1, 1))
    reports = check_expiry(env_file, today=date(2025, 1, 1))
    assert len(reports) == 1
    assert not reports[0].expired


def test_check_expiry_expired(env_file: Path) -> None:
    set_expiry(env_file, "DB_PASS", date(2020, 6, 1))
    reports = check_expiry(env_file, today=date(2025, 1, 1))
    assert len(reports) == 1
    assert reports[0].expired
    assert reports[0].key == "DB_PASS"


def test_check_expiry_multiple_keys(env_file: Path) -> None:
    set_expiry(env_file, "API_KEY", date(2099, 1, 1))
    set_expiry(env_file, "DB_PASS", date(2020, 1, 1))
    reports = check_expiry(env_file, today=date(2025, 6, 1))
    assert len(reports) == 2
    expired = [r for r in reports if r.expired]
    assert len(expired) == 1
    assert expired[0].key == "DB_PASS"


def test_expiry_report_str_ok(env_file: Path) -> None:
    r = ExpiryReport(key="API_KEY", expiry=date(2099, 1, 1), expired=False)
    assert "ok" in str(r)
    assert "API_KEY" in str(r)


def test_expiry_report_str_expired(env_file: Path) -> None:
    r = ExpiryReport(key="DB_PASS", expiry=date(2020, 1, 1), expired=True)
    assert "EXPIRED" in str(r)
    assert "DB_PASS" in str(r)


def test_expiry_file_is_sibling_of_env(env_file: Path) -> None:
    set_expiry(env_file, "KEY", date(2025, 1, 1))
    expire_file = env_file.parent / ".env.expire.json"
    assert expire_file.exists()
