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

    from lib.data.standardizer import standardize_all
    from lib.data.standardizer_utils import run_cross_checks

    source = raw_data.get("source", "unknown")

    # Try XBRL DataFrames first (have standard_concept for Layer 1)
    xbrl_data = None
    if source == "edgar":
        try:
            from lib.data.providers.edgar_xbrl import fetch_xbrl_statements
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

    # Top-down standardization — all 3 statements at once
    std_result = standardize_all(inc_df, bal_df, cf_df)

    income_audit = std_result["income_audit"]
    balance_audit = std_result["balance_audit"]
    cashflow_audit = std_result["cashflow_audit"]
    all_years = std_result["years"]

    # Cross-checks
    cross_checks = []
    cross_checks.extend(run_cross_checks(income_audit, "income"))
    cross_checks.extend(run_cross_checks(balance_audit, "balance"))

    # Flatten audit dicts to simple {key: value} for ratios/flags
    income = _flatten_audit(income_audit)
    balance = _flatten_audit(balance_audit)
    cashflow = _flatten_audit(cashflow_audit)

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


def _compute_cross_statement_fields(
    income_audit: dict, balance_audit: dict, cashflow_audit: dict,
) -> None:
    """Compute derived fields that need data from multiple statements.

    - EBITDA on IS: uses D&A from CF if not on IS
    - Net Debt on BS: uses total_debt (or components) - cash - STI
    """
    def _v(fields, k):
        info = fields.get(k)
        if isinstance(info, dict) and "value" in info:
            return info["value"]
        return info

    for year in income_audit:
        is_fields = income_audit[year]
        cf_fields = cashflow_audit.get(year, {})

        # EBITDA = EBIT + D&A (prefer IS D&A, fallback to CF D&A)
        ebit = _v(is_fields, "ebit")
        da = _v(is_fields, "da") or _v(cf_fields, "depreciation_amortization")
        if not _v(is_fields, "ebitda") and ebit and da:
            is_fields["ebitda"] = {
                "value": ebit + abs(da),
                "raw_label": "Derived: EBIT + D&A (from CF)",
                "layer": 0,
            }

    for year in balance_audit:
        bs_fields = balance_audit[year]

        # Net Debt = Total Debt - Cash - Short-term Investments
        # total_debt from Yahoo (if available), otherwise sum components
        total_debt = _v(bs_fields, "total_debt")
        if not total_debt:
            ltd = _v(bs_fields, "long_term_debt") or 0
            std = _v(bs_fields, "short_term_debt") or 0
            cpltd = _v(bs_fields, "current_portion_ltd") or 0
            cd = _v(bs_fields, "current_debt") or 0
            # current_debt includes commercial paper + current portion LTD
            # Use current_debt if available, otherwise sum components
            if cd and cd > std:
                total_debt = ltd + cd
            else:
                total_debt = ltd + std + cpltd

        cash = _v(bs_fields, "cash") or 0
        sti = _v(bs_fields, "short_term_investments") or 0

        if total_debt:
            bs_fields["total_debt"] = {
                "value": total_debt,
                "raw_label": "Derived or Yahoo: Total Debt",
                "layer": 0,
            }
            net_debt_val = total_debt - cash - sti
            bs_fields["net_debt"] = {
                "value": net_debt_val,
                "raw_label": "Derived: Total Debt - Cash - STI",
                "layer": 0,
            }


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


