"""Step 3: Peer Group Beta — fetch peers, unlever, median, relever.

Shows peer table with add/remove controls.
Returns relevered peer beta for use in Ke calculation.
"""

import statistics

import streamlit as st

from lib.analysis.valuation.wacc import unlever_beta, relever_beta
from lib.data.valuation_data import get_suggested_peers, get_peer_data
from components.layout import format_large_number


# ── Helpers ────────────────────────────────────────────────────────

_LABEL = "font-size:13px;opacity:0.6"
_TH = (
    "font-size:12px;font-weight:600;text-align:right;"
    "padding:4px 8px;border-bottom:1px solid rgba(128,128,128,0.3)"
)
_TD = "font-size:13px;text-align:right;padding:4px 8px"


def _pct(val: float) -> str:
    return f"{val * 100:.1f}%"


# ── Session state management ──────────────────────────────────────


def _get_peer_state(ticker: str) -> dict:
    """Get or initialize peer state in session_state."""
    key = "dcf_wacc_peers"
    existing = st.session_state.get(key)

    # Reset if ticker changed
    if existing and existing.get("_ticker") != ticker:
        existing = None

    if existing is None:
        st.session_state[key] = {
            "_ticker": ticker,
            "peer_tickers": [],
            "peer_data": [],
            "median_unlevered": None,
            "relevered_beta": None,
        }
    return st.session_state[key]


# ── Main render ────────────────────────────────────────────────────


def render_peer_beta(
    ticker: str, total_debt: float, market_cap: float, tax_rate: float,
) -> tuple[float, str]:
    """Render peer beta section. Returns (relevered_beta, info_string)."""

    state = _get_peer_state(ticker)

    # ── Initial load of peers ─────────────────────────────────
    if not state["peer_tickers"]:
        with st.spinner("Fetching suggested peers..."):
            suggested = get_suggested_peers(ticker)
        if suggested:
            state["peer_tickers"] = suggested
            _refresh_peer_data(state)
        else:
            st.info(
                "No suggested peers found. "
                "Add peers manually below."
            )

    # ── Add / Remove controls ─────────────────────────────────
    _render_controls(state)

    # ── Peer table ────────────────────────────────────────────
    if not state["peer_data"]:
        return 1.0, "No peer data available"

    _render_peer_table(state["peer_data"])

    # ── Compute median + relever ──────────────────────────────
    unlevered_betas = [
        p["unlevered_beta"] for p in state["peer_data"]
        if p.get("unlevered_beta") is not None
    ]
    if not unlevered_betas:
        return 1.0, "No valid peer betas"

    median_u = statistics.median(unlevered_betas)
    de = total_debt / market_cap if market_cap and market_cap > 0 else 0
    relevered = relever_beta(median_u, de, tax_rate)

    state["median_unlevered"] = median_u
    state["relevered_beta"] = relevered

    # Summary
    st.markdown(
        f'<div style="font-size:13px;margin-top:8px;'
        f'padding:8px 12px;background:rgba(28,131,225,0.08);'
        f'border-radius:6px">'
        f'<b>Median Unlevered Beta:</b> {median_u:.3f} '
        f'({len(unlevered_betas)} peers) &nbsp;→&nbsp; '
        f'<b>Relevered for {ticker}:</b> '
        f'<span style="color:#1c83e1;font-weight:700">'
        f'{relevered:.3f}</span> '
        f'(D/E={de:.3f}, t={_pct(tax_rate)})</div>',
        unsafe_allow_html=True,
    )

    info = f"Peer median: {median_u:.3f} → relevered: {relevered:.3f}"
    return round(relevered, 4), info


# ── Controls ──────────────────────────────────────────────────────


def _render_controls(state: dict) -> None:
    """Add/remove peer controls."""
    c_add, c_input, c_remove = st.columns([0.5, 1, 1.5])

    with c_input:
        new_peer = st.text_input(
            "Add peer ticker",
            key="wacc_peer_add_input",
            placeholder="e.g. MSFT",
            label_visibility="collapsed",
        )
    with c_add:
        if st.button("Add Peer", key="wacc_peer_add_btn"):
            if new_peer and new_peer.strip().upper() not in state["peer_tickers"]:
                state["peer_tickers"].append(new_peer.strip().upper())
                _refresh_peer_data(state)
                st.rerun()

    with c_remove:
        if state["peer_tickers"]:
            to_remove = st.multiselect(
                "Remove peers",
                state["peer_tickers"],
                key="wacc_peer_remove",
                label_visibility="collapsed",
                placeholder="Select peers to remove...",
            )
            if to_remove and st.button("Remove", key="wacc_peer_rm_btn"):
                state["peer_tickers"] = [
                    t for t in state["peer_tickers"] if t not in to_remove
                ]
                state["peer_data"] = [
                    p for p in state["peer_data"]
                    if p["ticker"] not in to_remove
                ]
                st.rerun()


# ── Data refresh ──────────────────────────────────────────────────


def _refresh_peer_data(state: dict) -> None:
    """Fetch/refresh peer data for current ticker list."""
    tickers = state["peer_tickers"]
    if not tickers:
        state["peer_data"] = []
        return

    raw = get_peer_data(tickers)

    # Compute unlevered beta for each; skip peers with missing tax data
    # (no silent 21% fallback — see fetch_status audit).
    filtered = []
    for p in raw:
        if p.get("tax_rate") is None:
            continue
        p["unlevered_beta"] = unlever_beta(
            p["beta"], p["de_ratio"], p["tax_rate"],
        )
        filtered.append(p)

    state["peer_data"] = filtered


# ── Table rendering ───────────────────────────────────────────────


def _render_peer_table(peers: list[dict]) -> None:
    """Render peer comparison table."""
    # Header
    cols = st.columns([1, 0.8, 0.8, 0.8, 0.8, 0.8])
    headers = ["Peer", "Raw Beta", "D/E", "Tax Rate", "Mkt Cap", "Unlev. Beta"]
    for col, hdr in zip(cols, headers):
        align = "left" if hdr == "Peer" else "right"
        col.markdown(
            f'<div style="{_TH};text-align:{align}">{hdr}</div>',
            unsafe_allow_html=True,
        )

    # Rows
    for p in peers:
        cols = st.columns([1, 0.8, 0.8, 0.8, 0.8, 0.8])
        cols[0].markdown(
            f'<div style="font-size:13px;padding:4px 8px;'
            f'font-weight:500">{p["ticker"]}</div>',
            unsafe_allow_html=True,
        )
        cols[1].markdown(f'<div style="{_TD}">{p["beta"]:.3f}</div>',
                         unsafe_allow_html=True)
        cols[2].markdown(f'<div style="{_TD}">{p["de_ratio"]:.3f}</div>',
                         unsafe_allow_html=True)
        cols[3].markdown(f'<div style="{_TD}">{_pct(p["tax_rate"])}</div>',
                         unsafe_allow_html=True)
        cols[4].markdown(
            f'<div style="{_TD}">'
            f'{format_large_number(p["market_cap"])}</div>',
            unsafe_allow_html=True,
        )
        ub = p.get("unlevered_beta")
        cols[5].markdown(
            f'<div style="{_TD};font-weight:600">'
            f'{ub:.3f}</div>' if ub else '<div style="{_TD}">—</div>',
            unsafe_allow_html=True,
        )
