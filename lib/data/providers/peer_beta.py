"""
Peer beta provider — fetches suggested peers and their beta data.

Uses Yahoo recommended symbols API for peer suggestions,
then fetches beta, D/E, tax rate for each via yfinance.
No Streamlit imports. Returns raw data only.
"""

import logging
from typing import Optional

import requests
import yfinance as yf

logger = logging.getLogger(__name__)

_TIMEOUT = 10
_YF_HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_suggested_peers(ticker: str, max_peers: int = 8) -> list[str]:
    """Fetch Yahoo's recommended/similar symbols for a ticker.

    Uses the v6/recommendationsbysymbol API endpoint.
    Returns list of ticker strings, or empty list on failure.
    """
    url = (
        f"https://query2.finance.yahoo.com/v6/finance/"
        f"recommendationsbysymbol/{ticker}"
    )
    try:
        resp = requests.get(url, headers=_YF_HEADERS, timeout=_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("finance", {}).get("result", [])
        if results:
            symbols = results[0].get("recommendedSymbols", [])
            return [s["symbol"] for s in symbols[:max_peers]]
    except Exception as exc:
        logger.warning("Peer suggestions failed for %s: %s", ticker, exc)
    return []


def fetch_peer_data(tickers: list[str]) -> list[dict]:
    """Fetch beta, D/E ratio, effective tax rate for a list of tickers.

    Returns list of dicts with keys: ticker, beta, de_ratio, tax_rate,
    market_cap. Skips tickers with missing critical data.
    """
    results = []
    for t in tickers:
        try:
            info = yf.Ticker(t).info
            if not info or len(info) < 5:
                continue

            beta = info.get("beta")
            de_raw = info.get("debtToEquity")  # Yahoo returns as pct
            mcap = info.get("marketCap")

            if beta is None or beta <= 0:
                continue

            de_ratio = de_raw / 100 if de_raw and de_raw > 0 else 0.0
            tax_rate = _estimate_tax_rate(t)

            results.append({
                "ticker": t.upper(),
                "beta": beta,
                "de_ratio": de_ratio,
                "tax_rate": tax_rate,
                "market_cap": mcap or 0,
            })
        except Exception as exc:
            logger.debug("Peer data failed for %s: %s", t, exc)
            continue

    return results


def _estimate_tax_rate(ticker: str) -> Optional[float]:
    """Estimate effective tax rate from income statement.

    Returns ``None`` when data is unavailable — callers must surface
    a warning instead of applying a hardcoded fallback.
    """
    try:
        inc = yf.Ticker(ticker).income_stmt
        if inc is None or inc.empty:
            return None

        def _val(row, col=0):
            if row in inc.index:
                v = inc.iloc[inc.index.get_loc(row), col]
                if v is not None and str(v) != "nan":
                    return float(v)
            return None

        tax = _val("Tax Provision")
        pretax = _val("Pretax Income")
        if tax and pretax and pretax > 0:
            rate = abs(tax) / pretax
            if 0 < rate < 0.60:
                return rate
    except Exception:
        pass
    return None
