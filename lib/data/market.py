"""
Market data middleware — price history and market data.

This layer:
1. Checks cache first
2. Calls provider if needed
3. Stores result in cache
4. Returns data (or stale fallback if API fails)
"""

import pandas as pd
from typing import Optional, Tuple

from lib import cache
from lib.data.providers import yahoo


def get_price_history(
    ticker: str,
    period: str = "5y",
    interval: str = "1d",
    force_refresh: bool = False,
) -> Tuple[Optional[pd.DataFrame], str]:
    """
    Get historical price data for a ticker.

    Returns:
        (DataFrame or None, status)
        status: "fresh", "stale", or "error"
    """
    cache_key = f"yahoo:{ticker}:price_history:{period}:{interval}"

    # Check cache first (unless forced refresh)
    if not force_refresh:
        cached = cache.get(cache_key)
        if cached is not None:
            return pd.DataFrame(cached), "fresh"

    # Fetch from provider
    df = yahoo.fetch_price_history(ticker, period, interval)

    if df is not None:
        # Store in cache (convert to dict for JSON serialization)
        cache.store(
            cache_key,
            df.reset_index().to_dict(orient="list"),
            provider="yahoo",
            ttl_key="price_daily",
        )
        return df, "fresh"

    # API failed — try stale cache
    stale = cache.get_stale(cache_key)
    if stale is not None:
        return pd.DataFrame(stale), "stale"

    return None, "error"
