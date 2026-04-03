"""Comps Step 2: Comps Table — data fetching, multiples, summary stats.

Fetches full comps data for target + selected peers, calculates
summary statistics (mean/median/high/low), and delegates rendering
to comps_step2_render.py.
"""

import statistics

import streamlit as st

from lib.data.valuation_data import get_comps_row
from pages.valuation.comps_step2_render import render_comps_table

# Multiples fields used for summary calculations
MULTIPLE_FIELDS = [
    "ev_revenue", "ev_ebitda", "ev_ebit",
    "trailing_pe", "forward_pe",
    "fwd_ev_revenue", "fwd_ev_ebitda",
]


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
        }
    return st.session_state[key]


# ── Main render ────────────────────────────────────────────────


def render(prepared: dict, ticker: str) -> None:
    """Render Step 2: Comps Table."""
    st.subheader("Step 2 - Comps Table")

    # Check if peers are selected
    peer_state = st.session_state.get("comps_peers", {})
    selected = peer_state.get("selected", [])

    if not selected or len(selected) < 3:
        st.warning(
            "Select at least 3 peers in Step 1 to build the comps table."
        )
        return

    state = _get_state()

    # Fetch data if not done yet or peers changed
    if not state["fetched"] or _peers_changed(state, ticker, selected):
        _fetch_all(state, ticker, selected)

    if not state["target"]:
        st.error("Could not fetch data for the target company.")
        return

    # Exclude toggles
    _render_exclude_controls(state)

    # Recompute summary with current exclusions
    state["summary"] = _compute_summary(
        state["peers"], state["excluded"],
    )

    # Render table
    render_comps_table(
        state["target"], state["peers"],
        state["summary"], state["excluded"],
    )

    # Footnote for FMP data
    has_fwd_ebitda = any(
        p.get("fwd_ev_ebitda") is not None
        for p in state["peers"]
    )
    if has_fwd_ebitda or (
        state["target"] and state["target"].get("fwd_ev_ebitda")
    ):
        st.caption(
            "\\* Fwd EV/EBITDA uses consensus estimates where available. "
            "Coverage varies by company."
        )


# ── Data fetching ──────────────────────────────────────────────


def _fetch_all(state: dict, ticker: str, selected: list[str]) -> None:
    """Fetch comps data for target + all peers."""
    with st.spinner(
        f"Fetching comps data for {len(selected) + 1} companies..."
    ):
        # Target
        state["target"] = get_comps_row(ticker)

        # Peers
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
    peers: list[dict], excluded: set,
) -> dict:
    """Compute mean, median, high, low for each multiple field."""
    included = [p for p in peers if p["ticker"] not in excluded]

    result = {}
    for stat_name in ["mean", "median", "high", "low"]:
        result[stat_name] = {}

    for field in MULTIPLE_FIELDS:
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
