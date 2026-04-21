"""env_cast.py — Type casting and coercion utilities for .env values.

Supports casting string values from .env files to Python native types:
  - bool  (true/false/yes/no/1/0)
  - int
  - float
  - list  (comma-separated)
  - str   (default, no-op)

Useful for reading .env files and working with typed configuration.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_TRUE_VALUES = {"true", "yes", "1", "on"}
_FALSE_VALUES = {"false", "no", "0", "off"}

_SUPPORTED_TYPES = ("str", "int", "float", "bool", "list")


class CastError(ValueError):
    """Raised when a value cannot be cast to the requested type."""


# ---------------------------------------------------------------------------
# Core casting
# ---------------------------------------------------------------------------

def cast_value(value: str, as_type: str) -> Any:
    """Cast *value* (a raw string from a .env file) to *as_type*.

    Parameters
    ----------
    value:
        The raw string value, e.g. ``"true"``, ``"42"``, ``"a,b,c"``.
    as_type:
        One of ``"str"``, ``"int"``, ``"float"``, ``"bool"``, ``"list"``.

    Returns
    -------
    Any
        The coerced Python value.

    Raises
    ------
    CastError
        If the value cannot be converted or the type is unsupported.
    """
    if as_type not in _SUPPORTED_TYPES:
        raise CastError(
            f"Unsupported type '{as_type}'. Choose from: {', '.join(_SUPPORTED_TYPES)}"
        )

    if as_type == "str":
        return value

    if as_type == "bool":
        lower = value.strip().lower()
        if lower in _TRUE_VALUES:
            return True
        if lower in _FALSE_VALUES:
            return False
        raise CastError(f"Cannot cast '{value}' to bool.")

    if as_type == "int":
        try:
            return int(value.strip())
        except ValueError:
            raise CastError(f"Cannot cast '{value}' to int.")

    if as_type == "float":
        try:
            return float(value.strip())
        except ValueError:
            raise CastError(f"Cannot cast '{value}' to float.")

    if as_type == "list":
        # Split on commas; strip whitespace from each item; drop empty strings
        return [item.strip() for item in value.split(",") if item.strip()]

    # Should never reach here given the guard above, but satisfies type checkers
    return value  # pragma: no cover


def detect_type(value: str) -> str:
    """Heuristically detect the most specific type for *value*.

    Order of precedence: bool → int → float → list → str.

    Parameters
    ----------
    value:
        Raw string from a .env file.

    Returns
    -------
    str
        One of the supported type names.
    """
    stripped = value.strip().lower()

    if stripped in _TRUE_VALUES | _FALSE_VALUES:
        return "bool"

    try:
        int(stripped)
        return "int"
    except ValueError:
        pass

    try:
        float(stripped)
        return "float"
    except ValueError:
        pass

    # Treat as list when there is at least one comma with content on both sides
    parts = [p.strip() for p in value.split(",") if p.strip()]
    if "," in value and len(parts) >= 2:
        return "list"

    return "str"


def cast_env(env: dict[str, str], schema: dict[str, str]) -> dict[str, Any]:
    """Apply a type schema to a parsed env dictionary.

    Parameters
    ----------
    env:
        Mapping of key → raw string value (as returned by ``_parse_env`` helpers).
    schema:
        Mapping of key → type name.  Keys absent from *schema* are kept as str.

    Returns
    -------
    dict[str, Any]
        New mapping with values coerced to the declared types.

    Raises
    ------
    CastError
        If any value cannot be cast to its declared type.
    """
    result: dict[str, Any] = {}
    for key, raw in env.items():
        as_type = schema.get(key, "str")
        try:
            result[key] = cast_value(raw, as_type)
        except CastError as exc:
            raise CastError(f"Key '{key}': {exc}") from exc
    return result
