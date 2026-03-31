"""Top-down financial statement standardizer.

Instead of bottom-up (concept -> key), this is top-down:
"I need revenue -- where do I find it?"

For each template line, tries concept match -> keyword match -> derived ->
combination -> bs_delta, in order. First match wins.

Search engine logic is in standardizer_engine.py.
No Streamlit imports (lib/ rule).
"""

import pandas as pd
from typing import Optional

from lib.data.template import SEARCH_RULES, TEMPLATE
from lib.data.standardizer_engine import (
    search_direct as _search_direct,
    try_combination as _try_combination,
    try_derived as _try_derived,
    try_bs_delta as _try_bs_delta,
    val as _val,
    prev_year as _prev_year,
    check_quality as _check_quality,
)


# Layer number mapping for backward compatibility
_LAYER_MAP = {
    "concept": 1, "sc": 1, "sc_subtotal": 1,
    "keyword": 2, "derived": 0, "combination": 0,
    "cross_statement": 0, "bs_delta": 0,
}


# ═══════════════════════════════════════════════════════════════════════
#  PUBLIC API
# ═══════════════════════════════════════════════════════════════════════

def standardize_all(
    raw_is: pd.DataFrame,
    raw_bs: pd.DataFrame,
    raw_cf: pd.DataFrame,
) -> dict:
    """Top-down standardization of all 3 statements at once.

    Returns:
        {
            "income_audit": {year: {key: {"value", "raw_label", "source"}}},
            "balance_audit": ...,
            "cashflow_audit": ...,
            "years": [sorted year strings],
            "quality": {"critical_missing": [...], "important_missing": [...]},
        }
    """
    is_parsed = _parse_df(raw_is) if raw_is is not None else {}
    bs_parsed = _parse_df(raw_bs) if raw_bs is not None else {}
    cf_parsed = _parse_df(raw_cf) if raw_cf is not None else {}

    parsed = {"income": is_parsed, "balance": bs_parsed, "cashflow": cf_parsed}

    all_years = set()
    for p in parsed.values():
        all_years.update(p.keys())
    years = sorted(all_years)

    results = {"income": {}, "balance": {}, "cashflow": {}}

    for year in years:
        year_data = _run_passes(year, years, parsed, results)

        # Distribute to statement-level results
        for key, info in year_data.items():
            if key not in SEARCH_RULES:
                continue
            if SEARCH_RULES.get(key, {}).get("helper"):
                continue
            stmt = SEARCH_RULES[key]["statement"]
            if year not in results[stmt]:
                results[stmt][year] = {}
            results[stmt][year][key] = {
                "value": info["value"],
                "raw_label": info["raw_label"],
                "layer": _LAYER_MAP.get(info["source"], 4),
            }

    latest = years[-1] if years else None
    quality = _check_quality(results, latest)

    return {
        "income_audit": results["income"],
        "balance_audit": results["balance"],
        "cashflow_audit": results["cashflow"],
        "years": years,
        "quality": quality,
    }


def standardize_statement(
    df: pd.DataFrame,
    statement_type: str,
) -> dict:
    """Backward-compatible per-statement standardization."""
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return {}

    parsed = _parse_df(df)
    years = sorted(set(yr for yr_data in parsed.values() for yr in yr_data.keys()))

    results = {}
    for year in years:
        year_data = {}

        for key, rules in SEARCH_RULES.items():
            if rules["statement"] != statement_type or key in year_data:
                continue
            val, label, source = _search_direct(key, rules, parsed.get(year, {}), year)
            if val is not None:
                year_data[key] = {"value": val, "raw_label": label, "source": source}

        for key, rules in SEARCH_RULES.items():
            if rules["statement"] != statement_type or key in year_data:
                continue
            val, source = _try_combination(key, rules, year_data)
            if val is not None:
                year_data[key] = {"value": val, "raw_label": source, "source": "combination"}

        for key, rules in SEARCH_RULES.items():
            if rules["statement"] != statement_type or key in year_data:
                continue
            val, formula = _try_derived(key, rules, year_data)
            if val is not None:
                year_data[key] = {"value": val, "raw_label": f"Derived: {formula}", "source": "derived"}

        if year not in results:
            results[year] = {}
        for key, info in year_data.items():
            if SEARCH_RULES.get(key, {}).get("helper"):
                continue
            results[year][key] = {
                "value": info["value"],
                "raw_label": info["raw_label"],
                "layer": _LAYER_MAP.get(info["source"], 4),
            }

    return results


# ═══════════════════════════════════════════════════════════════════════
#  INTERNAL — Multi-pass search
# ═══════════════════════════════════════════════════════════════════════

def _run_passes(year, years, parsed, results):
    """Run all 5 search passes for one year. Returns year_data dict."""
    year_data = {}

    # Pass 1: Direct lookups
    for key, rules in SEARCH_RULES.items():
        stmt = rules["statement"]
        if key in year_data:
            continue
        val, label, source = _search_direct(key, rules, parsed[stmt].get(year, {}), year)
        if val is not None:
            year_data[key] = {"value": val, "raw_label": label, "source": source}

    # Pass 2: Combinations
    for key, rules in SEARCH_RULES.items():
        if key in year_data:
            continue
        val, source = _try_combination(key, rules, year_data)
        if val is not None:
            year_data[key] = {"value": val, "raw_label": source, "source": "combination"}

    # Pass 3: Derived
    for key, rules in SEARCH_RULES.items():
        if key in year_data:
            continue
        val, formula = _try_derived(key, rules, year_data)
        if val is not None:
            year_data[key] = {"value": val, "raw_label": f"Derived: {formula}", "source": "derived"}

    # Pass 4: Cross-statement (EBITDA)
    if "ebitda" not in year_data:
        ebit = _val(year_data, "ebit")
        da = _val(year_data, "depreciation_amortization")
        if ebit is not None and da is not None:
            year_data["ebitda"] = {
                "value": ebit + abs(da),
                "raw_label": "Derived: EBIT + D&A (from CF)",
                "source": "cross_statement",
            }

    # Pass 5: BS delta fallbacks
    prev = _prev_year(year, years)
    if prev:
        prev_data = results.get("balance", {}).get(prev, {})
        for key, rules in SEARCH_RULES.items():
            if key in year_data:
                continue
            val, source = _try_bs_delta(key, rules, year_data, prev_data)
            if val is not None:
                year_data[key] = {"value": val, "raw_label": source, "source": "bs_delta"}

    return year_data


# ═══════════════════════════════════════════════════════════════════════
#  PARSING
# ═══════════════════════════════════════════════════════════════════════

def _parse_df(df: pd.DataFrame) -> dict:
    """Parse a raw DataFrame into {year: [{"concept", "sc", "label", "value"}]}."""
    has_xbrl = "standard_concept" in df.columns and "label" in df.columns
    return _parse_xbrl(df) if has_xbrl else _parse_simple(df)


def _parse_xbrl(df: pd.DataFrame) -> dict:
    if "dimension" in df.columns:
        df = df[df["dimension"] == False].copy()

    year_cols = [c for c in df.columns if len(str(c)) >= 8 and str(c)[:4].isdigit()]
    if not year_cols:
        return {}

    result = {}
    for _, row in df.iterrows():
        if row.get("abstract", False):
            continue
        raw_concept = str(row.get("concept", "") or "").strip()
        if raw_concept.startswith("us-gaap_"):
            raw_concept = raw_concept[8:]
        sc = str(row.get("standard_concept", "") or "").strip()
        if sc == "None":
            sc = ""
        label = str(row.get("label", "") or "").strip()

        for col in year_cols:
            year = str(col)[:4]
            val = row.get(col)
            if pd.isna(val):
                continue
            if year not in result:
                result[year] = []
            result[year].append({
                "concept": raw_concept, "sc": sc,
                "label": label, "value": float(val),
            })
    return result


def _parse_simple(df: pd.DataFrame) -> dict:
    result = {}
    for col in df.columns:
        year = str(col)[:4]
        if not year.isdigit():
            continue
        if year not in result:
            result[year] = []
        for label in df.index:
            val = df.loc[label, col]
            if pd.isna(val):
                continue
            result[year].append({
                "concept": "", "sc": "",
                "label": str(label), "value": float(val),
            })
    return result
