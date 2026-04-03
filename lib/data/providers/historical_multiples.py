"""Historical multiples provider — EDGAR (US, 10+yr) or yfinance
(non-US/fallback, ~3.5yr). No Streamlit imports.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import yfinance as yf

from lib.data.providers.historical_multiples_calc import (
    build_daily_multiples,
    compute_implied_values,
    compute_summary,
    get_mult_keys,
)

logger = logging.getLogger(__name__)

# Module-level caches (persist within Streamlit session)
_financial_cache: dict = {}  # ticker -> (df_q, df_a, df_bs, source)
_price_cache: dict = {}      # ticker -> (prices_df, currency, price)
_daily_cache: dict = {}      # (ticker, is_fin) -> daily_df


# ── Public API ────────────────────────────────────────────────


def get_historical_multiples(
    ticker: str, period_years: int = 3, is_financial: bool = False,
) -> dict:
    """Calculate daily TTM multiples over the requested period.

    For US tickers: tries EDGAR (10+ years), falls back to yfinance.
    For non-US tickers: uses yfinance hybrid (~3.5 years).
    """
    prices, currency, current_price = _get_prices(ticker)
    if prices is None:
        return {"error": "No price history available"}

    df_q, df_a, df_bs, source = _get_financials(ticker)

    n_q = len(df_q) if df_q is not None else 0
    n_a = len(df_a) if df_a is not None else 0
    if n_q < 4 and n_a < 1:
        return {"error": "Insufficient financial data", "quarters": n_q}
    if df_bs is None or df_bs.empty:
        return {"error": "Insufficient balance sheet data", "quarters": 0}

    # Build daily multiples (cached)
    daily_key = (ticker, is_financial)
    if daily_key not in _daily_cache:
        _daily_cache[daily_key] = build_daily_multiples(
            prices, df_q, df_a, df_bs, is_financial,
        )
    daily = _daily_cache[daily_key]

    # Apply period cutoff
    if period_years > 0:
        cutoff = datetime.now() - timedelta(days=period_years * 365)
        daily = daily.loc[daily.index >= cutoff]

    if daily.empty:
        return {"error": "No multiples could be calculated"}

    mult_keys = get_mult_keys(is_financial)
    summary = compute_summary(daily, mult_keys)

    impl_inc = df_q if n_q >= 4 else df_a
    implied = compute_implied_values(
        summary, impl_inc, df_bs, current_price, is_financial,
    )

    return {
        "daily_multiples": daily,
        "summary": summary,
        "implied_values": implied,
        "current_price": current_price,
        "currency": currency,
        "data_start": str(daily.index.min().date()),
        "data_end": str(daily.index.max().date()),
        "quarters_available": n_q,
        "annual_available": n_a,
        "data_source": source,
        "is_financial": is_financial,
    }


# ── Price data (yfinance, always) ────────────────────────────


def _get_prices(ticker: str) -> tuple:
    """Fetch and cache price data. Returns (prices_df, currency, price)."""
    if ticker in _price_cache:
        return _price_cache[ticker]

    stock = yf.Ticker(ticker)
    hist = stock.history(period="max")

    if hist.empty:
        _price_cache[ticker] = (None, "USD", None)
        return None, "USD", None

    info = stock.info or {}
    currency = info.get("currency", "USD")
    current_price = info.get("currentPrice") or info.get(
        "regularMarketPrice",
    )

    prices = hist[["Close"]].copy()
    prices.index = prices.index.tz_localize(None)
    _price_cache[ticker] = (prices, currency, current_price)
    return prices, currency, current_price


# ── Financial data routing ────────────────────────────────────


def _get_financials(ticker: str) -> tuple:
    """Try EDGAR for US tickers, fall back to yfinance.

    Returns (df_q_inc, df_a_inc, df_bs, source_name).
    """
    if ticker in _financial_cache:
        return _financial_cache[ticker]

    # Try EDGAR for US tickers
    result = _try_edgar(ticker)
    if result:
        _financial_cache[ticker] = result
        return result

    # Fall back to yfinance hybrid
    result = _try_yfinance(ticker)
    _financial_cache[ticker] = result
    return result


def _try_edgar(ticker: str) -> Optional[tuple]:
    """Attempt EDGAR fetch. Returns tuple or None."""
    try:
        from lib.data.providers.edgar_quarterly import (
            get_cik,
            get_edgar_quarterly,
        )
        cik = get_cik(ticker)
        if not cik:
            return None

        edgar = get_edgar_quarterly(ticker)
        if not edgar:
            return None

        rev = edgar.get("revenue", pd.Series(dtype=float))
        ni = edgar.get("net_income", pd.Series(dtype=float))
        if len(rev) < 8 and len(ni) < 8:
            return None

        # Normalize EDGAR shares to match yfinance split-adjusted prices.
        # EDGAR mixes original (pre-split) and restated (post-split)
        # values, so we normalize to current level instead of using
        # yfinance split factors (which would double-adjust restated).
        if "shares" in edgar:
            edgar["shares"] = _normalize_shares(edgar["shares"])

        df_q, df_bs = _edgar_to_dfs(edgar)
        if df_q is None or len(df_q) < 8:
            return None
        return (df_q, None, df_bs, "SEC EDGAR")
    except Exception as exc:
        logger.warning("EDGAR failed for %s: %s", ticker, exc)
        return None


def _try_yfinance(ticker: str) -> tuple:
    """yfinance hybrid (quarterly + annual). Always returns tuple."""
    from lib.data.providers.historical_multiples_yf import (
        get_yfinance_data,
    )
    df_q, df_a, df_bs = get_yfinance_data(ticker)
    return (df_q, df_a, df_bs, "Yahoo Finance")


def _edgar_to_dfs(
    edgar: dict,
) -> tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """Convert EDGAR Series dict to (df_q_inc, df_bs) DataFrames."""
    rev = edgar.get("revenue", pd.Series(dtype=float))
    ni = edgar.get("net_income", pd.Series(dtype=float))
    op_inc = edgar.get("operating_income", pd.Series(dtype=float))
    da = edgar.get("da", pd.Series(dtype=float))
    shares_s = edgar.get("shares", pd.Series(dtype=float))

    # Income: union of all flow-item dates
    all_dates = sorted(set(rev.index) | set(ni.index))
    inc_records = []
    for d in all_dates:
        oi = op_inc.get(d)
        dv = da.get(d)
        ebitda = (oi + dv) if oi is not None and dv is not None else None
        inc_records.append({
            "date": pd.Timestamp(d),
            "revenue": rev.get(d),
            "net_income": ni.get(d),
            "ebitda": ebitda,
            "shares": shares_s.get(d),
        })

    df_q = pd.DataFrame(inc_records).sort_values("date").reset_index(
        drop=True,
    )

    # Balance sheet: union of all stock-item dates
    debt = edgar.get("total_debt", pd.Series(dtype=float))
    cash = edgar.get("cash", pd.Series(dtype=float))
    equity = edgar.get("equity", pd.Series(dtype=float))
    intang = edgar.get("intangibles", pd.Series(dtype=float))

    bs_dates = sorted(
        set(debt.index) | set(cash.index)
        | set(equity.index) | set(shares_s.index),
    )
    bs_records = []
    for d in bs_dates:
        eq_val = equity.get(d)
        ig_val = intang.get(d)
        tbv = (eq_val - ig_val) if eq_val and ig_val else None
        bs_records.append({
            "date": pd.Timestamp(d),
            "total_debt": debt.get(d, 0) or 0,
            "cash": cash.get(d, 0) or 0,
            "equity": eq_val,
            "tangible_equity": tbv,
            "minority_interest": 0,
            "shares": shares_s.get(d),
        })

    df_bs = pd.DataFrame(bs_records).sort_values("date").reset_index(
        drop=True,
    )

    # Fill shares in income from BS
    if not df_q.empty and not df_bs.empty:
        _fill_shares_from_bs(df_q, df_bs)

    return (
        df_q if not df_q.empty else None,
        df_bs if not df_bs.empty else None,
    )


def _normalize_shares(shares: pd.Series) -> pd.Series:
    """Normalize EDGAR shares to match yfinance split-adjusted prices.

    EDGAR filings mix pre-split (original) and post-split (restated)
    share counts. yfinance prices are always split-adjusted to current
    level. We normalize all shares to the current level by detecting
    values that are ~Nx smaller than recent values (N = split factor).
    """
    valid = shares.dropna()
    if len(valid) < 2:
        return shares

    # Reference: median of last 4 values (robust to single outliers)
    ref = valid.tail(4).median()
    if ref <= 0:
        return shares

    adjusted = shares.copy()
    for i in range(len(adjusted)):
        val = adjusted.iloc[i]
        if pd.isna(val) or val <= 0:
            continue
        ratio = ref / val
        if ratio < 1.5:
            continue  # already at current level
        # Find closest integer factor (common: 2,3,4,5,6,7,8,10,14,28)
        factor = round(ratio)
        if factor >= 2 and abs(ratio - factor) / factor < 0.20:
            adjusted.iloc[i] = val * factor
    return adjusted


def _fill_shares_from_bs(df_inc: pd.DataFrame, df_bs: pd.DataFrame):
    """Fill missing shares in income df from balance sheet."""
    bs_valid = df_bs.dropna(subset=["shares"])
    if bs_valid.empty:
        return
    for i, row in df_inc.iterrows():
        if row.get("shares") is not None and row["shares"] > 0:
            continue
        mask = bs_valid["date"] <= row["date"]
        if mask.any():
            df_inc.at[i, "shares"] = float(
                bs_valid.loc[mask].iloc[-1]["shares"],
            )
        elif not bs_valid.empty:
            df_inc.at[i, "shares"] = float(bs_valid.iloc[0]["shares"])
