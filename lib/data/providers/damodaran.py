"""Damodaran provider — ERP, CRP, spreads, industry betas.

Data from Aswath Damodaran's datasets (Excel/NYU).
Cached 30 days via lib/cache.py. No Streamlit imports.
"""

import io
import logging
from typing import Optional

import pandas as pd
import requests

from config.constants import DAMODARAN_URLS
from lib import cache

logger = logging.getLogger(__name__)
_TIMEOUT = 15
_CACHE_TTL = "damodaran"


def _download_excel(url: str, **kwargs) -> Optional[pd.DataFrame]:
    """Download Excel file, return DataFrame. None on failure."""
    try:
        resp = requests.get(url, timeout=_TIMEOUT)
        resp.raise_for_status()
        return pd.read_excel(io.BytesIO(resp.content), **kwargs)
    except Exception as exc:
        logger.warning("Damodaran download failed (%s): %s", url, exc)
        return None


def _safe_float(val) -> Optional[float]:
    """Convert cell value to float, or None."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def fetch_erp() -> Optional[float]:
    """Latest implied ERP from ERPbymonth.xlsx, col 9 "ERP (T12m)".

    Returns decimal (e.g. 0.046 for 4.6%), or None.
    """
    cached = cache.get("damodaran_erp")
    if cached is not None and cached.get("erp") is not None:
        return cached.get("erp")

    df = _download_excel(DAMODARAN_URLS["erp_monthly"], header=None)
    if df is None or df.empty:
        stale = cache.get_stale("damodaran_erp")
        return stale.get("erp") if stale else None

    erp = None
    for i in range(len(df) - 1, 0, -1):
        val = _safe_float(df.iloc[i, 9])
        if val is not None and 0.0 < val < 0.30:
            erp = val
            break

    if erp is None:
        logger.warning("Could not parse ERP from Damodaran data")
        return None

    cache.store("damodaran_erp", {"erp": erp}, "damodaran", _CACHE_TTL)
    return erp


def fetch_crp(country: str) -> Optional[float]:
    """CRP for a country. Returns decimal, or None if not found."""
    table = _fetch_crp_table()
    if table is None:
        return None
    return table.get(country.strip().lower())


def _fetch_crp_table() -> Optional[dict]:
    """Build country (lowercase) → CRP dict from ctryprem.xlsx."""
    cached = cache.get("damodaran_crp")
    if cached is not None:
        return cached

    df = _download_excel(
        DAMODARAN_URLS["crp"],
        sheet_name="ERPs by country", header=None,
    )
    if df is None or df.empty:
        stale = cache.get_stale("damodaran_crp")
        return stale if stale else None

    result = {}
    for i in range(8, len(df)):
        name = df.iloc[i, 0]
        crp_val = _safe_float(df.iloc[i, 5])
        if name and isinstance(name, str) and crp_val is not None:
            result[name.strip().lower()] = crp_val

    if not result:
        logger.warning("Empty CRP table from Damodaran")
        return None

    cache.store("damodaran_crp", result, "damodaran", _CACHE_TTL)
    return result


from lib.data.providers.damodaran_spreads_fallback import FALLBACK_SPREADS as _FALLBACK_SPREADS


def fetch_spread(
    icr: float, firm_type: str = "small",
) -> Optional[tuple[str, float]]:
    """Look up credit rating + default spread from interest coverage.

    firm_type: "large", "small" (default), or "financial".
    Returns (rating, spread) e.g. ("A2/A", 0.0078). Falls back to a
    hardcoded Damodaran table if the live fetch fails or is incomplete.
    """
    key = firm_type.lower()
    table = _fetch_spread_table()
    rows = (table or {}).get(key) if table else None
    if not rows:
        rows = _FALLBACK_SPREADS.get(key) or _FALLBACK_SPREADS["small"]

    for lower, upper, rating, spread in rows:
        if lower <= icr < upper:
            return (rating, spread)

    # ICR above highest bracket → best rating (last row)
    last = rows[-1]
    return (last[2], last[3])


def _fetch_spread_table() -> Optional[dict]:
    """Build ICR→(rating, spread) tables from ratings.xlsx sheet 0.

    Three blocks: large (rows 18-32, cols 0-3),
    financial (rows 18-32, cols 5-8), small (rows 37-51, cols 0-3).
    """
    cached = cache.get("damodaran_spreads")
    if cached is not None:
        return {k: [tuple(r) for r in v] for k, v in cached.items()}

    df = _download_excel(DAMODARAN_URLS["spreads"], sheet_name=0, header=None)
    if df is None or df.empty:
        stale = cache.get_stale("damodaran_spreads")
        if stale:
            return {k: [tuple(r) for r in v] for k, v in stale.items()}
        return None

    def _parse_block(start, end, col_off):
        rows = []
        for i in range(start, min(end + 1, len(df))):
            lo = _safe_float(df.iloc[i, col_off])
            hi = _safe_float(df.iloc[i, col_off + 1])
            rating = df.iloc[i, col_off + 2]
            spread = _safe_float(df.iloc[i, col_off + 3])
            if lo is not None and hi is not None and spread is not None:
                rows.append((lo, hi, str(rating), spread))
        return rows

    result = {
        "large": _parse_block(18, 32, 0),
        "financial": _parse_block(18, 32, 5),
        "small": _parse_block(37, 51, 0),
    }

    if not any(result.values()):
        logger.warning("Empty spreads table from Damodaran")
        return None

    serializable = {k: [list(r) for r in v] for k, v in result.items()}
    cache.store("damodaran_spreads", serializable, "damodaran", _CACHE_TTL)
    return result


_BETA_REGION_KEYS = {
    "us": "betas_us",
    "global": "betas_global",
    "emerging": "betas_emerging",
}


def fetch_industry_beta(
    industry: str, region: str = "us",
) -> Optional[dict]:
    """Look up industry beta by name.

    Priority: manual map → exact → substring → fuzzy word overlap.
    region: "us" (default), "global", or "emerging".
    """
    from lib.data.providers.industry_map import YAHOO_TO_DAMODARAN

    table = _fetch_beta_table(region)
    if table is None:
        return None
    key = industry.strip().lower()

    # 1. Manual mapping (highest priority)
    dam_name = YAHOO_TO_DAMODARAN.get(key)
    if dam_name:
        dam_key = dam_name.strip().lower()
        if dam_key in table:
            return table[dam_key]

    # 2. Exact match
    if key in table:
        return table[key]

    # 3. Substring match (either direction)
    matches = [v for k, v in table.items() if key in k or k in key]
    if matches:
        return matches[0]

    # 4. Fuzzy word matching (with noise removal)
    return _fuzzy_industry_match(key, table)


_NOISE = {"diversified", "specialty", "general", "regulated", "other",
          "integrated", "independent", "producers", "non"}
_STOP = {"and", "the", "of", "for", "in"}


def _fuzzy_industry_match(key: str, table: dict) -> Optional[dict]:
    """Fuzzy word matching with noise removal. Fallback after manual map."""
    import re

    def _w(t):
        return {w for w in re.sub(r"[()&/\-\u2014,.]", " ", t).split()
                if len(w) >= 3 and w not in _STOP and w not in _NOISE}

    def _sm(a, b):
        if a == b: return True
        if len(a) < 4 or len(b) < 4: return False
        return ((a.startswith(b) or b.startswith(a))
                and min(len(a), len(b)) / max(len(a), len(b)) >= 0.75)

    search = _w(key)
    if not search: return None
    best, best_score = None, 0.0
    for k, v in table.items():
        dam = _w(k)
        if not dam: continue
        fwd = sum(1 for w in search if any(_sm(w, d) for d in dam))
        rev = sum(1 for w in dam if any(_sm(w, s) for s in search))
        score = (fwd / len(search) + rev / len(dam)) / 2
        if score > best_score:
            best_score, best = score, v
    return best if best and best_score >= 0.5 else None


def _fetch_beta_table(region: str = "us") -> Optional[dict]:
    """Build industry (lowercase) → beta dict. Supports us/global/emerging."""
    region = region.lower()
    url_key = _BETA_REGION_KEYS.get(region, "betas_us")
    cache_key = f"damodaran_betas_{region}"

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

    # Row 9 = header, data from row 10
    result = {}
    for i in range(10, len(df)):
        name = df.iloc[i, 0]
        if not name or not isinstance(name, str):
            continue
        beta = _safe_float(df.iloc[i, 2])
        ulev = _safe_float(df.iloc[i, 5])
        if beta is None and ulev is None:
            continue
        entry = {
            "industry": name.strip(),
            "beta": beta,
            "de_ratio": _safe_float(df.iloc[i, 3]),
            "tax_rate": _safe_float(df.iloc[i, 4]),
            "unlevered_beta": ulev,
        }
        result[name.strip().lower()] = entry

    if not result:
        logger.warning("Empty %s betas table from Damodaran", region)
        return None

    cache.store(cache_key, result, "damodaran", _CACHE_TTL)
    return result
