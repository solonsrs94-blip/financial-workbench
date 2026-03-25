"""Financials tab helpers — key row definitions and revenue chart."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from config.constants import CHART_TEMPLATE, CHART_COLORS


# Key rows for each statement type (shown by default, "Show all" reveals rest)
_KEY_ROWS = {
    "Income": [
        "Total Revenue", "Cost Of Revenue", "Gross Profit",
        "Operating Expense", "Operating Income", "Ebitda",
        "Net Income", "Basic Eps", "Diluted Eps",
    ],
    "Balance Sheet": [
        "Total Assets", "Current Assets", "Cash And Cash Equivalents",
        "Total Non Current Assets", "Investments And Advances",
        "Total Liabilities Net Minority Interest", "Current Liabilities",
        "Long Term Debt", "Total Debt",
        "Stockholders Equity", "Retained Earnings", "Common Stock Equity",
        "Working Capital", "Net Debt",
    ],
    "Cash Flow": [
        "Operating Cash Flow", "Capital Expenditure", "Free Cash Flow",
        "Investing Cash Flow", "Financing Cash Flow",
        "Repurchase Of Capital Stock", "Cash Dividends Paid",
        "Change In Cash Supplemental Reported", "End Cash Position",
    ],
}


def get_key_rows(fin_type: str, available_rows: list[str]) -> list[str]:
    """Return the most important rows for each statement type."""
    desired = _KEY_ROWS.get(fin_type, [])
    available_lower = {r.lower(): r for r in available_rows}
    return [available_lower[row.lower()] for row in desired if row.lower() in available_lower]


def render_revenue_chart(fin_data: dict) -> None:
    """Render revenue & earnings bar chart above the statement table."""
    income_df = fin_data.get("income_statement")
    if income_df is None or income_df.empty:
        return

    chart_df = income_df.copy()
    chart_df.columns = [
        c.strftime("%Y") if hasattr(c, "strftime") else str(c).split(" ")[0][:4]
        for c in chart_df.columns
    ]

    revenue_row = _find_row(chart_df, ["Total Revenue", "TotalRevenue"])
    net_income_row = _find_row(chart_df, ["Net Income", "NetIncome"])

    if revenue_row is None:
        return

    # Skip years with no revenue data
    all_years = list(reversed(revenue_row.index.tolist()))
    years = [y for y in all_years if pd.notna(revenue_row[y]) and revenue_row[y] != 0]
    if not years:
        return
    rev_vals = [revenue_row[y] / 1e9 for y in years]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=years, y=rev_vals, name="Revenue",
        marker_color=CHART_COLORS["primary"],
    ))

    if net_income_row is not None:
        ni_vals = [net_income_row[y] / 1e9 for y in years]
        fig.add_trace(go.Bar(
            x=years, y=ni_vals, name="Net Income",
            marker_color=CHART_COLORS["positive"],
        ))

    fig.update_layout(
        template=CHART_TEMPLATE, height=300,
        yaxis_title="USD (Billions)", barmode="group",
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        xaxis=dict(type="category"),  # Force category axis — no date interpolation
    )
    st.plotly_chart(fig, use_container_width=True)


def _find_row(df, labels: list):
    """Find first matching row label in DataFrame."""
    for label in labels:
        if label in df.index:
            return df.loc[label]
    return None
