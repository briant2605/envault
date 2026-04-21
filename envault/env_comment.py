"""Add, update, and remove inline comments on .env keys."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional


_KEY_RE = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=')


def _parse_lines(text: str) -> list[str]:
    return text.splitlines(keepends=True)


def set_comment(text: str, key: str, comment: str) -> str:
    """Set or replace the inline comment for *key*. Returns updated text."""
    lines = _parse_lines(text)
    result = []
    found = False
    for line in lines:
        m = _KEY_RE.match(line)
        if m and m.group(1) == key:
            found = True
            # Strip existing inline comment and trailing whitespace
            base = re.sub(r'\s*#.*$', '', line.rstrip())
            clean = comment.lstrip('#').strip()
            result.append(f"{base}  # {clean}\n")
        else:
            result.append(line)
    if not found:
        raise KeyError(f"Key '{key}' not found in env text")
    return ''.join(result)


def remove_comment(text: str, key: str) -> str:
    """Remove the inline comment for *key*. Returns updated text."""
    lines = _parse_lines(text)
    result = []
    found = False
    for line in lines:
        m = _KEY_RE.match(line)
        if m and m.group(1) == key:
            found = True
            base = re.sub(r'\s*#.*$', '', line.rstrip())
            result.append(f"{base}\n")
        else:
            result.append(line)
    if not found:
        raise KeyError(f"Key '{key}' not found in env text")
    return ''.join(result)


def get_comment(text: str, key: str) -> Optional[str]:
    """Return the inline comment for *key*, or None if absent."""
    for line in _parse_lines(text):
        m = _KEY_RE.match(line)
        if m and m.group(1) == key:
            cm = re.search(r'#(.*)$', line)
            return cm.group(1).strip() if cm else None
    raise KeyError(f"Key '{key}' not found in env text")


def set_comment_in_file(path: Path, key: str, comment: str) -> None:
    text = path.read_text()
    path.write_text(set_comment(text, key, comment))


def remove_comment_in_file(path: Path, key: str) -> None:
    text = path.read_text()
    path.write_text(remove_comment(text, key))


def get_comment_from_file(path: Path, key: str) -> Optional[str]:
    return get_comment(path.read_text(), key)
