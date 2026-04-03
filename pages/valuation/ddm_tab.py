"""DDM tab — Dividend Discount Model (Gordon Growth + 2-Stage).

Orchestrator: renders Step 1 (Ke), Step 2 (Assumptions), Step 3 (Output).
DDM is independent from DCF — has its own Ke calculation.
"""

import streamlit as st

from pages.valuation import ddm_step1_ke, ddm_step2_assumptions, ddm_step3_output


def render(prepared: dict, ticker: str) -> None:
    """Render DDM tab using prepared financial data."""
    ctype = prepared.get("company_type", {}).get("type", "normal")

    st.subheader("Dividend Discount Model")

    if ctype in ("financial", "dividend_stable"):
        st.success(
            "**DDM is the recommended valuation method** for this company "
            f"({ctype.replace('_', ' ')}). DDM values companies based on "
            "the present value of expected future dividends."
        )
    else:
        st.info(
            "DDM is not the primary method for this company, "
            "but can still be used for dividend-paying stocks."
        )

    # Step 1: Cost of Equity
    ke_result = ddm_step1_ke.render(prepared, ticker)

    st.divider()

    # Step 2: Dividend Assumptions
    assumptions = ddm_step2_assumptions.render(prepared, ticker)

    st.divider()

    # Step 3: Output (only if Steps 1-2 are complete)
    ddm_step3_output.render(prepared, ticker)
