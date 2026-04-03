"""Test DDM provider + engine on 5 tickers: JNJ, JPM, T, AAPL, TSLA."""

import sys
sys.path.insert(0, ".")

from lib.data.providers.ddm_provider import fetch_dividend_data
from lib.analysis.valuation.ddm import gordon_growth, two_stage_ddm, ddm_sensitivity
from lib.analysis.valuation.wacc import adjusted_beta, calc_capm, size_premium_bracket
import yfinance as yf

TICKERS = ["JNJ", "JPM", "T", "AAPL", "TSLA"]

def test_ticker(ticker):
    print(f"\n{'='*60}")
    print(f"  {ticker}")
    print(f"{'='*60}")

    # 1. Fetch dividend data
    data = fetch_dividend_data(ticker)
    print(f"\n--- Dividend Data ---")
    print(f"  has_dividend:      {data['has_dividend']}")
    print(f"  current_dps:       ${data['current_dps']:.2f}")
    print(f"  dividend_yield:    {data['dividend_yield']:.4f} ({data['dividend_yield']*100:.2f}%)")
    print(f"  trailing_eps:      ${data['trailing_eps']:.2f}")
    print(f"  forward_eps:       ${data['forward_eps']:.2f}")
    print(f"  payout_ratio:      {data['payout_ratio']:.2%}")
    print(f"  years_paying:      {data['years_paying']}")
    print(f"  years_increasing:  {data['years_increasing']}")
    print(f"  dividend_cuts:     {data['dividend_cuts']}")

    # DPS CAGR
    cagr = data["dps_cagr"]
    print(f"\n--- DPS CAGR ---")
    for k, v in cagr.items():
        print(f"  {k}: {v:.2%}")

    # Last 5 years history
    hist = data["dividend_history"]
    if hist:
        print(f"\n--- Last 5 Years DPS ---")
        for entry in hist[-5:]:
            print(f"  {entry['year']}: ${entry['dps']:.2f}")

    if not data["has_dividend"]:
        print(f"\n  ** NO DIVIDEND — skipping valuation **")
        return

    # 2. Get current price + beta for Ke
    t = yf.Ticker(ticker)
    info = t.info or {}
    current_price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
    raw_beta = info.get("beta") or 1.0
    market_cap = info.get("marketCap") or 0

    beta = adjusted_beta(raw_beta)
    sp, sp_label = size_premium_bracket(market_cap)
    rf = 0.043  # approximate 10Y UST
    erp = 0.046  # approximate Damodaran ERP
    ke = calc_capm(rf, beta, erp, sp, 0.0)

    print(f"\n--- Ke Calculation ---")
    print(f"  current_price:  ${current_price:.2f}")
    print(f"  raw_beta:       {raw_beta:.3f}")
    print(f"  blume_beta:     {beta:.3f}")
    print(f"  rf:             {rf:.2%}")
    print(f"  erp:            {erp:.2%}")
    print(f"  size_premium:   {sp:.2%} ({sp_label})")
    print(f"  Ke:             {ke:.2%}")

    # 3. Gordon Growth
    d0 = data["current_dps"]
    g = cagr.get("5y", cagr.get("3y", 0.03))
    print(f"\n--- Gordon Growth ---")
    print(f"  D0 = ${d0:.2f}, g = {g:.2%}")
    result = gordon_growth(d0, ke, g)
    if result.get("error"):
        print(f"  ERROR: {result['error']}")
    else:
        implied = result["implied_price"]
        upside = (implied / current_price - 1) * 100 if current_price > 0 else 0
        print(f"  D1 = ${result['d1']:.2f}")
        print(f"  Implied Price = ${implied:.2f}")
        print(f"  Current Price = ${current_price:.2f}")
        print(f"  Upside/Downside = {upside:+.1f}%")

    # 4. 2-Stage DDM
    g1 = cagr.get("3y", cagr.get("5y", 0.05))
    g2 = 0.025
    n = 5
    print(f"\n--- 2-Stage DDM ---")
    print(f"  D0 = ${d0:.2f}, g1 = {g1:.2%}, g2 = {g2:.2%}, N = {n}")
    result2 = two_stage_ddm(d0, ke, g1, g2, n)
    if result2.get("error"):
        print(f"  ERROR: {result2['error']}")
    else:
        implied2 = result2["implied_price"]
        pv1 = result2["pv_stage1"]
        pvtv = result2["pv_terminal"]
        upside2 = (implied2 / current_price - 1) * 100 if current_price > 0 else 0
        print(f"  PV Stage 1:     ${pv1:.2f}")
        print(f"  PV Terminal:    ${pvtv:.2f}")
        print(f"  Implied Price:  ${implied2:.2f}")
        print(f"  Upside/Downside: {upside2:+.1f}%")
        pct1 = pv1 / implied2 * 100 if implied2 > 0 else 0
        pct_tv = pvtv / implied2 * 100 if implied2 > 0 else 0
        print(f"  Stage 1 %:      {pct1:.0f}%")
        print(f"  Terminal %:     {pct_tv:.0f}%")

    # 5. Warnings check
    print(f"\n--- Warnings ---")
    if not data["has_dividend"]:
        print(f"  [!] No dividend")
    if data["years_paying"] < 5:
        print(f"  [!] Limited history ({data['years_paying']} years)")
    if data["payout_ratio"] > 1.0:
        print(f"  [!] Payout > 100% ({data['payout_ratio']:.0%})")
    if data["dividend_cuts"]:
        recent = [y for y in data["dividend_cuts"] if y >= 2015]
        if recent:
            print(f"  [!] Dividend cut in {recent}")
    if not any([
        not data["has_dividend"],
        data["years_paying"] < 5,
        data["payout_ratio"] > 1.0,
        any(y >= 2015 for y in data["dividend_cuts"]),
    ]):
        print(f"  (none)")


if __name__ == "__main__":
    for ticker in TICKERS:
        try:
            test_ticker(ticker)
        except Exception as e:
            print(f"\n  *** EXCEPTION for {ticker}: {e}")
            import traceback
            traceback.print_exc()
