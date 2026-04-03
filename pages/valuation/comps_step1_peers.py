"""Comps Step 1: Peer Selection — candidate generation + analyst picks.

Two-layer candidate generation:
  Layer 1: Finnhub peers (seed list, ~10 tickers)
  Layer 2: S&P 500 universe filtered by industry + market cap band

Analyst selects peers from candidate table via data_editor checkboxes.
Data_editor widget is the single source of truth for selections.
Manual ticker entry supported.

Table rendering split into comps_step1_table.py.
"""

import streamlit as st

from lib.data.valuation_data import (
    filter_peer_universe,
    get_comps_candidate_info,
    get_finnhub_peers,
    get_peer_universe,
)
from pages.valuation.comps_step1_table import (
    render_candidate_table,
    render_target_anchor,
)


# ── Session state ──────────────────────────────────────────────


def _get_state(ticker: str) -> dict:
    """Get or initialize comps peer state."""
    key = "comps_peers"
    existing = st.session_state.get(key)
    if existing and existing.get("target") == ticker:
        return existing

    st.session_state[key] = {
        "target": ticker,
        "candidates": [],       # list[dict] with info per candidate
        "selected": [],         # confirmed selection (after Generate)
        "generated": False,     # whether candidate generation ran
    }
    return st.session_state[key]


# ── Main render ────────────────────────────────────────────────


def render(prepared: dict, ticker: str) -> None:
    """Render Step 1: Peer Selection."""
    st.subheader("Step 1 · Peer Selection")
    st.caption(
        "Select comparable companies for trading multiples analysis. "
        "Candidates are generated from Finnhub peers and S&P 500 "
        "industry/market-cap filtering."
    )

    state = _get_state(ticker)

    # ── Generate candidates on first load ──────────────────
    if not state["generated"]:
        _generate_candidates(state, ticker)
        state["generated"] = True

    # ── Target anchor row ──────────────────────────────────
    target_info = get_comps_candidate_info(ticker)
    if target_info:
        render_target_anchor(target_info)

    # ── Candidate table — returns live checkbox selections ─
    if state["candidates"]:
        live_selected = render_candidate_table(state["candidates"])
    else:
        st.info("No peer candidates found. Add tickers manually below.")
        live_selected = []

    # ── Manual add ─────────────────────────────────────────
    _render_manual_add(state, ticker)

    # ── Selection summary + Generate button ────────────────
    _render_generate_section(state, live_selected)


# ── Candidate generation ───────────────────────────────────────


def _generate_candidates(state: dict, ticker: str) -> None:
    """Two-layer candidate generation: Finnhub + S&P 500 filter."""
    with st.spinner("Generating peer candidates..."):
        target_info = get_comps_candidate_info(ticker)
        target_industry = ""
        target_mcap = 0
        if target_info:
            target_industry = target_info.get("industry", "")
            target_mcap = target_info.get("market_cap", 0)

        finnhub_tickers = get_finnhub_peers(ticker)

        universe = get_peer_universe()
        if universe:
            st.session_state["peer_universe"] = universe

        universe_tickers = []
        if universe and target_mcap:
            universe_tickers = filter_peer_universe(
                universe, ticker, target_industry, target_mcap,
            )

        ordered = _merge_dedupe(ticker, finnhub_tickers, universe_tickers)

        candidates = []
        for t in ordered[:30]:
            info = get_comps_candidate_info(t)
            if info:
                candidates.append(info)

        state["candidates"] = _sort_candidates(
            candidates, target_industry, target_mcap,
        )


def _merge_dedupe(
    target: str, layer1: list[str], layer2: list[str],
) -> list[str]:
    """Merge two ticker lists, deduplicating. Layer 1 has priority."""
    seen = {target.upper()}
    result = []
    for t in layer1 + layer2:
        t_up = t.upper()
        if t_up not in seen:
            seen.add(t_up)
            result.append(t)
    return result


def _sort_candidates(
    candidates: list[dict],
    target_industry: str,
    target_mcap: float,
) -> list[dict]:
    """Sort: same industry first, then by market cap proximity."""
    def sort_key(c):
        same_ind = 0 if c.get("industry") == target_industry else 1
        mcap = c.get("market_cap") or 0
        mcap_dist = abs(mcap - target_mcap) / max(target_mcap, 1)
        return (same_ind, mcap_dist)

    return sorted(candidates, key=sort_key)


# ── Manual add ─────────────────────────────────────────────────


def _render_manual_add(state: dict, target: str) -> None:
    """Text input to add tickers manually."""
    st.markdown("---")
    c_input, c_btn = st.columns([2, 1])

    with c_input:
        new_tickers = st.text_input(
            "Add tickers manually",
            placeholder="e.g. DELL, HPQ, LOGI",
            key="comps_manual_add",
        )
    with c_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Add", key="comps_add_btn"):
            if new_tickers:
                _add_manual_tickers(state, new_tickers, target)
                st.rerun()


def _add_manual_tickers(
    state: dict, raw_input: str, target: str,
) -> None:
    """Parse comma-separated tickers, fetch info, add to candidates."""
    existing = {c["ticker"] for c in state["candidates"]}
    existing.add(target.upper())

    tickers = [
        t.strip().upper()
        for t in raw_input.replace(";", ",").split(",")
        if t.strip()
    ]

    for t in tickers:
        if t in existing:
            continue
        info = get_comps_candidate_info(t)
        if info:
            state["candidates"].append(info)
            existing.add(t)


# ── Generate section ──────────────────────────────────────────


def _render_generate_section(
    state: dict, live_selected: list[str],
) -> None:
    """Show selection count + Generate Comps Table button."""
    n = len(live_selected)
    st.markdown("---")

    if n > 0:
        names = ", ".join(live_selected)
        st.success(f"**{n} peers selected:** {names}")
    else:
        st.warning("Select at least 3 peers to continue.")

    # Check if selection changed since last generate
    confirmed = state.get("selected", [])
    selection_changed = sorted(live_selected) != sorted(confirmed)

    if confirmed and selection_changed:
        st.info(
            "Peer selection changed — click **Generate Comps Table** "
            "to update."
        )

    if st.button(
        "Generate Comps Table",
        key="comps_generate_btn",
        disabled=n < 3,
        type="primary",
    ):
        # Confirm selection — this triggers Step 2 data fetch
        state["selected"] = list(live_selected)
        # Clear Step 2 cache so it re-fetches
        if "comps_table" in st.session_state:
            st.session_state["comps_table"]["fetched"] = False
        st.rerun()
