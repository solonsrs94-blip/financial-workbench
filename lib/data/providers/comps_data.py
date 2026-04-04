"""
Comps data provider — fetches multiples-relevant data for comps table.

Per ticker: info (market data + trailing), quarterly_financials (EBIT),
revenue_estimate (forward revenue), FMP (forward EBITDA, optional).

No Streamlit imports. Returns raw data only.
"""

import logging
from typing import Optional

import requests
import yfinance as yf

logger = logging.getLogger(__name__)

_FMP_KEY = "nhFksOQCl83oEeFQgrjaNL99Hubzbb0z"
_TIMEOUT = 8


def _clean_numeric(val):
    """Ensure a value is a real finite float, or None.

    yfinance occasionally returns 'Infinity' as a string for PE etc.
    """
    if val is None:
        return None
    if isinstance(val, str):
        return None
    try:
        f = float(val)
        if not __import__("math").isfinite(f):
            return None
        return f
    except (TypeError, ValueError):
        return None


def fetch_comps_row(ticker: str) -> Optional[dict]:
    """Fetch all comps-relevant data for a single ticker.

    Returns dict with market data, trailing financials, pre-computed
    multiples, and forward estimates. Returns None if critical data missing.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info or len(info) < 5:
            return None

        mcap = info.get("marketCap")
        if not mcap:
            return None

        ev = info.get("enterpriseValue")
        revenue = info.get("totalRevenue")
        ebitda = info.get("ebitda")

        # EBIT: try quarterly_financials, fallback to rev * margin
        ebit = _get_ttm_ebit(stock, info)

        # Forward revenue from analyst estimates
        fwd_revenue = _get_forward_revenue(stock)

        # Forward EBITDA from FMP (best-effort)
        fwd_ebitda = _get_fmp_forward_ebitda(ticker)

        # Compute derived multiples
        ev_ebit = _safe_multiple(ev, ebit)
        fwd_ev_rev = _safe_multiple(ev, fwd_revenue)
        fwd_ev_ebitda = _safe_multiple(ev, fwd_ebitda)

        # Financial company fields (book value, tangible book, div yield)
        book_val_ps = info.get("bookValue")  # per share
        tbv_ps = _get_tangible_book_ps(stock, info)
        div_yield = info.get("dividendYield")
        # Yahoo dividendYield is already-percent (2.04 = 2.04%)
        if div_yield is not None:
            div_yield = div_yield / 100  # normalize to decimal
        p_book = info.get("priceToBook")
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        p_tbv = (price / tbv_ps) if price and tbv_ps and tbv_ps > 0 else None

        return {
            "ticker": ticker.upper(),
            "name": info.get("shortName") or info.get("longName") or ticker,
            "country": info.get("country", ""),
            "industry": info.get("industry", ""),
            "currency": info.get("currency", "USD"),
            # Market data
            "price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "shares_outstanding": info.get("sharesOutstanding"),
            "market_cap": mcap,
            "enterprise_value": ev,
            # Trailing financials (TTM)
            "revenue": revenue,
            "ebitda": ebitda,
            "ebit": ebit,
            "net_income": info.get("netIncomeToCommon"),
            "eps": _clean_numeric(info.get("trailingEps")),
            # Debt / cash
            "total_debt": info.get("totalDebt"),
            "cash": info.get("totalCash"),
            # Pre-computed trailing multiples from Yahoo
            "trailing_pe": _clean_numeric(info.get("trailingPE")),
            "forward_pe": _clean_numeric(info.get("forwardPE")),
            "ev_revenue": _clean_numeric(info.get("enterpriseToRevenue")),
            "ev_ebitda": _clean_numeric(info.get("enterpriseToEbitda")),
            # Calculated multiples
            "ev_ebit": ev_ebit,
            # Forward estimates
            "fwd_revenue": fwd_revenue,
            "fwd_ebitda": fwd_ebitda,
            "fwd_ev_revenue": fwd_ev_rev,
            "fwd_ev_ebitda": fwd_ev_ebitda,
            # Financial company fields
            "book_value_ps": book_val_ps,
            "tangible_book_ps": tbv_ps,
            "price_to_book": _clean_numeric(p_book),
            "price_to_tbv": p_tbv,
            "dividend_yield": div_yield,
            "dividend_rate": info.get("dividendRate"),
        }
    except Exception as exc:
        logger.warning("Comps row fetch failed for %s: %s", ticker, exc)
    return None


# ── EBIT (TTM from quarterly financials) ───────────────────────


def _get_ttm_ebit(stock, info: dict) -> Optional[float]:
    """Get TTM EBIT from quarterly financials, fallback to margin calc."""
    try:
        qf = stock.quarterly_financials
        if qf is not None and not qf.empty and "Operating Income" in qf.index:
            vals = qf.loc["Operating Income"].head(4).dropna()
            if len(vals) >= 4:
                return float(vals.sum())
    except Exception:
        pass

    # Fallback: revenue * operating margin
    rev = info.get("totalRevenue")
    margin = info.get("operatingMargins")
    if rev and margin:
        return rev * margin
    return None


# ── Forward revenue ────────────────────────────────────────────


def _get_forward_revenue(stock) -> Optional[float]:
    """Get next-year consensus revenue estimate from yfinance."""
    try:
        rev_est = getattr(stock, "revenue_estimate", None)
        if rev_est is None or rev_est.empty:
            return None
        if "avg" not in rev_est.columns:
            return None
        # Find the +1Y row (second row, or first with year > current)
        if len(rev_est) >= 2:
            val = rev_est.iloc[1]["avg"]
        else:
            val = rev_est.iloc[0]["avg"]
        if val is not None and str(val) != "nan":
            return float(val)
    except Exception:
        pass
    return None


# ── FMP forward EBITDA (optional) ──────────────────────────────


def _get_fmp_forward_ebitda(ticker: str) -> Optional[float]:
    """Best-effort forward EBITDA from FMP free tier."""
    url = (
        f"https://financialmodelingprep.com/stable/analyst-estimates"
        f"?symbol={ticker}&limit=2&apikey={_FMP_KEY}"
    )
    try:
        resp = requests.get(url, timeout=_TIMEOUT)
        if resp.status_code != 200:
            return None
        data = resp.json()
        if data and len(data) > 0:
            val = data[0].get("estimatedEbitdaAvg")
            if val and val > 0:
                return float(val)
    except Exception:
        pass
    return None


# ── Tangible book value ────────────────────────────────────────


def _get_tangible_book_ps(stock, info: dict) -> Optional[float]:
    """Get tangible book value per share from balance sheet."""
    shares = info.get("sharesOutstanding") or 1
    try:
        bs = stock.balance_sheet
        if bs is not None and not bs.empty:
            if "Tangible Book Value" in bs.index:
                tbv = float(bs.loc["Tangible Book Value"].iloc[0])
                if tbv and shares:
                    return tbv / shares
    except Exception:
        pass
    return None


# ── Helpers ────────────────────────────────────────────────────


def _safe_multiple(numerator, denominator) -> Optional[float]:
    """Compute multiple, returning None if invalid."""
    if numerator is None or denominator is None:
        return None
    if denominator <= 0:
        return None
    return numerator / denominator
