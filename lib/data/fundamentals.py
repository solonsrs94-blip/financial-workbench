"""
Fundamentals middleware — company info, ratios, and financial statements.

This layer:
1. Checks cache first
2. Calls provider if needed
3. Stores result in cache
4. Converts raw data into Company model
"""

import logging
import pandas as pd
from typing import Optional, Tuple

from lib import cache
from lib.data.providers import yahoo
from lib.data.serialization import serialize_df_dict, restore_df_dict
from models.company import Company, CompanyInfo, CompanyPrice, CompanyRatios

logger = logging.getLogger(__name__)


def get_company(
    ticker: str,
    force_refresh: bool = False,
) -> Tuple[Optional[Company], str]:
    """
    Get complete company data in ONE API call.

    Returns:
        (Company or None, status)
        status: "fresh", "stale", or "error"
    """
    ticker = ticker.upper().strip()
    if not ticker:
        return None, "error"

    cache_key = f"yahoo:{ticker}:all_info"

    # Check cache first
    if not force_refresh:
        cached = cache.get(cache_key)
        if cached is not None:
            return _build_company(cached), "fresh"

    # Fetch all info in one API call
    data = yahoo.fetch_all_info(ticker)

    if data is not None:
        cache.store(cache_key, data, provider="yahoo", ttl_key="ratios")
        return _build_company(data), "fresh"

    # API failed — try stale cache
    stale = cache.get_stale(cache_key)
    if stale is not None:
        return _build_company(stale), "stale"

    return None, "error"


def _build_company(data: dict) -> Company:
    """Build Company model from combined info/price/ratios dict."""
    info_data = data.get("info", {})
    price_data = data.get("price", {})
    ratios_data = data.get("ratios", {})

    company_info = CompanyInfo(
        ticker=info_data.get("ticker", ""),
        name=info_data.get("name", ""),
        sector=info_data.get("sector", ""),
        industry=info_data.get("industry", ""),
        country=info_data.get("country", ""),
        currency=info_data.get("currency", "USD"),
        exchange=info_data.get("exchange", ""),
        website=info_data.get("website", ""),
        description=info_data.get("description", ""),
        employees=info_data.get("employees"),
    )

    company_price = CompanyPrice(
        price=price_data.get("price"),
        change=price_data.get("change"),
        change_pct=price_data.get("change_pct"),
        market_cap=price_data.get("market_cap"),
        volume=price_data.get("volume"),
        avg_volume=price_data.get("avg_volume"),
        high_52w=price_data.get("high_52w"),
        low_52w=price_data.get("low_52w"),
        beta=price_data.get("beta"),
        target_mean=price_data.get("target_mean"),
        target_median=price_data.get("target_median"),
        target_high=price_data.get("target_high"),
        target_low=price_data.get("target_low"),
        analyst_rating=price_data.get("analyst_rating"),
        analyst_count=price_data.get("analyst_count"),
        dividend_rate=price_data.get("dividend_rate"),
        ex_dividend_date=price_data.get("ex_dividend_date"),
        next_earnings_date=price_data.get("next_earnings_date"),
    )

    company_ratios = CompanyRatios(**{
        k: v for k, v in ratios_data.items()
        if hasattr(CompanyRatios, k)
    })

    return Company(
        info=company_info,
        price=company_price,
        ratios=company_ratios,
    )


# --- Middleware for additional data types ---

def get_financials(
    ticker: str, force_refresh: bool = False,
) -> Tuple[Optional[dict], str]:
    """Get financial statements with cache."""
    ticker = ticker.upper().strip()
    cache_key = f"yahoo:{ticker}:financials"

    if not force_refresh:
        cached = cache.get(cache_key)
        if cached is not None:
            return restore_df_dict(cached), "fresh"

    data = yahoo.fetch_financials(ticker)
    if data is not None:
        cache.store(cache_key, serialize_df_dict(data), provider="yahoo", ttl_key="financials")
        return data, "fresh"

    stale = cache.get_stale(cache_key)
    if stale is not None:
        return restore_df_dict(stale), "stale"

    return None, "error"


def get_holders(
    ticker: str, force_refresh: bool = False,
) -> Tuple[Optional[dict], str]:
    """Get institutional holders and insider transactions with cache."""
    ticker = ticker.upper().strip()
    cache_key = f"yahoo:{ticker}:holders"

    if not force_refresh:
        cached = cache.get(cache_key)
        if cached is not None:
            return restore_df_dict(cached), "fresh"

    data = yahoo.fetch_holders(ticker)
    if data is not None:
        cache.store(cache_key, serialize_df_dict(data), provider="yahoo", ttl_key="insider")
        return data, "fresh"

    stale = cache.get_stale(cache_key)
    if stale is not None:
        return restore_df_dict(stale), "stale"

    return None, "error"


def get_recommendations(
    ticker: str, force_refresh: bool = False,
) -> Tuple[Optional[pd.DataFrame], str]:
    """Get analyst recommendations with cache."""
    ticker = ticker.upper().strip()
    cache_key = f"yahoo:{ticker}:recommendations"

    if not force_refresh:
        cached = cache.get(cache_key)
        if cached is not None:
            return pd.DataFrame(cached), "fresh"

    data = yahoo.fetch_recommendations(ticker)
    if data is not None:
        cache.store(cache_key, data.to_dict(orient="list"), provider="yahoo", ttl_key="ratios")
        return data, "fresh"

    stale = cache.get_stale(cache_key)
    if stale is not None:
        return pd.DataFrame(stale), "stale"

    return None, "error"


def get_news(
    ticker: str, force_refresh: bool = False,
) -> Tuple[list[dict], str]:
    """Get recent news with cache."""
    ticker = ticker.upper().strip()
    cache_key = f"yahoo:{ticker}:news"

    if not force_refresh:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached, "fresh"

    data = yahoo.fetch_news(ticker)
    if data:
        cache.store(cache_key, data, provider="yahoo", ttl_key="news")
        return data, "fresh"

    stale = cache.get_stale(cache_key)
    if stale is not None:
        return stale, "stale"

    return [], "error"


def get_events(
    ticker: str, force_refresh: bool = False,
) -> Tuple[dict, str]:
    """Get chart events (earnings, dividends, splits) with cache."""
    ticker = ticker.upper().strip()
    cache_key = f"yahoo:{ticker}:events"

    if not force_refresh:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached, "fresh"

    data = yahoo.fetch_events(ticker)
    if data and any(data.values()):
        cache.store(cache_key, data, provider="yahoo", ttl_key="price_daily")
        return data, "fresh"

    stale = cache.get_stale(cache_key)
    if stale is not None:
        return stale, "stale"

    return {"earnings": [], "dividends": [], "splits": []}, "error"
