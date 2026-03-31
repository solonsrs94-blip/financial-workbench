"""Preparation display helpers — charts, raw tables, standardized tables, ratios.

Split from preparation.py for file size compliance.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Optional

from components.layout import format_large_number
from components.financial_table import render_financial_table


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


# ── Raw Financials ───────────────────────────────────────────────────

def render_raw_statements(raw: Optional[dict], ticker: str) -> None:
    """Display raw DataFrames with formatted numbers."""
    if raw is None:
        return

    stmt_type = st.segmented_control(
        "Statement", ["Income", "Balance Sheet", "Cash Flow"],
        default="Income", key=f"prep_raw_type_{ticker}",
        label_visibility="collapsed",
    )
    key_map = {"Income": "income", "Balance Sheet": "balance",
               "Cash Flow": "cashflow"}
    df = raw.get(key_map[stmt_type])

    if df is not None and isinstance(df, pd.DataFrame) and not df.empty:
        display = df.map(
            lambda x: format_large_number(x, prefix="")
            if isinstance(x, (int, float)) and pd.notna(x) else ""
        )
        st.dataframe(
            display, use_container_width=True,
            height=min(len(display) * 38 + 50, 700),
        )
    else:
        st.info(f"No {stmt_type.lower()} data available.")


# ── Standardized Financials ──────────────────────────────────────────

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
    ("diluted_shares", "Diluted Shares", "auto"),
    ("diluted_eps", "Diluted EPS", "auto"),
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
    ("shares_outstanding", "Shares Outstanding", "auto"),
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


def render_standardized(data: dict, ticker: str) -> None:
    """Display standardized IS/BS/CF with audit trail."""
    tables = data.get("tables", {})
    is_t = tables.get("income")
    bs_t = tables.get("balance")
    cf_t = tables.get("cashflow")

    if not is_t:
        st.info("No standardized data available.")
        return

    # Cross-checks
    checks = data.get("standardized", {}).get("cross_checks", [])
    if checks:
        failed = [c for c in checks if not c.get("ok")]
        passed = [c for c in checks if c.get("ok")]
        if failed:
            for c in failed:
                st.warning(f"**{c['year']}**: {c['check']} -- "
                           f"off by ${c.get('diff', 0)/1e6:,.0f}M")
        if passed:
            st.caption(f"{len(passed)} cross-checks passed")

    stmt = st.segmented_control(
        "Statement", ["Income", "Balance Sheet", "Cash Flow"],
        default="Income", key=f"prep_std_type_{ticker}",
        label_visibility="collapsed",
    )
    if stmt == "Income":
        render_financial_table(is_t, _IS_FIELDS)
    elif stmt == "Balance Sheet":
        render_financial_table(bs_t, _BS_FIELDS)
    else:
        render_financial_table(cf_t, _CF_FIELDS)

    # Audit trail
    _render_audit(data, stmt, ticker)


def _render_audit(data: dict, stmt: str, ticker: str) -> None:
    """Show mapping audit trail."""
    audit_key = {"Income": "income_audit", "Balance Sheet": "balance_audit",
                 "Cash Flow": "cashflow_audit"}.get(stmt)
    audit = data.get("standardized", {}).get(audit_key, {})
    if not audit:
        return

    with st.expander("Audit Trail"):
        latest_yr = max(audit.keys())
        fields = audit[latest_yr]
        layer_names = {0: "Derived", 1: "XBRL", 2: "Keyword", 3: "Hierarchy",
                       4: "Other"}
        layer_icons = {0: "D", 1: "X", 2: "K", 3: "H", 4: "?"}

        for key, info in sorted(fields.items()):
            if not isinstance(info, dict):
                continue
            raw = info.get("raw_label", "?")
            layer = info.get("layer", "?")
            ln = layer_names.get(layer, f"L{layer}")
            icon = layer_icons.get(layer, "?")
            st.caption(f"[{icon}] `{key}` <- \"{raw}\" ({ln})")


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
