"""Step 3: WACC — Weighted Average Cost of Capital.

Calculates discount rate using CAPM for cost of equity
and market yields for cost of debt.

PLACEHOLDER — will be built after Step 2 is finalized.
"""

import streamlit as st


def render(prepared: dict, ticker: str) -> None:
    """Render WACC step."""
    st.markdown("### Step 3: WACC")
    st.caption(
        "Weighted Average Cost of Capital — discount rate for DCF. "
        "Uses CAPM for cost of equity, market data for cost of debt."
    )
    st.info(
        "**Coming next:** Risk-free rate, equity risk premium, beta, "
        "cost of debt, capital structure weights, WACC calculation."
    )
