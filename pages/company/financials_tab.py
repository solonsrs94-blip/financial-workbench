"""Financials tab — income statement, balance sheet, cash flow with charts."""

import streamlit as st
import pandas as pd
from lib.data.fundamentals import get_financials
from components.layout import format_large_number
from pages.company.financials_helpers import get_key_rows, render_revenue_chart


def render(ticker: str) -> None:
    cache_key = f"fin_data_{ticker}"
    if cache_key not in st.session_state:
        with st.spinner("Loading financials..."):
            st.session_state[cache_key], _ = get_financials(ticker)

    fin_data = st.session_state[cache_key]

    if fin_data is None:
        st.info("Financial data not available.")
        return

    render_revenue_chart(fin_data)
    _render_statement_table(fin_data)


@st.fragment
def _render_statement_table(fin_data: dict) -> None:
    """Statement sub-tab as a fragment — switching doesn't re-render the whole page."""
    col_type, col_view = st.columns([3, 1])

    with col_type:
        fin_type = st.segmented_control(
            "Statement", ["Income", "Balance Sheet", "Cash Flow"],
            default="Income", key="fin_type", label_visibility="collapsed",
        )

    with col_view:
        view = st.segmented_control(
            "View", ["Annual", "TTM"],
            default="Annual", key="fin_view", label_visibility="collapsed",
        )

    df = _get_statement_df(fin_data, fin_type, view)

    if df is not None and not df.empty:
        df = _drop_sparse_columns(df)
        df = _format_columns(df)

        key_rows = get_key_rows(fin_type, df.index.tolist())
        show_all = st.toggle("Show all line items", value=False, key="fin_show_all")

        if not show_all and key_rows:
            display_df = df.loc[[r for r in key_rows if r in df.index]]
        else:
            display_df = df

        display_df = display_df.map(_fmt_financial)

        styled = display_df.style.map(
            lambda val: "color: #d62728" if isinstance(val, str) and val.startswith("-") else ""
        )
        st.dataframe(styled, use_container_width=True, height=min(len(display_df) * 38 + 50, 600))
    else:
        st.info(f"No {fin_type.lower()} data available.")


def _get_statement_df(fin_data: dict, fin_type: str, view: str) -> pd.DataFrame:
    """Get the appropriate DataFrame based on type and view selection."""
    annual = {"Income": "income_statement", "Balance Sheet": "balance_sheet", "Cash Flow": "cash_flow"}
    quarterly = {"Income": "quarterly_income", "Balance Sheet": "quarterly_balance", "Cash Flow": "quarterly_cashflow"}

    if view == "TTM" and fin_type != "Balance Sheet":
        qdf = fin_data.get(quarterly[fin_type])
        if qdf is not None and not qdf.empty and qdf.shape[1] >= 4:
            ttm = qdf.iloc[:, :4].sum(axis=1).to_frame("TTM")
            df = pd.concat([ttm, qdf.iloc[:, :4]], axis=1)
            df.columns = ["TTM"] + [
                c.strftime("%b %Y") if hasattr(c, "strftime") else str(c) for c in qdf.columns[:4]
            ]
            return df

    if view == "TTM" and fin_type == "Balance Sheet":
        qdf = fin_data.get(quarterly[fin_type])
        if qdf is not None and not qdf.empty:
            return qdf.iloc[:, :4]

    return fin_data.get(annual[fin_type])


def _format_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Format column headers and index labels. Ensures unique column names."""
    df = df.copy()
    formatted_cols = []
    for c in df.columns:
        if hasattr(c, "strftime"):
            # Use YYYY-MM for quarterly, YYYY for annual (if only one per year)
            s = c.strftime("%Y")
        else:
            s = str(c)
            if " 00:00:00" in s:
                s = s.split(" ")[0]
            # Only shorten to year if it won't create duplicates
            if len(s) == 10 and s[4] == "-":
                s = s[:4]
        formatted_cols.append(s)

    # If duplicates exist, use YYYY-MM format instead
    if len(formatted_cols) != len(set(formatted_cols)):
        formatted_cols = []
        for c in df.columns:
            if hasattr(c, "strftime"):
                formatted_cols.append(c.strftime("%b %Y"))
            else:
                s = str(c)
                if " 00:00:00" in s:
                    s = s.split(" ")[0]
                formatted_cols.append(s)

    df.columns = formatted_cols
    df.index = [str(i).replace("_", " ").title() if isinstance(i, str) else str(i) for i in df.index]
    return df


def _drop_sparse_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Drop columns where more than 70% of values are missing.
    Called BEFORE _format_columns to avoid duplicate column name issues."""
    cols_to_drop = []
    for i, col in enumerate(df.columns):
        try:
            series = df.iloc[:, i]
            non_null = series.apply(
                lambda x: bool(pd.notna(x) and x != 0) if not isinstance(x, (pd.Series, pd.DataFrame)) else False
            ).sum()
            if non_null < len(df) * 0.3:
                cols_to_drop.append(i)
        except Exception:
            continue
    if cols_to_drop:
        df = df.drop(df.columns[cols_to_drop], axis=1)
    return df


def _fmt_financial(x):
    """Format financial numbers."""
    if not isinstance(x, (int, float)) or pd.isna(x):
        return ""
    return format_large_number(x, prefix="")
