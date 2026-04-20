"""Track unlock/lock history per .env file."""

import json
from datetime import datetime, timezone
from pathlib import Path

_HISTORY_DIR = Path.home() / ".envault" / "history"


def _history_path(env_file: Path) -> Path:
    """Return the history file path for a given .env file."""
    safe_name = str(env_file.resolve()).replace("/", "_").replace("\\", "_").lstrip("_")
    _HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    return _HISTORY_DIR / f"{safe_name}.json"


def _load(env_file: Path) -> list:
    path = _history_path(env_file)
    if not path.exists():
        return []
    with path.open() as f:
        return json.load(f)


def _save(env_file: Path, entries: list) -> None:
    path = _history_path(env_file)
    with path.open("w") as f:
        json.dump(entries, f, indent=2)


def record(env_file: Path, action: str, note: str = "") -> None:
    """Record a history entry (action: 'lock' or 'unlock')."""
    entries = _load(env_file)
    entries.append({
        "action": action,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "env_file": str(env_file.resolve()),
        "note": note,
    })
    _save(env_file, entries)


def get_history(env_file: Path) -> list:
    """Return all history entries for a .env file."""
    return _load(env_file)


def clear_history(env_file: Path) -> None:
    """Delete the history file for a .env file."""
    path = _history_path(env_file)
    if path.exists():
        path.unlink()
