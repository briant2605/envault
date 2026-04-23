"""Chain multiple .env files together, with later files overriding earlier ones."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple


def _parse_env(text: str) -> Dict[str, str]:
    """Parse env text into an ordered dict of key->value."""
    result: Dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            result[key] = value
    return result


def _to_dotenv(pairs: Dict[str, str]) -> str:
    """Serialize key/value pairs back to .env format."""
    lines = [f"{k}={v}" for k, v in sorted(pairs.items())]
    return "\n".join(lines) + ("\n" if lines else "")


def chain_env_texts(texts: List[str]) -> Dict[str, str]:
    """Merge a list of env texts left-to-right; later entries override earlier ones."""
    merged: Dict[str, str] = {}
    for text in texts:
        merged.update(_parse_env(text))
    return merged


def chain_env_files(paths: List[Path]) -> Dict[str, str]:
    """Load and chain env files from disk; missing files are silently skipped."""
    texts: List[str] = []
    for p in paths:
        if Path(p).exists():
            texts.append(Path(p).read_text())
    return chain_env_texts(texts)


def chain_sources(paths: List[Path]) -> Tuple[Dict[str, str], List[str]]:
    """Return merged env and a list of which file each key came from (last-wins)."""
    provenance: Dict[str, str] = {}
    merged: Dict[str, str] = {}
    for p in paths:
        path = Path(p)
        if not path.exists():
            continue
        parsed = _parse_env(path.read_text())
        for key, value in parsed.items():
            merged[key] = value
            provenance[key] = str(path)
    return merged, provenance
