"""Sort keys in a .env file alphabetically or by custom order."""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple


_COMMENT_OR_BLANK = re.compile(r'^\s*(#.*)?$')
_KEY_VALUE = re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)$')


def _parse_lines(text: str) -> List[Tuple[str | None, str]]:
    """Return list of (key_or_None, raw_line) pairs."""
    result = []
    for line in text.splitlines(keepends=True):
        m = _KEY_VALUE.match(line)
        if m:
            result.append((m.group(1), line))
        else:
            result.append((None, line))
    return result


def sort_env_text(
    text: str,
    reverse: bool = False,
    keep_comments_attached: bool = True,
) -> str:
    """Return *text* with key=value lines sorted alphabetically.

    Leading comment/blank lines that immediately precede a key=value line are
    treated as "attached" to that key and move with it when
    *keep_comments_attached* is True.
    """
    lines = _parse_lines(text)

    # Group lines into blocks: a block is (leading comments/blanks, key_line)
    # or standalone comment/blank lines at the top.
    blocks: list[tuple[list[str], str | None, str]] = []  # (prefix_lines, key, key_line)
    pending: list[str] = []

    for key, raw in lines:
        if key is None:
            if keep_comments_attached:
                pending.append(raw)
            else:
                blocks.append(([], None, raw))
        else:
            blocks.append((pending, key, raw))
            pending = []

    # Flush any trailing comments/blanks
    trailing = pending

    # Separate header (leading non-key blocks) from sortable blocks
    header: list[str] = []
    sortable: list[tuple[list[str], str, str]] = []

    for prefix, key, raw in blocks:
        if key is None:
            header.append(raw)
        else:
            sortable.append((prefix, key, raw))

    sortable.sort(key=lambda t: t[1].lower(), reverse=reverse)

    out_lines: list[str] = list(header)
    for prefix, _key, raw in sortable:
        out_lines.extend(prefix)
        out_lines.append(raw)
    out_lines.extend(trailing)

    return "".join(out_lines)


def sort_env_file(
    path: Path | str,
    reverse: bool = False,
    keep_comments_attached: bool = True,
) -> str:
    """Sort the .env file at *path* in-place. Returns the new content."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f".env file not found: {path}")
    original = path.read_text()
    sorted_text = sort_env_text(
        original,
        reverse=reverse,
        keep_comments_attached=keep_comments_attached,
    )
    path.write_text(sorted_text)
    return sorted_text
