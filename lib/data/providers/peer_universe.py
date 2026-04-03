"""
Peer universe provider — fetches index constituents from Wikipedia.

Supports: S&P 500, Euro STOXX 50, CAC 40, FTSE 100, S&P/TSX 60, Hang Seng.
Each index returns standardised dicts with: symbol, name, gics_sector,
gics_sub_industry, source_index.

No Streamlit imports. Returns raw data only.
"""

import logging
import re
from io import StringIO

import pandas as pd
import requests

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
_TIMEOUT = 15


# ── Index definitions ──────────────────────────────────────────

# (name, url, parser_function)
# Parsers return list[dict] with standardised keys.

def _parse_sp500(html: str) -> list[dict]:
    tables = pd.read_html(StringIO(html))
    df = tables[0]
    results = []
    for _, r in df.iterrows():
        results.append({
            "symbol": str(r.get("Symbol", "")).strip(),
            "name": str(r.get("Security", "")),
            "gics_sector": str(r.get("GICS Sector", "")),
            "gics_sub_industry": str(r.get("GICS Sub-Industry", "")),
            "source_index": "S&P 500",
        })
    return results


def _parse_euro_stoxx50(html: str) -> list[dict]:
    tables = pd.read_html(StringIO(html))
    # Find table with Ticker column and ~50 rows
    for t in tables:
        if "Ticker" in t.columns and len(t) >= 40:
            results = []
            for _, r in t.iterrows():
                results.append({
                    "symbol": str(r.get("Ticker", "")).strip(),
                    "name": str(r.get("Name", "")),
                    "gics_sector": str(r.get("Sector", "")),
                    "gics_sub_industry": "",  # only sector-level
                    "source_index": "Euro STOXX 50",
                })
            return results
    return []


def _parse_cac40(html: str) -> list[dict]:
    tables = pd.read_html(StringIO(html))
    for t in tables:
        if "Ticker" in t.columns and "Company" in t.columns and len(t) >= 30:
            results = []
            for _, r in t.iterrows():
                results.append({
                    "symbol": str(r.get("Ticker", "")).strip(),
                    "name": str(r.get("Company", "")),
                    "gics_sector": str(r.get("Sector", "")),
                    "gics_sub_industry": str(r.get("GICS Sub-Industry", "")),
                    "source_index": "CAC 40",
                })
            return results
    return []


def _parse_ftse100(html: str) -> list[dict]:
    tables = pd.read_html(StringIO(html))
    for t in tables:
        if "Ticker" in t.columns and len(t) >= 90:
            # Find the ICB sector column (name varies)
            sector_col = ""
            for c in t.columns:
                if "sector" in str(c).lower() or "icb" in str(c).lower():
                    sector_col = c
                    break
            results = []
            for _, r in t.iterrows():
                raw_ticker = str(r.get("Ticker", "")).strip()
                # Append .L for London Stock Exchange
                symbol = f"{raw_ticker}.L" if raw_ticker else ""
                results.append({
                    "symbol": symbol,
                    "name": str(r.get("Company", "")),
                    "gics_sector": str(r.get(sector_col, "")) if sector_col else "",
                    "gics_sub_industry": "",
                    "source_index": "FTSE 100",
                })
            return results
    return []


def _parse_tsx60(html: str) -> list[dict]:
    tables = pd.read_html(StringIO(html))
    for t in tables:
        if "Symbol" in t.columns and len(t) >= 50:
            results = []
            for _, r in t.iterrows():
                raw = str(r.get("Symbol", "")).strip()
                # Append .TO for Toronto; handle .UN suffix
                symbol = f"{raw}.TO" if raw and ".TO" not in raw else raw
                results.append({
                    "symbol": symbol,
                    "name": str(r.get("Company", "")),
                    "gics_sector": str(r.get("Sector", "")),
                    "gics_sub_industry": "",
                    "source_index": "S&P/TSX 60",
                })
            return results
    return []


def _parse_hangseng(html: str) -> list[dict]:
    tables = pd.read_html(StringIO(html))
    for t in tables:
        if "Ticker" in t.columns and len(t) >= 50:
            results = []
            for _, r in t.iterrows():
                raw = str(r.get("Ticker", ""))
                symbol = _convert_hk_ticker(raw)
                if not symbol:
                    continue
                results.append({
                    "symbol": symbol,
                    "name": str(r.get("Name", "")),
                    "gics_sector": str(r.get("Sub-index", "")),
                    "gics_sub_industry": "",
                    "source_index": "Hang Seng",
                })
            return results
    return []


def _convert_hk_ticker(raw: str) -> str:
    """Convert 'SEHK: 5' or 'SEHK:\\xa05' to '0005.HK'."""
    # Extract digits from "SEHK: XXXX" format
    cleaned = raw.replace("\xa0", " ")
    match = re.search(r"(\d+)", cleaned)
    if match:
        num = match.group(1)
        return f"{int(num):04d}.HK"
    return ""


# ── Index registry ─────────────────────────────────────────────

_INDICES = [
    (
        "S&P 500",
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        _parse_sp500,
    ),
    (
        "Euro STOXX 50",
        "https://en.wikipedia.org/wiki/EURO_STOXX_50",
        _parse_euro_stoxx50,
    ),
    (
        "CAC 40",
        "https://en.wikipedia.org/wiki/CAC_40",
        _parse_cac40,
    ),
    (
        "FTSE 100",
        "https://en.wikipedia.org/wiki/FTSE_100_Index",
        _parse_ftse100,
    ),
    (
        "S&P/TSX 60",
        "https://en.wikipedia.org/wiki/S%26P/TSX_60",
        _parse_tsx60,
    ),
    (
        "Hang Seng",
        "https://en.wikipedia.org/wiki/Hang_Seng_Index",
        _parse_hangseng,
    ),
]


# ── Public API ─────────────────────────────────────────────────


def fetch_global_universe() -> list[dict]:
    """Fetch all index constituents. Deduplicates by symbol.

    Returns combined list of standardised dicts.
    Gracefully skips indices that fail (403, timeout, etc.).
    """
    seen = set()
    combined = []

    for name, url, parser in _INDICES:
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
            if resp.status_code != 200:
                logger.warning(
                    "%s fetch returned HTTP %d — skipping",
                    name, resp.status_code,
                )
                continue

            entries = parser(resp.text)
            added = 0
            for entry in entries:
                sym = entry["symbol"].upper()
                if sym and sym not in seen:
                    seen.add(sym)
                    combined.append(entry)
                    added += 1

            logger.info("%s: %d constituents added", name, added)

        except Exception as exc:
            logger.warning("%s fetch failed: %s — skipping", name, exc)

    return combined
