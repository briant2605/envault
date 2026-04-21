"""Validate .env file values against a schema of rules."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ValidationRule:
    key: str
    required: bool = True
    pattern: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    allowed_values: List[str] = field(default_factory=list)


@dataclass
class ValidationError:
    key: str
    message: str

    def __str__(self) -> str:
        return f"[{self.key}] {self.message}"


def _parse_env(text: str) -> Dict[str, str]:
    env: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        v = v.strip().strip('"').strip("'")
        env[k.strip()] = v
    return env


def validate_env(
    env_path: Path,
    rules: List[ValidationRule],
) -> List[ValidationError]:
    """Validate an .env file against a list of rules."""
    if not env_path.exists():
        return [ValidationError("<file>", f"{env_path} does not exist")]

    env = _parse_env(env_path.read_text())
    errors: List[ValidationError] = []

    for rule in rules:
        value = env.get(rule.key)

        if value is None:
            if rule.required:
                errors.append(ValidationError(rule.key, "required key is missing"))
            continue

        if rule.min_length is not None and len(value) < rule.min_length:
            errors.append(
                ValidationError(rule.key, f"value too short (min {rule.min_length})")
            )

        if rule.max_length is not None and len(value) > rule.max_length:
            errors.append(
                ValidationError(rule.key, f"value too long (max {rule.max_length})")
            )

        if rule.pattern and not re.fullmatch(rule.pattern, value):
            errors.append(
                ValidationError(rule.key, f"value does not match pattern '{rule.pattern}'")
            )

        if rule.allowed_values and value not in rule.allowed_values:
            allowed = ", ".join(rule.allowed_values)
            errors.append(
                ValidationError(rule.key, f"value must be one of: {allowed}")
            )

    return errors
