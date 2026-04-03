"""DDM data provider — dividend history, DPS growth, payout analysis.

Pure Python + pandas — NO Streamlit imports.
Fetches all dividend-related data from yfinance for DDM valuation.
"""

import logging
from datetime import datetime

import yfinance as yf

logger = logging.getLogger(__name__)


def fetch_dividend_data(ticker: str) -> dict:
    """Fetch comprehensive dividend data for DDM.

    Returns dict with:
      - current_dps: annual dividend per share
      - dividend_yield: decimal (0.02 = 2%)
      - trailing_eps: trailing EPS
      - forward_eps: forward EPS (analyst consensus)
      - payout_ratio: DPS / EPS decimal
      - dividend_history: list of {"date": str, "amount": float} (annual)
      - dps_cagr: dict with 1y, 3y, 5y, 10y growth rates (decimal)
      - years_paying: consecutive years of payments
      - years_increasing: consecutive years of increases
      - dividend_cuts: list of years where dividend was cut
      - has_dividend: bool
    """
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}

        # Current dividend data
        current_dps = info.get("dividendRate") or 0.0
        raw_yield = info.get("dividendYield") or 0.0
        # Yahoo dividendYield is already-percent (2.14 = 2.14%)
        # Normalize to decimal: div_yield / 100 → 0.0214
        dividend_yield = raw_yield / 100 if raw_yield else 0.0
        trailing_eps = info.get("trailingEps") or 0.0
        forward_eps = info.get("forwardEps") or 0.0

        # Payout ratio
        payout = 0.0
        if trailing_eps and trailing_eps > 0 and current_dps:
            payout = current_dps / trailing_eps

        # Dividend history
        divs = t.dividends
        annual_dps = _aggregate_annual_dps(divs) if divs is not None and len(divs) > 0 else {}

        has_dividend = current_dps > 0 or len(annual_dps) > 0

        # DPS CAGR calculations
        dps_cagr = _calc_dps_cagr(annual_dps)

        # Streak analysis
        years_paying, years_increasing, cuts = _analyze_streaks(annual_dps)

        # Build history list (sorted chronologically)
        history = [
            {"year": y, "dps": d}
            for y, d in sorted(annual_dps.items())
        ]

        return {
            "current_dps": current_dps,
            "dividend_yield": dividend_yield,
            "trailing_eps": trailing_eps,
            "forward_eps": forward_eps,
            "payout_ratio": payout,
            "dividend_history": history,
            "annual_dps": annual_dps,
            "dps_cagr": dps_cagr,
            "years_paying": years_paying,
            "years_increasing": years_increasing,
            "dividend_cuts": cuts,
            "has_dividend": has_dividend,
        }

    except Exception as e:
        logger.warning("DDM provider error for %s: %s", ticker, e)
        return {
            "current_dps": 0.0,
            "dividend_yield": 0.0,
            "trailing_eps": 0.0,
            "forward_eps": 0.0,
            "payout_ratio": 0.0,
            "dividend_history": [],
            "annual_dps": {},
            "dps_cagr": {},
            "years_paying": 0,
            "years_increasing": 0,
            "dividend_cuts": [],
            "has_dividend": False,
        }


def _aggregate_annual_dps(dividends) -> dict[int, float]:
    """Aggregate quarterly/semi-annual dividends into annual DPS.

    Returns {year: total_dps} dict.
    """
    annual = {}
    for date, amount in dividends.items():
        year = date.year
        annual[year] = annual.get(year, 0.0) + float(amount)

    # Drop current year if incomplete (less than 2 payments expected)
    current_year = datetime.now().year
    if current_year in annual:
        # Count payments this year
        payments_this_year = sum(
            1 for d in dividends.index if d.year == current_year
        )
        # If fewer than 2 payments, likely incomplete
        if payments_this_year < 2:
            del annual[current_year]

    return annual


def _calc_dps_cagr(annual_dps: dict[int, float]) -> dict:
    """Calculate DPS CAGR for 1Y, 3Y, 5Y, 10Y periods.

    Returns dict: {"1y": float, "3y": float, ...} (decimals).
    """
    if not annual_dps:
        return {}

    years_sorted = sorted(annual_dps.keys())
    latest_year = years_sorted[-1]
    latest_dps = annual_dps[latest_year]

    if latest_dps <= 0:
        return {}

    cagr = {}
    for label, lookback in [("1y", 1), ("3y", 3), ("5y", 5), ("10y", 10)]:
        target_year = latest_year - lookback
        if target_year in annual_dps and annual_dps[target_year] > 0:
            base = annual_dps[target_year]
            rate = (latest_dps / base) ** (1 / lookback) - 1
            cagr[label] = rate

    return cagr


def _analyze_streaks(annual_dps: dict[int, float]) -> tuple:
    """Analyze dividend payment and increase streaks.

    Returns (years_paying, years_increasing, cuts_list).
    """
    if not annual_dps:
        return 0, 0, []

    years_sorted = sorted(annual_dps.keys())
    current_year = datetime.now().year

    # Consecutive years paying (counting back from most recent)
    years_paying = 0
    for i in range(len(years_sorted) - 1, -1, -1):
        expected = current_year - (len(years_sorted) - 1 - i)
        if years_sorted[i] == expected or years_sorted[i] == expected - 1:
            years_paying += 1
        else:
            break

    # Consecutive years of increases
    years_increasing = 0
    for i in range(len(years_sorted) - 1, 0, -1):
        if annual_dps[years_sorted[i]] > annual_dps[years_sorted[i - 1]]:
            years_increasing += 1
        else:
            break

    # Find dividend cuts (year-over-year decreases)
    cuts = []
    for i in range(1, len(years_sorted)):
        if annual_dps[years_sorted[i]] < annual_dps[years_sorted[i - 1]]:
            cuts.append(years_sorted[i])

    return years_paying, years_increasing, cuts
