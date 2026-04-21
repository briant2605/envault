"""Search for a pattern in env values (not just keys) within a vault."""
from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from envault.vault import unseal


@dataclass
class GrepMatch:
    key: str
    value: str
    line_number: int

    def __str__(self) -> str:
        return f"  [{self.line_number}] {self.key}={self.value}"


def _parse_env(text: str) -> List[tuple[int, str, str]]:
    """Return list of (lineno, key, value) for non-comment, non-blank lines."""
    results = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        results.append((lineno, key, value))
    return results


def grep_values(
    env_file: Path,
    password: str,
    pattern: str,
    *,
    use_regex: bool = False,
    case_sensitive: bool = True,
) -> List[GrepMatch]:
    """Return all key/value pairs whose value matches *pattern*.

    Args:
        env_file: Path to the .env file whose vault will be searched.
        password: Decryption password.
        pattern: Glob (default) or regex string to match against values.
        use_regex: When True, treat *pattern* as a regular expression.
        case_sensitive: When False, matching ignores case.
    """
    text = unseal(env_file, password)
    entries = _parse_env(text)

    flags = 0 if case_sensitive else re.IGNORECASE
    matches: List[GrepMatch] = []

    for lineno, key, value in entries:
        if use_regex:
            hit = re.search(pattern, value, flags)
        else:
            cmp_value = value if case_sensitive else value.lower()
            cmp_pattern = pattern if case_sensitive else pattern.lower()
            hit = fnmatch.fnmatch(cmp_value, cmp_pattern)

        if hit:
            matches.append(GrepMatch(key=key, value=value, line_number=lineno))

    return matches


def grep_keys_and_values(
    env_file: Path,
    password: str,
    pattern: str,
    *,
    use_regex: bool = False,
    case_sensitive: bool = True,
) -> List[GrepMatch]:
    """Like grep_values but also matches against key names."""
    text = unseal(env_file, password)
    entries = _parse_env(text)

    flags = 0 if case_sensitive else re.IGNORECASE
    matches: List[GrepMatch] = []

    for lineno, key, value in entries:
        target = f"{key}={value}"
        if use_regex:
            hit = re.search(pattern, target, flags)
        else:
            cmp_target = target if case_sensitive else target.lower()
            cmp_pattern = pattern if case_sensitive else pattern.lower()
            hit = fnmatch.fnmatch(cmp_target, cmp_pattern)

        if hit:
            matches.append(GrepMatch(key=key, value=value, line_number=lineno))

    return matches
