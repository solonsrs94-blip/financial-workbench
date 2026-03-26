"""
Valuation data middleware — fetches and caches valuation-specific data.

All functions follow: check cache → fetch → store → fallback to stale → default.
"""

import logging
from typing import Optional, Tuple
from lib import cache
from lib.data.providers import yahoo
from lib.data.providers import yahoo_valuation

logger = logging.getLogger(__name__)


def get_risk_free_rate(force_refresh: bool = False) -> float:
    """Get 10-year Treasury yield as decimal (e.g. 0.045 = 4.5%)."""
    cache_key = "yahoo:^TNX:yield"

    if not force_refresh:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached.get("rate", 0.04)

    data = yahoo.fetch_all_info("^TNX")
    if data and data.get("price", {}).get("price"):
        rate = data["price"]["price"] / 100
        cache.store(cache_key, {"rate": rate}, provider="yahoo", ttl_key="price_daily")
        return rate

    stale = cache.get_stale(cache_key)
    if stale is not None:
        return stale.get("rate", 0.04)
    return 0.04


def get_valuation_data(
    ticker: str, force_refresh: bool = False,
) -> Tuple[Optional[dict], str]:
    """Get detailed financials for valuation (BS, CF, IS details)."""
    cache_key = f"yahoo:{ticker}:valuation_data"

    if not force_refresh:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached, "fresh"

    data = yahoo_valuation.fetch_valuation_data(ticker)
    if data is not None:
        cache.store(cache_key, data, provider="yahoo", ttl_key="financials")
        return data, "fresh"

    stale = cache.get_stale(cache_key)
    if stale is not None:
        return stale, "stale"
    return None, "error"


def get_analyst_estimates(
    ticker: str, force_refresh: bool = False,
) -> Tuple[Optional[dict], str]:
    """Get analyst consensus estimates."""
    cache_key = f"yahoo:{ticker}:analyst_estimates"

    if not force_refresh:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached, "fresh"

    data = yahoo_valuation.fetch_analyst_estimates(ticker)
    if data is not None:
        cache.store(cache_key, data, provider="yahoo", ttl_key="ratios")
        return data, "fresh"

    stale = cache.get_stale(cache_key)
    if stale is not None:
        return stale, "stale"
    return None, "error"
