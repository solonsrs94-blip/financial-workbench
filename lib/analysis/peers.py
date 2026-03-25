"""
Peer comparison — find and compare companies in the same industry.
"""

import logging
import yfinance as yf
import pandas as pd
from typing import Optional
from yfinance.screener import EquityQuery, screen as yf_screen

logger = logging.getLogger(__name__)


# Fallback peers for industries where screener fails to return primary listings
# These are well-known companies in each industry — updated manually
_KNOWN_PEERS = {
    "Internet Content & Information": ["META", "GOOG", "GOOGL", "SNAP", "PINS", "BIDU", "ZIM", "MTCH", "SPOT"],
    "Semiconductors": ["NVDA", "AMD", "INTC", "TSM", "AVGO", "QCOM", "MU", "TXN", "ASML"],
    "Software - Infrastructure": ["MSFT", "ORCL", "CRM", "NOW", "ADBE", "INTU", "SNOW", "PLTR"],
    "Software - Application": ["ADBE", "CRM", "INTU", "NOW", "WDAY", "TEAM", "ZM", "DOCU"],
    "Consumer Electronics": ["AAPL", "SONY", "SSNLF", "LPL", "HEAR"],
    "E-Commerce": ["AMZN", "BABA", "JD", "SHOP", "MELI", "SE", "EBAY", "ETSY"],
    "Social Media": ["META", "SNAP", "PINS", "MTCH", "BMBL"],
}


def _find_peer_tickers(sector: str, industry: str, exclude_ticker: str) -> list[str]:
    """Find peer tickers via screener, filtering duplicates."""
    try:
        exclude_stock = yf.Ticker(exclude_ticker)
        exclude_name = (exclude_stock.info or {}).get("longName", "").lower()
    except Exception:
        exclude_name = ""

    try:
        q = EquityQuery("and", [
            EquityQuery("eq", ["sector", sector]),
            EquityQuery("eq", ["industry", industry]),
            EquityQuery("gt", ["intradaymarketcap", 1_000_000_000]),
        ])
        result = yf_screen(q, count=30, sortField="intradaymarketcap", sortAsc=False)

        if not result or "quotes" not in result:
            return []

        # Suffixes known to give distorted ratios (depositary receipts, foreign listings)
        BAD_SUFFIXES = {".BA", ".CL", ".SN", ".BK", ".MX", ".SA", ".WA", ".IL"}

        seen_names = set()
        tickers = []
        for r in result["quotes"]:
            symbol = r.get("symbol", "")
            name = r.get("longName", r.get("shortName", "")).lower()

            if exclude_name and exclude_name in name:
                continue

            # Skip known-bad foreign listings
            suffix = ""
            if "." in symbol:
                suffix = "." + symbol.split(".", 1)[1]
            if suffix in BAD_SUFFIXES:
                continue

            first_word = name.split(" ")[0] if name else ""
            if first_word in seen_names:
                continue

            seen_names.add(first_word)
            tickers.append(symbol)

            if len(tickers) >= 15:
                break

        return tickers
    except Exception:
        return []


def fetch_peers(sector: str, industry: str, exclude_ticker: str) -> list[dict]:
    """Fetch peer companies in the same industry with key metrics.
    All values converted to USD."""
    try:
        exclude_ticker_upper = exclude_ticker.upper()

        # Strategy 1: Use screener
        tickers = _find_peer_tickers(sector, industry, exclude_ticker_upper)

        # Strategy 2: Always add known peers to improve coverage
        known = _KNOWN_PEERS.get(industry, [])
        for sym in known:
            if sym.upper() != exclude_ticker_upper and sym not in tickers:
                tickers.append(sym)
            if len(tickers) >= 15:
                break

        if not tickers:
            return []

        # Determine target currency
        try:
            target_currency = yf.Ticker(exclude_ticker).info.get("currency", "USD")
        except Exception:
            target_currency = "USD"

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

                # Skip peers where ratios are clearly distorted
                # (foreign listings often have wrong P/E, P/B)
                raw_pe = info.get("trailingPE")
                raw_pb = info.get("priceToBook")
                if raw_pe and (raw_pe < 0 or raw_pe > 1000):
                    raw_pe = None
                if raw_pb and (raw_pb < 0.01 or raw_pb > 1000):
                    continue  # Skip clearly wrong listings

                if currency != "USD" and price is not None:
                    rate = _get_usd_rate(currency, usd_rates)
                    if rate:
                        price = price / rate
                        if mcap is not None:
                            mcap = mcap / rate

                div_yield = info.get("dividendYield")
                if div_yield is not None:
                    div_yield = div_yield / 100

                # Sanity check ratios — reject clearly wrong values
                pe = info.get("trailingPE")
                pb = info.get("priceToBook")
                if pe is not None and (pe < 0 or pe > 1000):
                    pe = None
                if pb is not None and (pb < 0 or pb > 1000):
                    pb = None

                peers.append({
                    "ticker": t,
                    "name": info.get("longName", info.get("shortName", t)),
                    "price": price,
                    "market_cap": mcap,
                    "pe": pe,
                    "pb": pb,
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
