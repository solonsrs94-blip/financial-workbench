"""Streamlit-side helpers for the fetch-status tracker.

Pages call ``record_fetch(...)`` after a data fetch, and
``render_fetch_warnings([keys...])`` at the top of a step to surface
one ``st.warning`` per failed fetch. The lib layer stays Streamlit-free.
"""

from typing import Iterable, Optional

import streamlit as st

from lib.data import fetch_status as _fs


_SESSION_KEY = "fetch_status"


# Human-friendly labels used in the default warning messages.
LABELS: dict[str, str] = {
    "rf": "Risk-free rate",
    "erp": "Equity risk premium (ERP)",
    "crp": "Country risk premium (CRP)",
    "beta": "Beta",
    "total_debt": "Total debt",
    "interest_expense": "Interest expense",
    "tax_rate": "Tax rate",
    "credit_spread": "Credit spread",
    "industry_averages": "Industry averages",
    "industry_beta": "Industry beta",
    "cogs_pct": "COGS %",
}


def _status_dict() -> dict:
    return st.session_state.setdefault(_SESSION_KEY, {})


def record_fetch(
    key: str,
    success: bool,
    *,
    source: str = "",
    message: str = "",
) -> None:
    """Record a fetch outcome in session state."""
    _fs.record(_status_dict(), key, success, source=source, message=message)


def fetch_succeeded(key: str) -> bool:
    """Return True only if an entry exists and succeeded."""
    entry = _fs.get(_status_dict(), key)
    return bool(entry and entry.get("success"))


def render_fetch_warnings(
    keys: Iterable[str],
    *,
    title: Optional[str] = None,
) -> int:
    """Emit one ``st.warning`` per failed fetch among ``keys``.

    Returns the number of warnings rendered.
    """
    status = _status_dict()
    failures = _fs.get_failures(status, list(keys))
    if not failures:
        return 0
    if title:
        st.markdown(f"**{title}**")
    for f in failures:
        label = LABELS.get(f["key"], f["key"])
        msg = f.get("message") or f"{label} fetch failed — enter value manually"
        st.warning(msg, icon="⚠️")
    return len(failures)


def clear_fetch_status() -> None:
    """Reset the whole fetch-status dict (e.g. on ticker change)."""
    _fs.clear(_status_dict())
