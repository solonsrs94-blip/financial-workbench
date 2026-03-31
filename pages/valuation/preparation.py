"""Financial Preparation — data loading, standardization, flagging, classification.

Runs BEFORE any valuation tab. Results stored in st.session_state["prepared_data"].
Reuses existing UI components from the old DCF Step 1 sub-files.
"""

import streamlit as st
from typing import Optional

from lib.data.historical import get_raw_statements, get_standardized_history
from lib.analysis.historical import (
    build_income_table, build_balance_table,
    build_cashflow_table, build_ratios_table,
)
from lib.analysis.historical_flags import detect_flags, compute_averages
from lib.analysis.company_classifier import classify_company
from lib.data.financial_data import (
    fetch_bank_financials, fetch_insurance_financials,
)
from pages.valuation.preparation_display import (
    render_charts, render_raw_statements, render_standardized, render_ratios,
)


# ── Data loading ─────────────────────────────────────────────────────

def _load_and_prepare(ticker: str, sector: str, sub_industry: str) -> dict:
    """Load raw data, standardize, build tables, flag, classify.

    Uses EDGAR for normal companies, SimFin for financial institutions.
    """
    # Pre-classify to determine data source
    # (need preliminary classification before loading data)
    preliminary_type = classify_company(ticker, sector, sub_industry, [])

    if preliminary_type.get("data_source") == "simfin":
        return _load_financial(ticker, sector, sub_industry, preliminary_type)

    return _load_normal(ticker, sector, sub_industry)


def _load_normal(ticker: str, sector: str, sub_industry: str) -> dict:
    """Load data for normal (non-financial) companies via EDGAR."""
    raw = get_raw_statements(ticker)
    if raw is None:
        return None

    std = get_standardized_history(ticker, raw_data=raw)
    if std is None:
        return {"raw_statements": raw, "error": "Standardization failed"}

    years = std["years"]
    is_t = build_income_table(std, years)
    bs_t = build_balance_table(std, years)
    cf_t = build_cashflow_table(std, years)
    ratios = build_ratios_table(is_t, bs_t, cf_t)
    flags = detect_flags(
        ratios, is_table=is_t, bs_table=bs_t, cf_table=cf_t,
        sector=sector, ticker=ticker,
    )
    avgs = compute_averages(ratios)
    company_type = classify_company(ticker, sector, sub_industry, ratios)

    return {
        "ticker": ticker,
        "company_type": company_type,
        "raw_statements": raw,
        "standardized": std,
        "tables": {"income": is_t, "balance": bs_t, "cashflow": cf_t},
        "ratios": ratios,
        "flags": flags,
        "averages": avgs,
        "years": years,
    }


def _load_financial(
    ticker: str, sector: str, sub_industry: str, company_type: dict,
) -> dict:
    """Load data for financial companies (banks, insurance) via SimFin."""
    subtype = company_type.get("subtype", "bank")

    if subtype == "insurance":
        std = fetch_insurance_financials(ticker)
    else:
        std = fetch_bank_financials(ticker)

    if std is None:
        # Fallback to EDGAR if SimFin fails
        return _load_normal(ticker, sector, sub_industry)

    years = std.get("years", [])

    # Build simplified tables from SimFin data (no flagging for banks)
    is_t = _simfin_audit_to_table(std.get("income_audit", {}), years)
    bs_t = _simfin_audit_to_table(std.get("balance_audit", {}), years)
    cf_t = _simfin_audit_to_table(std.get("cashflow_audit", {}), years)

    return {
        "ticker": ticker,
        "company_type": company_type,
        "raw_statements": None,  # SimFin doesn't provide raw
        "standardized": std,
        "tables": {"income": is_t, "balance": bs_t, "cashflow": cf_t},
        "ratios": [],  # Bank ratios are different — computed in bank display
        "flags": [],  # No flagging for banks yet
        "averages": {},
        "years": years,
    }


def _simfin_audit_to_table(audit: dict, years: list) -> list[dict]:
    """Convert SimFin audit format to table format (list of dicts per year)."""
    result = []
    for yr in years:
        yr_data = audit.get(yr, {})
        row = {"year": yr}
        for key, info in yr_data.items():
            if isinstance(info, dict):
                row[key] = info.get("value")
            else:
                row[key] = info
        result.append(row)
    return result


# ── Main render ──────────────────────────────────────────────────────

def render_preparation(ticker: str, company) -> None:
    """Run Financial Preparation and store results in session_state."""
    st.markdown("## Financial Preparation")

    sector = getattr(company, "sector", "") or ""
    sub_industry = getattr(company, "sub_industry", "") or ""

    cache_key = f"prepared_data_{ticker}"
    if cache_key not in st.session_state:
        with st.spinner("Loading and preparing financial data..."):
            data = _load_and_prepare(ticker, sector, sub_industry)
        if data is None:
            st.error("Could not load financial data.")
            return
        st.session_state[cache_key] = data

    data = st.session_state[cache_key]
    st.session_state["prepared_data"] = data

    if data.get("error"):
        st.warning(data["error"])
        return

    # ── Classification banner ────────────────────────────────────
    _render_classification(data["company_type"])

    # ── Flags ────────────────────────────────────────────────────
    _render_flags(data["flags"])

    # ── 3yr Averages dashboard ───────────────────────────────────
    avgs = data.get("averages")
    if avgs:
        _render_averages(avgs)

    # ── Charts ───────────────────────────────────────────────────
    render_charts(data)

    # ── Raw Financials (collapsible) ─────────────────────────────
    with st.expander("Raw Financials (as-reported)"):
        render_raw_statements(data["raw_statements"], ticker)

    # ── Standardized Financials (collapsible) ────────────────────
    with st.expander("Standardized Financials"):
        render_standardized(data, ticker)

    # ── Key Ratios (collapsible) ─────────────────────────────────
    with st.expander("Key Ratios & Drivers"):
        render_ratios(data["ratios"])


# ── UI sub-sections ──────────────────────────────────────────────────

def _render_classification(ctype: dict) -> None:
    """Show company classification banner."""
    t = ctype["type"]
    methods = ", ".join(m.upper() for m in ctype["recommended_methods"])
    reason = ctype["reason"]

    if t == "financial":
        st.warning(f"**{t.title()}** — {reason}. Recommended: {methods}.")
    elif t == "dividend_stable":
        st.info(f"**{t.replace('_', ' ').title()}** — {reason}. "
                f"Recommended: {methods}.")
    else:
        st.caption(f"Classification: **{t.title()}** — {reason}. "
                   f"Recommended: {methods}.")

    source = "EDGAR" if st.session_state.get("prepared_data", {}).get(
        "standardized", {}).get("source") == "edgar" else "Yahoo"
    n_years = len(st.session_state.get("prepared_data", {}).get("years", []))
    st.caption(f"{n_years} years of data | Source: {source}")


_CAT_LABELS = {
    "margin": "Margin", "debt": "Debt", "tax": "Tax",
    "m_and_a": "M&A", "quality": "Quality", "capex": "CapEx",
    "dilution": "Dilution", "event": "Event",
}


def _render_flags(flags: list[dict]) -> None:
    """Display flags in new format: what + possible_causes + impact."""
    if not flags:
        st.success("No anomalies detected in historical data.")
        return

    high = [f for f in flags if f["severity"] == "high"]
    medium = [f for f in flags if f["severity"] == "medium"]

    if high:
        st.markdown(f"**{len(high)} significant flags:**")
        for f in high:
            _render_single_flag(f, "flag-high")

    if medium:
        with st.expander(f"{len(medium)} other flags", expanded=False):
            for f in medium:
                _render_single_flag(f, "flag-medium")


def _render_single_flag(flag: dict, css_class: str) -> None:
    """Render one flag card."""
    cat = _CAT_LABELS.get(flag.get("category", ""), "Other")
    year = flag.get("year", "")
    what = flag.get("what", "")
    impact = flag.get("impact_mn")
    causes = flag.get("possible_causes")

    impact_s = ""
    if impact:
        impact_s = (f" | ${impact/1000:.1f}B" if abs(impact) >= 1000
                    else f" | ${impact:.0f}M")

    html = (
        f'<div class="{css_class}">'
        f'<strong>{year}</strong> '
        f'<span class="source-tag">{cat}</span>{impact_s}<br>'
        f'<span style="color:rgba(255,255,255,0.9)">{what}</span>'
    )
    if causes:
        causes_s = " / ".join(causes[:3])
        html += (f'<br><span style="color:rgba(255,255,255,0.5);'
                 f'font-size:12px">Possible: {causes_s}</span>')
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def _render_averages(avgs: dict) -> None:
    """3yr averages dashboard."""
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
            s = (f"{val:.0f} days" if fmt == "days" else
                 f"{val:.1f}x" if fmt == "ratio" else f"{val*100:.1f}%")
        else:
            s = "---"
        col.metric(f"3yr {label}", s)
