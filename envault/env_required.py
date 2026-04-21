"""Check for required keys in a .env file against a required-keys list."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class MissingKeyReport:
    missing: List[str] = field(default_factory=list)
    present: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.missing) == 0

    def summary(self) -> str:
        lines = []
        if self.present:
            lines.append(f"Present  ({len(self.present)}): {', '.join(sorted(self.present))}")
        if self.missing:
            lines.append(f"Missing  ({len(self.missing)}): {', '.join(sorted(self.missing))}")
        return "\n".join(lines) if lines else "No required keys defined."


def _required_path(env_file: Path) -> Path:
    return env_file.parent / (env_file.name + ".required.json")


def _parse_env(text: str) -> dict:
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, _ = line.partition("=")
            result[key.strip()] = True
    return result


def load_required_keys(env_file: Path) -> List[str]:
    path = _required_path(env_file)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def save_required_keys(env_file: Path, keys: List[str]) -> None:
    path = _required_path(env_file)
    path.write_text(json.dumps(sorted(set(keys)), indent=2))


def check_required(env_file: Path, required: Optional[List[str]] = None) -> MissingKeyReport:
    if required is None:
        required = load_required_keys(env_file)
    present_keys = _parse_env(env_file.read_text()).keys() if env_file.exists() else set()
    report = MissingKeyReport()
    for key in required:
        if key in present_keys:
            report.present.append(key)
        else:
            report.missing.append(key)
    return report
