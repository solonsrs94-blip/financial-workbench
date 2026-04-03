"""Comps Step 1 — table rendering for candidates and target anchor.

Uses st.data_editor for candidate selection (native checkbox alignment).
The data_editor widget key is the single source of truth for selections.
Split from comps_step1_peers.py for file size compliance.
"""

import pandas as pd
import streamlit as st

from components.layout import format_large_number, format_percentage


# ── Target anchor ──────────────────────────────────────────────


def render_target_anchor(info: dict) -> None:
    """Show target company as highlighted row above the candidate table."""
    mcap = info.get("market_cap")
    rev = info.get("revenue")
    margin = info.get("ebitda_margin")

    df = pd.DataFrame([{
        "Ticker": info.get("ticker", ""),
        "Company": info.get("name", ""),
        "Country": info.get("country", ""),
        "Industry": info.get("industry", ""),
        "Mkt Cap": format_large_number(mcap),
        "Revenue": format_large_number(rev) if rev else "N/A",
        "EBITDA Mgn": format_percentage(margin) if margin else "N/A",
    }])

    st.markdown(
        '<p style="font-size:12px;font-weight:600;color:#1c83e1;'
        'margin-bottom:2px">TARGET</p>',
        unsafe_allow_html=True,
    )
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )


# ── Candidate table ────────────────────────────────────────────

_EDITOR_KEY = "comps_peer_editor"


def render_candidate_table(candidates: list[dict]) -> list[str]:
    """Render candidate table with checkboxes via data_editor.

    Returns list of currently selected ticker symbols.
    The data_editor widget state is the single source of truth —
    we never overwrite it from external state.
    """
    # Build display DataFrame (Select column = False for all initially)
    rows = []
    for c in candidates:
        mcap = c.get("market_cap")
        rev = c.get("revenue")
        margin = c.get("ebitda_margin")
        rows.append({
            "Select": False,
            "Ticker": c["ticker"],
            "Company": c.get("name", ""),
            "Country": c.get("country", ""),
            "Industry": c.get("industry", ""),
            "Mkt Cap": format_large_number(mcap),
            "Revenue": format_large_number(rev) if rev else "N/A",
            "EBITDA Mgn": format_percentage(margin) if margin else "N/A",
        })

    df = pd.DataFrame(rows)

    edited = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        disabled=["Ticker", "Company", "Country", "Industry",
                   "Mkt Cap", "Revenue", "EBITDA Mgn"],
        column_config={
            "Select": st.column_config.CheckboxColumn(
                "Select", default=False, width="small",
            ),
            "Ticker": st.column_config.TextColumn("Ticker", width="small"),
            "Company": st.column_config.TextColumn(
                "Company", width="medium",
            ),
            "Country": st.column_config.TextColumn(
                "Country", width="small",
            ),
            "Industry": st.column_config.TextColumn(
                "Industry", width="medium",
            ),
            "Mkt Cap": st.column_config.TextColumn(
                "Mkt Cap", width="small",
            ),
            "Revenue": st.column_config.TextColumn(
                "Revenue", width="small",
            ),
            "EBITDA Mgn": st.column_config.TextColumn(
                "EBITDA Mgn", width="small",
            ),
        },
        key=_EDITOR_KEY,
    )

    # Read selections from the edited dataframe (widget is source of truth)
    selected = []
    for _, row in edited.iterrows():
        if row["Select"]:
            selected.append(row["Ticker"])
    return selected
