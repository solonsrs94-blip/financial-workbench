"""DDM Step 2 sub-renderer — reference data, warnings, dividend history.

Split from ddm_step2_assumptions.py for file size compliance.
"""

import streamlit as st
import pandas as pd

from components.layout import format_percentage


def render_warnings(ddm_data: dict) -> None:
    """Show dividend warnings."""
    if not ddm_data["has_dividend"]:
        st.warning(
            "**This company does not pay dividends.** "
            "DDM is not applicable. You may still model "
            "a hypothetical dividend scenario below."
        )
        return

    if ddm_data["years_paying"] < 5:
        st.warning(
            f"Limited dividend history ({ddm_data['years_paying']} years). "
            f"Results may be unreliable."
        )

    payout = ddm_data["payout_ratio"]
    if payout and payout > 1.0:
        st.warning(
            f"Payout ratio exceeds 100% ({payout:.0%}). "
            f"Current dividend may not be sustainable."
        )

    cuts = ddm_data["dividend_cuts"]
    if cuts:
        from datetime import datetime
        cutoff = datetime.now().year - 10
        recent = [y for y in cuts if y >= cutoff]
        if recent:
            st.warning(
                f"Dividend was cut in {', '.join(str(y) for y in recent)}. "
                f"Growth assumptions should reflect this risk."
            )


def render_reference(ddm_data: dict) -> None:
    """Show reference data (current dividend info + history)."""
    d0 = ddm_data["current_dps"]
    dy = ddm_data["dividend_yield"]
    eps = ddm_data["trailing_eps"]
    payout = ddm_data["payout_ratio"]
    cagr = ddm_data["dps_cagr"]

    # Current metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current DPS", f"${d0:.2f}")
    c2.metric("Dividend Yield", format_percentage(dy))
    c3.metric("Trailing EPS", f"${eps:.2f}" if eps else "N/A")
    c4.metric("Payout Ratio", format_percentage(payout) if payout else "N/A")

    # Historical DPS CAGR + streaks
    cols2 = st.columns(6)
    for i, (label, key) in enumerate([
        ("1Y CAGR", "1y"), ("3Y CAGR", "3y"),
        ("5Y CAGR", "5y"), ("10Y CAGR", "10y"),
    ]):
        val = cagr.get(key)
        cols2[i].metric(
            label, format_percentage(val) if val is not None else "N/A",
        )

    cols2[4].metric("Yrs Paying", ddm_data["years_paying"])
    cols2[5].metric("Yrs Increasing", ddm_data["years_increasing"])

    # DPS history expander
    history = ddm_data["dividend_history"]
    if history:
        with st.expander("Dividend History (Annual DPS)", expanded=False):
            df = pd.DataFrame(history)
            df["dps"] = df["dps"].apply(lambda x: f"${x:.2f}")
            st.dataframe(df, use_container_width=True, hide_index=True)
