"""DCF tab — IB-standard 6-step Discounted Cash Flow model.

Based on Wall Street Prep / BIWS / Training The Street methodology:
  Step 1: Historical Data & Spreading
  Step 2: Assumptions (all hard-coded inputs)
  Step 3: 3-Statement Model (IS/BS/CF projections + schedules)
  Step 4: WACC (discount rate)
  Step 5: Terminal Value
  Step 6: Valuation Output (discount, bridge, sensitivity)
"""

import streamlit as st
from models.company import Company
from typing import Optional

from lib.data.historical import get_raw_statements, get_standardized_history
from lib.analysis.historical import (
    build_income_table, build_balance_table,
    build_cashflow_table, build_ratios_table,
)
from lib.analysis.historical_flags import detect_flags, compute_averages

from pages.valuation import (
    dcf_step1_historical,
    dcf_step2_assumptions,
    dcf_step3_model,
    dcf_step4_wacc,
    dcf_step5_terminal,
    dcf_step6_output,
)


def _load_step1_data(ticker: str, sector: str = ""):
    """Load and cache all Step 1 data: raw statements + standardized."""
    cache_key = f"dcf_step1_{ticker}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]

    with st.spinner("Loading historical financials (EDGAR/Yahoo)..."):
        raw = get_raw_statements(ticker)

    if raw is None:
        return None

    with st.spinner("Standardizing..."):
        std = get_standardized_history(ticker, raw_data=raw)

    if std is None:
        return {"raw": raw}

    years = std["years"]
    is_t = build_income_table(std, years)
    bs_t = build_balance_table(std, years)
    cf_t = build_cashflow_table(std, years)
    ratios = build_ratios_table(is_t, bs_t, cf_t)
    flags = detect_flags(
        ratios, is_table=is_t, bs_table=bs_t, cf_table=cf_t,
        sector=sector, ticker=ticker,
    )
    avgs = compute_averages(ratios)

    result = {
        "raw": raw,
        "std": std,
        "is_table": is_t,
        "bs_table": bs_t,
        "cf_table": cf_t,
        "ratios": ratios,
        "flags": flags,
        "averages": avgs,
    }
    st.session_state[cache_key] = result
    return result


def render(company: Company, fin_data: Optional[dict], ticker: str) -> None:
    # --- Global settings ---
    n_years = st.slider(
        "Forecast Period (years)", 3, 10, 5, key="dcf_n_years",
        help="Explicit projection period. Most companies: 5-7 years.",
    )

    # --- Run button ---
    run = st.button(
        "Run DCF", type="primary", use_container_width=True,
        key="dcf_run_top",
    )
    if run:
        st.info("DCF engine not yet connected -- build Steps 2-6 first.")

    st.divider()

    # --- Load all Step 1 data ---
    sector = getattr(company, "sector", "") or ""
    step1_data = _load_step1_data(ticker, sector=sector)

    # === STEP 1 ===
    dcf_step1_historical.render(ticker=ticker, step1_data=step1_data)
    st.divider()

    # === STEPS 2-6 (placeholders) ===
    dcf_step2_assumptions.render(ticker)
    st.divider()

    dcf_step3_model.render(ticker)
    st.divider()

    dcf_step4_wacc.render(ticker)
    st.divider()

    dcf_step5_terminal.render(ticker)
    st.divider()

    dcf_step6_output.render(ticker)

    # --- Run button (bottom) ---
    st.divider()
    run_bottom = st.button(
        "Run DCF", type="primary", use_container_width=True,
        key="dcf_run_bottom",
    )
    if run_bottom:
        st.info("DCF engine not yet connected -- build Steps 2-6 first.")
