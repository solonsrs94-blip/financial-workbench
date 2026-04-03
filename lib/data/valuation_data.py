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
from lib.data.providers import comps_peers as comps_provider
from lib.data.providers import comps_data as comps_data_provider
from lib.data.providers import peer_universe as universe_provider
from lib.data.providers import historical_multiples as hist_mult_provider

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


# ── Comps peer middleware ──────────────────────────────────────


def get_finnhub_peers(ticker: str) -> list[str]:
    """Finnhub peer tickers for comps (seed list)."""
    cache_key = f"finnhub:{ticker}:comps_peers"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached.get("peers", [])

    peers = comps_provider.fetch_finnhub_peers(ticker)
    if peers:
        cache.store(
            cache_key, {"peers": peers},
            provider="finnhub", ttl_key="ratios",
        )
    return peers


def get_sp500_universe() -> list[dict]:
    """S&P 500 constituents with GICS classification (cached 30d).

    DEPRECATED: Use get_peer_universe() for global coverage.
    Kept for backward compatibility.
    """
    return [
        e for e in get_peer_universe()
        if e.get("source_index") == "S&P 500"
    ]


def filter_peer_universe(
    universe: list[dict],
    target_ticker: str,
    target_industry: str,
    target_market_cap: float,
) -> list[str]:
    """Filter global peer universe by industry + market cap band."""
    return comps_provider.filter_universe(
        universe, target_ticker, target_industry, target_market_cap,
    )


def get_peer_universe() -> list[dict]:
    """Global peer universe — S&P 500 + Euro STOXX 50 + CAC 40 +
    FTSE 100 + S&P/TSX 60 + Hang Seng (cached 30d)."""
    cache_key = "wikipedia:global_universe:constituents"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached.get("constituents", [])

    data = universe_provider.fetch_global_universe()
    if data:
        cache.store(
            cache_key, {"constituents": data},
            provider="wikipedia", ttl_key="damodaran",
        )
    return data


def get_comps_candidate_info(ticker: str) -> dict | None:
    """Comps-relevant info for a single candidate ticker (cached 24h)."""
    cache_key = f"yahoo:{ticker}:comps_info"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    data = comps_provider.fetch_candidate_info(ticker)
    if data:
        cache.store(cache_key, data, provider="yahoo", ttl_key="ratios")
    return data


# ── Comps table data middleware ────────────────────────────────


def get_comps_row(ticker: str, force_refresh: bool = False) -> dict | None:
    """Full comps multiples data for a single ticker (cached 24h)."""
    cache_key = f"yahoo:{ticker}:comps_row"

    if not force_refresh:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

    data = comps_data_provider.fetch_comps_row(ticker)
    if data:
        cache.store(cache_key, data, provider="yahoo", ttl_key="ratios")
        return data

    stale = cache.get_stale(cache_key)
    if stale is not None:
        return stale
    return None


# ── Historical multiples middleware ───────────────────────────


def get_historical_multiples(
    ticker: str, period_years: int = 3, is_financial: bool = False,
) -> dict:
    """Fetch historical TTM multiples (yfinance only). No caching here
    — provider is fast enough and data includes a large DataFrame that
    doesn't serialize well to SQLite. Session-state caching is done
    at the page level instead.
    """
    return hist_mult_provider.get_historical_multiples(
        ticker, period_years, is_financial,
    )
