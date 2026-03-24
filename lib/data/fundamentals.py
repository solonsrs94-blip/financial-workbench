"""
Fundamentals middleware — company info, ratios, and financial statements.

This layer:
1. Checks cache first
2. Calls provider if needed
3. Stores result in cache
4. Converts raw data into Company model
"""

from typing import Optional, Tuple

from lib import cache
from lib.data.providers import yahoo
from models.company import Company, CompanyInfo, CompanyPrice, CompanyRatios


def get_company(
    ticker: str,
    force_refresh: bool = False,
) -> Tuple[Optional[Company], str]:
    """
    Get complete company data.

    Returns:
        (Company or None, status)
        status: "fresh", "stale", or "error"
    """
    ticker = ticker.upper().strip()

    info, info_status = _get_company_info(ticker, force_refresh)
    price_data, price_status = _get_price_data(ticker, force_refresh)
    ratios_data, ratios_status = _get_ratios(ticker, force_refresh)

    if info is None:
        return None, "error"

    # Build Company model
    company_info = CompanyInfo(
        ticker=info.get("ticker", ticker),
        name=info.get("name", ticker),
        sector=info.get("sector", ""),
        industry=info.get("industry", ""),
        country=info.get("country", ""),
        currency=info.get("currency", "USD"),
        exchange=info.get("exchange", ""),
        website=info.get("website", ""),
        description=info.get("description", ""),
        employees=info.get("employees"),
    )

    company_price = CompanyPrice()
    if price_data:
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
        )

    company_ratios = CompanyRatios()
    if ratios_data:
        company_ratios = CompanyRatios(**{
            k: v for k, v in ratios_data.items()
            if hasattr(CompanyRatios, k)
        })

    company = Company(
        info=company_info,
        price=company_price,
        ratios=company_ratios,
    )

    # Determine overall status
    statuses = [info_status, price_status, ratios_status]
    if "error" in statuses and "fresh" not in statuses:
        overall = "error"
    elif "stale" in statuses:
        overall = "stale"
    else:
        overall = "fresh"

    return company, overall


def _get_company_info(
    ticker: str, force_refresh: bool
) -> Tuple[Optional[dict], str]:
    """Fetch company info with cache."""
    cache_key = f"yahoo:{ticker}:info"

    if not force_refresh:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached, "fresh"

    data = yahoo.fetch_company_info(ticker)
    if data is not None:
        cache.store(cache_key, data, provider="yahoo", ttl_key="company_info")
        return data, "fresh"

    stale = cache.get_stale(cache_key)
    if stale is not None:
        return stale, "stale"

    return None, "error"


def _get_price_data(
    ticker: str, force_refresh: bool
) -> Tuple[Optional[dict], str]:
    """Fetch price data with cache."""
    cache_key = f"yahoo:{ticker}:price"

    if not force_refresh:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached, "fresh"

    data = yahoo.fetch_price_data(ticker)
    if data is not None:
        cache.store(cache_key, data, provider="yahoo", ttl_key="ratios")
        return data, "fresh"

    stale = cache.get_stale(cache_key)
    if stale is not None:
        return stale, "stale"

    return None, "error"


def _get_ratios(
    ticker: str, force_refresh: bool
) -> Tuple[Optional[dict], str]:
    """Fetch financial ratios with cache."""
    cache_key = f"yahoo:{ticker}:ratios"

    if not force_refresh:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached, "fresh"

    data = yahoo.fetch_ratios(ticker)
    if data is not None:
        cache.store(cache_key, data, provider="yahoo", ttl_key="ratios")
        return data, "fresh"

    stale = cache.get_stale(cache_key)
    if stale is not None:
        return stale, "stale"

    return None, "error"
