"""Saved valuations — CRUD for valuation JSON files on disk.

Pure Python — NO streamlit imports.
"""

import json
from datetime import datetime
from pathlib import Path

from config.settings import SAVED_VALUATIONS_DIR


def _get_save_dir() -> Path:
    """Return (and ensure) the saved valuations directory."""
    SAVED_VALUATIONS_DIR.mkdir(parents=True, exist_ok=True)
    return SAVED_VALUATIONS_DIR


def save_valuation(data: dict, ticker: str) -> str:
    """Write a valuation dict to a new JSON file.

    Returns the filename (not the full path).
    """
    save_dir = _get_save_dir()
    now = datetime.now()
    filename = f"{ticker}_{now.strftime('%Y%m%d_%H%M%S')}.json"
    path = save_dir / filename

    json_str = json.dumps(data, indent=2, default=str, ensure_ascii=False)
    path.write_text(json_str, encoding="utf-8")
    return filename


def list_valuations() -> list[dict]:
    """List all saved valuations with metadata.

    Returns a list of metadata dicts (from _meta key), each enriched
    with 'filename'. Sorted newest first.
    """
    save_dir = _get_save_dir()
    results = []

    for path in save_dir.glob("*.json"):
        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
            meta = data.get("_meta", {})
            meta["filename"] = path.name
            results.append(meta)
        except (json.JSONDecodeError, OSError):
            continue

    results.sort(key=lambda m: m.get("save_date", ""), reverse=True)
    return results


def load_valuation(filename: str) -> dict:
    """Read and parse a saved valuation JSON file.

    Validates that filename is a simple name (no path traversal).
    """
    if "/" in filename or "\\" in filename or ".." in filename:
        raise ValueError(f"Invalid filename: {filename}")

    save_dir = _get_save_dir()
    path = save_dir / filename

    if not path.exists():
        raise FileNotFoundError(f"Valuation file not found: {filename}")

    raw = path.read_text(encoding="utf-8")
    return json.loads(raw)


def delete_valuation(filename: str) -> bool:
    """Delete a saved valuation file.

    Returns True on success, False if not found.
    """
    if "/" in filename or "\\" in filename or ".." in filename:
        raise ValueError(f"Invalid filename: {filename}")

    save_dir = _get_save_dir()
    path = save_dir / filename

    if not path.exists():
        return False

    path.unlink()
    return True
