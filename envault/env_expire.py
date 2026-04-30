"""env_expire.py — track expiry dates for .env keys."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Optional


def _expire_path(env_file: Path) -> Path:
    return env_file.parent / f".{env_file.name}.expire.json"


def _load_expiry(env_file: Path) -> dict[str, str]:
    p = _expire_path(env_file)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_expiry(env_file: Path, data: dict[str, str]) -> None:
    _expire_path(env_file).write_text(json.dumps(data, indent=2, sort_keys=True))


def set_expiry(env_file: Path, key: str, expiry: date) -> None:
    """Assign an expiry date (ISO format) to a key."""
    data = _load_expiry(env_file)
    data[key] = expiry.isoformat()
    _save_expiry(env_file, data)


def remove_expiry(env_file: Path, key: str) -> None:
    """Remove the expiry date for a key."""
    data = _load_expiry(env_file)
    data.pop(key, None)
    _save_expiry(env_file, data)


def get_expiry(env_file: Path, key: str) -> Optional[date]:
    """Return the expiry date for a key, or None."""
    data = _load_expiry(env_file)
    raw = data.get(key)
    return date.fromisoformat(raw) if raw else None


@dataclass
class ExpiryReport:
    key: str
    expiry: date
    expired: bool

    def __str__(self) -> str:
        status = "EXPIRED" if self.expired else "ok"
        return f"{self.key}: {self.expiry.isoformat()} [{status}]"


def check_expiry(env_file: Path, today: Optional[date] = None) -> list[ExpiryReport]:
    """Return expiry reports for all tracked keys."""
    today = today or datetime.utcnow().date()
    data = _load_expiry(env_file)
    reports = []
    for key, raw in sorted(data.items()):
        expiry = date.fromisoformat(raw)
        reports.append(ExpiryReport(key=key, expiry=expiry, expired=expiry < today))
    return reports
