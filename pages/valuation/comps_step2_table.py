"""Comps Step 2: Comps Table — data fetching, multiples, summary stats.

Fetches full comps data for target + selected peers, calculates
summary statistics (mean/median/high/low), and delegates rendering
to comps_step2_render.py.

Supports both normal and financial company column sets.
"""

import statistics

import streamlit as st

from lib.data.valuation_data import get_comps_row
from pages.valuation.comps_step2_render import (
    MULT_COLS_FINANCIAL,
    MULT_COLS_NORMAL,
    render_comps_table,
)

# Multiples fields used for summary calculations (by company type)
_MULT_FIELDS_NORMAL = [c[0] for c in MULT_COLS_NORMAL]
_MULT_FIELDS_FINANCIAL = [c[0] for c in MULT_COLS_FINANCIAL]


# ── Session state ──────────────────────────────────────────────


def _get_state() -> dict:
    """Get or initialize comps table state."""
    key = "comps_table"
    if key not in st.session_state:
        st.session_state[key] = {
            "target": None,
            "peers": [],
            "excluded": set(),
            "summary": {},
            "fetched": False,
            "is_financial": False,
        }
    return st.session_state[key]


def _is_financial(prepared: dict, ticker: str) -> bool:
    """Check if target is a financial institution.

    First checks prepared_data company_type (from classifier).
    Falls back to checking comps_table target data or comps candidate
    info, because the classifier may get empty sector if Company model
    lacks sector attribute.
    """
    _FIN_SECTORS = {"Financial Services", "Financials"}

    ctype = prepared.get("company_type", {})
    if ctype.get("type") == "financial":
        return True

    # Fallback: check target from comps_table (already fetched)
    comps_tbl = st.session_state.get("comps_table", {})
    target_row = comps_tbl.get("target")
    if target_row and target_row.get("industry", ""):
        ind = target_row["industry"].lower()
        if any(k in ind for k in ("bank", "insurance", "capital market")):
            return True

    # Fallback: check comps candidate info cache
    from lib.data.valuation_data import get_comps_candidate_info
    info = get_comps_candidate_info(ticker)
    if info and info.get("sector") in _FIN_SECTORS:
        return True

    return False


# ── Main render ────────────────────────────────────────────────


def render(prepared: dict, ticker: str) -> None:
    """Render Step 2: Comps Table."""
    st.subheader("Step 2 - Comps Table")

    peer_state = st.session_state.get("comps_peers", {})
    selected = peer_state.get("selected", [])

    if not selected or len(selected) < 3:
        st.warning(
            "Select at least 3 peers in Step 1 to build the comps table."
        )
        return

    state = _get_state()
    is_fin = _is_financial(prepared, ticker)
    state["is_financial"] = is_fin

    # Fetch data if not done yet or peers changed
    if not state["fetched"] or _peers_changed(state, ticker, selected):
        _fetch_all(state, ticker, selected)

    if not state["target"]:
        st.error("Could not fetch data for the target company.")
        return

    # Exclude toggles
    _render_exclude_controls(state)

    # Recompute summary with current exclusions
    mult_fields = _MULT_FIELDS_FINANCIAL if is_fin else _MULT_FIELDS_NORMAL
    state["summary"] = _compute_summary(
        state["peers"], state["excluded"], mult_fields,
    )

    # Render table
    render_comps_table(
        state["target"], state["peers"],
        state["summary"], state["excluded"],
        is_financial=is_fin,
    )

    # Footnotes
    if not is_fin:
        has_fwd_ebitda = any(
            p.get("fwd_ev_ebitda") is not None for p in state["peers"]
        )
        if has_fwd_ebitda or (
            state["target"] and state["target"].get("fwd_ev_ebitda")
        ):
            st.caption(
                "\\* Fwd EV/EBITDA uses consensus estimates. "
                "Coverage varies by company."
            )


# ── Data fetching ──────────────────────────────────────────────


def _fetch_all(state: dict, ticker: str, selected: list[str]) -> None:
    """Fetch comps data for target + all peers."""
    with st.spinner(
        f"Fetching comps data for {len(selected) + 1} companies..."
    ):
        state["target"] = get_comps_row(ticker)
        peers = []
        for t in selected:
            row = get_comps_row(t)
            if row:
                peers.append(row)
        state["peers"] = peers
        state["excluded"] = set()
        state["_ticker"] = ticker
        state["_selected"] = list(selected)
        state["fetched"] = True


def _peers_changed(
    state: dict, ticker: str, selected: list[str],
) -> bool:
    """Check if target or peer selection changed since last fetch."""
    return (
        state.get("_ticker") != ticker
        or state.get("_selected") != list(selected)
    )


# ── Exclude controls ──────────────────────────────────────────


def _render_exclude_controls(state: dict) -> None:
    """Render checkboxes to exclude peers from summary."""
    peers = state["peers"]
    if not peers:
        return

    with st.expander("Exclude peers from summary", expanded=False):
        excluded = set(state["excluded"])
        tickers = [p["ticker"] for p in peers]
        new_excluded = st.multiselect(
            "Select peers to exclude from Mean/Median calculations",
            tickers,
            default=list(excluded),
            key="comps_exclude_select",
        )
        state["excluded"] = set(new_excluded)


# ── Summary statistics ────────────────────────────────────────


def _compute_summary(
    peers: list[dict], excluded: set, mult_fields: list[str],
) -> dict:
    """Compute mean, median, high, low for each multiple field."""
    included = [p for p in peers if p["ticker"] not in excluded]

    result = {}
    for stat_name in ["mean", "median", "high", "low"]:
        result[stat_name] = {}

    for field in mult_fields:
        vals = [
            p[field] for p in included
            if p.get(field) is not None and p[field] > 0
        ]

        if vals:
            result["mean"][field] = statistics.mean(vals)
            result["median"][field] = statistics.median(vals)
            result["high"][field] = max(vals)
            result["low"][field] = min(vals)
        else:
            for stat_name in ["mean", "median", "high", "low"]:
                result[stat_name][field] = None

    return result
