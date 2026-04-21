"""Tests for envault.profile module."""

import json
import pytest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

import envault.profile as profile_mod


@pytest.fixture(autouse=True)
def isolated_profiles(tmp_path, monkeypatch):
    profiles_file = tmp_path / ".envault" / "profiles.json"
    monkeypatch.setattr(profile_mod, "PROFILES_FILE", profiles_file)
    yield profiles_file


def test_list_profiles_empty():
    assert profile_mod.list_profiles() == []


def test_set_profile_creates_entry(isolated_profiles):
    profile_mod.set_profile("dev", "secret123")
    assert "dev" in profile_mod.list_profiles()


def test_get_profile_returns_password(isolated_profiles):
    profile_mod.set_profile("dev", "secret123")
    p = profile_mod.get_profile("dev")
    assert p["password"] == "secret123"


def test_get_profile_missing_raises(isolated_profiles):
    with pytest.raises(KeyError, match="staging"):
        profile_mod.get_profile("staging")


def test_delete_profile_removes_entry(isolated_profiles):
    profile_mod.set_profile("dev", "secret123")
    profile_mod.delete_profile("dev")
    assert "dev" not in profile_mod.list_profiles()


def test_delete_profile_missing_raises(isolated_profiles):
    with pytest.raises(KeyError, match="ghost"):
        profile_mod.delete_profile("ghost")


def test_multiple_profiles(isolated_profiles):
    profile_mod.set_profile("dev", "devpass")
    profile_mod.set_profile("prod", "prodpass")
    names = profile_mod.list_profiles()
    assert "dev" in names and "prod" in names


def test_set_profile_overwrites(isolated_profiles):
    profile_mod.set_profile("dev", "old")
    profile_mod.set_profile("dev", "new")
    assert profile_mod.get_profile("dev")["password"] == "new"


def test_set_profile_persists_to_disk(isolated_profiles):
    """Ensure that set_profile writes data that survives a fresh load."""
    profile_mod.set_profile("dev", "secret123")

    # Reload profiles from disk by reading the file directly
    assert isolated_profiles.exists(), "Profiles file should have been created"
    data = json.loads(isolated_profiles.read_text())
    assert "dev" in data
    assert data["dev"]["password"] == "secret123"
