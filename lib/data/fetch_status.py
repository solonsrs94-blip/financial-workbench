"""Fetch-status tracker — pure Python, NO Streamlit imports.

Records whether each data fetch succeeded so the UI layer can surface
warnings instead of silently falling back to hardcoded defaults.

Usage (from page layer, after wrapping st.session_state dict):
    record(status, "erp", success=False, message="Damodaran ERP fetch failed")
    failures = get_failures(status, ["erp", "crp"])
"""

from typing import Optional


def record(
    status: dict,
    key: str,
    success: bool,
    *,
    source: str = "",
    message: str = "",
) -> None:
    """Record the outcome of a single fetch into the status dict."""
    if status is None:
        return
    status[key] = {
        "success": bool(success),
        "source": source,
        "message": message,
    }


def get(status: dict, key: str) -> Optional[dict]:
    """Return the stored entry for a key, or None if absent."""
    if not status:
        return None
    return status.get(key)


def get_failures(
    status: dict,
    keys: Optional[list[str]] = None,
) -> list[dict]:
    """Return a list of failure entries with their keys attached.

    If ``keys`` is None, returns failures across the whole status dict.
    """
    if not status:
        return []
    out: list[dict] = []
    iterable = keys if keys is not None else list(status.keys())
    for k in iterable:
        entry = status.get(k)
        if entry and entry.get("success") is False:
            out.append({"key": k, **entry})
    return out


def clear(status: dict) -> None:
    """Wipe all recorded statuses."""
    if status is None:
        return
    status.clear()
