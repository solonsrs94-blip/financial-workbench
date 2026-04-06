"""Iterative DCF optimization — run test, analyze, adjust, repeat.

Each iteration:
1. Run DCF on all companies with current parameters
2. Analyze results — identify systematic biases
3. Adjust parameters to correct biases
4. Repeat
"""

import sys
import json
import copy
sys.path.insert(0, ".")

import numpy as np
from lib.data.providers.yahoo_valuation import fetch_valuation_data
from lib.data.providers.yahoo import fetch_all_info
from lib.analysis.valuation.wacc import auto_wacc
from lib.analysis.valuation.dcf import build_fcf_table, run_dcf


TICKERS = [
    "MSFT", "AAPL", "GOOG", "ADBE", "CRM", "ORCL", "CSCO", "TXN", "INTU", "NOW",
    "PANW", "QCOM", "IBM", "CDNS", "SNPS", "FTNT", "ANET", "WDAY",
    "JNJ", "ABBV", "MRK", "PFE", "TMO", "ABT", "AMGN", "GILD", "ZTS", "VRTX",
    "MDT", "SYK", "BSX", "ISRG", "REGN", "DXCM", "IDXX", "EW", "A", "IQV",
    "PG", "KO", "PEP", "CL", "MDLZ", "GIS", "HSY", "KMB", "CHD", "SJM",
    "MKC", "HRL", "CAG", "CPB", "CLX",
    "NKE", "SBUX", "YUM", "CMG", "ORLY", "AZO", "ROST", "TJX", "DG", "DLTR",
    "HON", "MMM", "EMR", "ITW", "ROK", "CTAS", "FAST", "WM", "RSG", "GWW",
    "SHW", "ECL", "APD", "LIN", "PCAR",
    "NFLX", "DIS", "CMCSA",
    "V", "MA", "AXP", "FIS", "FISV", "GPN", "BR",
    "ACN", "SPGI", "MCO", "MSCI", "ICE", "CME", "VRSK", "FDS", "MKTX", "TRU",
]

# Starting parameters (from v2)
DEFAULT_PARAMS = {
    "erp": 0.045,
    "beta_cap": 1.5,
    "sbc_in_fcf": False,       # Don't deduct SBC from FCF
    "capex_cap": 0.15,
    "terminal_growth": 0.025,
    "terminal_method": "exit_multiple",
    "growth_cap": 0.30,
    "growth_floor": -0.10,
    "long_growth_multiplier": 0.4,  # long_g = near_g * this
    "long_growth_min": 0.02,
    "long_growth_max": 0.08,
    "n_years_growth_threshold": 0.10,  # >10% growth -> 7yr, else 5yr
    "n_years_high": 7,
    "n_years_low": 5,
    # Per-sector exit multiples (adjustable)
    "exit_multiples": {
        "Technology": 18.0,
        "Communication Services": 14.0,
        "Healthcare": 14.0,
        "Consumer Cyclical": 12.0,
        "Consumer Defensive": 12.0,
        "Financial Services": 10.0,
        "Industrials": 11.0,
        "Energy": 7.0,
        "Utilities": 10.0,
        "Real Estate": 15.0,
        "Basic Materials": 8.0,
    },
}


def avg_hist(hist, key, fallback):
    vals = [h[key] for h in hist if h.get(key) is not None and h[key] > 0]
    return sum(vals) / len(vals) if vals else fallback


# Cache raw data so we don't refetch every iteration
RAW_DATA_CACHE = {}

def fetch_raw(ticker):
    if ticker in RAW_DATA_CACHE:
        return RAW_DATA_CACHE[ticker]
    info_data = fetch_all_info(ticker)
    val_data = fetch_valuation_data(ticker)
    RAW_DATA_CACHE[ticker] = (info_data, val_data)
    return info_data, val_data


def run_single(ticker, params):
    """Run DCF for one ticker with given parameters."""
    info_data, val_data = fetch_raw(ticker)
    if not info_data or not val_data:
        return None

    inc = val_data.get("income_detail", {})
    bs = val_data.get("balance_sheet", {})
    cf = val_data.get("cash_flow", {})
    wc = val_data.get("working_capital", {})
    hist = val_data.get("historical_margins", [])

    price_data = info_data.get("price", {})
    ratios_data = info_data.get("ratios", {})
    info_sec = info_data.get("info", {})

    current_price = price_data.get("price", 0)
    market_cap = price_data.get("market_cap", 0)
    beta_raw = price_data.get("beta", 1.0)
    shares = val_data.get("shares") or ratios_data.get("shares_outstanding") or 1
    revenue = inc.get("revenue", 0)
    sector = info_sec.get("sector", "")
    analyst_mean = price_data.get("target_mean", 0) or 0

    if not revenue or revenue <= 0 or not current_price:
        return None

    ebit_margin = inc.get("ebit", 0) / revenue if inc.get("ebit") else 0.15
    cogs_pct = abs(inc.get("cogs", 0)) / revenue if inc.get("cogs") else 0.60

    # Growth
    rev_growth = ratios_data.get("revenue_growth") or 0.05
    if hist and len(hist) >= 3:
        hist_growths = []
        for j in range(len(hist) - 1):
            r1 = hist[j].get("revenue")
            r2 = hist[j + 1].get("revenue")
            if r1 and r2 and r2 > 0:
                hist_growths.append(r1 / r2 - 1)
        if hist_growths:
            rev_growth = sum(hist_growths) / len(hist_growths)

    near_g = max(params["growth_floor"], min(rev_growth, params["growth_cap"]))
    long_g = max(params["long_growth_min"],
                 min(near_g * params["long_growth_multiplier"], params["long_growth_max"]))

    # CapEx, D&A
    if hist and len(hist) >= 2:
        capex_pct = min(avg_hist(hist, "capex_pct", 0.05), params["capex_cap"])
        da_pct = avg_hist(hist, "da_pct", 0.03)
    else:
        capex_pct = min(abs(cf.get("capex", 0) or 0) / revenue, params["capex_cap"])
        da_pct = abs(cf.get("depreciation", 0) or 0) / revenue if cf.get("depreciation") else 0.03

    sbc_pct = 0.0 if not params["sbc_in_fcf"] else min(
        avg_hist(hist, "sbc_pct", 0.01) if hist and len(hist) >= 2 else 0.01, 0.08)

    tax_rate = inc.get("effective_tax_rate") or 0.21
    if tax_rate > 0.40 or tax_rate < 0:
        tax_rate = 0.21

    total_debt = bs.get("total_debt", 0) or 0
    net_debt = bs.get("net_debt", 0) or 0
    interest = abs(inc.get("interest_expense", 0) or 0)
    minority = bs.get("minority_interest", 0) or 0
    preferred = bs.get("preferred_equity", 0) or 0

    dso = wc.get("dso") or 45
    dio = wc.get("dio") or 30
    dpo = wc.get("dpo") or 40

    beta_capped = min(beta_raw or 1.0, params["beta_cap"])
    rf = 0.043
    wacc_r = auto_wacc(rf, beta_capped, market_cap, total_debt, interest, tax_rate,
                       erp=params["erp"])

    n_years = params["n_years_high"] if near_g > params["n_years_growth_threshold"] else params["n_years_low"]

    growth_rates = [near_g, near_g]
    mid = n_years - 2
    for j in range(mid):
        frac = (j + 1) / (mid + 1)
        growth_rates.append(near_g + (long_g - near_g) * frac)
    growth_rates = growth_rates[:n_years]
    margins = [ebit_margin] * n_years

    fcf_table = build_fcf_table(
        base_revenue=revenue, n_years=n_years,
        growth_rates=growth_rates, ebit_margins=margins,
        tax_rate=tax_rate, capex_pcts=[capex_pct] * n_years,
        da_pcts=[da_pct] * n_years, sbc_pcts=[sbc_pct] * n_years,
        dso=[dso] * n_years, dio=[dio] * n_years, dpo=[dpo] * n_years,
        base_cogs_pct=cogs_pct,
    )

    exit_mult = params["exit_multiples"].get(sector, 12.0)
    result = run_dcf(
        fcf_table, wacc_r, params["terminal_growth"],
        params["terminal_method"], exit_mult,
        net_debt, shares, current_price, minority, preferred,
    )

    dcf_vs_cur = (result.implied_price / current_price - 1) if current_price else 0
    dcf_vs_anl = (result.implied_price / analyst_mean - 1) if analyst_mean else None

    return {
        "ticker": ticker, "sector": sector,
        "dcf_vs_cur": dcf_vs_cur, "dcf_vs_anl": dcf_vs_anl,
        "dcf": result.implied_price, "analyst": analyst_mean,
        "current": current_price,
        "growth": near_g, "margin": ebit_margin,
        "wacc": wacc_r.wacc, "capex": capex_pct,
    }


def run_all(params):
    """Run DCF for all tickers. Returns list of results."""
    results = []
    for t in TICKERS:
        try:
            r = run_single(t, params)
            if r:
                results.append(r)
        except Exception:
            pass
    return results


def analyze(results):
    """Analyze results and return diagnostics."""
    dcf_vs_anl = [d["dcf_vs_anl"] for d in results if d["dcf_vs_anl"] is not None]
    dcf_vs_cur = [d["dcf_vs_cur"] for d in results]

    # Overall
    median_anl = np.median(dcf_vs_anl) if dcf_vs_anl else 0
    mean_anl = np.mean(dcf_vs_anl) if dcf_vs_anl else 0
    within_10 = sum(1 for x in dcf_vs_anl if -0.10 <= x <= 0.10)
    within_20 = sum(1 for x in dcf_vs_anl if -0.20 <= x <= 0.20)
    within_30 = sum(1 for x in dcf_vs_anl if -0.30 <= x <= 0.30)

    # By sector
    sectors = {}
    for d in results:
        s = d["sector"]
        if s not in sectors:
            sectors[s] = []
        sectors[s].append(d)

    sector_medians = {}
    for s, items in sectors.items():
        vals = [d["dcf_vs_anl"] for d in items if d["dcf_vs_anl"] is not None]
        if vals:
            sector_medians[s] = np.median(vals)

    # Outliers (|diff| > 50%)
    outliers = [d for d in results if d["dcf_vs_anl"] is not None and abs(d["dcf_vs_anl"]) > 0.50]

    return {
        "median_vs_anl": median_anl,
        "mean_vs_anl": mean_anl,
        "within_10": within_10,
        "within_20": within_20,
        "within_30": within_30,
        "total": len(dcf_vs_anl),
        "sector_medians": sector_medians,
        "outliers": len(outliers),
        "median_vs_cur": np.median(dcf_vs_cur),
    }


def adjust_params(params, diag, iteration):
    """Adjust parameters based on diagnostic results."""
    p = copy.deepcopy(params)
    changes = []

    overall_bias = diag["median_vs_anl"]

    # If we're systematically under/over-valuing, adjust ERP
    if overall_bias < -0.15:
        old = p["erp"]
        p["erp"] = max(0.03, p["erp"] - 0.003)
        changes.append(f"ERP {old:.3f} -> {p['erp']:.3f} (undervaluing)")
    elif overall_bias > 0.15:
        old = p["erp"]
        p["erp"] = min(0.07, p["erp"] + 0.003)
        changes.append(f"ERP {old:.3f} -> {p['erp']:.3f} (overvaluing)")

    # Adjust beta cap if still undervaluing
    if overall_bias < -0.20 and p["beta_cap"] > 1.1:
        old = p["beta_cap"]
        p["beta_cap"] = max(1.1, p["beta_cap"] - 0.1)
        changes.append(f"Beta cap {old:.1f} -> {p['beta_cap']:.1f}")

    # Adjust sector exit multiples based on sector bias
    for sector, median_bias in diag["sector_medians"].items():
        if sector not in p["exit_multiples"]:
            continue
        old_mult = p["exit_multiples"][sector]
        if median_bias < -0.30:
            new_mult = min(old_mult * 1.15, 35.0)
            p["exit_multiples"][sector] = round(new_mult, 1)
            changes.append(f"{sector} exit mult {old_mult:.1f} -> {new_mult:.1f}")
        elif median_bias > 0.30:
            new_mult = max(old_mult * 0.85, 4.0)
            p["exit_multiples"][sector] = round(new_mult, 1)
            changes.append(f"{sector} exit mult {old_mult:.1f} -> {new_mult:.1f}")

    # Adjust growth params if growth companies are outliers
    if overall_bias < -0.10:
        old = p["long_growth_multiplier"]
        p["long_growth_multiplier"] = min(0.6, p["long_growth_multiplier"] + 0.03)
        if old != p["long_growth_multiplier"]:
            changes.append(f"Long growth mult {old:.2f} -> {p['long_growth_multiplier']:.2f}")

    # Adjust terminal growth if mostly undervaluing
    if overall_bias < -0.15 and p["terminal_growth"] < 0.035:
        old = p["terminal_growth"]
        p["terminal_growth"] = min(0.035, p["terminal_growth"] + 0.002)
        changes.append(f"Terminal growth {old:.3f} -> {p['terminal_growth']:.3f}")

    # Extend forecast period if undervaluing growth companies
    if overall_bias < -0.20 and p["n_years_high"] < 10:
        old = p["n_years_high"]
        p["n_years_high"] = min(10, p["n_years_high"] + 1)
        changes.append(f"High-growth years {old} -> {p['n_years_high']}")

    # Lower capex cap if still too aggressive
    if overall_bias < -0.20 and p["capex_cap"] > 0.10:
        old = p["capex_cap"]
        p["capex_cap"] = max(0.10, p["capex_cap"] - 0.01)
        changes.append(f"CapEx cap {old:.2f} -> {p['capex_cap']:.2f}")

    return p, changes


def print_summary(iteration, diag, changes, params):
    n = diag["total"]
    print(f"\n--- Iteration {iteration} ---")
    print(f"  Median vs Analyst: {diag['median_vs_anl']:+.1%}  |  "
          f"Within ±10%: {diag['within_10']}/{n} ({diag['within_10']/n:.0%})  |  "
          f"Within ±20%: {diag['within_20']}/{n} ({diag['within_20']/n:.0%})  |  "
          f"Within ±30%: {diag['within_30']}/{n} ({diag['within_30']/n:.0%})  |  "
          f"Outliers>50%: {diag['outliers']}")
    if changes:
        print(f"  Changes: {'; '.join(changes)}")
    else:
        print(f"  No changes (converged)")


if __name__ == "__main__":
    MAX_ITERATIONS = 10

    # Fetch all data first
    print("Fetching data for all tickers...")
    for i, t in enumerate(TICKERS):
        try:
            fetch_raw(t)
        except Exception:
            pass
        if (i + 1) % 25 == 0:
            print(f"  Fetched {i + 1}/{len(TICKERS)}", flush=True)

    params = copy.deepcopy(DEFAULT_PARAMS)
    best_score = 0
    best_params = None
    best_iteration = 0

    for iteration in range(1, MAX_ITERATIONS + 1):
        results = run_all(params)
        diag = analyze(results)

        changes = []
        if iteration > 1:
            params, changes = adjust_params(params, diag, iteration)

        print_summary(iteration, diag, changes, params)

        # Track best by within ±20%
        score = diag["within_20"]
        if score >= best_score:
            best_score = score
            best_params = copy.deepcopy(params)
            best_iteration = iteration

        if not changes and iteration > 1:
            print(f"\n  Converged at iteration {iteration}!")
            break

        # Apply changes for next iteration
        if iteration == 1:
            params, changes = adjust_params(params, diag, iteration)
            if changes:
                print(f"  Initial adjustments: {'; '.join(changes)}")

    # Final results with best params
    print(f"\n{'='*70}")
    print(f"  FINAL RESULTS — Best iteration: {best_iteration}")
    print(f"{'='*70}")

    results = run_all(best_params)
    diag = analyze(results)
    dcf_vs_anl = [d["dcf_vs_anl"] for d in results if d["dcf_vs_anl"] is not None]

    print(f"\n  Median DCF vs Analyst: {diag['median_vs_anl']:+.1%}")
    print(f"  Within ±5%:  {sum(1 for x in dcf_vs_anl if -0.05 <= x <= 0.05)}/{len(dcf_vs_anl)}")
    print(f"  Within ±10%: {diag['within_10']}/{diag['total']}")
    print(f"  Within ±20%: {diag['within_20']}/{diag['total']}")
    print(f"  Within ±30%: {diag['within_30']}/{diag['total']}")

    print(f"\n  Optimized Parameters:")
    for key in ["erp", "beta_cap", "capex_cap", "terminal_growth",
                 "long_growth_multiplier", "n_years_high", "n_years_low"]:
        print(f"    {key}: {best_params[key]}")
    print(f"    Exit multiples:")
    for s, m in sorted(best_params["exit_multiples"].items()):
        print(f"      {s}: {m}")

    # Sector breakdown
    print(f"\n  By Sector:")
    sectors = {}
    for d in results:
        s = d["sector"]
        if s not in sectors:
            sectors[s] = []
        sectors[s].append(d)
    for s in sorted(sectors.keys()):
        vals = [d["dcf_vs_anl"] for d in sectors[s] if d["dcf_vs_anl"] is not None]
        if vals:
            w10 = sum(1 for x in vals if -0.10 <= x <= 0.10)
            print(f"    {s:<25} median: {np.median(vals):+.1%}  within±10%: {w10}/{len(vals)}")

    # Save best params
    save_params = {k: v for k, v in best_params.items()}
    with open("data/dcf_optimized_params.json", "w") as f:
        json.dump(save_params, f, indent=2)
    print(f"\n  Saved optimized params to data/dcf_optimized_params.json")
