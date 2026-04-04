"""
yfinance data extraction helpers for Historical Multiples.

Fetches quarterly + annual financials from yfinance, returns
DataFrames in the format expected by historical_multiples_calc.

No Streamlit imports. Split from historical_multiples.py for
file size compliance.
"""

from typing import Optional

import pandas as pd
import yfinance as yf


def get_yfinance_data(ticker: str) -> tuple:
    """Fetch quarterly + annual data from yfinance.

    Returns (df_q_inc, df_a_inc, df_bs, currency_info).
    df_q_inc/df_a_inc: [date, revenue, net_income, ebitda, shares]
    df_bs: [date, total_debt, cash, equity, tangible_equity, minority_interest, shares]
    currency_info: dict with currency, financialCurrency, currentPrice, marketCap, shares
    """
    stock = yf.Ticker(ticker)

    df_q_inc = _build_financial_df(stock.quarterly_financials, _inc_records)
    df_a_inc = _build_financial_df(stock.financials, _inc_records)

    df_q_bs = _build_financial_df(
        stock.quarterly_balance_sheet, _bs_records,
    )
    df_a_bs = _build_financial_df(stock.balance_sheet, _bs_records)
    df_bs = _combine_bs(df_q_bs, df_a_bs)

    # Fill shares from BS into income
    if df_q_inc is not None and df_bs is not None:
        _fill_shares(df_q_inc, df_bs)

    # Currency metadata for price_factor calculation
    info = stock.info or {}
    currency_info = {
        "currency": info.get("currency", "USD"),
        "financialCurrency": info.get(
            "financialCurrency", info.get("currency", "USD"),
        ),
        "currentPrice": (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
        ),
        "marketCap": info.get("marketCap"),
        "sharesOutstanding": (
            info.get("impliedSharesOutstanding")
            or info.get("sharesOutstanding")
        ),
    }

    return df_q_inc, df_a_inc, df_bs, currency_info


# ── Record extractors ─────────────────────────────────────────


def _inc_records(df: pd.DataFrame) -> list[dict]:
    """Extract income statement records from yfinance DataFrame."""
    revenue = _get_item(df, "Total Revenue", "Revenue")
    net_income = _get_item(
        df, "Net Income", "Net Income Common Stockholders",
    )
    ebitda = _get_item(df, "EBITDA", "Normalized EBITDA")
    if revenue is None and net_income is None:
        return []

    if ebitda is None:
        op_inc = _get_item(df, "Operating Income")
        dep = _get_item(
            df, "Reconciled Depreciation",
            "Depreciation And Amortization",
        )
        if op_inc is not None and dep is not None:
            ebitda = op_inc + dep

    return [
        {
            "date": pd.Timestamp(col),
            "revenue": _safe_val(revenue, col),
            "net_income": _safe_val(net_income, col),
            "ebitda": _safe_val(ebitda, col),
            "shares": None,
        }
        for col in df.columns
    ]


def _bs_records(df: pd.DataFrame) -> list[dict]:
    """Extract balance sheet records from yfinance DataFrame."""
    total_debt = _get_item(df, "Total Debt", "Long Term Debt")
    cash = _get_item(
        df, "Cash Cash Equivalents And Short Term Investments",
        "Cash And Cash Equivalents", "Cash",
    )
    equity = _get_item(
        df, "Stockholders Equity",
        "Total Stockholders Equity", "Common Stock Equity",
    )
    tangible_bv = _get_item(df, "Tangible Book Value")
    shares = _get_item(df, "Ordinary Shares Number", "Share Issued")
    minority = _get_item(df, "Minority Interest")

    return [
        {
            "date": pd.Timestamp(col),
            "total_debt": _safe_val(total_debt, col) or 0,
            "cash": _safe_val(cash, col) or 0,
            "equity": _safe_val(equity, col),
            "tangible_equity": _safe_val(tangible_bv, col),
            "minority_interest": _safe_val(minority, col) or 0,
            "shares": _safe_val(shares, col),
        }
        for col in df.columns
    ]


# ── DataFrame builders ───────────────────────────────────────


def _build_financial_df(source, extractor) -> Optional[pd.DataFrame]:
    """Build DataFrame from a yfinance financial source + extractor."""
    try:
        if source is None or source.empty:
            return None
    except Exception:
        return None
    records = extractor(source)
    if not records:
        return None
    df = pd.DataFrame(records).sort_values("date").reset_index(drop=True)
    return df if not df.empty else None


def _combine_bs(df_q, df_a) -> Optional[pd.DataFrame]:
    """Merge quarterly + annual BS. Prefer quarterly on date collision."""
    frames = [f for f in [df_q, df_a] if f is not None and not f.empty]
    if not frames:
        return None
    combined = pd.concat(frames, ignore_index=True)
    combined = combined.drop_duplicates(subset=["date"], keep="first")
    return combined.sort_values("date").reset_index(drop=True)


def _fill_shares(df_inc: pd.DataFrame, df_bs: pd.DataFrame) -> None:
    """Fill shares in income df from balance sheet (nearest earlier)."""
    bs_valid = df_bs.dropna(subset=["shares"])
    if bs_valid.empty:
        return
    for i, row in df_inc.iterrows():
        mask = bs_valid["date"] <= row["date"]
        if mask.any():
            df_inc.at[i, "shares"] = float(
                bs_valid.loc[mask].iloc[-1]["shares"],
            )
        else:
            df_inc.at[i, "shares"] = float(bs_valid.iloc[0]["shares"])


# ── Helpers ───────────────────────────────────────────────────


def _get_item(df: pd.DataFrame, *names) -> Optional[pd.Series]:
    """Safely get a line item from a yfinance financial DataFrame."""
    for name in names:
        if name in df.index:
            series = df.loc[name]
            if not series.isna().all():
                return series
    return None


def normalize_shares(shares: pd.Series) -> pd.Series:
    """Normalize EDGAR shares to match yfinance split-adjusted prices.

    EDGAR filings mix pre-split (original) and post-split (restated)
    share counts. yfinance prices are always split-adjusted to current
    level. We normalize all shares to the current level by detecting
    values that are ~Nx smaller than recent values (N = split factor).
    """
    valid = shares.dropna()
    if len(valid) < 2:
        return shares

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
            continue
        factor = round(ratio)
        if factor >= 2 and abs(ratio - factor) / factor < 0.20:
            adjusted.iloc[i] = val * factor
    return adjusted


def fill_shares_from_bs(df_inc: pd.DataFrame, df_bs: pd.DataFrame):
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


def _safe_val(series: Optional[pd.Series], key) -> Optional[float]:
    """Safely extract a float value from a pandas Series."""
    if series is None:
        return None
    try:
        val = series[key]
        if pd.isna(val):
            return None
        return float(val)
    except (KeyError, TypeError, ValueError):
        return None
