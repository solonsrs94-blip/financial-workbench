"""Preparation display helpers — charts, financial tables, ratios.

Split from preparation.py for file size compliance.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from components.financial_table import render_financial_table
from lib.data.override_utils import count_overrides
from pages.valuation.preparation_editor import render_editable_table


# ── Charts ───────────────────────────────────────────────────────────

def render_charts(data: dict) -> None:
    """Revenue/FCF bar chart + margin trend line chart."""
    is_t = data["tables"]["income"]
    cf_t = data["tables"]["cashflow"]
    ratios = data["ratios"]

    if not is_t or not ratios:
        return

    c1, c2 = st.columns(2)
    with c1:
        _revenue_fcf_chart(is_t, cf_t)
    with c2:
        _margin_chart(ratios)


def _margin_chart(ratios: list[dict]) -> None:
    """Plotly line chart showing margin trends."""
    years = [r["year"] for r in ratios]
    fig = go.Figure()
    for key, name, color in [
        ("gross_margin", "Gross Margin", "#2ca02c"),
        ("ebit_margin", "EBIT Margin", "#1f77b4"),
        ("net_margin", "Net Margin", "#ff7f0e"),
        ("fcf_margin", "FCF Margin", "#9467bd"),
    ]:
        vals = [r.get(key) for r in ratios]
        pct = [v * 100 if v is not None else None for v in vals]
        fig.add_trace(go.Scatter(
            x=years, y=pct, name=name,
            mode="lines+markers", line=dict(color=color, width=2),
            marker=dict(size=5),
        ))
    fig.update_layout(
        title="Margin Trends", yaxis_title="%", height=350,
        margin=dict(l=40, r=20, t=40, b=30),
        legend=dict(orientation="h", y=-0.15), hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)


def _revenue_fcf_chart(is_table: list[dict], cf_table: list[dict]) -> None:
    """Bar chart: revenue with FCF line overlay."""
    years = [r["year"] for r in is_table]
    rev = [r.get("revenue") for r in is_table]
    fcf = [r.get("free_cash_flow") for r in cf_table] if cf_table else []

    rev_b = [v / 1e9 if v else None for v in rev]
    fcf_b = [v / 1e9 if v else None for v in fcf]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=years, y=rev_b, name="Revenue",
        marker_color="rgba(28, 131, 225, 0.6)",
    ))
    if fcf_b:
        fig.add_trace(go.Scatter(
            x=years[:len(fcf_b)], y=fcf_b, name="FCF",
            mode="lines+markers", line=dict(color="#2ca02c", width=2),
            marker=dict(size=6),
        ))
    fig.update_layout(
        title="Revenue & Free Cash Flow ($B)", yaxis_title="$B", height=350,
        margin=dict(l=40, r=20, t=40, b=30),
        legend=dict(orientation="h", y=-0.15),
        hovermode="x unified", barmode="group",
    )
    st.plotly_chart(fig, use_container_width=True)


# ── Financial Statements ─────────────────────────────────────────────

_IS_FIELDS = [
    ("revenue", "Revenue", "auto"),
    ("cogs", "Cost of Revenue", "auto", False),
    ("gross_profit", "= Gross Profit", "auto"),
    ("sga", "SG&A", "auto", False),
    ("rd", "R&D", "auto", False),
    ("da", "D&A", "auto", False),
    ("total_opex", "Total OpEx", "auto", False),
    ("ebit", "= EBIT (Operating Income)", "auto"),
    ("ebitda", "EBITDA", "auto"),
    ("interest_expense", "Interest Expense", "auto", False),
    ("interest_income", "Interest Income", "auto"),
    ("other_non_operating", "Other Non-Operating", "auto"),
    ("pretax_income", "= Pretax Income", "auto"),
    ("tax_provision", "Tax Provision", "auto", False),
    ("net_income", "= Net Income", "auto"),
    ("diluted_shares", "Diluted Shares", "shares"),
    ("diluted_eps", "Diluted EPS", "per_share"),
]

_BS_FIELDS = [
    ("cash", "Cash & Equivalents", "auto"),
    ("short_term_investments", "Short-term Investments", "auto"),
    ("accounts_receivable", "Accounts Receivable", "auto"),
    ("inventories", "Inventories", "auto"),
    ("total_current_assets", "= Current Assets", "auto"),
    ("pp_and_e", "PP&E (net)", "auto"),
    ("goodwill", "Goodwill", "auto"),
    ("intangible_assets", "Intangible Assets", "auto"),
    ("total_assets", ">> Total Assets", "auto"),
    ("accounts_payable", "Accounts Payable", "auto"),
    ("deferred_revenue_current", "Deferred Revenue", "auto"),
    ("total_current_liabilities", "= Current Liabilities", "auto"),
    ("long_term_debt", "Long-term Debt", "auto"),
    ("total_liabilities", "= Total Liabilities", "auto"),
    ("total_equity", "= Total Equity", "auto"),
    ("total_debt", ">> Total Debt", "auto"),
    ("net_debt", ">> Net Debt", "auto"),
    ("shares_outstanding", "Shares Outstanding", "shares"),
]

_CF_FIELDS = [
    ("net_income_cf", "Net Income", "auto"),
    ("depreciation_amortization", "D&A", "auto"),
    ("stock_based_compensation", "Stock-Based Compensation", "auto"),
    ("change_in_receivables", "Change in Receivables", "auto"),
    ("change_in_payables", "Change in Payables", "auto"),
    ("change_in_inventory", "Change in Inventory", "auto"),
    ("operating_cash_flow", "= Operating Cash Flow", "auto"),
    ("capital_expenditure", "Capital Expenditure", "auto", False),
    ("acquisitions", "Acquisitions", "auto", False),
    ("investment_purchases", "Investment Purchases", "auto", False),
    ("investing_cash_flow", "= Investing Cash Flow", "auto", False),
    ("dividends_paid", "Dividends Paid", "auto", False),
    ("buybacks_and_issuance", "Buybacks / Stock Issuance", "auto", False),
    ("debt_issuance", "Debt Issuance", "auto"),
    ("debt_repayment", "Debt Repayment", "auto", False),
    ("financing_cash_flow", "= Financing Cash Flow", "auto", False),
    ("free_cash_flow", ">> Free Cash Flow", "auto"),
]


_STMT_MAP = {"Income": "income", "Balance Sheet": "balance",
             "Cash Flow": "cashflow"}
_FIELD_MAP = {"Income": _IS_FIELDS, "Balance Sheet": _BS_FIELDS,
              "Cash Flow": _CF_FIELDS}


def render_standardized(
    data: dict, ticker: str, overrides: dict | None = None,
) -> None:
    """Display IS/BS/CF tables with optional edit mode for overrides."""
    tables = data.get("tables", {})
    if not tables.get("income"):
        st.info("No financial data available.")
        return

    overrides = overrides or {}
    ovr_key = f"financial_overrides_{ticker}"
    n_ovr = count_overrides(overrides)

    # ── Header row: statement selector + edit toggle + reset ──
    h1, h2, h3 = st.columns([5, 2, 2])
    with h1:
        stmt = st.segmented_control(
            "Statement", ["Income", "Balance Sheet", "Cash Flow"],
            default="Income", key=f"prep_std_type_{ticker}",
            label_visibility="collapsed",
        )
    with h2:
        edit_mode = st.toggle(
            "Edit values", key=f"prep_edit_mode_{ticker}",
        )
    with h3:
        if n_ovr > 0:
            if st.button(f"Reset all ({n_ovr})", key=f"prep_reset_{ticker}"):
                st.session_state[ovr_key] = {
                    "income": {}, "balance": {}, "cashflow": {},
                }
                st.rerun()

    stmt_key = _STMT_MAP[stmt]
    fields = _FIELD_MAP[stmt]
    rows = tables.get(stmt_key, [])
    stmt_overrides = overrides.get(stmt_key, {})

    if edit_mode:
        render_editable_table(rows, fields, stmt_key, ticker, overrides, data)
    else:
        render_financial_table(
            rows, fields, show_source=False, overrides=stmt_overrides,
        )


# ── Ratios ───────────────────────────────────────────────────────────

_RATIO_FIELDS = [
    ("revenue_growth", "Revenue Growth", "pct"),
    ("ebitda_growth", "EBITDA Growth", "pct"),
    ("gross_margin", "Gross Margin", "pct"),
    ("ebit_margin", "EBIT Margin", "pct"),
    ("ebitda_margin", "EBITDA Margin", "pct"),
    ("net_margin", "Net Margin", "pct"),
    ("fcf_margin", "FCF Margin", "pct"),
    ("effective_tax_rate", "Effective Tax Rate", "pct"),
    ("dso", "DSO (days)", "days"),
    ("dio", "DIO (days)", "days"),
    ("dpo", "DPO (days)", "days"),
    ("capex_pct", "CapEx / Revenue", "pct"),
    ("da_pct", "D&A / Revenue", "pct"),
    ("sbc_pct", "SBC / Revenue", "pct"),
    ("interest_coverage", "Interest Coverage", "ratio"),
    ("debt_ebitda", "Debt / EBITDA", "ratio"),
    ("roic", "ROIC", "pct"),
    ("roe", "ROE", "pct"),
    ("fcf_conversion", "FCF Conversion", "pct"),
]


def render_ratios(ratios: list[dict]) -> None:
    """Render key ratios table."""
    render_financial_table(ratios, _RATIO_FIELDS, show_source=False)


# ── 3yr Averages dashboard ──────────────────────────────────────────

_AVG_ROWS = [
    [("Gross Margin", "gross_margin_3yr", "pct"),
     ("EBIT Margin", "ebit_margin_3yr", "pct"),
     ("Rev Growth", "revenue_growth_3yr", "pct"),
     ("CapEx/Rev", "capex_pct_3yr", "pct"),
     ("ROIC", "roic_3yr", "pct")],
    [("DSO", "dso_3yr", "days"), ("DIO", "dio_3yr", "days"),
     ("DPO", "dpo_3yr", "days"), ("Int. Cov.", "interest_coverage_3yr", "ratio"),
     ("Eff Tax", "eff_tax_3yr", "pct")],
]


def render_averages(avgs: dict) -> None:
    """3yr averages dashboard."""
    _fmt = {"days": lambda v: f"{v:.0f} days",
            "ratio": lambda v: f"{v:.1f}x",
            "pct": lambda v: f"{v*100:.1f}%"}
    for row_def in _AVG_ROWS:
        cols = st.columns(len(row_def))
        for col, (label, key, fmt) in zip(cols, row_def):
            v = avgs.get(key)
            col.metric(f"3yr {label}", _fmt[fmt](v) if v is not None else "---")
