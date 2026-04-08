"""DDM Step 1: Cost of Equity (Ke) — independent CAPM.

Ke = Rf + Beta × ERP + Size Premium + CRP
Same providers as DCF WACC, but standalone UI (no Kd, no cap structure).
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
from pages.valuation.ddm_step1_peers import render_ddm_peer_beta
from components.fetch_warnings import record_fetch, render_fetch_warnings


_LABEL = "font-size:13px;opacity:0.6"


def _pct(val: float) -> str:
    return f"{val * 100:.2f}%"


def render(prepared: dict, ticker: str) -> dict | None:
    """Render DDM Cost of Equity section. Returns ke_result dict."""
    st.markdown("### Step 1: Cost of Equity (Ke)")
    st.caption("CAPM: Ke = Rf + Beta × ERP + Size Premium + CRP")

    render_fetch_warnings(["rf", "erp", "crp", "beta", "tax_rate"])

    inputs = _extract_inputs(prepared, ticker)
    if inputs is None:
        st.warning("Could not load company data for Ke calculation.")
        return None

    rf = inputs["rf"]
    raw_beta = inputs["raw_beta"]
    market_cap = inputs["market_cap"]
    total_debt = inputs["total_debt"]
    country = inputs["country"]
    industry = inputs["industry"]
    eff_tax = inputs["effective_tax_rate"]

    record_fetch("rf", rf is not None, message="Risk-free rate fetch failed")
    record_fetch("beta", raw_beta is not None, message="Beta fetch failed")
    record_fetch("tax_rate", eff_tax is not None, message="Tax rate not available")

    # ── Risk-free rate ──────────────────────────────────────
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        rf_input = st.number_input(
            "Risk-Free Rate (%)",
            min_value=0.0, max_value=15.0,
            value=(rf * 100) if rf is not None else None,
            step=0.05, format="%.2f",
            key="ddm_rf",
            help="10-Year US Treasury yield (auto-fetched, editable)",
        )
        st.markdown(
            f'<div style="{_LABEL}">Source: US 10Y Treasury</div>',
            unsafe_allow_html=True,
        )
    rf_val = rf_input / 100 if rf_input is not None else None

    # ── Beta ────────────────────────────────────────────────
    with c2:
        beta_options = [
            "Blume-adjusted",
            "Industry (Damodaran)",
            "Peer Group",
        ]
        beta_method = st.selectbox(
            "Beta Method", beta_options, key="ddm_beta_method",
        )

    # Reset beta override on method change
    prev = st.session_state.get("_ddm_prev_beta_method")
    if prev and prev != beta_method:
        st.session_state.pop("ddm_beta", None)
    st.session_state["_ddm_prev_beta_method"] = beta_method

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
            key="ddm_beta",
        )
        st.markdown(
            f'<div style="{_LABEL}">{beta_info}</div>',
            unsafe_allow_html=True,
        )

    # ── ERP + Size Premium + CRP ────────────────────────────
    erp_fetched = get_erp()
    record_fetch("erp", erp_fetched is not None, source="Damodaran",
                 message="Damodaran ERP fetch failed — enter ERP manually")
    sp_val, sp_label = size_premium_bracket(market_cap)

    col_erp, col_sp, col_crp = st.columns([1, 1, 1])

    with col_erp:
        erp_input = st.number_input(
            "Equity Risk Premium (%)",
            min_value=0.0, max_value=20.0,
            value=(erp_fetched * 100) if erp_fetched is not None else None,
            step=0.1, format="%.2f",
            key="ddm_erp",
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
            key="ddm_size_premium",
            help=sp_label,
        )
        st.markdown(
            f'<div style="{_LABEL}">{sp_label}</div>',
            unsafe_allow_html=True,
        )
    sp_final = sp_input / 100

    # CRP: only for non-US
    is_us = country.lower() in ("united states", "us", "usa", "")
    crp_val = 0.0
    if not is_us:
        crp_fetched = get_crp(country)
        record_fetch(
            "crp", crp_fetched is not None, source="Damodaran",
            message=f"Damodaran CRP fetch failed for {country} — enter manually",
        )
        with col_crp:
            crp_input = st.number_input(
                "Country Risk Premium (%)",
                min_value=0.0, max_value=30.0,
                value=(crp_fetched * 100) if crp_fetched is not None else None,
                step=0.1, format="%.2f",
                key="ddm_crp",
                help=f"Damodaran CRP for {country}",
            )
            st.markdown(
                f'<div style="{_LABEL}">CRP: {country}</div>',
                unsafe_allow_html=True,
            )
        crp_val = crp_input / 100 if crp_input is not None else None

    # ── Ke result ───────────────────────────────────────────
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
        st.session_state.pop("ddm_ke", None)
        return None

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

    result = {
        "ke": ke, "rf": rf_val, "beta": beta_override,
        "beta_method": method_key, "erp": erp_val,
        "size_premium": sp_final, "crp": crp_val or 0.0,
    }
    st.session_state["ddm_ke"] = result
    return result


# ── Input extraction ─────────────────────────────────────────


def _extract_inputs(prepared: dict, ticker: str) -> dict | None:
    """Extract Ke inputs from prepared data and session state."""
    company = st.session_state.get(f"company_{ticker}")
    val_data = st.session_state.get(f"val_data_{ticker}") or {}
    rf = st.session_state.get("val_risk_free_rate")  # may be None

    if company is None:
        return None

    price_obj = getattr(company, "price", None)
    info_obj = getattr(company, "info", None)

    raw_beta = (
        getattr(price_obj, "beta", None)
        or val_data.get("beta")
    )
    market_cap = getattr(price_obj, "market_cap", None) or 0

    # Total debt from val_data or standardized
    bs = val_data.get("balance_sheet", {})
    total_debt = bs.get("total_debt")
    if not total_debt:
        years = prepared.get("years", [])
        if years:
            last_bs = prepared.get("standardized", {}).get(
                "balance", {},
            ).get(years[-1], {})
            total_debt = last_bs.get("total_debt")

    country = getattr(info_obj, "country", "") or ""
    industry = getattr(info_obj, "industry", "") or ""

    # Effective tax rate from ratios — None if unavailable (no silent 21%)
    ratios_list = prepared.get("ratios", [])
    eff_tax = None
    if ratios_list:
        last_tax = ratios_list[-1].get("effective_tax_rate")
        if last_tax and 0 < last_tax < 0.5:
            eff_tax = last_tax

    return {
        "rf": rf,
        "raw_beta": raw_beta,
        "market_cap": market_cap,
        "total_debt": total_debt,
        "country": country,
        "industry": industry,
        "effective_tax_rate": eff_tax,
    }


# ── Beta computation ─────────────────────────────────────────


def _compute_beta(
    method: str, raw_beta, industry: str,
    total_debt, market_cap: float, tax_rate,
    ticker: str = "",
) -> tuple:
    """Compute beta and info string based on selected method.

    Returns (None, info) when real data is unavailable — no silent 1.0.
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
        beta_val, info = render_ddm_peer_beta(
            ticker, total_debt or 0, market_cap, tax_rate or 0,
        )
        return beta_val, info

    # Default: Blume-adjusted
    if not raw_beta or raw_beta <= 0:
        return None, "Raw beta not available"
    blume = adjusted_beta(raw_beta)
    return round(blume, 4), f"Raw: {raw_beta:.3f} → Blume: {blume:.3f}"
