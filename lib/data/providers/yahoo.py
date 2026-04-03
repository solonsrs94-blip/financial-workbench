"""
Yahoo Finance provider — fetches data via yfinance.
No API key needed. This is the primary data source.

RULE: This file only fetches and returns raw data as dicts.
It does NOT know about models, cache, or UI.
"""

import logging
import yfinance as yf
import pandas as pd
from typing import Optional

logger = logging.getLogger(__name__)


def _get_info(ticker: str) -> Optional[dict]:
    """Fetch .info once — shared by info/price/ratios functions."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info or len(info) < 5:
            logger.warning("No info data for %s", ticker)
            return None
        return info
    except Exception as e:
        logger.error("Failed to fetch info for %s: %s", ticker, e)
        return None


def search_companies(query: str, max_results: int = 10) -> list[dict]:
    """Search for companies by name or ticker."""
    try:
        s = yf.Search(query)
        results = []
        for q in s.quotes[:max_results]:
            if q.get("quoteType") == "EQUITY":
                results.append({
                    "ticker": q.get("symbol", ""),
                    "name": q.get("longname", q.get("shortname", "")),
                    "exchange": q.get("exchDisp", q.get("exchange", "")),
                    "sector": q.get("sectorDisp", q.get("sector", "")),
                    "industry": q.get("industryDisp", q.get("industry", "")),
                })
        return results
    except Exception as e:
        logger.error("Search failed for '%s': %s", query, e)
        return []


def fetch_all_info(ticker: str) -> Optional[dict]:
    """Fetch company info, price data, and ratios in ONE API call.
    Returns a dict with keys: 'info', 'price', 'ratios'."""
    info = _get_info(ticker)
    if info is None:
        return None

    price = info.get("currentPrice", info.get("previousClose"))
    prev_close = info.get("previousClose")
    change = None
    change_pct = None
    if price and prev_close and prev_close > 0:
        change = price - prev_close
        change_pct = (change / prev_close) * 100

    div_yield = info.get("dividendYield")
    if div_yield is not None:
        div_yield = div_yield / 100

    # Convert Unix timestamps to ISO date strings
    from datetime import datetime

    def _ts_to_date(ts):
        if ts:
            try:
                return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
            except (OSError, ValueError):
                return None
        return None

    return {
        "info": {
            "ticker": ticker.upper(),
            "name": info.get("longName", ticker),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "country": info.get("country", ""),
            "currency": info.get("currency", "USD"),
            "exchange": info.get("exchange", ""),
            "website": info.get("website", ""),
            "description": info.get("longBusinessSummary", ""),
            "employees": info.get("fullTimeEmployees"),
        },
        "price": {
            "price": price,
            "change": change,
            "change_pct": change_pct,
            "market_cap": info.get("marketCap"),
            "volume": info.get("volume"),
            "avg_volume": info.get("averageVolume"),
            "high_52w": info.get("fiftyTwoWeekHigh"),
            "low_52w": info.get("fiftyTwoWeekLow"),
            "beta": info.get("beta"),
            "target_mean": info.get("targetMeanPrice"),
            "target_median": info.get("targetMedianPrice"),
            "target_high": info.get("targetHighPrice"),
            "target_low": info.get("targetLowPrice"),
            "analyst_rating": info.get("averageAnalystRating"),
            "analyst_count": info.get("numberOfAnalystOpinions"),
            "dividend_rate": info.get("dividendRate"),
            "ex_dividend_date": _ts_to_date(info.get("exDividendDate")),
            "next_earnings_date": _ts_to_date(info.get("earningsTimestampStart")),
        },
        "ratios": {
            "pe_trailing": info.get("trailingPE"),
            "pe_forward": info.get("forwardPE"),
            "peg": info.get("pegRatio"),
            "pb": info.get("priceToBook"),
            "ps": info.get("priceToSalesTrailing12Months"),
            "ev_ebitda": info.get("enterpriseToEbitda"),
            "ev_revenue": info.get("enterpriseToRevenue"),
            "dividend_yield": div_yield,
            "payout_ratio": info.get("payoutRatio"),
            "roe": info.get("returnOnEquity"),
            "roa": info.get("returnOnAssets"),
            "profit_margin": info.get("profitMargins"),
            "operating_margin": info.get("operatingMargins"),
            "gross_margin": info.get("grossMargins"),
            "debt_to_equity": info.get("debtToEquity"),
            "current_ratio": info.get("currentRatio"),
            "quick_ratio": info.get("quickRatio"),
            "eps_trailing": info.get("trailingEps"),
            "eps_forward": info.get("forwardEps"),
            "revenue_growth": info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsGrowth"),
            "short_pct_float": info.get("shortPercentOfFloat"),
            "shares_outstanding": (info.get("impliedSharesOutstanding")
                                    or info.get("sharesOutstanding")),
        },
    }


def fetch_price_history(
    ticker: str, period: str = "5y", interval: str = "1d",
) -> Optional[pd.DataFrame]:
    """Fetch historical price data."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)
        if hist.empty:
            return None
        hist.index = hist.index.tz_localize(None)
        return hist
    except Exception as e:
        logger.error("Price history failed for %s: %s", ticker, e)
        return None


# Financial statements, holders, news, events — see yahoo_financials.py
from lib.data.providers.yahoo_financials import (  # noqa: F401 — re-export
    fetch_financials,
    fetch_holders,
    fetch_recommendations,
    fetch_news,
    fetch_events,
)
