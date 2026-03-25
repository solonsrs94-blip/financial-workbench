"""Yahoo Finance provider — financial statements, holders, news, events.

Split from yahoo.py to keep files under 200 lines.
"""

import logging
import yfinance as yf
import pandas as pd
from typing import Optional

logger = logging.getLogger(__name__)


def fetch_financials(ticker: str) -> Optional[dict]:
    """Fetch annual and quarterly financial statements."""
    try:
        stock = yf.Ticker(ticker)
        income = stock.income_stmt
        balance = stock.balance_sheet
        cashflow = stock.cashflow
        q_income = stock.quarterly_income_stmt
        q_balance = stock.quarterly_balance_sheet
        q_cashflow = stock.quarterly_cashflow
        return {
            "income_statement": income if income is not None and not income.empty else None,
            "balance_sheet": balance if balance is not None and not balance.empty else None,
            "cash_flow": cashflow if cashflow is not None and not cashflow.empty else None,
            "quarterly_income": q_income if q_income is not None and not q_income.empty else None,
            "quarterly_balance": q_balance if q_balance is not None and not q_balance.empty else None,
            "quarterly_cashflow": q_cashflow if q_cashflow is not None and not q_cashflow.empty else None,
        }
    except Exception as e:
        logger.error("Financials failed for %s: %s", ticker, e)
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
    except Exception as e:
        logger.error("Holders failed for %s: %s", ticker, e)
        return None


def fetch_recommendations(ticker: str) -> Optional[pd.DataFrame]:
    """Fetch analyst recommendations."""
    try:
        stock = yf.Ticker(ticker)
        recs = stock.recommendations
        if recs is not None and not recs.empty:
            return recs
        return None
    except Exception as e:
        logger.error("Recommendations failed for %s: %s", ticker, e)
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
    except Exception as e:
        logger.error("News failed for %s: %s", ticker, e)
        return []


def fetch_events(ticker: str) -> dict:
    """Fetch earnings dates, dividends, and splits for chart annotations."""
    result = {"earnings": [], "dividends": [], "splits": []}
    try:
        stock = yf.Ticker(ticker)

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

        try:
            splits = stock.splits
            if splits is not None and not splits.empty:
                for date, ratio in splits.items():
                    if pd.isna(ratio) or ratio == 0:
                        continue
                    if ratio >= 1:
                        label = f"Split {ratio:.0f}:1"
                    else:
                        label = f"Reverse Split 1:{1/ratio:.0f}"
                    result["splits"].append({"date": str(date), "label": label})
        except Exception:
            pass
    except Exception as e:
        logger.error("Events failed for %s: %s", ticker, e)
    return result
