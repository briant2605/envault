"""Detect and report unresolved placeholders in .env files.

A placeholder is a value matching patterns like ${VAR}, {{VAR}}, or <VAR>.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

_PLACEHOLDER_RE = re.compile(
    r"(\$\{[^}]+\}|\{\{[^}]+\}\}|<[A-Z_][A-Z0-9_]*>)"
)


@dataclass
class PlaceholderMatch:
    key: str
    value: str
    placeholders: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        ph = ", ".join(self.placeholders)
        return f"{self.key}={self.value!r}  [{ph}]"


def _parse_env(text: str) -> List[tuple]:
    """Return list of (key, value) for non-comment, non-blank lines."""
    pairs = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        value = value.strip().strip('"').strip("'")
        pairs.append((key.strip(), value))
    return pairs


def find_placeholders(text: str) -> List[PlaceholderMatch]:
    """Return all keys whose values contain unresolved placeholders."""
    results = []
    for key, value in _parse_env(text):
        found = _PLACEHOLDER_RE.findall(value)
        if found:
            results.append(PlaceholderMatch(key=key, value=value, placeholders=found))
    return results


def find_placeholders_in_file(env_file: Path) -> List[PlaceholderMatch]:
    """Read *env_file* and return placeholder matches."""
    if not env_file.exists():
        raise FileNotFoundError(f"{env_file} does not exist")
    return find_placeholders(env_file.read_text())


def has_placeholders(text: str) -> bool:
    return bool(find_placeholders(text))


def summary(matches: List[PlaceholderMatch]) -> str:
    if not matches:
        return "No unresolved placeholders found."
    lines = [f"{len(matches)} key(s) with unresolved placeholders:"]
    for m in matches:
        lines.append(f"  {m}")
    return "\n".join(lines)
