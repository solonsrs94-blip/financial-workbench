"""
Comps peer provider — Finnhub peers + S&P 500 universe + candidate info.

Two-layer peer candidate generation:
  Layer 1: Finnhub peers API (seed list, ~10 tickers)
  Layer 2: S&P 500 universe filtered by industry + market cap band

No Streamlit imports. Returns raw data only.
"""

import logging
from io import StringIO
from typing import Optional

import pandas as pd
import requests
import yfinance as yf

logger = logging.getLogger(__name__)

_TIMEOUT = 10
from config.settings import FINNHUB_API_KEY

_FINNHUB_KEY = FINNHUB_API_KEY
_SP500_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


# ── Layer 1: Finnhub peers ─────────────────────────────────────


def fetch_finnhub_peers(ticker: str) -> list[str]:
    """Fetch peer tickers from Finnhub stock/peers endpoint.

    Returns list of ticker strings, or empty list on failure.
    Free tier, no rate limit issues at this volume.
    """
    url = (
        f"https://finnhub.io/api/v1/stock/peers"
        f"?symbol={ticker}&token={_FINNHUB_KEY}"
    )
    try:
        resp = requests.get(url, timeout=_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            # Remove target itself from the list
            return [t for t in data if t != ticker]
    except Exception as exc:
        logger.warning("Finnhub peers failed for %s: %s", ticker, exc)
    return []


# ── Layer 2: S&P 500 universe ──────────────────────────────────


def fetch_sp500_constituents() -> list[dict]:
    """Fetch S&P 500 constituents from Wikipedia.

    Returns list of dicts with keys: symbol, name, gics_sector,
    gics_sub_industry. Cached by caller (session_state).
    """
    try:
        resp = requests.get(_SP500_URL, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        tables = pd.read_html(StringIO(resp.text))
        # S&P 500 table is always the first (largest) table
        df = tables[0]
        results = []
        for _, row in df.iterrows():
            results.append({
                "symbol": str(row.get("Symbol", "")).strip(),
                "name": str(row.get("Security", "")),
                "gics_sector": str(row.get("GICS Sector", "")),
                "gics_sub_industry": str(row.get("GICS Sub-Industry", "")),
            })
        return results
    except Exception as exc:
        logger.warning("S&P 500 fetch failed: %s", exc)
    return []


def filter_universe(
    universe: list[dict],
    target_ticker: str,
    target_industry: str,
    target_market_cap: float,
    mcap_low: float = 0.25,
    mcap_high: float = 4.0,
) -> list[str]:
    """Filter global peer universe by industry + market cap band.

    Works with entries from multiple indices (S&P 500, Euro STOXX 50,
    CAC 40, FTSE 100, TSX 60, Hang Seng). Handles entries with
    GICS sub-industry, sector-only, or no classification.

    Matching strategy:
    1. Map target yfinance industry -> matching GICS Sub-Industries
    2. Match entries by GICS sub-industry OR sector
    3. Falls back to broader sector match if <3 matches

    Returns list of ticker symbols (without info data).
    """
    from lib.data.providers.gics_yf_map import YF_TO_GICS

    target_upper = target_ticker.upper()

    # Find target's GICS info if it's in the universe
    target_gics_sub = ""
    target_gics_sector = ""
    for entry in universe:
        if entry["symbol"].upper() == target_upper:
            target_gics_sub = entry["gics_sub_industry"]
            target_gics_sector = entry["gics_sector"]
            break

    # Build set of matching GICS Sub-Industries
    matching_gics_sub = set()
    if target_gics_sub:
        matching_gics_sub.add(target_gics_sub)

    # Use mapping: yfinance industry -> GICS Sub-Industries
    if target_industry and target_industry in YF_TO_GICS:
        for gics in YF_TO_GICS[target_industry]:
            matching_gics_sub.add(gics)

    # Build set of matching GICS Sectors (for sector-only entries)
    matching_sectors = set()
    if target_gics_sector:
        matching_sectors.add(target_gics_sector)
    # Also find sectors that contain any matching sub-industry
    for entry in universe:
        if entry["gics_sub_industry"] in matching_gics_sub:
            matching_sectors.add(entry["gics_sector"])

    # Pass 1: sub-industry match (entries with gics_sub_industry)
    #        + sector match (entries WITHOUT sub-industry, e.g. FTSE/HSI)
    sub_matches = []
    for entry in universe:
        sym = entry["symbol"].upper()
        if sym == target_upper:
            continue
        gics_sub = entry.get("gics_sub_industry", "")
        gics_sector = entry.get("gics_sector", "")
        if gics_sub and gics_sub in matching_gics_sub:
            sub_matches.append(sym)
        elif not gics_sub and gics_sector and gics_sector in matching_sectors:
            sub_matches.append(sym)

    # Pass 2: if too few, broaden to all sector matches
    sector_matches = []
    if len(sub_matches) < 3 and matching_sectors:
        sub_set = set(sub_matches)
        for entry in universe:
            sym = entry["symbol"].upper()
            if sym == target_upper or sym in sub_set:
                continue
            if entry["gics_sector"] in matching_sectors:
                sector_matches.append(sym)

    return sub_matches + sector_matches


# ── Candidate info fetcher ─────────────────────────────────────


def fetch_candidate_info(ticker: str) -> Optional[dict]:
    """Fetch comps-relevant info for a single candidate ticker.

    Returns dict with: ticker, name, country, industry, market_cap,
    revenue, ebitda_margin, gics_sub_industry.
    Returns None if critical data missing.
    """
    try:
        info = yf.Ticker(ticker).info
        if not info or len(info) < 5:
            return None

        mcap = info.get("marketCap")
        if not mcap:
            return None

        return {
            "ticker": ticker.upper(),
            "name": info.get("shortName") or info.get("longName") or ticker,
            "country": info.get("country", ""),
            "industry": info.get("industry", ""),
            "sector": info.get("sector", ""),
            "market_cap": mcap,
            "revenue": info.get("totalRevenue"),
            "ebitda_margin": info.get("ebitdaMargins"),
        }
    except Exception as exc:
        logger.debug("Candidate info failed for %s: %s", ticker, exc)
    return None


def fetch_candidates_batch(tickers: list[str]) -> list[dict]:
    """Fetch info for multiple candidates. Skips failures."""
    results = []
    for t in tickers:
        data = fetch_candidate_info(t)
        if data:
            results.append(data)
    return results
