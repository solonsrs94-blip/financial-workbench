"""Full DDM integration test — simulates the complete Step 1→2→3 flow.

Tests: JNJ, JPM, T, AAPL, TSLA
Validates: provider data, Ke calculation, Gordon/2-Stage, sensitivity, warnings.
"""

import sys
sys.path.insert(0, ".")

from lib.data.providers.ddm_provider import fetch_dividend_data
from lib.analysis.valuation.ddm import gordon_growth, two_stage_ddm, ddm_sensitivity
from lib.analysis.valuation.wacc import adjusted_beta, calc_capm, size_premium_bracket
from lib.data.valuation_data import get_erp, get_risk_free_rate
import yfinance as yf
from datetime import datetime

TICKERS = ["JNJ", "JPM", "T", "AAPL", "TSLA"]
ISSUES = []


def log(msg, indent=0):
    print(f"{'  ' * indent}{msg}")


def check(condition, msg, ticker):
    if not condition:
        ISSUES.append(f"[{ticker}] {msg}")
        log(f"  ✗ FAIL: {msg}")
    else:
        log(f"  ✓ {msg}")


def test_ticker(ticker):
    log(f"\n{'='*65}")
    log(f"  {ticker}")
    log(f"{'='*65}")

    # ════════════════════════════════════════════════════════════
    # STEP 0: Fetch raw data
    # ════════════════════════════════════════════════════════════
    log("\n── Provider Data ──")
    data = fetch_dividend_data(ticker)
    check(isinstance(data, dict), "Provider returns dict", ticker)
    check("has_dividend" in data, "has_dividend field present", ticker)
    check("current_dps" in data, "current_dps field present", ticker)
    check("dps_cagr" in data, "dps_cagr field present", ticker)
    check("dividend_cuts" in data, "dividend_cuts field present", ticker)
    check("years_paying" in data, "years_paying field present", ticker)
    check("years_increasing" in data, "years_increasing field present", ticker)
    check("dividend_history" in data, "dividend_history field present", ticker)

    log(f"\n  has_dividend:     {data['has_dividend']}")
    log(f"  current_dps:      ${data['current_dps']:.2f}")
    log(f"  dividend_yield:   {data['dividend_yield']*100:.2f}%")
    log(f"  trailing_eps:     ${data['trailing_eps']:.2f}")
    log(f"  payout_ratio:     {data['payout_ratio']:.1%}")
    log(f"  years_paying:     {data['years_paying']}")
    log(f"  years_increasing: {data['years_increasing']}")
    log(f"  dividend_cuts:    {data['dividend_cuts']}")

    # Dividend yield check — must be reasonable decimal
    dy = data["dividend_yield"]
    check(dy < 0.20 or not data["has_dividend"],
          f"Dividend yield is reasonable decimal ({dy:.4f} = {dy*100:.2f}%)", ticker)

    # DPS CAGR
    cagr = data["dps_cagr"]
    log(f"  DPS CAGR: {', '.join(f'{k}={v:.2%}' for k, v in cagr.items())}")

    # ════════════════════════════════════════════════════════════
    # WARNINGS CHECK
    # ════════════════════════════════════════════════════════════
    log("\n── Warnings ──")
    cutoff = datetime.now().year - 10

    if not data["has_dividend"]:
        log("  [WARNING] No dividend — DDM not applicable")
    if data["years_paying"] > 0 and data["years_paying"] < 5:
        log(f"  [WARNING] Limited history ({data['years_paying']} years)")
    if data["payout_ratio"] > 1.0:
        log(f"  [WARNING] Payout > 100% ({data['payout_ratio']:.0%})")
    recent_cuts = [y for y in data["dividend_cuts"] if y >= cutoff]
    if recent_cuts:
        log(f"  [WARNING] Dividend cut in {recent_cuts}")
    if data["has_dividend"] and data["years_paying"] >= 5 \
       and data["payout_ratio"] <= 1.0 and not recent_cuts:
        log("  (no warnings)")

    # Ticker-specific warning checks
    if ticker == "TSLA":
        check(not data["has_dividend"], "TSLA: no dividend detected", ticker)
    if ticker == "T":
        check(len(recent_cuts) > 0, f"T: dividend cut detected ({recent_cuts})", ticker)
    if ticker == "JNJ":
        check(data["years_increasing"] > 50,
              f"JNJ: 50+ years of increases ({data['years_increasing']})", ticker)

    if not data["has_dividend"]:
        log("\n  ** Skipping valuation (no dividend) **")
        return

    # ════════════════════════════════════════════════════════════
    # STEP 1: Cost of Equity (Ke)
    # ════════════════════════════════════════════════════════════
    log("\n── Step 1: Cost of Equity ──")

    t = yf.Ticker(ticker)
    info = t.info or {}
    current_price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
    raw_beta = info.get("beta") or 1.0
    market_cap = info.get("marketCap") or 0

    # Rf
    rf = get_risk_free_rate() or 0.04
    log(f"  Rf (10Y UST):  {rf:.2%}")

    # Beta (Blume-adjusted)
    beta = adjusted_beta(raw_beta)
    log(f"  Raw Beta:      {raw_beta:.3f}")
    log(f"  Blume Beta:    {beta:.3f}")

    # ERP
    erp = get_erp() or 0.055
    log(f"  ERP:           {erp:.2%}")

    # Size premium
    sp, sp_label = size_premium_bracket(market_cap)
    log(f"  Size Premium:  {sp:.2%} ({sp_label})")

    # Ke = CAPM
    ke = calc_capm(rf, beta, erp, sp, 0.0)
    log(f"  Ke:            {ke:.2%}")
    log(f"  Current Price: ${current_price:.2f}")

    check(0.03 < ke < 0.25, f"Ke is in reasonable range ({ke:.2%})", ticker)
    check(current_price > 0, f"Current price available (${current_price:.2f})", ticker)

    d0 = data["current_dps"]

    # ════════════════════════════════════════════════════════════
    # STEP 2A: Gordon Growth Model
    # ════════════════════════════════════════════════════════════
    log("\n── Step 2A: Gordon Growth ──")

    g = cagr.get("5y", cagr.get("3y", 0.03))
    log(f"  D0 = ${d0:.2f}, g = {g:.2%}, Ke = {ke:.2%}")

    if g >= ke:
        log(f"  ✗ g >= Ke → Gordon Growth invalid (expected for high-growth dividend)")
        check(ticker in ("JPM",),
              f"g >= Ke only expected for certain tickers, got {ticker}", ticker)
    else:
        result = gordon_growth(d0, ke, g)
        check("implied_price" in result, "Gordon returns implied_price", ticker)
        check(result["implied_price"] > 0, "Implied price > 0", ticker)

        implied = result["implied_price"]
        d1 = result["d1"]
        upside = (implied / current_price - 1) * 100 if current_price > 0 else 0

        log(f"  D1 = ${d1:.2f}")
        log(f"  Implied Price: ${implied:.2f}")
        log(f"  Upside/Down:   {upside:+.1f}%")

        # Sanity: price should be in $1-$5000 range
        check(0 < implied < 5000,
              f"Gordon price in reasonable range (${implied:.2f})", ticker)

    # ════════════════════════════════════════════════════════════
    # STEP 2B: 2-Stage DDM
    # ════════════════════════════════════════════════════════════
    log("\n── Step 2B: 2-Stage DDM ──")

    g1 = cagr.get("3y", cagr.get("5y", 0.05))
    g2 = 0.025
    n = 5
    log(f"  D0=${d0:.2f}, g1={g1:.2%}, g2={g2:.2%}, N={n}")

    if g2 >= ke:
        log(f"  ✗ Terminal growth >= Ke → 2-Stage invalid")
    else:
        result2 = two_stage_ddm(d0, ke, g1, g2, n)
        check("implied_price" in result2, "2-Stage returns implied_price", ticker)
        check("pv_stage1" in result2, "2-Stage returns pv_stage1", ticker)
        check("pv_terminal" in result2, "2-Stage returns pv_terminal", ticker)
        check("projection" in result2, "2-Stage returns projection table", ticker)

        if result2.get("error"):
            log(f"  ERROR: {result2['error']}")
        else:
            implied2 = result2["implied_price"]
            pv1 = result2["pv_stage1"]
            pvtv = result2["pv_terminal"]
            upside2 = (implied2 / current_price - 1) * 100 if current_price > 0 else 0

            log(f"  PV Stage 1:    ${pv1:.2f} ({pv1/implied2*100:.0f}%)")
            log(f"  PV Terminal:   ${pvtv:.2f} ({pvtv/implied2*100:.0f}%)")
            log(f"  Implied Price: ${implied2:.2f}")
            log(f"  Upside/Down:   {upside2:+.1f}%")

            check(0 < implied2 < 5000,
                  f"2-Stage price in reasonable range (${implied2:.2f})", ticker)
            check(pv1 > 0, "PV Stage 1 > 0", ticker)
            check(pvtv > 0, "PV Terminal > 0", ticker)
            check(pv1 + pvtv - implied2 < 0.01,
                  "PV1 + PV_TV = implied price (math check)", ticker)

            # Projection table check
            proj = result2["projection"]
            check(len(proj) == n,
                  f"Projection table has {n} rows (got {len(proj)})", ticker)

    # ════════════════════════════════════════════════════════════
    # STEP 2C: 2-Stage with EPS × Payout
    # ════════════════════════════════════════════════════════════
    log("\n── Step 2C: 2-Stage (EPS × Payout) ──")

    eps0 = data["trailing_eps"]
    payout = data["payout_ratio"] or 0.40
    eps_g1 = g1  # same growth for simplicity
    eps_g2 = g2

    if eps0 <= 0:
        log(f"  Skipping (EPS <= 0)")
    elif eps_g2 >= ke:
        log(f"  ✗ Terminal EPS growth >= Ke")
    else:
        log(f"  EPS0=${eps0:.2f}, EPS_g1={eps_g1:.2%}, Payout={payout:.0%}")
        result3 = two_stage_ddm(
            d0, ke, g1=0, g2=g2, n=n,
            eps0=eps0, eps_growth1=eps_g1, payout1=payout,
            eps_growth2=eps_g2, payout2=payout,
            use_eps_method=True,
        )

        if result3.get("error"):
            log(f"  ERROR: {result3['error']}")
        else:
            implied3 = result3["implied_price"]
            log(f"  Implied Price: ${implied3:.2f}")
            check(implied3 > 0, f"EPS×Payout implied > 0 (${implied3:.2f})", ticker)

            # Check projection has EPS column
            proj3 = result3.get("projection")
            if proj3 is not None and len(proj3) > 0:
                check("EPS" in proj3.columns,
                      "EPS column in projection table", ticker)
                check("Payout" in proj3.columns,
                      "Payout column in projection table", ticker)

    # ════════════════════════════════════════════════════════════
    # STEP 3: Sensitivity Table
    # ════════════════════════════════════════════════════════════
    log("\n── Step 3: Sensitivity ──")

    g_base = cagr.get("5y", 0.03)
    if g_base >= ke:
        g_base = ke - 0.02  # ensure valid range for sensitivity

    df_sens = ddm_sensitivity(d0, ke, g_base, model="gordon")
    check(df_sens is not None, "Sensitivity table generated", ticker)
    check(len(df_sens) == 9, f"9 rows in sensitivity ({len(df_sens)})", ticker)
    check(len(df_sens.columns) == 9, f"9 cols in sensitivity ({len(df_sens.columns)})", ticker)

    # All values should be non-negative
    neg_count = (df_sens < 0).sum().sum()
    check(neg_count == 0, f"No negative prices in sensitivity (neg={neg_count})", ticker)

    # Middle cell should be close to gordon implied
    mid_r, mid_c = len(df_sens) // 2, len(df_sens.columns) // 2
    mid_val = df_sens.iloc[mid_r, mid_c]
    log(f"  Sensitivity center: ${mid_val:.2f}")
    log(f"  Shape: {df_sens.shape}")

    # 2-Stage sensitivity
    df_sens2 = ddm_sensitivity(d0, ke, g2, model="two_stage", g1=g1, n=n)
    check(df_sens2 is not None, "2-Stage sensitivity generated", ticker)
    log(f"  2-Stage sensitivity center: ${df_sens2.iloc[mid_r, mid_c]:.2f}")


def main():
    log("=" * 65)
    log("  DDM FULL INTEGRATION TEST")
    log("=" * 65)

    for ticker in TICKERS:
        try:
            test_ticker(ticker)
        except Exception as e:
            ISSUES.append(f"[{ticker}] EXCEPTION: {e}")
            log(f"\n  *** EXCEPTION: {e}")
            import traceback
            traceback.print_exc()

    # ════════════════════════════════════════════════════════════
    # SUMMARY
    # ════════════════════════════════════════════════════════════
    log(f"\n{'='*65}")
    log(f"  SUMMARY")
    log(f"{'='*65}")

    if ISSUES:
        log(f"\n  {len(ISSUES)} issue(s) found:")
        for issue in ISSUES:
            log(f"    ✗ {issue}")
    else:
        log(f"\n  ✓ ALL TESTS PASSED — no issues found")


if __name__ == "__main__":
    main()
