"""Financial Preparation — loading, standardization, flagging, classification.

Results stored in st.session_state["prepared_data"].
"""
import streamlit as st
from typing import Optional

from lib.data.yfinance_standardizer import standardize_yfinance
from lib.data.override_utils import count_overrides
from lib.analysis.historical import (
    build_income_table, build_balance_table,
    build_cashflow_table, build_ratios_table,
)
from lib.analysis.historical_flags import detect_flags, compute_averages
from lib.analysis.company_classifier import classify_company
from lib.data.financial_data import (
    fetch_bank_financials, fetch_insurance_financials,
)
from pages.valuation.preparation_overrides import rebuild_with_overrides
from pages.valuation.preparation_display import (
    render_charts, render_standardized, render_ratios,
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
    """Load data for normal (non-financial) companies via yfinance."""
    import yfinance as yf

    t = yf.Ticker(ticker)
    income_stmt = t.income_stmt
    balance_sheet = t.balance_sheet
    cashflow = t.cashflow

    std = standardize_yfinance(income_stmt, balance_sheet, cashflow)
    if std is None:
        return None

    years = std["years"]
    is_t = build_income_table(std, years)
    bs_t = build_balance_table(std, years)
    cf_t = build_cashflow_table(std, years)
    ratios = build_ratios_table(is_t, bs_t, cf_t)
    company_type = classify_company(ticker, sector, sub_industry, ratios)
    from lib.data.valuation_data import get_industry_averages
    ind_avg = get_industry_averages(sub_industry)
    flags = detect_flags(
        ratios, is_table=is_t, bs_table=bs_t, cf_table=cf_t,
        sector=sector, ticker=ticker,
        industry=sub_industry, company_type=company_type.get("type", ""),
        industry_averages=ind_avg,
    )
    avgs = compute_averages(ratios)

    return {
        "ticker": ticker,
        "company_type": company_type,
        "original_standardized": std,
        "standardized": std,
        "tables": {"income": is_t, "balance": bs_t, "cashflow": cf_t},
        "ratios": ratios,
        "flags": flags,
        "averages": avgs,
        "years": years,
        "industry_averages": ind_avg,
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
        # Fallback to yfinance if SimFin fails
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
    return [
        {"year": yr, **{
            k: (v.get("value") if isinstance(v, dict) else v)
            for k, v in audit.get(yr, {}).items()
        }} for yr in years
    ]


# ── Main render ──────────────────────────────────────────────────────

def render_preparation(ticker: str, company) -> None:
    """Run Financial Preparation and store results in session_state."""
    st.markdown("## Financial Preparation")

    info = getattr(company, "info", None)
    sector = getattr(info, "sector", "") or "" if info else ""
    sub_industry = getattr(info, "industry", "") or "" if info else ""

    cache_key = f"prepared_data_{ticker}"
    if cache_key not in st.session_state:
        with st.spinner("Loading and preparing financial data..."):
            data = _load_and_prepare(ticker, sector, sub_industry)
        if data is None:
            st.error("Could not load financial data.")
            return
        st.session_state[cache_key] = data

    data = st.session_state[cache_key]

    # ── Apply overrides if any ────────────────────────────────────
    ovr_key = f"financial_overrides_{ticker}"
    if ovr_key not in st.session_state:
        st.session_state[ovr_key] = {
            "income": {}, "balance": {}, "cashflow": {},
        }
    overrides = st.session_state[ovr_key]

    if count_overrides(overrides) > 0 and data.get("original_standardized"):
        ctype = data.get("company_type", {}).get("type", "")
        rebuild_with_overrides(data, overrides, sector, ticker,
                               industry=sub_industry, company_type=ctype,
                               industry_averages=data.get("industry_averages"))

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

    # ── Financial Statements (collapsible) ────────────────────
    with st.expander("Financial Statements"):
        render_standardized(data, ticker, overrides)

    # ── Key Ratios (collapsible) ─────────────────────────────────
    with st.expander("Key Ratios & Drivers"):
        render_ratios(data["ratios"])


# ── UI sub-sections ──────────────────────────────────────────────────

def _render_classification(ctype: dict) -> None:
    """Show company classification banner with reasoning."""
    t = ctype["type"]
    methods = ", ".join(m.upper() for m in ctype["recommended_methods"])
    signals = ctype.get("signals", {})
    sect = signals.get("sector", "")
    ind = signals.get("industry", "")
    method = signals.get("method", "")

    # Type label
    label = t.replace("_", " ").title()
    if t == "financial":
        sub = ctype.get("subtype", "")
        label = f"Financial ({sub.title()})" if sub else "Financial"

    # Build detail line
    parts = [s for s in [f"Sector: {sect}" if sect else "",
                         f"Industry: {ind}" if ind else "",
                         f"Matched: {method}" if method else ""] if s]
    detail = " | ".join(parts)

    msg = f"**{label}** — {ctype['reason']}. Recommended: {methods}."
    renderer = (st.warning if t == "financial" else
                st.info if t == "dividend_stable" else st.caption)
    renderer(msg)

    # Data source + classification detail
    pd_data = st.session_state.get("prepared_data", {})
    src = pd_data.get("standardized", {}).get("source", "yfinance")
    src_lbl = {"yfinance": "Yahoo Finance", "simfin": "SimFin",
               "edgar": "EDGAR"}.get(src, src)
    n_years = len(pd_data.get("years", []))
    caption_parts = [f"{n_years} years of data", f"Source: {src_lbl}"]
    if detail:
        caption_parts.append(detail)
    st.caption(" | ".join(caption_parts))


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
    yr, what = flag.get("year", ""), flag.get("what", "")
    imp = flag.get("impact_mn")
    imp_s = (f" | ${imp/1000:.1f}B" if imp and abs(imp) >= 1000
             else f" | ${imp:.0f}M" if imp else "")
    causes = flag.get("possible_causes")
    causes_s = ("<br><span style=\"color:rgba(255,255,255,0.5);"
                f"font-size:12px\">Possible: {' / '.join(causes[:3])}</span>"
                if causes else "")
    st.markdown(
        f'<div class="{css_class}"><strong>{yr}</strong> '
        f'<span class="source-tag">{cat}</span>{imp_s}<br>'
        f'<span style="color:rgba(255,255,255,0.9)">{what}</span>'
        f'{causes_s}</div>', unsafe_allow_html=True,
    )


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

def _render_averages(avgs: dict) -> None:
    """3yr averages dashboard."""
    _fmt = {"days": lambda v: f"{v:.0f} days",
            "ratio": lambda v: f"{v:.1f}x",
            "pct": lambda v: f"{v*100:.1f}%"}
    for row_def in _AVG_ROWS:
        cols = st.columns(len(row_def))
        for col, (label, key, fmt) in zip(cols, row_def):
            v = avgs.get(key)
            col.metric(f"3yr {label}", _fmt[fmt](v) if v is not None else "---")
