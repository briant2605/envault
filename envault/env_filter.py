"""Filter .env keys by prefix, suffix, or pattern."""
from __future__ import annotations

import fnmatch
import re
from pathlib import Path
from typing import Dict, List, Optional


def _parse_env(text: str) -> Dict[str, str]:
    """Parse env text into an ordered dict of key -> value."""
    result: Dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        result[key] = value
    return result


def filter_by_prefix(env: Dict[str, str], prefix: str) -> Dict[str, str]:
    """Return entries whose key starts with *prefix*."""
    return {k: v for k, v in env.items() if k.startswith(prefix)}


def filter_by_suffix(env: Dict[str, str], suffix: str) -> Dict[str, str]:
    """Return entries whose key ends with *suffix*."""
    return {k: v for k, v in env.items() if k.endswith(suffix)}


def filter_by_glob(env: Dict[str, str], pattern: str) -> Dict[str, str]:
    """Return entries whose key matches a glob *pattern*."""
    return {k: v for k, v in env.items() if fnmatch.fnmatch(k, pattern)}


def filter_by_regex(env: Dict[str, str], pattern: str) -> Dict[str, str]:
    """Return entries whose key matches a regex *pattern*."""
    rx = re.compile(pattern)
    return {k: v for k, v in env.items() if rx.search(k)}


def filter_env_text(
    text: str,
    *,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
    glob: Optional[str] = None,
    regex: Optional[str] = None,
) -> Dict[str, str]:
    """Parse *text* and apply one or more filter criteria (ANDed together)."""
    env = _parse_env(text)
    if prefix is not None:
        env = filter_by_prefix(env, prefix)
    if suffix is not None:
        env = filter_by_suffix(env, suffix)
    if glob is not None:
        env = filter_by_glob(env, glob)
    if regex is not None:
        env = filter_by_regex(env, regex)
    return env


def filter_env_file(
    path: Path,
    **kwargs,
) -> Dict[str, str]:
    """Read *path* and apply filters. Returns empty dict if file missing."""
    if not path.exists():
        return {}
    return filter_env_text(path.read_text(encoding="utf-8"), **kwargs)
