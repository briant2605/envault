"""Tests for envault.env_dedup."""
from pathlib import Path

import pytest

from envault.env_dedup import DuplicateReport, dedup_env_file, dedup_env_text, find_duplicates


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("A=1\nB=2\nA=3\n", encoding="utf-8")
    return p


def test_find_duplicates_detects_repeated_key(env_file: Path) -> None:
    text = env_file.read_text()
    report = find_duplicates(text)
    assert report.has_duplicates
    assert "A" in report.duplicates
    assert report.duplicates["A"] == [1, 3]


def test_find_duplicates_no_duplicates() -> None:
    text = "X=1\nY=2\nZ=3\n"
    report = find_duplicates(text)
    assert not report.has_duplicates
    assert report.duplicates == {}


def test_find_duplicates_ignores_comments() -> None:
    text = "# A=1\nA=2\nB=3\n"
    report = find_duplicates(text)
    assert not report.has_duplicates


def test_find_duplicates_ignores_blank_lines() -> None:
    text = "A=1\n\nA=2\n"
    report = find_duplicates(text)
    assert "A" in report.duplicates
    assert len(report.duplicates["A"]) == 2


def test_summary_no_duplicates() -> None:
    report = DuplicateReport()
    assert report.summary() == "No duplicate keys found."


def test_summary_with_duplicates() -> None:
    report = DuplicateReport(duplicates={"A": [1, 3]})
    summary = report.summary()
    assert "A" in summary
    assert "1" in summary
    assert "3" in summary


def test_dedup_env_text_keep_last() -> None:
    text = "A=first\nB=2\nA=last\n"
    result = dedup_env_text(text, keep="last")
    assert "A=last" in result
    assert "A=first" not in result
    assert "B=2" in result


def test_dedup_env_text_keep_first() -> None:
    text = "A=first\nB=2\nA=last\n"
    result = dedup_env_text(text, keep="first")
    assert "A=first" in result
    assert "A=last" not in result


def test_dedup_env_text_no_duplicates_unchanged() -> None:
    text = "X=1\nY=2\n"
    assert dedup_env_text(text) == text


def test_dedup_env_text_invalid_keep_raises() -> None:
    with pytest.raises(ValueError, match="keep must be"):
        dedup_env_text("A=1\n", keep="middle")


def test_dedup_env_file_rewrites_file(env_file: Path) -> None:
    changed, report = dedup_env_file(env_file)
    assert changed
    assert report.has_duplicates
    content = env_file.read_text()
    assert content.count("A=") == 1


def test_dedup_env_file_no_change_when_clean(tmp_path: Path) -> None:
    p = tmp_path / ".env"
    p.write_text("X=1\nY=2\n", encoding="utf-8")
    changed, report = dedup_env_file(p)
    assert not changed
    assert not report.has_duplicates
