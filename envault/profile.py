"""Profile management: named password profiles for multiple vaults."""

import json
import os
from pathlib import Path

PROFILES_FILE = Path.home() / ".envault" / "profiles.json"


def _load_profiles() -> dict:
    if not PROFILES_FILE.exists():
        return {}
    with open(PROFILES_FILE, "r") as f:
        return json.load(f)


def _save_profiles(profiles: dict) -> None:
    PROFILES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles, f, indent=2)


def set_profile(name: str, password: str) -> None:
    """Store a named profile with its password (plaintext, user-controlled)."""
    profiles = _load_profiles()
    profiles[name] = {"password": password}
    _save_profiles(profiles)


def get_profile(name: str) -> dict:
    """Retrieve a profile by name. Raises KeyError if not found."""
    profiles = _load_profiles()
    if name not in profiles:
        raise KeyError(f"Profile '{name}' not found.")
    return profiles[name]


def delete_profile(name: str) -> None:
    """Remove a named profile."""
    profiles = _load_profiles()
    if name not in profiles:
        raise KeyError(f"Profile '{name}' not found.")
    del profiles[name]
    _save_profiles(profiles)


def list_profiles() -> list:
    """Return all profile names."""
    return list(_load_profiles().keys())
