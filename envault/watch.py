"""Watch a .env file for changes and automatically re-lock the vault."""

import time
import os
from pathlib import Path
from typing import Optional, Callable

from envault.vault import vault_path_for, seal
from envault.audit import record_event


def get_mtime(path: Path) -> Optional[float]:
    """Return the modification time of a file, or None if it doesn't exist."""
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return None


def watch_env(
    env_file: Path,
    password: str,
    interval: float = 1.0,
    max_iterations: Optional[int] = None,
    on_change: Optional[Callable[[Path], None]] = None,
) -> int:
    """
    Watch *env_file* for modifications and re-seal the vault on every change.

    Parameters
    ----------
    env_file:       Path to the .env file to watch.
    password:       Password used to seal the vault.
    interval:       Polling interval in seconds.
    max_iterations: Stop after this many poll loops (useful for testing).
    on_change:      Optional callback invoked with the env_file path after each seal.

    Returns the total number of re-seal operations performed.
    """
    if not env_file.exists():
        raise FileNotFoundError(f"env file not found: {env_file}")

    last_mtime = get_mtime(env_file)
    seals_performed = 0
    iterations = 0

    while True:
        if max_iterations is not None and iterations >= max_iterations:
            break

        time.sleep(interval)
        iterations += 1

        current_mtime = get_mtime(env_file)
        if current_mtime is None:
            continue

        if current_mtime != last_mtime:
            seal(env_file, password)
            record_event(env_file, "watch-reseal")
            last_mtime = current_mtime
            seals_performed += 1
            if on_change:
                on_change(env_file)

    return seals_performed
