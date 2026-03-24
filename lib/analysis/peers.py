"""
Peer comparison — find and compare companies in the same industry.
"""

import logging
import yfinance as yf
import pandas as pd
from typing import Optional
from yfinance.screener import EquityQuery, screen as yf_screen

logger = logging.getLogger(__name__)


def fetch_peers(sector: str, industry: str, exclude_ticker: str) -> list[dict]:
    """Fetch peer companies in the same industry with key metrics.
    All values converted to USD."""
    try:
        exclude_stock = yf.Ticker(exclude_ticker)
        exclude_name = (exclude_stock.info or {}).get("longName", "").lower()

        q = EquityQuery("and", [
            EquityQuery("eq", ["sector", sector]),
            EquityQuery("eq", ["industry", industry]),
            EquityQuery("gt", ["intradaymarketcap", 1_000_000_000]),
        ])
        result = yf_screen(q, count=30, sortField="intradaymarketcap", sortAsc=False)

        if not result or "quotes" not in result:
            return []

        seen_names = set()
        tickers = []
        for r in result["quotes"]:
            symbol = r.get("symbol", "")
            name = r.get("longName", r.get("shortName", "")).lower()

            if exclude_name and exclude_name in name:
                continue

            first_word = name.split(" ")[0] if name else ""
            if first_word in seen_names:
                continue

            seen_names.add(first_word)
            tickers.append(symbol)

            if len(tickers) >= 10:
                break

        usd_rates = {}
        peers = []
        for t in tickers:
            try:
                stock = yf.Ticker(t)
                info = stock.info
                if not info or len(info) < 5:
                    continue

                currency = info.get("currency", "USD")
                price = info.get("currentPrice", info.get("previousClose"))
                mcap = info.get("marketCap")

                if currency != "USD" and price is not None:
                    rate = _get_usd_rate(currency, usd_rates)
                    if rate:
                        price = price / rate
                        if mcap is not None:
                            mcap = mcap / rate

                div_yield = info.get("dividendYield")
                if div_yield is not None:
                    div_yield = div_yield / 100

                peers.append({
                    "ticker": t,
                    "name": info.get("longName", info.get("shortName", t)),
                    "price": price,
                    "market_cap": mcap,
                    "pe": info.get("trailingPE"),
                    "pb": info.get("priceToBook"),
                    "profit_margin": info.get("profitMargins"),
                    "roe": info.get("returnOnEquity"),
                    "div_yield": div_yield,
                })
            except Exception:
                continue

            if len(peers) >= 6:
                break

        return peers
    except Exception as e:
        logger.error("Peer fetch failed: %s", e)
        return []


def _get_usd_rate(currency: str, rate_cache: dict) -> float:
    """Get exchange rate: how many units of currency per 1 USD."""
    if currency == "USD":
        return 1.0
    if currency in rate_cache:
        return rate_cache[currency]
    try:
        pair = yf.Ticker(f"{currency}=X")
        rate = pair.info.get("previousClose", None)
        if rate:
            rate_cache[currency] = rate
            return rate
    except Exception:
        pass
    return 0.0
