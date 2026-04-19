"""Audit log for vault operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

AUDIT_LOG_NAME = ".envault_audit.log"


def audit_log_path(env_file: Path) -> Path:
    """Return the audit log path for a given .env file."""
    return env_file.parent / AUDIT_LOG_NAME


def record_event(env_file: Path, action: str, user: str | None = None) -> None:
    """Append an audit event to the log file."""
    log_path = audit_log_path(env_file)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "env_file": str(env_file.resolve()),
        "user": user or os.environ.get("USER", "unknown"),
    }
    with log_path.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def read_events(env_file: Path) -> list[dict]:
    """Read all audit events for a given .env file."""
    log_path = audit_log_path(env_file)
    if not log_path.exists():
        return []
    events = []
    with log_path.open("r") as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def clear_events(env_file: Path) -> None:
    """Clear the audit log for a given .env file."""
    log_path = audit_log_path(env_file)
    if log_path.exists():
        log_path.unlink()
