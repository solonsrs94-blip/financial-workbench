"""Export analysis data to JSON for Claude report generation.

Pure Python — NO streamlit imports.
"""

from datetime import date

from lib.analysis.flags_helpers import _get_company_category
from lib.exports.company_data import (
    extract_company_description,
    extract_ratios,
    extract_extended_meta,
    extract_historical_financials,
    extract_industry_averages,
    compute_weighted_fair_value,
)

_SCENARIOS = ["base", "bull", "bear"]


def build_export_json(
    state: dict,
    ticker: str,
    included_modules: dict,
    default_templates: dict | None = None,
) -> dict:
    """Build structured export dict from session state."""
    defaults = default_templates or {}
    company = state.get(f"company_{ticker}")
    prepared = state.get("prepared_data") or {}

    # Build in specified section order
    result = {"meta": _build_meta(state, ticker, company)}
    result["company_description"] = extract_company_description(company)
    result["ratios"] = extract_ratios(company)
    result["historical_financials"] = extract_historical_financials(prepared)
    result["historical_ratios"] = prepared.get("ratios")
    result["historical_averages"] = prepared.get("averages")
    result["flags"] = _build_flags(prepared)
    result["industry_averages"] = extract_industry_averages(prepared)
    result["recommendations"] = state.get("recommendations")

    if included_modules.get("DCF"):
        result["dcf"] = _build_dcf(state, ticker, defaults)
    if included_modules.get("DDM"):
        result["ddm"] = _build_ddm(state, ticker, defaults)
    if included_modules.get("Comps"):
        result["comps"] = _build_comps(state, ticker, defaults)
    if included_modules.get("Historical"):
        result["historical_multiples"] = _build_historical(
            state, ticker, defaults,
        )

    result["summary"] = _build_summary(state, included_modules, defaults)
    result["overrides"] = _build_overrides(state, ticker)
    return result


def _build_meta(state: dict, ticker: str, company=None) -> dict:
    val_data = state.get(f"val_data_{ticker}") or {}
    prepared = state.get("prepared_data") or {}
    ctype = prepared.get("company_type", {})

    price = 0
    name = sector = industry = currency = ""
    if company:
        price_obj = getattr(company, "price", None)
        price = getattr(price_obj, "price", 0) or 0
        info = getattr(company, "info", None)
        name = getattr(info, "name", "") or ""
        sector = getattr(info, "sector", "") or ""
        industry = getattr(info, "industry", "") or ""
        currency = getattr(price_obj, "currency", "USD") or "USD"

    company_category = _get_company_category(
        sector, industry, ctype.get("type", "normal"),
    )

    meta = {
        "ticker": ticker,
        "company_name": name,
        "sector": sector,
        "industry": industry,
        "company_type": ctype.get("type", "normal"),
        "company_category": company_category,
        "export_date": str(date.today()),
        "share_price": price,
        "market_cap": val_data.get("market_cap"),
        "shares_outstanding": val_data.get("shares"),
        "enterprise_value": val_data.get("enterprise_value"),
        "currency": val_data.get("currency", currency),
        "financial_currency": val_data.get("financial_currency", currency),
        "ebitda_ttm": val_data.get("ebitda_ttm"),
        "ebitda_ttm_source": "ttm_quarterly" if val_data.get("ebitda_ttm") else None,
    }
    meta.update(extract_extended_meta(company))
    return meta


def _build_flags(prepared: dict) -> list:
    """Export triggered quality flags (already JSON-serializable dicts)."""
    return list(prepared.get("flags") or [])


def _build_dcf(state: dict, ticker: str, defaults: dict) -> dict:
    scenarios_data = state.get("dcf_scenarios") or {}
    terminals = state.get("dcf_scenarios_terminal") or {}
    output = state.get("dcf_output") or {}

    scenarios = {}
    for s in _SCENARIOS:
        assumptions = scenarios_data.get(s)
        terminal = terminals.get(s)
        results = output.get(s) if isinstance(output, dict) else None
        if not assumptions and not results:
            continue
        scenarios[s] = {
            "assumptions": assumptions,
            "terminal": terminal,
            "results": results,
            "commentary_step2": _get_commentary(
                state, f"commentary_dcf_step2_{s}", defaults,
            ),
            "commentary_step4": _get_commentary(
                state, f"commentary_dcf_step4_{s}", defaults,
            ),
        }

    return {
        "sector_template": state.get("dcf_sector_template"),
        "wacc": state.get("dcf_wacc"),
        "scenarios": scenarios,
        "commentary_wacc": _get_commentary(
            state, "commentary_dcf_step3", defaults,
        ),
        "commentary_step5": _get_commentary(
            state, "commentary_dcf_step5", defaults,
        ),
    }


def _build_ddm(state: dict, ticker: str, defaults: dict) -> dict:
    scenarios_data = state.get("ddm_scenarios") or {}
    output = state.get("ddm_output") or {}

    scenarios = {}
    for s in _SCENARIOS:
        assumptions = scenarios_data.get(s)
        results = output.get(s) if isinstance(output, dict) else None
        if not assumptions and not results:
            continue
        scenarios[s] = {
            "assumptions": assumptions,
            "results": results,
            "commentary_step2": _get_commentary(
                state, f"commentary_ddm_step2_{s}", defaults,
            ),
        }

    return {
        "ke": state.get("ddm_ke"),
        "dividend_data": state.get(f"ddm_data_{ticker}"),
        "scenarios": scenarios,
        "alternate_model": state.get("ddm_output_alt"),
        "commentary_step3": _get_commentary(
            state, "commentary_ddm_step3", defaults,
        ),
    }


def _build_comps(state: dict, ticker: str, defaults: dict) -> dict:
    comps_table = state.get("comps_table") or {}
    valuation = state.get("comps_valuation") or {}

    scenarios = {}
    for s in _SCENARIOS:
        sv = valuation.get(s)
        if not sv or not isinstance(sv, dict):
            continue
        scenarios[s] = {
            "applied_multiple": sv.get("applied_mult"),
            "premium_discount": sv.get("premium"),
            "final_multiple": sv.get("final_mult"),
            "implied_price": sv.get("implied_price"),
            "commentary": _get_commentary(
                state, f"commentary_comps_step3_{s}", defaults,
            ),
        }

    excluded = comps_table.get("excluded")
    return {
        "target": comps_table.get("target"),
        "peers": comps_table.get("peers"),
        "excluded_peers": list(excluded) if excluded else [],
        "peer_statistics": comps_table.get("summary"),
        "is_financial": comps_table.get("is_financial", False),
        "scenarios": scenarios,
        "commentary_comparison": _get_commentary(
            state, "commentary_comps_comparison", defaults,
        ),
    }


def _build_historical(state: dict, ticker: str, defaults: dict) -> dict:
    hist = state.get("historical_result") or {}

    scenarios = {}
    for s in _SCENARIOS:
        sv = hist.get(s)
        if not sv or not isinstance(sv, dict):
            continue
        scenarios[s] = {
            "multiple_used": sv.get("mult_key"),
            "applied_multiple": sv.get("applied_mult"),
            "implied_price": sv.get("implied_price"),
            "commentary": _get_commentary(
                state, f"commentary_historical_{s}", defaults,
            ),
        }

    result = {
        "statistics": hist.get("summary"),
        "implied_values": hist.get("implied_values"),
        "scenarios": scenarios,
        "commentary_comparison": _get_commentary(
            state, "commentary_historical_comparison", defaults,
        ),
    }
    if hist.get("eps_basis"):
        result["eps_basis"] = hist["eps_basis"]
        result["eps_used"] = hist.get("eps_used")
    return result


def _build_summary(
    state: dict, included: dict, defaults: dict,
) -> dict:
    models_used = [
        k.lower() for k, v in included.items() if v
    ]

    _KEY_MAP = {"DCF": "dcf_output", "Comps": "comps_valuation",
                "Historical": "historical_result", "DDM": "ddm_output"}
    _LABEL = {"DCF": "dcf", "Comps": "comps",
              "Historical": "historical_multiples", "DDM": "ddm"}
    football = {}
    for group, key in _KEY_MAP.items():
        if included.get(group):
            football[_LABEL[group]] = _extract_scenario_prices(state.get(key))

    # Weighted fair value from analyst-set weights
    weights = state.get("summary_weights") or {}
    weighted_result = compute_weighted_fair_value(football, weights)

    result = {
        "models_used": models_used,
        "football_field": football,
        "commentary": _get_commentary(
            state, "commentary_summary", defaults,
        ),
    }
    if weighted_result:
        result.update(weighted_result)
    return result


def _extract_scenario_prices(data: dict | None) -> dict | None:
    """Extract bear/base/bull implied prices from scenario data."""
    if not data or not isinstance(data, dict):
        return None
    if "base" in data and isinstance(data.get("base"), dict):
        return {
            s: data[s].get("implied_price")
            for s in _SCENARIOS if s in data and isinstance(data[s], dict)
        }
    # Legacy single-value format
    if data.get("implied_price"):
        return {"base": data["implied_price"]}
    return None

def _build_overrides(state: dict, ticker: str) -> dict:
    overrides = state.get(f"financial_overrides_{ticker}")
    has = bool(overrides and any(overrides.values()))
    return {
        "has_overrides": has,
        "details": overrides if has else None,
    }


def _get_commentary(
    state: dict, key: str, defaults: dict,
) -> str | None:
    """Get commentary text. Returns None if unchanged from default."""
    text = state.get(key)
    if not text:
        return None
    default = defaults.get(key, "")
    if text.strip() == default.strip():
        return None
    return text
