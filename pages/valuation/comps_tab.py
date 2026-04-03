"""Comps tab — Comparable Company Analysis (trading multiples).

Steps:
  1. Peer Selection (candidate generation + analyst picks)
  2. Comps Table (trailing + forward multiples)
  3. Implied Valuation (peer multiples -> implied price + football field)
"""

import streamlit as st

from pages.valuation import (
    comps_step1_peers,
    comps_step2_table,
    comps_step3_valuation,
)


def render(prepared: dict, ticker: str) -> None:
    """Render Comps tab using prepared financial data."""
    company_type = prepared.get("company_type", {})

    # Financial institution warning
    if company_type.get("type") == "financial":
        st.warning(
            "**Comps for financial institutions** require specialized "
            "multiples (P/B, P/TBV, P/PPOP). Standard EV-based "
            "multiples may not be meaningful."
        )

    # === STEP 1: Peer Selection ===
    comps_step1_peers.render(prepared, ticker)

    # === STEP 2: Comps Table ===
    st.divider()
    comps_step2_table.render(prepared, ticker)

    # === STEP 3: Implied Valuation ===
    st.divider()
    comps_step3_valuation.render(prepared, ticker)
