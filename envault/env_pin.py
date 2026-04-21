"""Pin/unpin specific keys to prevent accidental overwrite during merge or import."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

_PINS_FILENAME = ".envault_pins.json"


def _pins_path(env_file: Path) -> Path:
    return env_file.parent / _PINS_FILENAME


def _load_pins(env_file: Path) -> dict:
    path = _pins_path(env_file)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_pins(env_file: Path, data: dict) -> None:
    _pins_path(env_file).write_text(json.dumps(data, indent=2))


def pin_key(env_file: Path, key: str) -> None:
    """Mark *key* as pinned for *env_file*."""
    data = _load_pins(env_file)
    pins: List[str] = data.get(str(env_file), [])
    if key not in pins:
        pins.append(key)
    data[str(env_file)] = pins
    _save_pins(env_file, data)


def unpin_key(env_file: Path, key: str) -> None:
    """Remove pin from *key* for *env_file*. Raises KeyError if not pinned."""
    data = _load_pins(env_file)
    pins: List[str] = data.get(str(env_file), [])
    if key not in pins:
        raise KeyError(f"{key!r} is not pinned")
    pins.remove(key)
    data[str(env_file)] = pins
    _save_pins(env_file, data)


def get_pinned(env_file: Path) -> List[str]:
    """Return the list of pinned keys for *env_file*."""
    data = _load_pins(env_file)
    return list(data.get(str(env_file), []))


def is_pinned(env_file: Path, key: str) -> bool:
    return key in get_pinned(env_file)


def clear_pins(env_file: Path) -> None:
    """Remove all pins for *env_file*."""
    data = _load_pins(env_file)
    data.pop(str(env_file), None)
    _save_pins(env_file, data)
