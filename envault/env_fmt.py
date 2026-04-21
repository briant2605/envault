"""env_fmt.py — Format and normalize .env files.

Provides utilities to sort, align, and clean up .env files for
consistent style across a team. Supports optional grouping by
prefix and alignment of values.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional, Tuple

# Matches: KEY=VALUE, KEY="VALUE", KEY='VALUE', or KEY= (empty)
_PAIR_RE = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$')


class EnvLine:
    """Represents a single line in a .env file."""

    def __init__(self, raw: str):
        self.raw = raw
        m = _PAIR_RE.match(raw.strip())
        if m:
            self.key: Optional[str] = m.group(1)
            self.value: str = m.group(2)
            self.is_pair = True
        else:
            self.key = None
            self.value = ""
            self.is_pair = False

    @property
    def is_comment(self) -> bool:
        return self.raw.strip().startswith("#")

    @property
    def is_blank(self) -> bool:
        return self.raw.strip() == ""


def parse_lines(text: str) -> List[EnvLine]:
    """Parse raw .env text into a list of EnvLine objects."""
    return [EnvLine(line) for line in text.splitlines()]


def _strip_quotes(value: str) -> Tuple[str, str]:
    """Return (quote_char, inner_value) for a possibly-quoted value."""
    if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
        return value[0], value[1:-1]
    return "", value


def format_env(
    text: str,
    *,
    sort_keys: bool = False,
    strip_blanks: bool = False,
    normalize_quotes: Optional[str] = None,
    align_values: bool = False,
) -> str:
    """Return a reformatted version of the .env text.

    Args:
        text:             Raw .env file content.
        sort_keys:        If True, sort key=value pairs alphabetically.
                          Comments and blank lines preceding a block are
                          kept together with that block when sorting is
                          not requested; with sorting they move to the top.
        strip_blanks:     Remove consecutive duplicate blank lines.
        normalize_quotes: One of None (leave as-is), '"', or "'".
                          Re-wraps every value in the chosen quote style.
        align_values:     Pad keys with spaces so that all '=' signs line up.

    Returns:
        Formatted .env text (no trailing newline added automatically).
    """
    lines = parse_lines(text)

    # --- normalise quotes ---------------------------------------------------
    if normalize_quotes in ('"', "'"):
        q = normalize_quotes
        for ln in lines:
            if ln.is_pair:
                _, inner = _strip_quotes(ln.value)
                ln.value = f"{q}{inner}{q}"
                ln.raw = f"{ln.key}={ln.value}"

    # --- sort key=value pairs -----------------------------------------------
    if sort_keys:
        pairs = [ln for ln in lines if ln.is_pair]
        non_pairs = [ln for ln in lines if not ln.is_pair]
        pairs.sort(key=lambda ln: (ln.key or "").lower())
        # Rebuild: comments/blanks first, then sorted pairs
        lines = non_pairs + pairs

    # --- strip duplicate blank lines ----------------------------------------
    if strip_blanks:
        result: List[EnvLine] = []
        prev_blank = False
        for ln in lines:
            if ln.is_blank:
                if not prev_blank:
                    result.append(ln)
                prev_blank = True
            else:
                prev_blank = False
                result.append(ln)
        lines = result

    # --- align values -------------------------------------------------------
    if align_values:
        max_key_len = max(
            (len(ln.key) for ln in lines if ln.is_pair),
            default=0,
        )
        for ln in lines:
            if ln.is_pair:
                padding = " " * (max_key_len - len(ln.key))  # type: ignore[arg-type]
                ln.raw = f"{ln.key}{padding}= {ln.value}"

    return "\n".join(ln.raw for ln in lines)


def format_file(
    env_path: Path,
    *,
    sort_keys: bool = False,
    strip_blanks: bool = False,
    normalize_quotes: Optional[str] = None,
    align_values: bool = False,
    in_place: bool = False,
) -> str:
    """Format a .env file on disk.

    Args:
        env_path:  Path to the .env file.
        in_place:  If True, overwrite the file with the formatted content.

    Returns:
        The formatted text (whether or not written to disk).

    Raises:
        FileNotFoundError: If *env_path* does not exist.
    """
    if not env_path.exists():
        raise FileNotFoundError(f".env file not found: {env_path}")

    text = env_path.read_text(encoding="utf-8")
    formatted = format_env(
        text,
        sort_keys=sort_keys,
        strip_blanks=strip_blanks,
        normalize_quotes=normalize_quotes,
        align_values=align_values,
    )

    if in_place:
        env_path.write_text(formatted, encoding="utf-8")

    return formatted
