"""
Yahoo Finance provider — fetches data via yfinance.
No API key needed. This is the primary data source.

RULE: This file only fetches and returns raw data as dicts.
It does NOT know about models, cache, or UI.
"""

import yfinance as yf
import pandas as pd
from typing import Optional


def fetch_company_info(ticker: str) -> Optional[dict]:
    """Fetch basic company information."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or len(info) < 5:
            return None

        return {
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
        }
    except Exception:
        return None


def fetch_price_data(ticker: str) -> Optional[dict]:
    """Fetch current price and market data."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or len(info) < 5:
            return None

        price = info.get("currentPrice", info.get("previousClose"))
        prev_close = info.get("previousClose")

        change = None
        change_pct = None
        if price and prev_close and prev_close > 0:
            change = price - prev_close
            change_pct = (change / prev_close) * 100

        return {
            "price": price,
            "change": change,
            "change_pct": change_pct,
            "market_cap": info.get("marketCap"),
            "volume": info.get("volume"),
            "avg_volume": info.get("averageVolume"),
            "high_52w": info.get("fiftyTwoWeekHigh"),
            "low_52w": info.get("fiftyTwoWeekLow"),
            "beta": info.get("beta"),
        }
    except Exception:
        return None


def fetch_ratios(ticker: str) -> Optional[dict]:
    """Fetch key financial ratios."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or len(info) < 5:
            return None

        return {
            "pe_trailing": info.get("trailingPE"),
            "pe_forward": info.get("forwardPE"),
            "peg": info.get("pegRatio"),
            "pb": info.get("priceToBook"),
            "ps": info.get("priceToSalesTrailing12Months"),
            "ev_ebitda": info.get("enterpriseToEbitda"),
            "ev_revenue": info.get("enterpriseToRevenue"),
            "dividend_yield": info.get("dividendYield"),
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
        }
    except Exception:
        return None


def fetch_price_history(ticker: str, period: str = "5y") -> Optional[pd.DataFrame]:
    """Fetch historical price data."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if hist.empty:
            return None

        hist.index = hist.index.tz_localize(None)
        return hist
    except Exception:
        return None


def fetch_financials(ticker: str) -> Optional[dict]:
    """Fetch financial statements (income, balance sheet, cash flow)."""
    try:
        stock = yf.Ticker(ticker)

        income = stock.income_stmt
        balance = stock.balance_sheet
        cashflow = stock.cashflow

        return {
            "income_statement": income if income is not None and not income.empty else None,
            "balance_sheet": balance if balance is not None and not balance.empty else None,
            "cash_flow": cashflow if cashflow is not None and not cashflow.empty else None,
        }
    except Exception:
        return None
