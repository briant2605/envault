"""Import/export .env files to/from different formats (dotenv, JSON, YAML)."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict


FORMATS = ("dotenv", "json", "yaml")


def _parse_env(text: str) -> Dict[str, str]:
    """Parse dotenv-style text into a dict."""
    result: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            result[key] = value
    return result


def _to_dotenv(data: Dict[str, str]) -> str:
    lines = [f'{k}="{v}"' for k, v in sorted(data.items())]
    return "\n".join(lines) + "\n" if lines else ""


def _to_json(data: Dict[str, str]) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def _to_yaml(data: Dict[str, str]) -> str:
    lines = []
    for k, v in sorted(data.items()):
        safe_v = f'"{v}"' if any(c in v for c in (":", "#", "{", "}")) else v
        lines.append(f"{k}: {safe_v}")
    return "\n".join(lines) + "\n" if lines else ""


def export_env(env_path: Path, fmt: str) -> str:
    """Read an env file and return its contents in the requested format."""
    if fmt not in FORMATS:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {', '.join(FORMATS)}")
    if not env_path.exists():
        raise FileNotFoundError(f"Env file not found: {env_path}")
    data = _parse_env(env_path.read_text())
    if fmt == "dotenv":
        return _to_dotenv(data)
    if fmt == "json":
        return _to_json(data)
    return _to_yaml(data)


def import_env(source: str, fmt: str) -> Dict[str, str]:
    """Parse env data from the given format string and return a dict."""
    if fmt not in FORMATS:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {', '.join(FORMATS)}")
    if fmt == "dotenv":
        return _parse_env(source)
    if fmt == "json":
        raw = json.loads(source)
        if not isinstance(raw, dict):
            raise ValueError("JSON input must be a top-level object")
        return {str(k): str(v) for k, v in raw.items()}
    # yaml — minimal key: value parser (no external dep)
    result: Dict[str, str] = {}
    for line in source.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def write_env(data: Dict[str, str], dest: Path) -> None:
    """Write a dict of key/value pairs to a dotenv file."""
    dest.write_text(_to_dotenv(data))
