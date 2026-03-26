"""Step 1c sub-component: Review & Override adjustments."""

import streamlit as st
from typing import Optional

from pages.valuation.dcf_step1_flags import _get_applied


def render_overrides(ticker: str, step1_data: Optional[dict]) -> None:
    """Show applied flag adjustments + manual override inputs."""
    years = []
    if step1_data and step1_data.get("std"):
        years = step1_data["std"].get("years", [])

    # Show applied flags first
    applied = _get_applied(ticker)
    if applied:
        st.markdown(f"**{len(applied)} applied from flags:**")
        for i, adj in enumerate(applied):
            impact = adj.get("impact_mn", 0)
            imp_s = (
                f"${impact/1000:.1f}B" if abs(impact) >= 1000
                else f"${impact:.0f}M"
            )
            c1, c2, c3, c4 = st.columns([1, 1.5, 2, 0.5])
            with c1:
                st.text(adj.get("year", ""))
            with c2:
                st.text(adj.get("line_item", ""))
            with c3:
                st.text(adj.get("reason", "")[:50])
            with c4:
                st.text(imp_s)
        st.divider()

    # Manual additions
    st.caption("Add manual adjustments:")
    n_adj = st.number_input(
        "Additional adjustments", 0, 10, 0,
        key=f"dcf_n_adj_{ticker}",
    )
    for i in range(int(n_adj)):
        c1, c2, c3, c4 = st.columns([1, 1.5, 1.5, 1])
        with c1:
            st.selectbox("Year", years, key=f"dcf_adj_yr_{ticker}_{i}")
        with c2:
            st.selectbox(
                "Line item",
                ["EBIT", "Revenue", "COGS", "SGA", "R&D",
                 "Tax", "Net Income", "Other"],
                key=f"dcf_adj_item_{ticker}_{i}",
            )
        with c3:
            st.text_input(
                "Reason", placeholder="e.g. Restructuring charge",
                key=f"dcf_adj_desc_{ticker}_{i}",
            )
        with c4:
            st.number_input(
                "Impact ($M)", value=0.0, step=10.0,
                key=f"dcf_adj_amt_{ticker}_{i}",
            )

    if not applied and int(n_adj) == 0:
        st.caption(
            "No adjustments yet. Use 'Apply' on flags above, "
            "or add manually."
        )
