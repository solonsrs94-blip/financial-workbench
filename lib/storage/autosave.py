"""Auto-save session state to disk as a safety net against session loss.

Pure Python — NO streamlit imports. Reuses session_collector/session_restorer.
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

from lib.exports.session_collector import collect_valuation_state


def _base_dir() -> Path:
    return Path.home() / ".workbench" / "sessions"


def autosave_path(ticker: str) -> Path:
    return _base_dir() / f"{ticker.upper()}_autosave.json"


def write_autosave(state: dict, ticker: str) -> bool:
    """Collect and write autosave for ticker. Returns True on success."""
    if not ticker:
        return False
    try:
        payload = collect_valuation_state(state, ticker)
        path = autosave_path(ticker)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Atomic write: tmp + rename
        fd, tmp_path = tempfile.mkstemp(
            prefix=f".{ticker}_", suffix=".json.tmp", dir=str(path.parent)
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f)
            os.replace(tmp_path, path)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
        return True
    except (OSError, TypeError, ValueError):
        return False


def read_autosave(ticker: str) -> dict | None:
    """Load raw autosave payload. Returns None if missing/unreadable."""
    if not ticker:
        return None
    path = autosave_path(ticker)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def delete_autosave(ticker: str) -> bool:
    """Remove autosave file for ticker. Returns True if removed."""
    path = autosave_path(ticker)
    try:
        if path.exists():
            path.unlink()
            return True
    except OSError:
        pass
    return False


def autosave_age_seconds(ticker: str) -> float | None:
    """Seconds since autosave was last modified, or None if no file."""
    path = autosave_path(ticker)
    if not path.exists():
        return None
    try:
        mtime = path.stat().st_mtime
        return (datetime.now().timestamp() - mtime)
    except OSError:
        return None


def format_age(seconds: float) -> str:
    """Human-readable age string."""
    if seconds < 60:
        return f"{int(seconds)}s ago"
    if seconds < 3600:
        return f"{int(seconds / 60)}m ago"
    if seconds < 86400:
        return f"{int(seconds / 3600)}h ago"
    return f"{int(seconds / 86400)}d ago"


def list_autosaves() -> list[dict]:
    """List all autosave files with metadata."""
    base = _base_dir()
    if not base.exists():
        return []
    out = []
    for p in base.glob("*_autosave.json"):
        try:
            ticker = p.stem.replace("_autosave", "")
            mtime = p.stat().st_mtime
            age = datetime.now().timestamp() - mtime
            out.append({
                "ticker": ticker,
                "path": str(p),
                "saved_at": datetime.fromtimestamp(mtime).isoformat(),
                "age_seconds": age,
            })
        except OSError:
            continue
    return sorted(out, key=lambda x: x["age_seconds"])
