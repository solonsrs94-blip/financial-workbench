"""Step 3A: Cost of Equity (Ke) — CAPM with method selection.

Ke = Rf + Beta x ERP + Size Premium + CRP
All values auto-fetched, all editable.
"""

import streamlit as st

from lib.analysis.valuation.wacc import (
    adjusted_beta,
    relever_beta,
    calc_capm,
    size_premium_bracket,
)
from lib.data.valuation_data import get_erp, get_crp, get_industry_beta
from pages.valuation.dcf_step3_peers import render_peer_beta
from components.fetch_warnings import record_fetch, render_fetch_warnings


# ── Helpers ────────────────────────────────────────────────────────

_LABEL = "font-size:13px;opacity:0.6"


def _pct(val: float) -> str:
    """Format decimal as percent string."""
    return f"{val * 100:.2f}%"


# ── Main render ────────────────────────────────────────────────────


def render_cost_of_equity(inputs: dict) -> dict:
    """Render Cost of Equity section. Returns ke_result dict."""
    st.markdown("#### A. Cost of Equity (Ke)")
    st.caption("CAPM: Ke = Rf + Beta x ERP + Size Premium + CRP")

    render_fetch_warnings(["rf", "erp", "crp", "beta"])

    rf = inputs["rf"]
    raw_beta = inputs["raw_beta"]
    market_cap = inputs["market_cap"]
    total_debt = inputs["total_debt"]
    country = inputs["country"]
    industry = inputs["industry"]
    eff_tax = inputs["effective_tax_rate"]
    ticker = inputs.get("ticker", "")

    # ── Risk-free rate ────────────────────────────────────────
    record_fetch(
        "rf",
        rf is not None,
        source="US 10Y Treasury (^TNX)",
        message="Risk-free rate fetch failed — enter Rf manually",
    )
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        rf_input = st.number_input(
            "Risk-Free Rate (%)",
            min_value=0.0, max_value=15.0,
            value=(rf * 100) if rf is not None else None,
            step=0.05, format="%.2f",
            key="wacc_rf",
            help="10-Year US Treasury yield (auto-fetched, editable)",
        )
        st.markdown(
            f'<div style="{_LABEL}">Source: US 10Y Treasury</div>',
            unsafe_allow_html=True,
        )
    rf_val = rf_input / 100 if rf_input is not None else None

    # ── Beta ──────────────────────────────────────────────────
    with c2:
        beta_options = [
            "Blume-adjusted",
            "Industry (Damodaran)",
            "Peer Group",
        ]
        beta_method = st.selectbox(
            "Beta Method", beta_options, key="wacc_beta_method",
        )

    # Detect method change → reset beta override
    prev_method = st.session_state.get("_wacc_prev_beta_method")
    if prev_method and prev_method != beta_method:
        st.session_state.pop("wacc_beta", None)
    st.session_state["_wacc_prev_beta_method"] = beta_method

    # Calculate beta based on method
    beta_val, beta_info = _compute_beta(
        beta_method, raw_beta, industry, total_debt,
        market_cap, eff_tax, ticker,
    )

    with c3:
        beta_override = st.number_input(
            "Beta (editable)",
            min_value=0.0, max_value=5.0,
            value=beta_val if beta_val is not None else None,
            step=0.05, format="%.3f",
            key="wacc_beta",
        )
        st.markdown(
            f'<div style="{_LABEL}">{beta_info}</div>',
            unsafe_allow_html=True,
        )

    # ── ERP + Size Premium + CRP ──────────────────────────────
    erp_fetched = get_erp()
    record_fetch(
        "erp",
        erp_fetched is not None,
        source="Damodaran",
        message="Damodaran ERP fetch failed — enter ERP manually",
    )
    sp_val, sp_label = size_premium_bracket(market_cap)

    col_erp, col_sp, col_crp = st.columns([1, 1, 1])

    with col_erp:
        erp_input = st.number_input(
            "Equity Risk Premium (%)",
            min_value=0.0, max_value=20.0,
            value=(erp_fetched * 100) if erp_fetched is not None else None,
            step=0.1, format="%.2f",
            key="wacc_erp",
            help="Damodaran implied ERP (auto-fetched monthly)",
        )
        st.markdown(
            f'<div style="{_LABEL}">Damodaran Implied ERP</div>',
            unsafe_allow_html=True,
        )
    erp_val = erp_input / 100 if erp_input is not None else None

    with col_sp:
        sp_input = st.number_input(
            "Size Premium (%)",
            min_value=0.0, max_value=10.0,
            value=sp_val * 100, step=0.25, format="%.2f",
            key="wacc_size_premium",
            help=sp_label,
        )
        st.markdown(
            f'<div style="{_LABEL}">{sp_label}</div>',
            unsafe_allow_html=True,
        )
    sp_final = sp_input / 100

    # CRP: only show for non-US companies
    is_us = country.lower() in ("united states", "us", "usa", "")
    crp_val = 0.0
    if not is_us:
        crp_fetched = get_crp(country)
        record_fetch(
            "crp",
            crp_fetched is not None,
            source="Damodaran",
            message=(
                f"Damodaran CRP fetch failed for {country} — "
                "enter CRP manually"
            ),
        )
        with col_crp:
            crp_input = st.number_input(
                "Country Risk Premium (%)",
                min_value=0.0, max_value=30.0,
                value=(crp_fetched * 100) if crp_fetched is not None else None,
                step=0.1, format="%.2f",
                key="wacc_crp",
                help=f"Damodaran CRP for {country}",
            )
            st.markdown(
                f'<div style="{_LABEL}">CRP: {country}</div>',
                unsafe_allow_html=True,
            )
        crp_val = crp_input / 100 if crp_input is not None else None

    # ── Ke result ─────────────────────────────────────────────
    can_compute = all(
        v is not None for v in (rf_val, beta_override, erp_val, sp_final)
    ) and (is_us or crp_val is not None)
    ke = (
        calc_capm(rf_val, beta_override, erp_val, sp_final, crp_val or 0.0)
        if can_compute else None
    )

    if ke is None:
        st.info(
            "Ke cannot be calculated — one or more required inputs "
            "(Rf, ERP, Beta, CRP) is missing. See warnings above.",
            icon="ℹ️",
        )
    else:
        st.markdown(
            f'<div style="font-size:14px;margin-top:8px">'
            f'<b>Ke = </b>{_pct(rf_val)} + {beta_override:.3f} × '
            f'{_pct(erp_val)} + {_pct(sp_final)}'
            f'{f" + {_pct(crp_val)}" if (crp_val or 0) > 0 else ""}'
            f' = <b style="color:#1c83e1">{_pct(ke)}</b></div>',
            unsafe_allow_html=True,
        )

    method_key = "blume"
    if "Industry" in beta_method:
        method_key = "industry"
    elif "Peer" in beta_method:
        method_key = "peer"

    return {
        "ke": ke, "rf": rf_val, "beta": beta_override,
        "beta_method": method_key, "erp": erp_val,
        "size_premium": sp_final, "crp": crp_val,
    }


# ── Beta computation ──────────────────────────────────────────────


def _compute_beta(
    method: str, raw_beta, industry: str,
    total_debt, market_cap: float, tax_rate,
    ticker: str = "",
) -> tuple:
    """Compute beta and info string based on selected method.

    Returns ``(None, info)`` when the beta cannot be computed from
    real data — caller surfaces a warning, no silent 1.0 fallback.
    """
    if "Industry" in method:
        ind = get_industry_beta(industry)
        if (
            ind and ind.get("unlevered_beta") is not None
            and tax_rate is not None
        ):
            de = total_debt / market_cap if market_cap and market_cap > 0 and total_debt else 0
            relevered = relever_beta(ind["unlevered_beta"], de, tax_rate)
            info = (
                f"{ind['industry']}: "
                f"unlevered={ind['unlevered_beta']:.3f}, "
                f"relevered={relevered:.3f}"
            )
            return round(relevered, 4), info
        return None, "Industry beta not available"

    if "Peer" in method:
        beta_val, info = render_peer_beta(
            ticker, total_debt or 0, market_cap, tax_rate or 0,
        )
        return beta_val, info

    # Default: Blume-adjusted
    if not raw_beta or raw_beta <= 0:
        return None, "Raw beta not available"
    blume = adjusted_beta(raw_beta)
    return round(blume, 4), f"Raw: {raw_beta:.3f} → Blume: {blume:.3f}"
