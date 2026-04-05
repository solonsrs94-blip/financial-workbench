"""Test flagging system on 40+ companies across all major sectors.

Outputs JSON results for analysis.
"""
import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import yfinance as yf
from lib.data.yfinance_standardizer import standardize_yfinance
from lib.analysis.historical import (
    build_income_table, build_balance_table,
    build_cashflow_table, build_ratios_table,
)
from lib.analysis.flags import detect_flags
from lib.analysis.company_classifier import classify_company
from lib.data.valuation_data import get_industry_averages

COMPANIES = {
    # Consumer
    "PEP":  ("Consumer Defensive", "beverages - non-alcoholic"),
    "KO":   ("Consumer Defensive", "beverages - non-alcoholic"),
    "PG":   ("Consumer Defensive", "household & personal products"),
    "CL":   ("Consumer Defensive", "household & personal products"),
    "WMT":  ("Consumer Defensive", "discount stores"),
    "COST": ("Consumer Defensive", "discount stores"),
    # Tech
    "AAPL": ("Technology", "consumer electronics"),
    "MSFT": ("Technology", "software - infrastructure"),
    "NVDA": ("Technology", "semiconductors"),
    "GOOG": ("Communication Services", "internet content & information"),
    "META": ("Communication Services", "internet content & information"),
    "INTC": ("Technology", "semiconductors"),
    # Banks
    "JPM":  ("Financial Services", "banks - diversified"),
    "BAC":  ("Financial Services", "banks - diversified"),
    "WFC":  ("Financial Services", "banks - diversified"),
    "GS":   ("Financial Services", "capital markets"),
    "C":    ("Financial Services", "banks - diversified"),
    # Insurance
    "MET":  ("Financial Services", "insurance - life"),
    "PRU":  ("Financial Services", "insurance - life"),
    "ALL":  ("Financial Services", "insurance - property & casualty"),
    # REITs
    "O":    ("Real Estate", "reit - retail"),
    "SPG":  ("Real Estate", "reit - retail"),
    "AMT":  ("Real Estate", "reit - specialty"),
    "PLD":  ("Real Estate", "reit - industrial"),
    # Utilities
    "DUK":  ("Utilities", "utilities - regulated electric"),
    "SO":   ("Utilities", "utilities - regulated electric"),
    "NEE":  ("Utilities", "utilities - regulated electric"),
    # Energy
    "XOM":  ("Energy", "oil & gas integrated"),
    "CVX":  ("Energy", "oil & gas integrated"),
    "COP":  ("Energy", "oil & gas exploration & production"),
    # Healthcare
    "JNJ":  ("Healthcare", "drug manufacturers - general"),
    "UNH":  ("Healthcare", "healthcare plans"),
    "ABBV": ("Healthcare", "drug manufacturers - general"),
    "PFE":  ("Healthcare", "drug manufacturers - general"),
    # Industrials
    "CAT":  ("Industrials", "farm & heavy construction machinery"),
    "HON":  ("Industrials", "specialty industrial machinery"),
    "GE":   ("Industrials", "specialty industrial machinery"),
    "MMM":  ("Industrials", "conglomerates"),
    # Telecom
    "T":    ("Communication Services", "telecom services"),
    "VZ":   ("Communication Services", "telecom services"),
    # Other
    "TSLA": ("Consumer Cyclical", "auto manufacturers"),
    "AMZN": ("Consumer Cyclical", "internet retail"),
    "DIS":  ("Communication Services", "entertainment"),
}

results = {}
for ticker, (sector, sub_industry) in COMPANIES.items():
    print(f"Processing {ticker}...", end=" ", flush=True)
    try:
        t = yf.Ticker(ticker)
        std = standardize_yfinance(t.income_stmt, t.balance_sheet, t.cashflow)
        if std is None:
            print("NO DATA")
            results[ticker] = {"error": "no data"}
            continue

        years = std["years"]
        is_t = build_income_table(std, years)
        bs_t = build_balance_table(std, years)
        cf_t = build_cashflow_table(std, years)
        ratios = build_ratios_table(is_t, bs_t, cf_t)
        ct = classify_company(ticker, sector, sub_industry, ratios)
        ind_avg = get_industry_averages(sub_industry)

        flags = detect_flags(
            ratios, is_table=is_t, bs_table=bs_t, cf_table=cf_t,
            sector=sector, ticker=ticker,
            industry=sub_industry, company_type=ct.get("type", ""),
            industry_averages=ind_avg,
        )

        # Collect company metrics for context
        r = ratios[-1] if ratios else {}
        metrics = {
            "ebit_margin": r.get("ebit_margin"),
            "net_margin": r.get("net_margin"),
            "debt_ebitda": r.get("debt_ebitda"),
            "payout_ratio": r.get("payout_ratio"),
            "roe": r.get("roe"),
            "interest_coverage": r.get("interest_coverage"),
            "fcf_conversion": r.get("fcf_conversion"),
            "revenue_growth": r.get("revenue_growth"),
            "current_ratio": r.get("current_ratio"),
        }

        results[ticker] = {
            "sector": sector,
            "sub_industry": sub_industry,
            "classification": ct.get("type", ""),
            "industry_match": ind_avg.get("industry_name") if ind_avg else None,
            "n_firms": ind_avg.get("n_firms") if ind_avg else None,
            "metrics": {k: round(v, 4) if v else None for k, v in metrics.items()},
            "flag_count": len(flags),
            "flags": [
                {
                    "severity": f["severity"],
                    "year": f["year"],
                    "category": f["category"],
                    "what": f["what"],
                }
                for f in flags
            ],
        }
        print(f"OK — {len(flags)} flags")
    except Exception as e:
        print(f"ERROR: {e}")
        results[ticker] = {"error": str(e)}
    time.sleep(0.3)

# Save results
out_path = os.path.join(os.path.dirname(__file__), "..", "test_results")
os.makedirs(out_path, exist_ok=True)
with open(os.path.join(out_path, "flags_baseline_40.json"), "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to test_results/flags_baseline_40.json")

# Print summary
print(f"\n{'='*80}")
print(f"{'TICKER':<6} {'TYPE':<16} {'INDUSTRY':<35} {'FLAGS':>5}")
print(f"{'='*80}")
for ticker, data in results.items():
    if "error" in data:
        print(f"{ticker:<6} ERROR: {data['error']}")
        continue
    print(f"{ticker:<6} {data['classification']:<16} "
          f"{(data['industry_match'] or '?'):<35} {data['flag_count']:>5}")

# Print all flags grouped by ticker
print(f"\n{'='*80}")
print("DETAILED FLAGS")
print(f"{'='*80}")
for ticker, data in results.items():
    if "error" in data or not data.get("flags"):
        continue
    print(f"\n{ticker} ({data['classification']}, {data.get('industry_match', '?')}):")
    m = data.get("metrics", {})
    parts = []
    if m.get("ebit_margin"): parts.append(f"EBIT margin={m['ebit_margin']*100:.1f}%")
    if m.get("debt_ebitda"): parts.append(f"D/EBITDA={m['debt_ebitda']:.1f}x")
    if m.get("payout_ratio"): parts.append(f"Payout={m['payout_ratio']*100:.0f}%")
    if m.get("roe"): parts.append(f"ROE={m['roe']*100:.1f}%")
    if parts:
        print(f"  Metrics: {', '.join(parts)}")
    for f in data["flags"]:
        print(f"  [{f['severity']:6s}] {f['year']} {f['category']:8s} | {f['what']}")
