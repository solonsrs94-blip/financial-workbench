"""Export helpers — company metadata, ratios, historical financials.

Extracts data from the Company model and prepared_data for export.
Pure Python — NO streamlit imports.
"""

_RATIO_FIELDS = [
    "pe_trailing", "pe_forward", "peg", "pb", "ps",
    "ev_ebitda", "ev_revenue", "dividend_yield", "payout_ratio",
    "roe", "roa", "profit_margin", "operating_margin", "gross_margin",
    "debt_to_equity", "current_ratio", "quick_ratio",
    "eps_trailing", "eps_forward", "revenue_growth", "earnings_growth",
    "short_pct_float", "shares_outstanding",
]


def extract_company_description(company) -> str | None:
    """Get business description from Company model."""
    if not company:
        return None
    info = getattr(company, "info", None)
    return getattr(info, "description", None) if info else None


def extract_ratios(company) -> dict | None:
    """Extract all ratios from Company model as a flat dict."""
    if not company:
        return None
    ratios = getattr(company, "ratios", None)
    if not ratios:
        return None
    result = {}
    for field in _RATIO_FIELDS:
        result[field] = getattr(ratios, field, None)
    # Beta is in price, not ratios — include for completeness
    price_obj = getattr(company, "price", None)
    result["beta"] = getattr(price_obj, "beta", None) if price_obj else None
    return result


def extract_extended_meta(company) -> dict:
    """Extract additional meta fields from Company model.

    Returns dict of new fields to merge into the meta section.
    """
    if not company:
        return {}

    info = getattr(company, "info", None)
    price_obj = getattr(company, "price", None)

    result = {}
    if info:
        result["country"] = getattr(info, "country", None)
        result["exchange"] = getattr(info, "exchange", None)
        result["website"] = getattr(info, "website", None)

    if price_obj:
        result["beta"] = getattr(price_obj, "beta", None)
        result["fifty_two_week_high"] = getattr(price_obj, "high_52w", None)
        result["fifty_two_week_low"] = getattr(price_obj, "low_52w", None)
        result["analyst_target_mean"] = getattr(price_obj, "target_mean", None)
        result["analyst_target_high"] = getattr(price_obj, "target_high", None)
        result["analyst_target_low"] = getattr(price_obj, "target_low", None)
        result["analyst_rating"] = getattr(price_obj, "analyst_rating", None)
        result["analyst_count"] = getattr(price_obj, "analyst_count", None)
        result["dividend_rate"] = getattr(price_obj, "dividend_rate", None)
        result["ex_dividend_date"] = getattr(
            price_obj, "ex_dividend_date", None,
        )
        result["next_earnings_date"] = getattr(
            price_obj, "next_earnings_date", None,
        )

    return result


def compute_weighted_fair_value(
    football: dict, weights: dict,
) -> dict | None:
    """Compute weighted fair value for export from football field base prices.

    Returns dict with weighted_fair_value, model_weights, weighted_components
    or None if insufficient data.
    """
    if not weights or not football:
        return None

    _LABEL_TO_KEY = {
        "dcf": "dcf", "comps": "comps",
        "historical_multiples": "historical", "ddm": "ddm",
    }
    base_prices = {}
    for label, scenarios in football.items():
        if not scenarios or not isinstance(scenarios, dict):
            continue
        key = _LABEL_TO_KEY.get(label, label)
        price = scenarios.get("base")
        if price and price > 0:
            base_prices[key] = price

    if not base_prices:
        return None

    active = {k: weights[k] for k in base_prices if k in weights}
    total = sum(active.values())
    if total <= 0:
        return None

    components = {}
    weighted = 0.0
    for key, price in base_prices.items():
        if key not in active:
            continue
        norm_w = active[key] / total
        contrib = price * norm_w
        weighted += contrib
        components[key] = {
            "price": price,
            "weight": round(norm_w, 4),
            "contribution": round(contrib, 2),
        }

    return {
        "weighted_fair_value": round(weighted, 2),
        "model_weights": {k: round(v / total, 4) for k, v in active.items()},
        "weighted_components": components,
    }


def extract_historical_financials(prepared: dict) -> dict | None:
    """Extract standardized financial statements from prepared_data."""
    if not prepared:
        return None
    standardized = prepared.get("standardized")
    years = prepared.get("years")
    if not standardized or not years:
        return None

    result = {"years": list(years)}

    for section_key, export_key in [
        ("income", "income_statement"),
        ("balance", "balance_sheet"),
        ("cashflow", "cash_flow"),
    ]:
        section = standardized.get(section_key, {})
        if section:
            result[export_key] = {
                yr: data for yr, data in section.items()
                if isinstance(data, dict)
            }

    return result


def extract_industry_averages(prepared: dict) -> dict | None:
    """Export Damodaran industry averages if available.

    Passes through all keys from the fetched dict so new Damodaran fields
    (debt_capital, interest_coverage, eff_tax_rate, etc.) flow through
    automatically. Keeps both `industry_name` and a `damodaran_industry`
    alias for downstream consumers.
    """
    ia = prepared.get("industry_averages")
    # Fallback: re-fetch if missing (covers cache misses at prep time)
    if not ia or not isinstance(ia, dict):
        ctype = prepared.get("company_type") or {}
        industry = (ctype.get("signals") or {}).get("industry", "")
        if industry:
            try:
                from lib.data.valuation_data import get_industry_averages
                ia = get_industry_averages(industry)
            except Exception:
                ia = None
        if not ia or not isinstance(ia, dict):
            return None
    result = dict(ia)
    if ia.get("industry_name"):
        result["damodaran_industry"] = ia["industry_name"]
    return result
