"""Lint .env files for common issues: duplicates, empty values, invalid format."""

from __future__ import annotations

import re
from pathlib import Path
from typing import NamedTuple

_LINE_RE = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)$')


class LintIssue(NamedTuple):
    line: int
    key: str | None
    code: str
    message: str


def lint_env(env_path: Path) -> list[LintIssue]:
    """Return a list of LintIssue found in *env_path*.

    Checks performed:
    - E001: line is not blank, not a comment, and not a valid KEY=VALUE pair
    - E002: duplicate key defined more than once
    - W001: key present but value is empty
    """
    if not env_path.exists():
        raise FileNotFoundError(f"{env_path} does not exist")

    issues: list[LintIssue] = []
    seen: dict[str, int] = {}  # key -> first line number

    for lineno, raw in enumerate(env_path.read_text().splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        m = _LINE_RE.match(line)
        if not m:
            issues.append(LintIssue(lineno, None, "E001", f"Invalid line format: {raw!r}"))
            continue

        key, value = m.group(1), m.group(2).strip()

        if key in seen:
            issues.append(
                LintIssue(lineno, key, "E002", f"Duplicate key '{key}' (first seen at line {seen[key]})")
            )
        else:
            seen[key] = lineno

        if value == "" or value in ('""', "''"):
            issues.append(LintIssue(lineno, key, "W001", f"Key '{key}' has an empty value"))

    return issues


def format_issues(issues: list[LintIssue]) -> str:
    """Return a human-readable string summarising *issues*."""
    if not issues:
        return "No issues found."
    lines = []
    for issue in issues:
        loc = f"line {issue.line}"
        key_part = f" [{issue.key}]" if issue.key else ""
        lines.append(f"{issue.code}{key_part} @ {loc}: {issue.message}")
    return "\n".join(lines)
