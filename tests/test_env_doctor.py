"""Tests for envault.env_doctor."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_doctor import run_doctor, DoctorReport
from envault.vault import seal


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("API_KEY=secret\nDB_URL=postgres://localhost/db\n")
    return f


def test_missing_env_file_gives_error(tmp_path: Path) -> None:
    report = run_doctor(tmp_path / ".env")
    assert not report.ok
    assert any("not found" in e for e in report.errors)


def test_existing_env_file_passes_exists_check(env_file: Path) -> None:
    report = run_doctor(env_file)
    assert any(".env file exists" in c for c in report.checks)


def test_no_vault_produces_warning(env_file: Path) -> None:
    report = run_doctor(env_file)
    assert any("vault" in w.lower() for w in report.warnings)


def test_vault_present_removes_vault_warning(env_file: Path) -> None:
    seal(env_file, "password")
    report = run_doctor(env_file)
    vault_warnings = [w for w in report.warnings if "vault" in w.lower() and "lock" in w.lower()]
    assert vault_warnings == []
    assert any("Vault file exists" in c for c in report.checks)


def test_gitignore_missing_gives_warning(env_file: Path) -> None:
    report = run_doctor(env_file)
    assert any(".gitignore" in w for w in report.warnings)


def test_gitignore_with_env_clears_warning(env_file: Path) -> None:
    gi = env_file.parent / ".gitignore"
    gi.write_text(".env\n")
    report = run_doctor(env_file)
    assert not any(".gitignore not found" in w for w in report.warnings)
    assert any(".gitignore" in c for c in report.checks)


def test_lint_warning_surfaces_in_report(env_file: Path) -> None:
    # empty value triggers a lint warning
    env_file.write_text("API_KEY=\n")
    report = run_doctor(env_file)
    assert any("Lint warning" in w or "Lint error" in w for w in report.warnings + report.errors)


def test_report_ok_for_clean_file(env_file: Path) -> None:
    env_file.parent.joinpath(".gitignore").write_text(".env\n")
    seal(env_file, "pw")
    report = run_doctor(env_file)
    assert report.ok
