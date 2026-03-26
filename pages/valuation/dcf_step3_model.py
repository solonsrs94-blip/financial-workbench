"""Step 3: 3-Statement Model — the core of the DCF.

Integrated IS/BS/CF projections with supporting schedules:
- Income Statement: Historical | Projected (side by side)
- Balance Sheet: Historical | Projected
- Cash Flow Statement: Derived from IS + BS changes
- Supporting: Working Capital schedule, D&A/PP&E rollforward, Debt schedule
- Circularity resolution (debt -> interest -> NI -> cash -> debt)
- UFCF calculated from projected IS + BS

PLACEHOLDER — will be built after Steps 1-2 are finalized.
"""

import streamlit as st


def render(ticker: str) -> None:
    st.markdown("### Step 3: 3-Statement Model")
    st.caption(
        "Integrated financial model: historical on the left, "
        "projections on the right. CF is derived from IS + BS changes."
    )

    st.info(
        "**Coming next:** Full 3-statement model with:\n"
        "- Projected Income Statement (Revenue -> EBIT -> NI)\n"
        "- Projected Balance Sheet (WC, PP&E, Debt, Equity)\n"
        "- Cash Flow Statement (derived, not manual)\n"
        "- Working Capital schedule (DSO/DIO/DPO -> dollar amounts)\n"
        "- PP&E rollforward (CapEx, D&A, net PP&E)\n"
        "- Debt schedule (tranches, interest, repayment)\n"
        "- Circular reference resolution\n"
        "- Unlevered Free Cash Flow build-up"
    )
