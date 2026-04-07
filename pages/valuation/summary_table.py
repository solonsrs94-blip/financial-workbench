"""Summary — Valuation Overview Table.

Shows implied price, upside/downside, and key assumptions
for each completed valuation method.
"""

import streamlit as st
import pandas as pd


def render_valuation_table(
    rows: list[dict], current_price: float,
) -> None:
    """Render valuation overview table."""
    st.markdown("#### Valuation Overview")

    records = []
    for r in rows:
        implied = r["implied"]
        upside = (
            (implied / current_price - 1) * 100
            if current_price > 0 else 0
        )
        records.append({
            "Method": r["method"],
            "Implied Price": f"${implied:,.2f}",
            "Upside / Downside": f"{upside:+.1f}%",
            "Key Assumptions": r.get("notes", ""),
        })

    df = pd.DataFrame(records)

    # Color code upside/downside column
    def _style_upside(val):
        try:
            pct = float(val.replace("%", "").replace("+", ""))
        except (ValueError, TypeError, AttributeError):
            return ""
        if pct > 0:
            return "color: #2ea043; font-weight: 600"
        return "color: #f85149; font-weight: 600"

    styled = df.style.map(
        _style_upside, subset=["Upside / Downside"],
    ).set_properties(
        **{"font-size": "13px"},
    ).hide(axis="index")

    st.dataframe(
        styled,
        use_container_width=True,
        height=min(400, 50 + len(records) * 40),
    )
