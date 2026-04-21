"""Set, unset, and get individual keys in a .env file."""

from pathlib import Path
from typing import Optional


def _parse_env(text: str) -> list[tuple[str, str, str]]:
    """Return list of (kind, key_or_raw, value) tuples.
    kind is 'pair', 'comment', or 'blank'.
    """
    rows = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            rows.append(("blank", "", ""))
        elif stripped.startswith("#"):
            rows.append(("comment", line, ""))
        elif "=" in stripped:
            key, _, value = stripped.partition("=")
            rows.append(("pair", key.strip(), value.strip()))
        else:
            rows.append(("comment", line, ""))
    return rows


def _to_dotenv(rows: list[tuple[str, str, str]]) -> str:
    parts = []
    for kind, key, value in rows:
        if kind == "pair":
            parts.append(f"{key}={value}")
        elif kind == "comment":
            parts.append(key)
        else:
            parts.append("")
    text = "\n".join(parts)
    if text and not text.endswith("\n"):
        text += "\n"
    return text


def set_key(env_path: Path, key: str, value: str) -> None:
    """Set a key in the .env file, adding it if absent."""
    text = env_path.read_text() if env_path.exists() else ""
    rows = _parse_env(text)
    found = False
    for i, (kind, k, _) in enumerate(rows):
        if kind == "pair" and k == key:
            rows[i] = ("pair", key, value)
            found = True
            break
    if not found:
        rows.append(("pair", key, value))
    env_path.write_text(_to_dotenv(rows))


def unset_key(env_path: Path, key: str) -> None:
    """Remove a key from the .env file. Raises KeyError if not found."""
    if not env_path.exists():
        raise KeyError(f"Key '{key}' not found (file missing)")
    rows = _parse_env(env_path.read_text())
    new_rows = [r for r in rows if not (r[0] == "pair" and r[1] == key)]
    if len(new_rows) == len(rows):
        raise KeyError(f"Key '{key}' not found")
    env_path.write_text(_to_dotenv(new_rows))


def get_key(env_path: Path, key: str) -> Optional[str]:
    """Return the value for a key, or None if not present."""
    if not env_path.exists():
        return None
    for kind, k, value in _parse_env(env_path.read_text()):
        if kind == "pair" and k == key:
            return value
    return None
