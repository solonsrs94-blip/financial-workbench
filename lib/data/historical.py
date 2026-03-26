"""Historical data middleware — EDGAR primary for US, Yahoo fallback.

For US companies: EDGAR is primary (10+ years, official 10-K data).
For non-US: Yahoo + SimFin.
Yahoo always used for market data (price, cap, beta).

Two outputs:
1. Raw DataFrames (for Step 1a display) — as-reported labels
2. Standardized dicts (for ratios, flags, DCF) — normalized keys
"""

import logging
from typing import Optional

import pandas as pd

from lib import cache

logger = logging.getLogger(__name__)


def get_raw_statements(
    ticker: str, force_refresh: bool = False,
) -> Optional[dict]:
    """Get raw financial statement DataFrames for display.

    For US: EDGAR (10+ years, as-reported labels).
    For non-US: Yahoo DataFrames.

    Returns dict with 'income', 'balance', 'cashflow' DataFrames.
    """
    # Try EDGAR first (US companies)
    result = _try_edgar_raw(ticker)

    if result is None:
        # Fallback to Yahoo
        result = _try_yahoo_raw(ticker)

    return result


def _try_edgar_raw(ticker: str) -> Optional[dict]:
    """Try to fetch raw statements from EDGAR."""
    try:
        from lib.data.providers.edgar_provider import fetch_statements
        data = fetch_statements(ticker, n_filings=10)
        if data and data.get("income") is not None:
            return data
    except Exception as e:
        logger.warning("EDGAR raw fetch failed: %s", e)
    return None


def _try_yahoo_raw(ticker: str) -> Optional[dict]:
    """Fallback: convert Yahoo financials to same format."""
    try:
        from lib.data.providers.yahoo_financials import fetch_financials
        data = fetch_financials(ticker)
        if data is None:
            return None

        result = {}
        mapping = {
            "income": "income_statement",
            "balance": "balance_sheet",
            "cashflow": "cash_flow",
        }
        for our_key, yf_key in mapping.items():
            df = data.get(yf_key)
            if df is not None and not df.empty:
                # Yahoo: columns are dates, rows are labels
                # Convert column names to year strings
                df = df.copy()
                df.columns = [
                    str(c.year) if hasattr(c, "year")
                    else str(c)[:4]
                    for c in df.columns
                ]
                # Clean index labels
                df.index = [
                    str(i).replace("_", " ").title()
                    if isinstance(i, str) else str(i)
                    for i in df.index
                ]
                result[our_key] = df

        if result:
            result["source"] = "yahoo"
            return result
    except Exception as e:
        logger.warning("Yahoo raw fetch failed: %s", e)
    return None


def get_standardized_history(
    ticker: str,
    raw_data: Optional[dict] = None,
    force_refresh: bool = False,
) -> Optional[dict]:
    """Get standardized historical data for ratios and DCF.

    Uses the 4-layer standardizer:
      L1: XBRL concept mapping (EDGAR)
      L2: Keyword matching (all sources)
      L3: Hierarchy inference
      L4: "Other" catch-all

    Returns:
        {
            "income": {year: {field: value}},
            "balance": {year: {field: value}},
            "cashflow": {year: {field: value}},
            "income_audit": {year: {field: {value, raw_label, layer}}},
            "balance_audit": {year: {field: {value, raw_label, layer}}},
            "cashflow_audit": {year: {field: {value, raw_label, layer}}},
            "cross_checks": [...],
            "years": [sorted years],
            "source": str,
        }
    """
    cache_key = f"std_hist:{ticker}"
    if not force_refresh:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

    if raw_data is None:
        raw_data = get_raw_statements(ticker)
    if raw_data is None:
        return None

    from lib.data.standardizer import standardize_statement
    from lib.data.standardizer_utils import compute_derived_fields, run_cross_checks

    source = raw_data.get("source", "unknown")

    # Try XBRL DataFrames first (have standard_concept for Layer 1)
    xbrl_data = None
    if source == "edgar":
        try:
            from lib.data.providers.edgar_provider import fetch_xbrl_statements
            xbrl_data = fetch_xbrl_statements(ticker)
        except Exception as e:
            logger.warning("XBRL fetch failed, falling back to label match: %s", e)

    # Use XBRL DataFrames if available, otherwise raw (label-only)
    def _pick_df(xbrl_key, raw_key):
        if xbrl_data and xbrl_key in xbrl_data:
            v = xbrl_data[xbrl_key]
            if isinstance(v, pd.DataFrame) and not v.empty:
                return v
        return raw_data.get(raw_key)

    inc_df = _pick_df("income", "income")
    bal_df = _pick_df("balance", "balance")
    cf_df = _pick_df("cashflow", "cashflow")

    # Standardize each statement (returns audit-trail format)
    income_audit = standardize_statement(inc_df, "income")
    balance_audit = standardize_statement(bal_df, "balance")
    cashflow_audit = standardize_statement(cf_df, "cashflow")

    # Compute derived fields (modifies in place)
    for audit in [income_audit, balance_audit, cashflow_audit]:
        compute_derived_fields(audit)

    # Cross-checks
    cross_checks = []
    cross_checks.extend(run_cross_checks(income_audit, "income"))
    cross_checks.extend(run_cross_checks(balance_audit, "balance"))

    # Flatten audit dicts to simple {key: value} for ratios/flags
    income = _flatten_audit(income_audit)
    balance = _flatten_audit(balance_audit)
    cashflow = _flatten_audit(cashflow_audit)

    all_years = sorted(
        set(income.keys()) | set(balance.keys()) | set(cashflow.keys())
    )

    if not all_years:
        return None

    result = {
        "income": income,
        "balance": balance,
        "cashflow": cashflow,
        "income_audit": income_audit,
        "balance_audit": balance_audit,
        "cashflow_audit": cashflow_audit,
        "cross_checks": cross_checks,
        "years": all_years,
        "source": source,
    }
    cache.store(cache_key, result, provider="multi", ttl_key="financials")
    return result


def _flatten_audit(audit: dict) -> dict:
    """Convert {year: {key: {value, raw_label, layer}}} to {year: {key: value}}."""
    flat = {}
    for year, fields in audit.items():
        flat[year] = {}
        for key, info in fields.items():
            if isinstance(info, dict) and "value" in info:
                flat[year][key] = info["value"]
            else:
                flat[year][key] = info
    return flat


def _standardize_df(
    df: Optional[pd.DataFrame], label_map: dict,
) -> dict:
    """Convert a raw DataFrame to {year: {standardized_key: value}}.

    Matches row labels (case-insensitive, stripped) against label_map.
    """
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return {}

    result = {}
    for col in df.columns:
        year = str(col)[:4]
        mapped = {}
        for label in df.index:
            val = df.loc[label, col]
            if pd.isna(val):
                continue
            clean = str(label).lower().strip()
            # Exact match first
            if clean in label_map:
                mapped[label_map[clean]] = float(val)
            else:
                # Fuzzy fallback: match on substring contains
                for pattern, key in _FUZZY_FALLBACKS:
                    if pattern in clean and key not in mapped:
                        mapped[key] = float(val)
                        break
        if mapped:
            result[year] = mapped
    return result


# Fuzzy fallback patterns — (substring, standardized_key)
# Only used if no exact match found. More specific patterns first.
_FUZZY_FALLBACKS = [
    ("net income attributable to", "net_income"),
    ("net earnings attributable to", "net_income"),
    ("net income (loss) attributable to", "net_income"),
    ("earnings before provision for taxes", "pretax_income"),
    ("profit before taxes", "pretax_income"),
    ("provision for taxes", "tax_provision"),
    ("provision for income taxes", "tax_provision"),
    ("stockholders' equity/(deficit)", "total_equity"),
    ("stockholders' equity attributable to parent", "total_equity"),
    ("shareholders' equity (deficit)", "total_equity"),
    ("shareholders' equity", "total_equity"),
    ("total equity (deficit)", "total_equity"),
    ("total stockholders' equity (deficit)", "total_equity"),
    ("retained earnings (accumulated deficit)", "retained_earnings"),
]
