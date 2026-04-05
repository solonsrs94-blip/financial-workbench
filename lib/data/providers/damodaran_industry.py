"""Damodaran industry averages — margins, leverage, payout, ROE.

Fetches four Excel files from Damodaran's datasets, caches full tables
for 30 days, and returns a consolidated dict for a given industry.
Sibling to damodaran.py (split for 300-line limit).
No Streamlit imports.
"""

import logging
from typing import Optional

from config.constants import DAMODARAN_URLS
from lib import cache
from lib.data.providers.damodaran import (
    _download_excel, _safe_float, _CACHE_TTL,
    _fuzzy_industry_match, _NOISE, _STOP,
)

logger = logging.getLogger(__name__)

# ── Header row = 7 (0-indexed), data starts at row 8 in all sheets ──

_HEADER_ROW = 7
_DATA_START = 8


def _parse_table(url_key: str, cache_key: str,
                 col_map: dict) -> Optional[dict]:
    """Generic: download Excel, parse Industry Averages sheet, cache."""
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    df = _download_excel(
        DAMODARAN_URLS[url_key],
        sheet_name="Industry Averages", header=None,
    )
    if df is None or df.empty:
        stale = cache.get_stale(cache_key)
        return stale if stale else None

    result = {}
    for i in range(_DATA_START, len(df)):
        name = df.iloc[i, 0]
        if not name or not isinstance(name, str):
            continue
        if name.lower().startswith("total market"):
            continue
        entry = {"industry_name": name.strip()}
        n = _safe_float(df.iloc[i, 1])
        if n is not None:
            entry["n_firms"] = int(n)
        for field, col_idx in col_map.items():
            if col_idx < df.shape[1]:
                entry[field] = _safe_float(df.iloc[i, col_idx])
        result[name.strip().lower()] = entry

    if not result:
        logger.warning("Empty %s table from Damodaran", cache_key)
        return None

    cache.store(cache_key, result, "damodaran", _CACHE_TTL)
    return result


def _fetch_margins_table() -> Optional[dict]:
    return _parse_table("margins", "damodaran_margins", {
        "gross_margin": 2,
        "net_margin": 3,
        "operating_margin": 5,   # Pre-tax Unadjusted Operating Margin
        "ebitda_margin": 11,     # EBITDA/Sales
    })


def _fetch_leverage_table() -> Optional[dict]:
    return _parse_table("leverage", "damodaran_leverage", {
        "debt_capital": 3,       # Market Debt to Capital (Unadjusted)
        "debt_equity": 4,        # Market D/E (unadjusted)
        "interest_coverage": 7,  # Interest Coverage Ratio
        "debt_ebitda": 8,        # Debt to EBITDA
        "eff_tax_rate": 9,       # Effective tax rate
    })


def _fetch_payout_table() -> Optional[dict]:
    return _parse_table("payout", "damodaran_payout", {
        "payout_ratio": 4,       # Dividend Payout
        "dividend_yield": 5,     # Dividend Yield
    })


def _fetch_roe_table() -> Optional[dict]:
    return _parse_table("roe", "damodaran_roe", {
        "roe": 2,                # ROE (unadjusted)
    })


# ── Industry lookup (same chain as damodaran.py) ────────────────────

def _lookup(key: str, table: dict) -> Optional[dict]:
    """manual map → exact → substring → fuzzy. Returns entry or None."""
    from lib.data.providers.industry_map import YAHOO_TO_DAMODARAN

    dam_name = YAHOO_TO_DAMODARAN.get(key)
    if dam_name:
        dam_key = dam_name.strip().lower()
        if dam_key in table:
            return table[dam_key]

    if key in table:
        return table[key]

    matches = [v for k, v in table.items() if key in k or k in key]
    if matches:
        return matches[0]

    return _fuzzy_industry_match(key, table)


# ── Public API ──────────────────────────────────────────────────────

def fetch_industry_averages(
    industry: str, region: str = "us",
) -> Optional[dict]:
    """Consolidated industry averages from Damodaran.

    Returns dict with operating_margin, net_margin, gross_margin,
    ebitda_margin, debt_ebitda, debt_equity, payout_ratio,
    dividend_yield, roe, n_firms, industry_name.
    None if industry not found.
    """
    key = industry.strip().lower()
    if not key:
        return None

    tables = [
        _fetch_margins_table(),
        _fetch_leverage_table(),
        _fetch_payout_table(),
        _fetch_roe_table(),
    ]

    result = {}
    matched_name = None
    n_firms = None

    for table in tables:
        if table is None:
            continue
        entry = _lookup(key, table)
        if entry is None:
            continue
        if matched_name is None:
            matched_name = entry.get("industry_name")
            n_firms = entry.get("n_firms")
        for k, v in entry.items():
            if k not in ("industry_name", "n_firms") and v is not None:
                result[k] = v

    if not result:
        return None

    result["industry_name"] = matched_name or industry
    if n_firms is not None:
        result["n_firms"] = n_firms
    return result
