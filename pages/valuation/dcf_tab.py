"""DCF tab — IB-standard 5-step Discounted Cash Flow model.

Receives prepared_data from Financial Preparation.
Step 1 is now in preparation.py — this tab starts at Step 2.

Steps:
  2. Assumptions & Projected Financials (analyst inputs)
  3. WACC (discount rate)
  4. Terminal Value (perpetuity growth or exit multiple)
  5. DCF Output (EV, equity bridge, implied price, sensitivity)
"""

import streamlit as st

from pages.valuation import (
    dcf_step2_assumptions,
    dcf_step3_wacc,
    dcf_step4_terminal,
    dcf_step5_output,
)


def render(prepared: dict, ticker: str) -> None:
    """Render DCF tab using prepared financial data."""
    company_type = prepared.get("company_type", {})

    # Financial institution warning
    if company_type.get("type") == "financial":
        st.warning(
            "**DCF is not recommended for financial institutions.** "
            "Banks and insurance companies earn revenue from "
            "interest/premiums — standard FCF projections don't apply. "
            "Consider the DDM tab instead."
        )

    # === STEPS 2-5 (Step 1 is now in Financial Preparation) ===
    dcf_step2_assumptions.render(prepared, ticker)
    st.divider()

    dcf_step3_wacc.render(prepared, ticker)
    st.divider()

    dcf_step4_terminal.render(prepared, ticker)
    st.divider()

    dcf_step5_output.render(prepared, ticker)
