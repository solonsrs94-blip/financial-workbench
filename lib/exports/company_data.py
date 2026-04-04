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
