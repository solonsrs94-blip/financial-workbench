"""Step 1: Historical Data & Spreading.

Sub-sections:
  1a. Raw Financials (as-reported, flagged cells highlighted)
  1b. Spreading & Normalization (AI Phase 3 + rule-based flags now)
  1c. Review & Override (applied flags + manual adjustments)
  1d. Standardized Financials (cleaned result)
  1e. Ratios & Drivers (calculated from 1d)
"""

import streamlit as st
import pandas as pd
from typing import Optional

from components.layout import format_large_number
from pages.valuation.dcf_step1_charts import (
    render_margin_chart, render_revenue_fcf_chart,
)
from pages.valuation.dcf_step1_ratios import render_ratios_section
from pages.valuation.dcf_step1_flags import render_flags_section
from pages.valuation.dcf_step1_overrides import render_overrides
from pages.valuation.dcf_step1_standardized import render_standardized


def render(ticker: str, step1_data: Optional[dict] = None) -> None:
    st.markdown("### Step 1: Historical Data & Spreading")

    if step1_data is None:
        st.info("Loading data...")
        return

    raw = step1_data.get("raw")
    source = raw.get("source", "unknown") if raw else "unknown"
    n_years = raw.get("n_years", 0) if raw else 0
    flags = step1_data.get("flags", [])
    st.caption(f"{n_years} years | Source: {source}")

    # === 1a. Raw Financials ===
    st.markdown("#### 1a. Raw Financials")
    st.caption("As-reported from SEC filings. Flagged cells highlighted.")
    _render_raw_statements(raw, ticker, flags)
    st.divider()

    # === 1b. Spreading & Normalization ===
    st.markdown("#### 1b. Spreading & Normalization")
    render_flags_section(flags, ticker)
    with st.expander("AI Spreading & Normalization (Phase 3)"):
        st.info(
            "**Coming in Phase 3:** AI reads raw financials + 10-K, "
            "spreads into model format, and normalizes automatically."
        )
    st.divider()

    # === 1c. Review & Override ===
    st.markdown("#### 1c. Review & Override")
    st.caption("Applied flags and manual adjustments.")
    render_overrides(ticker, step1_data)
    st.divider()

    # === 1d. Standardized Financials ===
    st.markdown("#### 1d. Standardized Financials")
    st.caption("Cleaned and normalized. Feeds into ratios and projections.")
    render_standardized(step1_data, ticker)
    st.divider()

    # === 1e. Ratios & Drivers ===
    st.markdown("#### 1e. Ratios & Drivers")
    st.caption("Calculated from standardized data.")
    avgs = step1_data.get("averages")
    if avgs:
        _render_averages(avgs)

    is_t = step1_data.get("is_table")
    cf_t = step1_data.get("cf_table")
    ratios = step1_data.get("ratios")
    if is_t and cf_t and ratios:
        c1, c2 = st.columns(2)
        with c1:
            render_revenue_fcf_chart(is_t, cf_t)
        with c2:
            render_margin_chart(ratios)
    if ratios:
        render_ratios_section(ratios)


def _get_flag_severity_by_year(flags: list[dict]) -> dict:
    """Build {year: max_severity} from flags."""
    sev_map = {}
    for f in flags:
        yr = f.get("year", "")
        sev = f.get("severity", "low")
        if yr not in sev_map or sev == "high":
            sev_map[yr] = sev
        elif sev == "medium" and sev_map.get(yr) != "high":
            sev_map[yr] = "medium"
    return sev_map


def _get_flagged_cells(flags: list[dict]) -> dict:
    """Build {(year, line_item): {severity, labels}} for cell highlighting."""
    key_to_labels = {
        "ebit": ["operating income", "income from operations"],
        "gross_profit": ["gross profit", "gross margin"],
        "net_income": ["net income"],
        "revenue": ["revenue", "net sales", "total revenue"],
        "tax_provision": ["income tax", "tax provision", "provision for income"],
        "cost_of_revenue": ["cost of revenue", "cost of sales"],
        "sbc": ["stock-based comp", "share-based comp"],
        "capital_expenditure": ["capital expenditure", "acquisition of property"],
        "total_debt": ["total debt", "term debt"],
        "selling_general_admin": ["selling, general", "selling general"],
    }
    cells = {}
    for f in flags:
        yr, li, sev = f.get("year", ""), f.get("line_item", ""), f.get("severity", "medium")
        cells[(yr, li)] = {"severity": sev, "labels": key_to_labels.get(li, [])}
    return cells


def _render_raw_statements(
    raw: Optional[dict], ticker: str, flags: list[dict],
) -> None:
    """Display raw DataFrames with flagged cells highlighted."""
    if raw is None:
        return

    with st.expander("Financial Statements (as-reported)", expanded=True):
        stmt_type = st.segmented_control(
            "Statement", ["Income", "Balance Sheet", "Cash Flow"],
            default="Income", key=f"dcf_raw_type_{ticker}",
            label_visibility="collapsed",
        )
        df = raw.get({"Income": "income", "Balance Sheet": "balance", "Cash Flow": "cashflow"}[stmt_type])

        if df is not None and isinstance(df, pd.DataFrame) and not df.empty:
            sev_map = _get_flag_severity_by_year(flags)
            flagged = _get_flagged_cells(flags)

            # Column headers with flag indicators
            display = df.copy()
            display.columns = [
                f"{c} !!" if sev_map.get(str(c)[:4]) == "high"
                else f"{c} !" if sev_map.get(str(c)[:4]) == "medium"
                else str(c)
                for c in display.columns
            ]

            # Format numbers
            display = display.map(
                lambda x: format_large_number(x, prefix="")
                if isinstance(x, (int, float)) and pd.notna(x) else ""
            )

            # Cell-level styles
            def _style(df_s):
                styles = pd.DataFrame("", index=df_s.index, columns=df_s.columns)
                for col in df_s.columns:
                    yr = str(col)[:4]
                    for row in df_s.index:
                        val = df_s.loc[row, col]
                        css = ""
                        if isinstance(val, str) and val.startswith("-"):
                            css = "color: #d62728; "
                        rl = str(row).lower()
                        for (fy, fl), info in flagged.items():
                            if yr == fy and any(lb in rl for lb in info["labels"]):
                                bg = "rgba(255,59,48,0.2)" if info["severity"] == "high" else "rgba(255,204,0,0.15)"
                                css += f"background-color: {bg}; font-weight: 700; "
                                break
                        styles.loc[row, col] = css
                return styles

            st.dataframe(
                display.style.apply(_style, axis=None),
                use_container_width=True,
                height=min(len(display) * 38 + 50, 700),
            )
        else:
            st.info(f"No {stmt_type.lower()} data available.")


def _render_averages(avgs: dict) -> None:
    cols = st.columns(5)
    for col, (label, key) in zip(cols, [
        ("Gross Margin", "gross_margin_3yr"),
        ("EBIT Margin", "ebit_margin_3yr"),
        ("Rev Growth", "revenue_growth_3yr"),
        ("CapEx/Rev", "capex_pct_3yr"),
        ("ROIC", "roic_3yr"),
    ]):
        val = avgs.get(key)
        col.metric(f"3yr {label}", f"{val*100:.1f}%" if val else "---")

    cols2 = st.columns(5)
    for col, (label, key, fmt) in zip(cols2, [
        ("DSO", "dso_3yr", "days"),
        ("DIO", "dio_3yr", "days"),
        ("DPO", "dpo_3yr", "days"),
        ("Int. Cov.", "interest_coverage_3yr", "ratio"),
        ("Eff Tax", "eff_tax_3yr", "pct"),
    ]):
        val = avgs.get(key)
        if val is not None:
            s = f"{val:.0f} days" if fmt == "days" else (
                f"{val:.1f}x" if fmt == "ratio" else f"{val*100:.1f}%"
            )
        else:
            s = "---"
        col.metric(f"3yr {label}", s)
