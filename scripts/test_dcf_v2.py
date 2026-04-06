"""Test Simple DCF v2 — with fixes for systematic undervaluation.

Fixes applied:
1. SBC removed from FCF (handle via diluted shares instead — no double-counting)
2. ERP lowered to 4.5% (closer to what banks use)
3. Smarter forecast period: 7yr for growth >10%, 5yr for stable
4. Exit multiple as default terminal method (sector-based)
5. Beta cap at 1.5
"""

import sys
import json
sys.path.insert(0, ".")

import numpy as np
from lib.data.providers.yahoo_valuation import fetch_valuation_data
from lib.data.providers.yahoo import fetch_all_info
from lib.analysis.valuation.wacc import auto_wacc
from lib.analysis.valuation.dcf import build_fcf_table, run_dcf
from config.constants import SECTOR_EXIT_MULTIPLES


def avg_hist(hist, key, fallback):
    vals = [h[key] for h in hist if h.get(key) is not None and h[key] > 0]
    return sum(vals) / len(vals) if vals else fallback


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


def run_test(ticker):
    info_data = fetch_all_info(ticker)
    val_data = fetch_valuation_data(ticker)
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

    # Growth: historical avg if available, capped
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
    near_g = max(-0.10, min(rev_growth, 0.30))
    long_g = max(0.02, min(near_g * 0.4, 0.08))

    # CapEx, D&A: historical avg, capped
    if hist and len(hist) >= 2:
        capex_pct = min(avg_hist(hist, "capex_pct", 0.05), 0.15)
        da_pct = avg_hist(hist, "da_pct", 0.03)
    else:
        capex_pct = min(abs(cf.get("capex", 0) or 0) / revenue, 0.15)
        da_pct = abs(cf.get("depreciation", 0) or 0) / revenue if cf.get("depreciation") else 0.03

    # FIX 1: SBC = 0 in FCF (handle via diluted shares, not FCF deduction)
    sbc_pct = 0.0

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

    # FIX 2: Lower ERP to 4.5%, cap beta at 1.5
    rf = 0.043
    beta_capped = min(beta_raw or 1.0, 1.5)
    wacc_r = auto_wacc(rf, beta_capped, market_cap, total_debt, interest, tax_rate, erp=0.045)

    # FIX 3: Smarter forecast period
    n_years = 7 if near_g > 0.10 else 5

    growth_rates = [near_g, near_g]
    mid_years = n_years - 2
    for j in range(mid_years):
        frac = (j + 1) / (mid_years + 1)
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

    # FIX 4: Exit multiple as terminal method (sector default)
    exit_mult = SECTOR_EXIT_MULTIPLES.get(sector, 12.0)

    result = run_dcf(
        fcf_table, wacc_r, 0.025, "exit_multiple", exit_mult,
        net_debt, shares, current_price, minority, preferred,
    )

    dcf_vs_cur = (result.implied_price / current_price - 1) if current_price else 0
    dcf_vs_anl = (result.implied_price / analyst_mean - 1) if analyst_mean else None

    return {
        "ticker": ticker, "sector": sector,
        "current": round(current_price, 2),
        "dcf": round(result.implied_price, 2),
        "analyst": round(analyst_mean, 2),
        "dcf_vs_cur": dcf_vs_cur,
        "dcf_vs_anl": dcf_vs_anl,
        "growth": near_g, "margin": ebit_margin,
        "wacc": wacc_r.wacc, "capex": capex_pct,
        "da": da_pct, "sbc": sbc_pct,
        "tv_pct": result.tv_pct_of_ev,
        "n_years": n_years, "exit_mult": exit_mult,
    }


def analyze(results):
    dcf_vs_cur = [d["dcf_vs_cur"] for d in results]
    dcf_vs_anl = [d["dcf_vs_anl"] for d in results if d["dcf_vs_anl"] is not None]

    print(f"\n{'=' * 70}")
    print(f"  DCF v2 TEST — {len(results)} companies")
    print(f"  Fixes: no SBC in FCF, ERP=4.5%, beta cap=1.5,")
    print(f"         7yr for growth>10%, exit multiple terminal")
    print(f"{'=' * 70}")

    print(f"\n  DCF vs Current Price:")
    print(f"    Median: {np.median(dcf_vs_cur):+.1%}   Mean: {np.mean(dcf_vs_cur):+.1%}")
    print(f"\n  DCF vs Analyst Target:")
    print(f"    Median: {np.median(dcf_vs_anl):+.1%}   Mean: {np.mean(dcf_vs_anl):+.1%}")

    print(f"\n  Accuracy (DCF vs Analyst):")
    for pct in [5, 10, 15, 20, 30, 50]:
        n = sum(1 for x in dcf_vs_anl if -pct / 100 <= x <= pct / 100)
        print(f"    Within +/-{pct}%: {n}/{len(dcf_vs_anl)} ({n / len(dcf_vs_anl):.0%})")

    print(f"\n  Distribution (DCF vs Analyst):")
    buckets = [("<-50%", -999, -0.50), ("-50 to -30%", -0.50, -0.30),
               ("-30 to -10%", -0.30, -0.10), ("-10 to +10%", -0.10, 0.10),
               ("+10 to +30%", 0.10, 0.30), ("+30 to +50%", 0.30, 0.50),
               (">+50%", 0.50, 999)]
    for label, lo, hi in buckets:
        count = sum(1 for x in dcf_vs_anl if lo <= x < hi)
        bar = "#" * count
        print(f"    {label:>14}: {count:>3} {bar}")

    # By sector
    print(f"\n  By Sector (median DCF vs Analyst):")
    sectors = {}
    for d in results:
        s = d["sector"]
        if s not in sectors:
            sectors[s] = []
        sectors[s].append(d)
    for s in sorted(sectors.keys(), key=lambda x: abs(np.median(
            [d["dcf_vs_anl"] for d in sectors[x] if d["dcf_vs_anl"] is not None] or [0]))):
        vals = [d["dcf_vs_anl"] for d in sectors[s] if d["dcf_vs_anl"] is not None]
        if vals:
            print(f"    {s:<25} {np.median(vals):+.1%}  (n={len(vals)})")

    # Closest to analyst
    by_anl = sorted(
        [d for d in results if d["dcf_vs_anl"] is not None],
        key=lambda x: abs(x["dcf_vs_anl"]),
    )
    print(f"\n  Top 15 closest to Analyst:")
    for d in by_anl[:15]:
        print(f"    {d['ticker']:<6} DCF:${d['dcf']:>8.2f}  Anl:${d['analyst']:>8.2f}  "
              f"Diff:{d['dcf_vs_anl']:+.1%}")

    print(f"\n  Top 10 furthest from Analyst:")
    for d in by_anl[-10:]:
        print(f"    {d['ticker']:<6} DCF:${d['dcf']:>8.2f}  Anl:${d['analyst']:>8.2f}  "
              f"Diff:{d['dcf_vs_anl']:+.1%}  m={d['margin']:.0%} capex={d['capex']:.1%} w={d['wacc']:.1%}")


if __name__ == "__main__":
    results = []
    for i, t in enumerate(TICKERS):
        try:
            r = run_test(t)
            if r:
                results.append(r)
        except Exception as e:
            print(f"  {t}: ERROR {e}")
        if (i + 1) % 25 == 0:
            print(f"Progress: {i + 1}/{len(TICKERS)} ({len(results)} ok)", flush=True)

    with open("data/dcf_test_v2.json", "w") as f:
        json.dump(results, f, indent=2)

    analyze(results)
