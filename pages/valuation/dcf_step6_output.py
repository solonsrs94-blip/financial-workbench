"""Step 6: Valuation Output — discount, bridge, sensitivity, football field.

The final step: discount UFCFs + terminal value, bridge to equity,
calculate implied share price, run sensitivity analysis.

Sub-sections:
- Discount & sum -> Enterprise Value
- Equity Bridge -> Equity Value -> Implied Price per Share
- Sensitivity tables (WACC vs growth, WACC vs exit multiple)
- Scenario analysis (bull/base/bear)
- Reverse DCF (what is market pricing in?)
- Sanity checks
- Football field chart (integrates with Comps/DDM tabs)

PLACEHOLDER — will be built after Step 5 is finalized.
"""

import streamlit as st


def render(ticker: str) -> None:
    st.markdown("### Step 6: Valuation Output")
    st.caption(
        "Discount, bridge to equity, sensitivity analysis, "
        "and final implied share price."
    )

    st.info(
        "**Coming next:**\n"
        "- PV of UFCFs + PV of Terminal Value = Enterprise Value\n"
        "- Equity Bridge: EV + Cash - Debt - Minorities = Equity\n"
        "- Implied share price vs current price\n"
        "- Sensitivity: WACC vs growth, WACC vs exit multiple\n"
        "- Scenario analysis: Bull / Base / Bear\n"
        "- Reverse DCF: What growth is market pricing in?\n"
        "- Sanity checks: TV%, implied multiples, CAGR\n"
        "- Football field chart (combined with Comps & DDM)"
    )
