"""Reusable financial statement table — renders Yahoo DataFrames.

Used by both Company Overview (financials_tab) and DCF Step 1.
Shows as-reported line items with "Show all" toggle.
"""

import streamlit as st
import pandas as pd
from typing import Optional
from components.layout import format_large_number
from pages.company.financials_helpers import get_key_rows


def render_statement(
    fin_data: dict,
    type_key: str = "dcf_fin_type",
    view_key: str = "dcf_fin_view",
    show_all_key: str = "dcf_show_all",
) -> None:
    """Render IS/BS/CF statement with type/view controls."""
    col_type, col_view = st.columns([3, 1])
    with col_type:
        fin_type = st.segmented_control(
            "Statement", ["Income", "Balance Sheet", "Cash Flow"],
            default="Income", key=type_key, label_visibility="collapsed",
        )
    with col_view:
        view = st.segmented_control(
            "View", ["Annual", "TTM"],
            default="Annual", key=view_key, label_visibility="collapsed",
        )

    df = _get_statement_df(fin_data, fin_type, view)
    if df is not None and not df.empty:
        df = _drop_sparse(df)
        df = _format_cols(df)

        key_rows = get_key_rows(fin_type, df.index.tolist())
        show_all = st.toggle("Show all line items", value=False, key=show_all_key)

        if not show_all and key_rows:
            display_df = df.loc[[r for r in key_rows if r in df.index]]
        else:
            display_df = df

        display_df = display_df.map(
            lambda x: format_large_number(x, prefix="")
            if isinstance(x, (int, float)) and pd.notna(x) else ""
        )
        styled = display_df.style.map(
            lambda v: "color: #d62728"
            if isinstance(v, str) and v.startswith("-") else ""
        )
        st.dataframe(
            styled, use_container_width=True,
            height=min(len(display_df) * 38 + 50, 600),
        )
    else:
        st.info(f"No {fin_type.lower()} data available.")


def _get_statement_df(
    fin_data: dict, fin_type: str, view: str,
) -> Optional[pd.DataFrame]:
    annual = {
        "Income": "income_statement",
        "Balance Sheet": "balance_sheet",
        "Cash Flow": "cash_flow",
    }
    quarterly = {
        "Income": "quarterly_income",
        "Balance Sheet": "quarterly_balance",
        "Cash Flow": "quarterly_cashflow",
    }
    if view == "TTM" and fin_type != "Balance Sheet":
        qdf = fin_data.get(quarterly[fin_type])
        if qdf is not None and not qdf.empty and qdf.shape[1] >= 4:
            ttm = qdf.iloc[:, :4].sum(axis=1).to_frame("TTM")
            df = pd.concat([ttm, qdf.iloc[:, :4]], axis=1)
            df.columns = ["TTM"] + [
                c.strftime("%b %Y") if hasattr(c, "strftime") else str(c)
                for c in qdf.columns[:4]
            ]
            return df
    if view == "TTM" and fin_type == "Balance Sheet":
        qdf = fin_data.get(quarterly[fin_type])
        if qdf is not None and not qdf.empty:
            return qdf.iloc[:, :4]
    return fin_data.get(annual[fin_type])


def _format_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cols = []
    for c in df.columns:
        if hasattr(c, "strftime"):
            cols.append(c.strftime("%Y"))
        else:
            s = str(c)
            if " 00:00:00" in s:
                s = s.split(" ")[0]
            if len(s) == 10 and s[4] == "-":
                s = s[:4]
            cols.append(s)
    if len(cols) != len(set(cols)):
        cols = [
            c.strftime("%b %Y") if hasattr(c, "strftime")
            else str(c).split(" ")[0]
            for c in df.columns
        ]
    df.columns = cols
    df.index = [
        str(i).replace("_", " ").title() if isinstance(i, str) else str(i)
        for i in df.index
    ]
    return df


def _drop_sparse(df: pd.DataFrame) -> pd.DataFrame:
    drops = []
    for i in range(len(df.columns)):
        try:
            s = df.iloc[:, i]
            non_null = s.apply(
                lambda x: bool(pd.notna(x) and x != 0)
                if not isinstance(x, (pd.Series, pd.DataFrame)) else False
            ).sum()
            if non_null < len(df) * 0.3:
                drops.append(i)
        except Exception:
            continue
    if drops:
        df = df.drop(df.columns[drops], axis=1)
    return df
