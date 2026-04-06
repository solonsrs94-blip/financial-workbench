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
from pages.valuation.historical_scenarios import render_scenario_valuation


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

_EPS_OPTIONS = [
    "Trailing EPS (TTM)",
    "Forward EPS (Consensus)",
    "Normalized EPS (Manual)",
]


def _render_eps_selector(ticker: str, data: dict, selected: list) -> dict:
    """Render EPS basis selector. Returns dict with eps_basis, override, scale."""
    if "pe" not in selected:
        return {"eps_basis": "trailing", "override": False, "scale": 1.0}

    company = st.session_state.get(f"company_{ticker}")
    ratios = getattr(company, "ratios", None) if company else None
    trailing = getattr(ratios, "eps_trailing", None) or 0.0
    forward = getattr(ratios, "eps_forward", None) or 0.0

    with st.expander("EPS Basis (for P/E implied values)", expanded=False):
        ref_parts = []
        if trailing:
            ref_parts.append(f"Trailing: ${trailing:.2f}")
        if forward:
            ref_parts.append(f"Forward: ${forward:.2f}")
        if ref_parts:
            st.caption(" | ".join(ref_parts))

        basis = st.selectbox(
            "EPS Basis", _EPS_OPTIONS, index=0, key="hist_eps_basis",
        )

        if basis == _EPS_OPTIONS[1] and forward and forward > 0:
            eps_used = forward
        elif basis == _EPS_OPTIONS[2]:
            eps_used = st.number_input(
                "Normalized EPS",
                min_value=0.01, max_value=9999.0,
                value=None, step=0.10, format="%.2f",
                key="hist_eps_manual",
                placeholder="Enter analyst estimate",
            )
        else:
            eps_used = None

    if eps_used and trailing and trailing > 0:
        return {
            "eps_basis": basis, "override": True,
            "scale": eps_used / trailing, "eps_used": eps_used,
        }
    return {"eps_basis": "trailing", "override": False, "scale": 1.0}


def _scale_pe_implied(implied_values: dict, scale: float) -> dict:
    """Scale P/E implied prices by EPS ratio (override / trailing)."""
    result = dict(implied_values)
    pe_iv = implied_values.get("pe")
    if not pe_iv or not isinstance(pe_iv, dict):
        return result
    scaled = {}
    for key, val in pe_iv.items():
        if isinstance(val, (int, float)) and val > 0:
            scaled[key] = val * scale
        else:
            scaled[key] = val
    result["pe"] = scaled
    return result


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

    # ── EPS Basis (for P/E implied values) ────────────────────
    implied_values = data["implied_values"]
    eps_info = _render_eps_selector(ticker, data, selected)
    if eps_info.get("override") and "pe" in implied_values:
        implied_values = _scale_pe_implied(
            implied_values, eps_info["scale"],
        )

    # ── Section 1: Charts ─────────────────────────────────────
    render_historical_charts(
        data["daily_multiples"], data["summary"], selected,
    )

    # ── Section 2: Summary + Implied Value ────────────────────
    st.divider()
    render_historical_summary(
        data["summary"], implied_values,
        data["current_price"], data["currency"],
    )

    # ── Section 3: Football Field ─────────────────────────────
    st.divider()
    render_historical_football(
        data["summary"], implied_values,
        data["current_price"], data["currency"],
    )

    # ── Section 4: Scenario Valuation ───────────────────────────
    st.divider()
    st.markdown("#### Scenario Valuation")
    st.caption(
        "Select a primary multiple and set bear/base/bull values "
        "based on historical statistics."
    )
    render_scenario_valuation(
        data["summary"], implied_values,
        data["current_price"], data["currency"],
        eps_info=eps_info,
    )
