"""Step 5: Terminal Value — value beyond explicit forecast period.

Two methods calculated and cross-checked:
- Gordon Growth Model (perpetuity)
- Exit Multiple (EV/EBITDA)
- Terminal year normalization
- Cross-checks: implied exit multiple, implied growth, TV% of EV

PLACEHOLDER — will be built after Step 4 is finalized.
"""

import streamlit as st


def render(ticker: str) -> None:
    st.markdown("### Step 5: Terminal Value")
    st.caption(
        "Captures all cash flows beyond the forecast period. "
        "Typically 60-80% of total enterprise value."
    )

    st.info(
        "**Coming next:**\n"
        "- Gordon Growth Model: TV = FCF * (1+g) / (WACC-g)\n"
        "- Exit Multiple: TV = EBITDA * EV/EBITDA\n"
        "- Terminal year normalization (margins, capex)\n"
        "- Cross-checks: implied exit multiple, implied growth\n"
        "- TV as % of EV sanity check"
    )
