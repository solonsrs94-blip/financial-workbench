"""
Valuation data middleware — fetches and caches valuation-specific data.

All functions follow: check cache → fetch → store → fallback to stale → default.
"""

import logging
from typing import Optional, Tuple
from lib import cache
from lib.data.providers import yahoo
from lib.data.providers import yahoo_valuation
from lib.data.providers import damodaran as dam_provider
from lib.data.providers import peer_beta as peer_provider

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


# ── Damodaran middleware ──────────────────────────────────────────


def get_erp() -> Optional[float]:
    """Implied Equity Risk Premium from Damodaran (cached 30d)."""
    return dam_provider.fetch_erp()


def get_crp(country: str) -> Optional[float]:
    """Country Risk Premium from Damodaran (cached 30d)."""
    return dam_provider.fetch_crp(country)


def get_spread(icr: float, firm_type: str = "small"):
    """Default spread lookup from Damodaran (cached 30d)."""
    return dam_provider.fetch_spread(icr, firm_type)


def get_industry_beta(industry: str, region: str = "us"):
    """Industry beta from Damodaran (cached 30d)."""
    return dam_provider.fetch_industry_beta(industry, region)


# ── Peer beta middleware ─────────────────────────────────────────


def get_suggested_peers(ticker: str, max_peers: int = 8) -> list[str]:
    """Yahoo recommended peers for a ticker."""
    return peer_provider.fetch_suggested_peers(ticker, max_peers)


def get_peer_data(tickers: list[str]) -> list[dict]:
    """Beta, D/E, tax rate for a list of peer tickers."""
    return peer_provider.fetch_peer_data(tickers)
