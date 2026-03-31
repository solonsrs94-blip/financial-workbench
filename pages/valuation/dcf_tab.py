"""DCF tab — IB-standard 6-step Discounted Cash Flow model.

Receives prepared_data from Financial Preparation.
Step 1 is now in preparation.py — this tab starts at Step 2.
"""

import streamlit as st

from pages.valuation import (
    dcf_step2_assumptions,
    dcf_step3_model,
    dcf_step4_wacc,
    dcf_step5_terminal,
    dcf_step6_output,
)


def render(prepared: dict, ticker: str) -> None:
    """Render DCF tab using prepared financial data."""
    company_type = prepared.get("company_type", {})

    # Financial institution warning
    if company_type.get("type") == "financial":
        st.warning(
            "**DCF is not recommended for financial institutions.** "
            "Banks and insurance companies earn revenue from interest/premiums — "
            "standard FCF projections don't apply. Consider the DDM tab instead."
        )

    # --- Global settings ---
    n_years = st.slider(
        "Forecast Period (years)", 3, 10, 5, key="dcf_n_years",
        help="Explicit projection period. Most companies: 5-7 years.",
    )

    run = st.button(
        "Run DCF", type="primary", use_container_width=True,
        key="dcf_run_top",
    )
    if run:
        st.info("DCF engine not yet connected -- build Steps 2-6 first.")

    st.divider()

    # === STEPS 2-6 (placeholders — Step 1 is now in Financial Preparation) ===
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
