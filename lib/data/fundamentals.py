"""
Fundamentals middleware — company info, ratios, and financial statements.

This layer:
1. Checks cache first
2. Calls provider if needed
3. Stores result in cache
4. Converts raw data into Company model
"""

import logging
from typing import Optional, Tuple

from lib import cache
from lib.data.providers import yahoo
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
