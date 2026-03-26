"""Step 2: Assumptions — all hard-coded inputs in one place.

Revenue growth, margin targets, WC days, CapEx%, tax rate, SBC, etc.
Blue-coded inputs that the analyst controls.
These assumptions drive the 3-statement model projections.

PLACEHOLDER — will be built after Step 1 is finalized.
"""

import streamlit as st


def render(ticker: str) -> None:
    st.markdown("### Step 2: Assumptions")
    st.caption(
        "All projection assumptions in one place. These drive the "
        "3-statement model. Blue = your input, Black = calculated."
    )
    st.info(
        "**Coming next:** Revenue growth (per year), margin targets, "
        "working capital days (DSO/DIO/DPO), CapEx/Revenue %, D&A policy, "
        "tax rate, SBC %, dilution, dividend policy, debt schedule."
    )
