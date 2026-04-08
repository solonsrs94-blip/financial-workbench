"""Intelligent Recommendations — analyst briefing generator.

Composes recommendations from building-block rules based on company
characteristics, triggered flags, industry data, and dividend history.

Input: prepared_data dict + optional dividend_data dict.
Output: structured dict with 4 sections (model_suitability,
limited_value_models, attention_items, risks).

No Streamlit imports (lib/ rule).
"""

import statistics
from typing import Optional

from lib.analysis.recommendations_rules import (
    assess_dcf, assess_ddm, assess_comps, assess_historical,
)
from lib.analysis.recommendations_risks import (
    attention_from_flags, attention_dividend_health,
    attention_negative_equity, attention_sbc_dilution,
    attention_cyclicality,
    risk_industry_specific, risk_leverage,
    risk_margin_vs_industry, risk_growth_deceleration,
)
from lib.analysis.flags_helpers import _get_company_category


def generate_recommendations(
    prepared_data: dict,
    dividend_data: dict | None = None,
) -> dict:
    """Generate the full recommendation briefing.

    Args:
        prepared_data: From Financial Preparation — contains company_type,
            flags, industry_averages, averages, ratios, tables.
        dividend_data: Optional DDM provider data (has_dividend, years_paying,
            dps_cagr, dividend_cuts, payout_ratio, etc.).

    Returns: dict with model_suitability, limited_value_models,
             attention_items, risks.
    """
    ctx = _build_context(prepared_data, dividend_data)

    # Model assessments
    models = [
        assess_dcf(ctx),
        assess_ddm(ctx),
        assess_comps(ctx),
        assess_historical(ctx),
    ]
    suitability, limited = _partition_models(models)

    # Attention items
    items = []
    items.extend(attention_from_flags(ctx))
    for fn in (attention_dividend_health, attention_negative_equity,
               attention_sbc_dilution, attention_cyclicality):
        result = fn(ctx)
        if result:
            items.append(result)
    # Sort: high first
    items.sort(key=lambda x: 0 if x["severity"] == "high" else 1)

    # Risks
    risks = []
    for fn in (risk_industry_specific, risk_leverage,
               risk_margin_vs_industry, risk_growth_deceleration):
        result = fn(ctx)
        if result:
            risks.append(result)

    return {
        "model_suitability": suitability,
        "limited_value_models": limited,
        "attention_items": items,
        "risks": risks,
    }


# ── Context builder ─────────────────────────────────────────────────

def _build_context(prepared_data: dict, dividend_data: dict | None) -> dict:
    """Derive all boolean/metric signals that rules consume."""
    ctype = prepared_data.get("company_type", {})
    typ = ctype.get("type", "normal")
    signals = ctype.get("signals", {})
    sector = signals.get("sector", "")
    industry = signals.get("industry", "")

    category = _get_company_category(sector, industry, typ)
    flags = prepared_data.get("flags", [])
    averages = prepared_data.get("averages", {})
    ratios = prepared_data.get("ratios", [])
    ind_avg = prepared_data.get("industry_averages")
    # Fallback: re-fetch if missing (covers cache misses / transient failures)
    if not ind_avg and industry:
        try:
            from lib.data.valuation_data import get_industry_averages
            ind_avg = get_industry_averages(industry)
        except Exception:
            ind_avg = None

    # FCF analysis
    cf_table = prepared_data.get("tables", {}).get("cashflow", [])
    fcf_values = [r.get("free_cash_flow") for r in cf_table
                  if r.get("free_cash_flow") is not None]
    fcf_positive_years = sum(1 for v in fcf_values if v > 0)
    n_years = len(prepared_data.get("years", []))

    # Margin stability
    ebit_margins = [r.get("ebit_margin") for r in ratios
                    if r.get("ebit_margin") is not None]
    margin_stable = False
    margin_volatile = False
    if len(ebit_margins) >= 3:
        sd = statistics.stdev(ebit_margins)
        margin_stable = sd < 0.03
        margin_volatile = sd > 0.05

    # Revenue volatility
    rev_growths = [r.get("revenue_growth") for r in ratios
                   if r.get("revenue_growth") is not None]
    revenue_volatile = False
    if len(rev_growths) >= 3:
        revenue_volatile = statistics.stdev(rev_growths) > 0.15

    # Latest cashflow row for buyback data
    latest_cf = cf_table[0] if cf_table else {}

    # Latest balance sheet for equity check
    bs_table = prepared_data.get("tables", {}).get("balance", [])
    latest_bs = bs_table[0] if bs_table else {}
    negative_equity = (latest_bs.get("total_equity") or 0) < 0

    # Revenue direction
    rev_g = averages.get("revenue_growth_3yr")

    return {
        # Company identity
        "is_financial": typ == "financial",
        "is_dividend_stable": typ == "dividend_stable",
        "is_normal": typ == "normal",
        "subtype": ctype.get("subtype", ""),
        "sector": sector,
        "industry": industry,
        "category": category,
        # Data
        "averages": averages,
        "ratios": ratios,
        "flags": flags,
        "flag_categories": {f.get("category", "") for f in flags},
        "high_flag_count": sum(1 for f in flags if f["severity"] == "high"),
        "industry_averages": ind_avg,
        "dividend_data": dividend_data,
        # Derived signals
        "n_years": n_years,
        "has_positive_fcf": fcf_positive_years == len(fcf_values) and len(fcf_values) > 0,
        "fcf_positive_years": fcf_positive_years,
        "fcf_volatile": _is_fcf_volatile(fcf_values),
        "margin_stable": margin_stable,
        "margin_volatile": margin_volatile,
        "revenue_volatile": revenue_volatile,
        "revenue_growing": rev_g is not None and rev_g > 0,
        "revenue_declining": rev_g is not None and rev_g < -0.02,
        "negative_equity": negative_equity,
        "latest_cf": latest_cf,
    }


def _is_fcf_volatile(fcf_values: list) -> bool:
    """Check if FCF is volatile (has both positive and negative years)."""
    if len(fcf_values) < 2:
        return False
    has_pos = any(v > 0 for v in fcf_values)
    has_neg = any(v < 0 for v in fcf_values)
    return has_pos and has_neg


def _partition_models(models: list[dict]) -> tuple[list, list]:
    """Split model assessments into suitable vs limited-value."""
    suitable = [m for m in models if m["fit"] in ("strong", "moderate")]
    limited = [m for m in models if m["fit"] == "weak"]
    # Sort suitable: strong first, then moderate
    suitable.sort(key=lambda m: 0 if m["fit"] == "strong" else 1)
    return suitable, limited
