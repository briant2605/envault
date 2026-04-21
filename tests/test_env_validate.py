"""Tests for envault.env_validate."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_validate import ValidationError, ValidationRule, validate_env


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "APP_ENV=production\n"
        "SECRET_KEY=supersecret123\n"
        "PORT=8080\n"
        "DEBUG=false\n"
    )
    return p


def test_validate_no_errors(env_file: Path) -> None:
    rules = [ValidationRule(key="APP_ENV"), ValidationRule(key="PORT")]
    errors = validate_env(env_file, rules)
    assert errors == []


def test_validate_missing_required_key(env_file: Path) -> None:
    rules = [ValidationRule(key="MISSING_KEY", required=True)]
    errors = validate_env(env_file, rules)
    assert len(errors) == 1
    assert errors[0].key == "MISSING_KEY"
    assert "missing" in errors[0].message


def test_validate_optional_missing_key_no_error(env_file: Path) -> None:
    rules = [ValidationRule(key="NOT_THERE", required=False)]
    errors = validate_env(env_file, rules)
    assert errors == []


def test_validate_pattern_pass(env_file: Path) -> None:
    rules = [ValidationRule(key="PORT", pattern=r"\d+")]
    errors = validate_env(env_file, rules)
    assert errors == []


def test_validate_pattern_fail(env_file: Path) -> None:
    rules = [ValidationRule(key="APP_ENV", pattern=r"\d+")]
    errors = validate_env(env_file, rules)
    assert len(errors) == 1
    assert "pattern" in errors[0].message


def test_validate_min_length_fail(env_file: Path) -> None:
    rules = [ValidationRule(key="APP_ENV", min_length=50)]
    errors = validate_env(env_file, rules)
    assert len(errors) == 1
    assert "too short" in errors[0].message


def test_validate_max_length_fail(env_file: Path) -> None:
    rules = [ValidationRule(key="SECRET_KEY", max_length=3)]
    errors = validate_env(env_file, rules)
    assert len(errors) == 1
    assert "too long" in errors[0].message


def test_validate_allowed_values_pass(env_file: Path) -> None:
    rules = [ValidationRule(key="DEBUG", allowed_values=["true", "false"])]
    errors = validate_env(env_file, rules)
    assert errors == []


def test_validate_allowed_values_fail(env_file: Path) -> None:
    rules = [ValidationRule(key="APP_ENV", allowed_values=["staging", "development"])]
    errors = validate_env(env_file, rules)
    assert len(errors) == 1
    assert "must be one of" in errors[0].message


def test_validate_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "nonexistent.env"
    errors = validate_env(missing, [])
    assert len(errors) == 1
    assert "does not exist" in errors[0].message


def test_validation_error_str() -> None:
    err = ValidationError(key="FOO", message="required key is missing")
    assert str(err) == "[FOO] required key is missing"
