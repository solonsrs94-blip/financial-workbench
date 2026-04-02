"""Step 5: DCF Output — enterprise value, equity bridge, implied price.

Combines FCF projections, WACC, and terminal value into final valuation.
Includes sensitivity analysis, football field, and sanity checks.

PLACEHOLDER — will be built after Steps 2-4 are finalized.
"""

import streamlit as st


def render(prepared: dict, ticker: str) -> None:
    """Render DCF output step."""
    st.markdown("### Step 5: DCF Output")
    st.caption(
        "Enterprise value, equity bridge, implied share price. "
        "Sensitivity tables and sanity checks."
    )
    st.info(
        "**Coming next:** EV calculation, equity bridge (net debt, "
        "minorities, preferred), implied price vs market, "
        "sensitivity matrix (WACC × terminal growth), football field chart."
    )
