"""Template support for envault.

Allows generating .env files from template files (.env.template or .env.example)
by filling in values from a sealed vault or interactively prompting the user.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from envault.vault import unseal

# Regex to match template placeholders like {{KEY}} or ${KEY}
_PLACEHOLDER_RE = re.compile(r"\{\{\s*(\w+)\s*\}\}|\$\{(\w+)\}")


def find_template(env_file: Path) -> Optional[Path]:
    """Locate a template file alongside the given .env file.

    Looks for <name>.template and <name>.example variants.
    Returns the first match, or None if none found.
    """
    candidates = [
        env_file.parent / (env_file.name + ".template"),
        env_file.parent / (env_file.name + ".example"),
        env_file.parent / ".env.template",
        env_file.parent / ".env.example",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def parse_template_keys(template_path: Path) -> list[str]:
    """Extract all placeholder key names from a template file.

    Supports both {{KEY}} and ${KEY} syntax.
    Returns a list of unique key names in order of first appearance.
    """
    text = template_path.read_text(encoding="utf-8")
    seen: list[str] = []
    for match in _PLACEHOLDER_RE.finditer(text):
        key = match.group(1) or match.group(2)
        if key and key not in seen:
            seen.append(key)
    return seen


def render_template(
    template_path: Path,
    values: dict[str, str],
    missing_marker: str = "<MISSING>",
) -> str:
    """Render a template file by substituting placeholders with provided values.

    Keys not present in *values* are replaced with *missing_marker*.

    Args:
        template_path: Path to the .env.template / .env.example file.
        values: Mapping of key names to their string values.
        missing_marker: Replacement text for keys absent from *values*.

    Returns:
        The rendered text with all placeholders substituted.
    """
    text = template_path.read_text(encoding="utf-8")

    def _replace(match: re.Match) -> str:  # type: ignore[type-arg]
        key = match.group(1) or match.group(2)
        return values.get(key, missing_marker)

    return _PLACEHOLDER_RE.sub(_replace, text)


def fill_from_vault(
    template_path: Path,
    env_file: Path,
    password: str,
    missing_marker: str = "<MISSING>",
) -> str:
    """Render a template using values decrypted from the vault for *env_file*.

    Args:
        template_path: Path to the template file.
        env_file: The .env file whose sealed vault will be used as the value source.
        password: Password to unseal the vault.
        missing_marker: Replacement text for keys absent from the vault.

    Returns:
        Rendered template text.

    Raises:
        FileNotFoundError: If the vault for *env_file* does not exist.
        ValueError: If the password is incorrect or the vault is corrupted.
    """
    raw = unseal(env_file, password)
    values = _parse_env_text(raw)
    return render_template(template_path, values, missing_marker=missing_marker)


def _parse_env_text(text: str) -> dict[str, str]:
    """Parse a plain .env text blob into a key→value mapping.

    Handles KEY=VALUE, KEY="VALUE", KEY='VALUE', and ignores comments / blank lines.
    """
    result: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, raw_value = line.partition("=")
        key = key.strip()
        raw_value = raw_value.strip()
        # Strip surrounding quotes
        if len(raw_value) >= 2 and raw_value[0] in ('"', "'") and raw_value[0] == raw_value[-1]:
            raw_value = raw_value[1:-1]
        result[key] = raw_value
    return result
