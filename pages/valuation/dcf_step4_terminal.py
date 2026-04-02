"""Step 4: Terminal Value — perpetuity growth or exit multiple.

Calculates the value of cash flows beyond the projection period.

PLACEHOLDER — will be built after Steps 2-3 are finalized.
"""

import streamlit as st


def render(prepared: dict, ticker: str) -> None:
    """Render terminal value step."""
    st.markdown("### Step 4: Terminal Value")
    st.caption(
        "Value of all cash flows beyond the projection period. "
        "Gordon Growth Model or EV/EBITDA exit multiple."
    )
    st.info(
        "**Coming next:** Terminal growth rate, exit multiple, "
        "Gordon Growth vs Exit Multiple comparison, implied metrics."
    )
