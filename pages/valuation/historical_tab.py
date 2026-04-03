"""Historical Multiples tab — orchestrator.

Compares a company to itself over time using trailing multiples.
Controls at top (period, multiple selection), content below.

Fetches ALL data once per ticker (EDGAR ~40s, yfinance ~5s), then
period switching is instant (module-level caches in provider).
"""

import streamlit as st

from lib.data.valuation_data import get_historical_multiples
from pages.valuation.historical_chart import render_historical_charts
from pages.valuation.historical_summary import render_historical_summary
from pages.valuation.historical_football import render_historical_football


# ── Financial detection (reuse Comps logic) ───────────────────

_FIN_SECTORS = {"Financial Services", "Financials"}
_FIN_KEYWORDS = ("bank", "insurance", "capital market")


def _is_financial(prepared: dict, ticker: str) -> bool:
    """Detect financial company using 3-tier fallback."""
    ctype = prepared.get("company_type", {})
    if ctype.get("type") == "financial":
        return True
    industry = prepared.get("industry", "").lower()
    if any(k in industry for k in _FIN_KEYWORDS):
        return True
    from lib.data.valuation_data import get_comps_candidate_info
    info = get_comps_candidate_info(ticker)
    if info and info.get("sector") in _FIN_SECTORS:
        return True
    return False


# ── Multiple labels ───────────────────────────────────────────

MULT_LABELS = {
    "pe": "P/E",
    "ev_ebitda": "EV/EBITDA",
    "ev_revenue": "EV/Revenue",
    "p_book": "P/Book",
    "p_tbv": "P/TBV",
}

MULT_KEYS_NORMAL = ["pe", "ev_ebitda", "ev_revenue"]
MULT_KEYS_FINANCIAL = ["pe", "p_book", "p_tbv"]


# ── Main render ───────────────────────────────────────────────


def render(prepared: dict, ticker: str) -> None:
    """Render Historical Multiples tab."""
    st.subheader("Historical Multiples")
    st.caption(
        "How does the stock compare to its own trading history? "
        "Daily trailing 12-month multiples over time."
    )

    is_fin = _is_financial(prepared, ticker)
    mult_keys = MULT_KEYS_FINANCIAL if is_fin else MULT_KEYS_NORMAL

    # ── Fetch max data once (cached by provider module) ───────
    cache_key = f"hist_mult_{ticker}_{is_fin}"
    if cache_key not in st.session_state:
        with st.spinner("Calculating historical multiples..."):
            st.session_state[cache_key] = get_historical_multiples(
                ticker, period_years=0, is_financial=is_fin,
            )

    full_data = st.session_state[cache_key]

    if full_data.get("error"):
        st.error(f"Could not calculate multiples: {full_data['error']}")
        return

    # ── Determine available periods ───────────────────────────
    from datetime import datetime
    d_start = datetime.strptime(full_data["data_start"], "%Y-%m-%d")
    d_end = datetime.strptime(full_data["data_end"], "%Y-%m-%d")
    years_avail = (d_end - d_start).days / 365

    period_options = [1, 3]
    if years_avail >= 4.5:
        period_options.append(5)
    if years_avail >= 9:
        period_options.append(10)

    # Default: largest available
    default_idx = len(period_options) - 1

    # ── Controls ──────────────────────────────────────────────
    col1, col2 = st.columns([1, 3])

    with col1:
        period = st.radio(
            "Period", period_options, index=default_idx,
            format_func=lambda x: f"{x}Y",
            horizontal=True, key="hist_mult_period",
        )

    with col2:
        selected = st.multiselect(
            "Multiples",
            options=mult_keys,
            default=mult_keys,
            format_func=lambda k: MULT_LABELS.get(k, k),
            key=f"hist_mult_sel_{is_fin}",
        )

    if not selected:
        st.warning("Select at least one multiple.")
        return

    # ── Apply period filter (instant — no re-fetch) ───────────
    period_key = f"hist_mult_{ticker}_{period}_{is_fin}"
    if period_key not in st.session_state:
        st.session_state[period_key] = get_historical_multiples(
            ticker, period_years=period, is_financial=is_fin,
        )

    data = st.session_state[period_key]

    if data.get("error"):
        st.error(f"Could not calculate multiples: {data['error']}")
        return

    # ── Metadata ──────────────────────────────────────────────
    source = data.get("data_source", "")
    n_q = data.get("quarters_available", 0)
    st.caption(
        f"Data: {data['data_start']} to {data['data_end']} · "
        f"{n_q} quarters · {source} · "
        f"Currency: {data['currency']}"
    )

    # ── Section 1: Charts ─────────────────────────────────────
    render_historical_charts(
        data["daily_multiples"], data["summary"], selected,
    )

    # ── Section 2: Summary + Implied Value ────────────────────
    st.divider()
    render_historical_summary(
        data["summary"], data["implied_values"],
        data["current_price"], data["currency"],
    )

    # ── Section 3: Football Field ─────────────────────────────
    st.divider()
    render_historical_football(
        data["summary"], data["implied_values"],
        data["current_price"], data["currency"],
    )
