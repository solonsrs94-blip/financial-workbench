"""DDM Step 1: Peer Group Beta — fetch peers, unlever, median, relever.

Identical logic to dcf_step3_peers.py but with ddm_ session keys
to keep DDM independent from DCF WACC.
"""

import statistics

import streamlit as st

from lib.analysis.valuation.wacc import unlever_beta, relever_beta
from lib.data.valuation_data import get_suggested_peers, get_peer_data
from components.layout import format_large_number


_LABEL = "font-size:13px;opacity:0.6"
_TH = (
    "font-size:12px;font-weight:600;text-align:right;"
    "padding:4px 8px;border-bottom:1px solid rgba(128,128,128,0.3)"
)
_TD = "font-size:13px;text-align:right;padding:4px 8px"


def _pct(val: float) -> str:
    return f"{val * 100:.1f}%"


def _get_peer_state(ticker: str) -> dict:
    key = "ddm_ke_peers"
    existing = st.session_state.get(key)
    if existing and existing.get("_ticker") != ticker:
        existing = None
    if existing is None:
        st.session_state[key] = {
            "_ticker": ticker,
            "peer_tickers": [],
            "peer_data": [],
        }
    return st.session_state[key]


def render_ddm_peer_beta(
    ticker: str, total_debt: float, market_cap: float, tax_rate: float,
) -> tuple[float, str]:
    """Render peer beta section for DDM. Returns (beta, info)."""
    state = _get_peer_state(ticker)

    if not state["peer_tickers"]:
        with st.spinner("Fetching suggested peers..."):
            suggested = get_suggested_peers(ticker)
        if suggested:
            state["peer_tickers"] = suggested
            _refresh(state)
        else:
            st.info("No suggested peers found. Add peers manually.")

    _render_controls(state)

    if not state["peer_data"]:
        return 1.0, "No peer data available"

    _render_table(state["peer_data"])

    unlevered = [
        p["unlevered_beta"] for p in state["peer_data"]
        if p.get("unlevered_beta") is not None
    ]
    if not unlevered:
        return 1.0, "No valid peer betas"

    median_u = statistics.median(unlevered)
    de = total_debt / market_cap if market_cap and market_cap > 0 else 0
    relevered = relever_beta(median_u, de, tax_rate)

    st.markdown(
        f'<div style="font-size:13px;margin-top:8px;'
        f'padding:8px 12px;background:rgba(28,131,225,0.08);'
        f'border-radius:6px">'
        f'<b>Median Unlevered Beta:</b> {median_u:.3f} '
        f'({len(unlevered)} peers) → '
        f'<b>Relevered:</b> '
        f'<span style="color:#1c83e1;font-weight:700">'
        f'{relevered:.3f}</span> '
        f'(D/E={de:.3f}, t={_pct(tax_rate)})</div>',
        unsafe_allow_html=True,
    )
    return round(relevered, 4), f"Peer median: {median_u:.3f} → {relevered:.3f}"


def _render_controls(state: dict) -> None:
    c_add, c_input, c_remove = st.columns([0.5, 1, 1.5])
    with c_input:
        new_peer = st.text_input(
            "Add peer", key="ddm_peer_add_input",
            placeholder="e.g. MSFT", label_visibility="collapsed",
        )
    with c_add:
        if st.button("Add Peer", key="ddm_peer_add_btn"):
            t = new_peer.strip().upper() if new_peer else ""
            if t and t not in state["peer_tickers"]:
                state["peer_tickers"].append(t)
                _refresh(state)
                st.rerun()
    with c_remove:
        if state["peer_tickers"]:
            to_rm = st.multiselect(
                "Remove", state["peer_tickers"],
                key="ddm_peer_remove", label_visibility="collapsed",
                placeholder="Select peers to remove...",
            )
            if to_rm and st.button("Remove", key="ddm_peer_rm_btn"):
                state["peer_tickers"] = [
                    t for t in state["peer_tickers"] if t not in to_rm
                ]
                state["peer_data"] = [
                    p for p in state["peer_data"] if p["ticker"] not in to_rm
                ]
                st.rerun()


def _refresh(state: dict) -> None:
    if not state["peer_tickers"]:
        state["peer_data"] = []
        return
    raw = get_peer_data(state["peer_tickers"])
    for p in raw:
        p["unlevered_beta"] = unlever_beta(p["beta"], p["de_ratio"], p["tax_rate"])
    state["peer_data"] = raw


def _render_table(peers: list[dict]) -> None:
    cols = st.columns([1, 0.8, 0.8, 0.8, 0.8, 0.8])
    for col, hdr in zip(cols, ["Peer", "Raw β", "D/E", "Tax", "Mkt Cap", "Unlev. β"]):
        align = "left" if hdr == "Peer" else "right"
        col.markdown(
            f'<div style="{_TH};text-align:{align}">{hdr}</div>',
            unsafe_allow_html=True,
        )
    for p in peers:
        cols = st.columns([1, 0.8, 0.8, 0.8, 0.8, 0.8])
        cols[0].markdown(
            f'<div style="font-size:13px;padding:4px 8px;font-weight:500">'
            f'{p["ticker"]}</div>', unsafe_allow_html=True,
        )
        cols[1].markdown(f'<div style="{_TD}">{p["beta"]:.3f}</div>',
                         unsafe_allow_html=True)
        cols[2].markdown(f'<div style="{_TD}">{p["de_ratio"]:.3f}</div>',
                         unsafe_allow_html=True)
        cols[3].markdown(f'<div style="{_TD}">{_pct(p["tax_rate"])}</div>',
                         unsafe_allow_html=True)
        cols[4].markdown(
            f'<div style="{_TD}">{format_large_number(p["market_cap"])}</div>',
            unsafe_allow_html=True,
        )
        ub = p.get("unlevered_beta")
        cols[5].markdown(
            f'<div style="{_TD};font-weight:600">{ub:.3f}</div>'
            if ub else f'<div style="{_TD}">—</div>',
            unsafe_allow_html=True,
        )
