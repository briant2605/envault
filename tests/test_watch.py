"""Tests for envault.watch module."""

import time
import pytest
from pathlib import Path

from envault.watch import get_mtime, watch_env
from envault.vault import unseal


PASSWORD = "watchpass"


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("KEY=original\n")
    return f


def test_get_mtime_existing(env_file: Path) -> None:
    mtime = get_mtime(env_file)
    assert mtime is not None
    assert isinstance(mtime, float)


def test_get_mtime_missing(tmp_path: Path) -> None:
    missing = tmp_path / "ghost.env"
    assert get_mtime(missing) is None


def test_watch_env_missing_file_raises(tmp_path: Path) -> None:
    missing = tmp_path / "nope.env"
    with pytest.raises(FileNotFoundError, match="env file not found"):
        watch_env(missing, PASSWORD, interval=0.01, max_iterations=0)


def test_watch_env_no_change_no_seal(env_file: Path) -> None:
    """Running watch_env with no file changes should perform zero seals."""
    count = watch_env(env_file, PASSWORD, interval=0.01, max_iterations=3)
    assert count == 0


def test_watch_env_detects_change_and_reseals(env_file: Path, tmp_path: Path) -> None:
    """Modifying the file during watch should trigger a re-seal."""
    changed_calls = []

    def _on_change(p: Path) -> None:
        changed_calls.append(p)

    # We'll run one iteration that detects a pre-staged mtime change.
    # Patch the mtime by rewriting the file between construction and first poll.
    import envault.watch as watch_mod

    original_sleep = time.sleep
    iteration = [0]

    def fake_sleep(seconds: float) -> None:  # noqa: ARG001
        iteration[0] += 1
        if iteration[0] == 1:
            # Simulate a file change
            env_file.write_text("KEY=modified\n")
        original_sleep(0)

    import unittest.mock as mock

    with mock.patch("envault.watch.time.sleep", side_effect=fake_sleep):
        count = watch_env(
            env_file,
            PASSWORD,
            interval=0.01,
            max_iterations=2,
            on_change=_on_change,
        )

    assert count == 1
    assert len(changed_calls) == 1
    assert changed_calls[0] == env_file


def test_watch_env_resealed_vault_is_readable(env_file: Path) -> None:
    """After a watch-triggered re-seal the vault should be unsealable."""
    import envault.watch as watch_mod
    import unittest.mock as mock
    import time as _time

    original_sleep = _time.sleep
    iteration = [0]

    def fake_sleep(seconds: float) -> None:  # noqa: ARG001
        iteration[0] += 1
        if iteration[0] == 1:
            env_file.write_text("NEWKEY=hello\n")
        original_sleep(0)

    with mock.patch("envault.watch.time.sleep", side_effect=fake_sleep):
        watch_env(env_file, PASSWORD, interval=0.01, max_iterations=2)

    recovered = unseal(env_file, PASSWORD)
    assert recovered == {"NEWKEY": "hello"}
