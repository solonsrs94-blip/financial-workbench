"""Historical multiples calculations — daily TTM builder,
summary stats, and implied values. No Streamlit imports.
"""

from typing import Optional

import numpy as np
import pandas as pd


def get_mult_keys(is_financial: bool) -> list[str]:
    """Return multiple column names based on company type."""
    if is_financial:
        return ["pe", "p_book", "p_tbv"]
    return ["pe", "ev_ebitda", "ev_revenue"]


def build_daily_multiples(
    prices: pd.DataFrame,
    df_q_inc: Optional[pd.DataFrame],
    df_a_inc: Optional[pd.DataFrame],
    df_bs: pd.DataFrame,
    is_financial: bool,
    price_factor: float = 1.0,
) -> pd.DataFrame:
    """Compute TTM multiples for each trading day.

    price_factor converts listing-currency prices to financial currency.
    """
    q_dates = (
        df_q_inc["date"].values
        if df_q_inc is not None and not df_q_inc.empty
        else np.array([], dtype="datetime64[ns]")
    )
    a_dates = (
        df_a_inc["date"].values
        if df_a_inc is not None and not df_a_inc.empty
        else np.array([], dtype="datetime64[ns]")
    )
    bs_dates = df_bs["date"].values

    results = []
    for trade_date in prices.index:
        ts = pd.Timestamp(trade_date)
        ts64 = np.datetime64(ts)
        close = prices.loc[trade_date, "Close"]

        # Balance sheet lookup (always use most recent available)
        mask_bs = bs_dates <= ts64
        if not mask_bs.any():
            continue
        latest_bs = df_bs.loc[mask_bs].iloc[-1]

        # Try quarterly TTM first (need 4 quarters)
        mask_q = q_dates <= ts64
        if mask_q.sum() >= 4:
            q4 = df_q_inc.loc[mask_q].tail(4)
            ttm_rev = q4["revenue"].sum()
            ttm_ni = q4["net_income"].sum()
            # EBITDA needs all 4 quarters valid (partial sums misleading)
            ttm_ebitda = q4["ebitda"].sum(min_count=4)
            shares = _get_shares(latest_bs, q4.iloc[-1])
        else:
            # Fall back to most recent annual report
            mask_a = a_dates <= ts64
            if not mask_a.any():
                continue
            annual = df_a_inc.loc[mask_a].iloc[-1]
            ttm_rev = annual["revenue"]
            ttm_ni = annual["net_income"]
            ttm_ebitda = annual["ebitda"]
            shares = _get_shares(latest_bs, annual)

        if not shares or shares <= 0:
            continue

        row = _calc_row(
            ts, close, ttm_rev, ttm_ni, ttm_ebitda,
            shares, latest_bs, is_financial, price_factor,
        )
        if row:
            results.append(row)

    if not results:
        return pd.DataFrame()
    return pd.DataFrame(results).set_index("date")


def _get_shares(latest_bs, inc_row) -> Optional[float]:
    """Get shares: prefer BS, fallback to income row."""
    shares = latest_bs.get("shares")
    if shares and shares > 0:
        return shares
    shares = inc_row.get("shares")
    if shares and shares > 0:
        return shares
    return None


def _calc_row(
    ts, close, ttm_rev, ttm_ni, ttm_ebitda,
    shares, latest_bs, is_financial, price_factor=1.0,
):
    """Calculate one day's multiples. price_factor aligns currencies."""
    # Convert price to financial currency (e.g. GBp → USD)
    close_fin = close * price_factor

    debt = latest_bs["total_debt"] or 0
    cash = latest_bs["cash"] or 0
    minority = latest_bs["minority_interest"] or 0
    equity_bv = latest_bs["equity"]
    tangible_bv = latest_bs["tangible_equity"]

    mcap = close_fin * shares
    ev = mcap + debt - cash + minority
    eps = ttm_ni / shares if ttm_ni else None
    bvps = equity_bv / shares if equity_bv else None
    tbvps = tangible_bv / shares if tangible_bv else None

    row = {"date": ts}
    if is_financial:
        row["pe"] = (close_fin / eps) if eps and eps > 0 else np.nan
        row["p_book"] = (
            (close_fin / bvps) if bvps and bvps > 0 else np.nan
        )
        row["p_tbv"] = (
            (close_fin / tbvps) if tbvps and tbvps > 0 else np.nan
        )
    else:
        row["pe"] = (close_fin / eps) if eps and eps > 0 else np.nan
        row["ev_ebitda"] = (
            (ev / ttm_ebitda) if ttm_ebitda and ttm_ebitda > 0
            else np.nan
        )
        row["ev_revenue"] = (
            (ev / ttm_rev) if ttm_rev and ttm_rev > 0
            else np.nan
        )
    return row


def compute_summary(daily: pd.DataFrame, keys: list[str]) -> dict:
    """Compute mean, median, min, max, std, percentiles per multiple."""
    summary = {}
    for key in keys:
        if key not in daily.columns:
            continue
        series = daily[key].dropna()
        if len(series) < 10:
            continue

        current = series.iloc[-1]
        pctile = float((series < current).mean() * 100)

        summary[key] = {
            "current": round(float(current), 2),
            "mean": round(float(series.mean()), 2),
            "median": round(float(series.median()), 2),
            "min": round(float(series.min()), 2),
            "max": round(float(series.max()), 2),
            "std": round(float(series.std()), 2),
            "p10": round(float(series.quantile(0.10)), 2),
            "p90": round(float(series.quantile(0.90)), 2),
            "percentile": round(pctile),
            "minus_1std": round(float(series.mean() - series.std()), 2),
            "plus_1std": round(float(series.mean() + series.std()), 2),
        }
    return summary


def compute_implied_values(
    summary: dict,
    df_inc: pd.DataFrame,
    df_bs: pd.DataFrame,
    current_price: float,
    is_financial: bool,
    is_quarterly: bool = True,
    price_factor: float = 1.0,
    eps_override: float | None = None,
) -> dict:
    """Implied share price at historical mean/median/-1σ.

    is_quarterly=False uses last 1 row (annual = already TTM).
    price_factor: implied prices converted back to listing currency.
    eps_override: if set, uses this value instead of TTM EPS for P/E implied prices.
    """
    if not current_price:
        return {}

    if is_quarterly:
        n = min(4, len(df_inc))
        last_n = df_inc.tail(n)
    else:
        last_n = df_inc.tail(1)
    shares = last_n.iloc[-1]["shares"]
    if not shares or shares <= 0:
        # Try BS shares as fallback
        bs_shares = df_bs.iloc[-1].get("shares")
        if not bs_shares or bs_shares <= 0:
            return {}
        shares = bs_shares

    if is_quarterly:
        ttm_revenue = last_n["revenue"].sum()
        ttm_ebitda = last_n["ebitda"].sum()
        ttm_ni = last_n["net_income"].sum()
    else:
        ttm_revenue = last_n.iloc[0]["revenue"]
        ttm_ebitda = last_n.iloc[0]["ebitda"]
        ttm_ni = last_n.iloc[0]["net_income"]
    eps = eps_override if eps_override else (ttm_ni / shares if ttm_ni else None)

    # Use latest BS with valid equity (not just latest date, which
    # may be from a dei filing with no financial data)
    valid_bs = df_bs.dropna(subset=["equity"])
    latest_bs = valid_bs.iloc[-1] if not valid_bs.empty else df_bs.iloc[-1]
    debt = latest_bs["total_debt"] or 0
    cash = latest_bs["cash"] or 0
    minority = latest_bs["minority_interest"] or 0
    equity_bv = latest_bs["equity"]
    tangible_bv = latest_bs["tangible_equity"]
    bvps = equity_bv / shares if equity_bv else None
    tbvps = tangible_bv / shares if tangible_bv else None
    net_debt_ps = (debt - cash + minority) / shares

    # Implied prices are computed in financial currency (per-share metric
    # × multiple), then converted back to listing currency via inv_factor.
    inv_factor = 1.0 / price_factor if price_factor and price_factor != 0 else 1.0

    implied = {}
    for key, stats in summary.items():
        if key == "pe" and eps and eps > 0:
            implied[key] = _implied_equity(
                eps, stats, current_price, inv_factor,
            )
        elif key == "p_book" and bvps and bvps > 0:
            implied[key] = _implied_equity(
                bvps, stats, current_price, inv_factor,
            )
        elif key == "p_tbv" and tbvps and tbvps > 0:
            implied[key] = _implied_equity(
                tbvps, stats, current_price, inv_factor,
            )
        elif key == "ev_ebitda" and ttm_ebitda and ttm_ebitda > 0:
            metric_ps = ttm_ebitda / shares
            implied[key] = _implied_ev(
                metric_ps, net_debt_ps, stats, current_price,
                inv_factor,
            )
        elif key == "ev_revenue" and ttm_revenue and ttm_revenue > 0:
            metric_ps = ttm_revenue / shares
            implied[key] = _implied_ev(
                metric_ps, net_debt_ps, stats, current_price,
                inv_factor,
            )
    return implied


def _implied_equity(per_share_metric, stats, current_price, inv=1.0):
    """Implied price for equity-based multiples (P/E, P/Book).

    per_share_metric is in financial currency. Result is converted
    to listing currency via inv (= 1/price_factor).
    """
    at_mean = per_share_metric * stats["mean"] * inv
    at_median = per_share_metric * stats["median"] * inv
    at_m1s = per_share_metric * stats["minus_1std"] * inv
    at_p10 = per_share_metric * stats["p10"] * inv
    at_p90 = per_share_metric * stats["p90"] * inv
    upside = (at_mean - current_price) / current_price
    return {
        "at_mean": round(at_mean, 2),
        "at_median": round(at_median, 2),
        "at_minus_1std": round(at_m1s, 2),
        "at_p10": round(at_p10, 2),
        "at_p90": round(at_p90, 2),
        "upside_mean": round(upside, 4),
    }


def _implied_ev(metric_ps, net_debt_ps, stats, current_price, inv=1.0):
    """Implied price for EV-based multiples (EV/EBITDA, EV/Revenue).

    metric_ps and net_debt_ps are in financial currency. Result is
    converted to listing currency via inv (= 1/price_factor).
    """
    at_mean = (metric_ps * stats["mean"] - net_debt_ps) * inv
    at_median = (metric_ps * stats["median"] - net_debt_ps) * inv
    at_m1s = (metric_ps * stats["minus_1std"] - net_debt_ps) * inv
    at_p10 = (metric_ps * stats["p10"] - net_debt_ps) * inv
    at_p90 = (metric_ps * stats["p90"] - net_debt_ps) * inv
    upside = (at_mean - current_price) / current_price
    return {
        "at_mean": round(at_mean, 2),
        "at_median": round(at_median, 2),
        "at_minus_1std": round(at_m1s, 2),
        "at_p10": round(at_p10, 2),
        "at_p90": round(at_p90, 2),
        "upside_mean": round(upside, 4),
    }
