"""Step 4: WACC — Weighted Average Cost of Capital.

Full discount rate calculation with multiple methods per component:
- Risk-Free Rate (maturity selection, regional)
- Equity Risk Premium (Damodaran/historical/manual)
- Beta (6 methods including Vasicek, bottom-up)
- Cost of Equity (CAPM + size premium + CRP)
- Cost of Debt (3 methods: interest/debt, synthetic, FRED spread)
- Capital Structure (market/book/target/industry)
- Final WACC + RRE cross-check

PLACEHOLDER — will be built after Step 3 is finalized.
"""

import streamlit as st


def render(ticker: str) -> None:
    st.markdown("### Step 4: WACC")
    st.caption(
        "Weighted Average Cost of Capital — the discount rate for your DCF. "
        "Each component offers multiple methods."
    )

    st.info(
        "**Coming next:** Full WACC calculation:\n"
        "- Rf: Auto-fetched, maturity selection, regional\n"
        "- Beta: Vasicek, Adjusted, Raw regression, Industry, Bottom-up, Manual\n"
        "- ERP: Damodaran implied, Historical, Manual + CRP\n"
        "- Cost of Equity: CAPM + Size premium + Alpha\n"
        "- Cost of Debt: Interest/Debt, FRED spread, Synthetic rating, Manual\n"
        "- Capital Structure: Market, Book, Target, Industry + MV of Debt\n"
        "- Debt schedule integration\n"
        "- WACC result + RRE (Modigliani-Miller) cross-check"
    )
