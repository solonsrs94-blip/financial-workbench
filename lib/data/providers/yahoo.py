"""
Yahoo Finance provider — fetches data via yfinance.
No API key needed. This is the primary data source.

RULE: This file only fetches and returns raw data as dicts.
It does NOT know about models, cache, or UI.
"""

import yfinance as yf
import pandas as pd
from typing import Optional


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
    except Exception:
        return []


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
            "target_mean": info.get("targetMeanPrice"),
            "target_median": info.get("targetMedianPrice"),
            "target_high": info.get("targetHighPrice"),
            "target_low": info.get("targetLowPrice"),
            "analyst_rating": info.get("averageAnalystRating"),
            "analyst_count": info.get("numberOfAnalystOpinions"),
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

        # Yahoo returns dividendYield as already-percent (0.41 = 0.41%).
        # Other fields like profitMargins are decimal (0.27 = 27%).
        # We normalize ALL to decimal form: 0.0041 = 0.41%.
        div_yield = info.get("dividendYield")
        if div_yield is not None:
            div_yield = div_yield / 100  # 0.41 → 0.0041

        return {
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
        }
    except Exception:
        return None


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
    except Exception:
        return None


def fetch_events(ticker: str) -> dict:
    """Fetch earnings dates, dividends, and splits for chart annotations."""
    result = {"earnings": [], "dividends": [], "splits": []}
    try:
        stock = yf.Ticker(ticker)

        # Earnings dates
        try:
            ed = stock.earnings_dates
            if ed is not None and not ed.empty:
                for date, row in ed.iterrows():
                    eps_est = row.get("EPS Estimate", None)
                    eps_act = row.get("Reported EPS", None)
                    surprise = row.get("Surprise(%)", None)

                    label = "Earnings"
                    if eps_act is not None and not pd.isna(eps_act):
                        label = f"EPS: ${eps_act:.2f}"
                        if surprise is not None and not pd.isna(surprise):
                            label += f" ({surprise:+.1f}%)"
                    elif eps_est is not None and not pd.isna(eps_est):
                        label = f"EPS Est: ${eps_est:.2f}"

                    result["earnings"].append({"date": str(date), "label": label})
        except Exception:
            pass

        # Dividends
        try:
            divs = stock.dividends
            if divs is not None and not divs.empty:
                for date, amount in divs.items():
                    result["dividends"].append({
                        "date": str(date),
                        "label": f"Div: ${amount:.2f}",
                    })
        except Exception:
            pass

        # Splits
        try:
            splits = stock.splits
            if splits is not None and not splits.empty:
                for date, ratio in splits.items():
                    result["splits"].append({
                        "date": str(date),
                        "label": f"Split {ratio:.0f}:1",
                    })
        except Exception:
            pass

    except Exception:
        pass
    return result


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


def fetch_holders(ticker: str) -> Optional[dict]:
    """Fetch institutional and insider holder data."""
    try:
        stock = yf.Ticker(ticker)

        institutional = stock.institutional_holders
        insider = stock.insider_transactions

        return {
            "institutional": institutional if institutional is not None and not institutional.empty else None,
            "insider_transactions": insider if insider is not None and not insider.empty else None,
        }
    except Exception:
        return None


def fetch_recommendations(ticker: str) -> Optional[pd.DataFrame]:
    """Fetch analyst recommendations."""
    try:
        stock = yf.Ticker(ticker)
        recs = stock.recommendations
        if recs is not None and not recs.empty:
            return recs
        return None
    except Exception:
        return None


def fetch_news(ticker: str) -> list[dict]:
    """Fetch recent news for a ticker."""
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        if not news:
            return []

        results = []
        for n in news[:10]:
            content = n.get("content", {})
            provider = content.get("provider", {})
            canonical = content.get("canonicalUrl", {})
            results.append({
                "title": content.get("title", ""),
                "publisher": provider.get("displayName", ""),
                "link": canonical.get("url", ""),
                "published": content.get("pubDate", ""),
            })
        return results
    except Exception:
        return []
