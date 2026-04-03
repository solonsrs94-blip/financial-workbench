"""Step 5 sub-renderer — Sensitivity Analysis tables.

Two tables:
  1. WACC vs Terminal Growth Rate → implied price
  2. WACC vs Exit Multiple → implied price

Color coded: green = upside, red = downside vs current price.
Base case cell highlighted.
"""

import streamlit as st
import pandas as pd

from lib.analysis.valuation.sensitivity import (
    sensitivity_table,
    exit_sensitivity_table,
)
from models.valuation import WACCResult


def render_sensitivity(
    fcf_table: pd.DataFrame,
    wacc_result: WACCResult,
    terminal: dict,
    bridge_inputs: dict,
    current_price: float,
) -> None:
    """Render two sensitivity tables side by side."""
    st.markdown("#### Sensitivity Analysis")
    st.caption(
        "How implied share price changes with different assumptions. "
        "Green = upside vs current price, red = downside."
    )

    net_debt = bridge_inputs["net_debt"]
    shares = bridge_inputs["shares"]
    minority = bridge_inputs["minority"]
    preferred = bridge_inputs["preferred"]
    g = terminal["terminal_growth"]
    mult = terminal["exit_multiple"]

    tab1, tab2 = st.tabs([
        "WACC vs Terminal Growth",
        "WACC vs Exit Multiple",
    ])

    with tab1:
        df_g = sensitivity_table(
            fcf_table, wacc_result, g, terminal["method"], mult,
            net_debt, shares, current_price, minority, preferred,
        )
        _render_table(df_g, current_price, "Terminal Growth Rate")

    with tab2:
        df_m = exit_sensitivity_table(
            fcf_table, wacc_result, g, mult,
            net_debt, shares, current_price, minority, preferred,
        )
        _render_table(df_m, current_price, "Exit Multiple (EV/EBITDA)")


def _render_table(
    df: pd.DataFrame, current_price: float, col_label: str,
) -> None:
    """Render a sensitivity DataFrame with color coding."""
    # Format as price strings
    formatted = df.map(lambda x: f"${x:,.2f}" if x else "—")

    # Build color styling
    def _style(val):
        try:
            price = float(str(val).replace("$", "").replace(",", ""))
        except (ValueError, TypeError):
            return ""
        if price > current_price:
            return "background-color: rgba(46, 160, 67, 0.25); color: #2ea043"
        return "background-color: rgba(248, 81, 73, 0.2); color: #f85149"

    # Find base case (middle row, middle col) and highlight
    mid_r = len(df) // 2
    mid_c = len(df.columns) // 2

    def _highlight_base(row_idx, col_idx):
        if row_idx == mid_r and col_idx == mid_c:
            return "border: 2px solid #1c83e1; font-weight: 700"
        return ""

    # Apply styling
    styled = formatted.style.applymap(_style)

    # Highlight base case cell
    styles = []
    for r in range(len(formatted)):
        for c in range(len(formatted.columns)):
            extra = _highlight_base(r, c)
            if extra:
                styles.append({
                    "selector": f"td:nth-child({c + 2})",
                    "props": extra,
                })

    # Column header
    st.markdown(
        f'<div style="font-size:12px;opacity:0.5;margin-bottom:4px">'
        f'Rows: WACC &nbsp;|&nbsp; Columns: {col_label}'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.dataframe(
        styled,
        use_container_width=True,
        height=min(250, 50 + len(df) * 40),
    )

    # Base case marker
    base_price = df.iloc[mid_r, mid_c]
    upside = (base_price / current_price - 1) * 100 if current_price > 0 else 0
    color = "#2ea043" if upside > 0 else "#f85149"
    st.markdown(
        f'<div style="font-size:12px;opacity:0.6">'
        f'Base case (highlighted): ${base_price:,.2f} '
        f'(<span style="color:{color}">{upside:+.1f}%</span> '
        f'vs ${current_price:,.2f})</div>',
        unsafe_allow_html=True,
    )
