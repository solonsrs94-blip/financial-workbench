"""Large-scale flagging test — 85 companies across all sectors."""
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
    # Consumer Staples
    "PEP":  ("Consumer Defensive", "beverages - non-alcoholic"),
    "KO":   ("Consumer Defensive", "beverages - non-alcoholic"),
    "PG":   ("Consumer Defensive", "household & personal products"),
    "CL":   ("Consumer Defensive", "household & personal products"),
    "WMT":  ("Consumer Defensive", "discount stores"),
    "COST": ("Consumer Defensive", "discount stores"),
    "MDLZ": ("Consumer Defensive", "confectioners"),
    "KHC":  ("Consumer Defensive", "packaged foods"),
    "GIS":  ("Consumer Defensive", "packaged foods"),
    "HSY":  ("Consumer Defensive", "confectioners"),
    "MO":   ("Consumer Defensive", "tobacco"),
    "PM":   ("Consumer Defensive", "tobacco"),
    "STZ":  ("Consumer Defensive", "beverages - brewers"),
    "KDP":  ("Consumer Defensive", "beverages - non-alcoholic"),
    # Technology
    "AAPL": ("Technology", "consumer electronics"),
    "MSFT": ("Technology", "software - infrastructure"),
    "NVDA": ("Technology", "semiconductors"),
    "GOOG": ("Communication Services", "internet content & information"),
    "META": ("Communication Services", "internet content & information"),
    "INTC": ("Technology", "semiconductors"),
    "AMD":  ("Technology", "semiconductors"),
    "CRM":  ("Technology", "software - application"),
    "ADBE": ("Technology", "software - application"),
    "ORCL": ("Technology", "software - infrastructure"),
    "IBM":  ("Technology", "information technology services"),
    "CSCO": ("Technology", "communication equipment"),
    # Banks
    "JPM":  ("Financial Services", "banks - diversified"),
    "BAC":  ("Financial Services", "banks - diversified"),
    "WFC":  ("Financial Services", "banks - diversified"),
    "GS":   ("Financial Services", "capital markets"),
    "MS":   ("Financial Services", "capital markets"),
    "C":    ("Financial Services", "banks - diversified"),
    "USB":  ("Financial Services", "banks - regional"),
    "SCHW": ("Financial Services", "capital markets"),
    # Insurance
    "MET":  ("Financial Services", "insurance - life"),
    "PRU":  ("Financial Services", "insurance - life"),
    "ALL":  ("Financial Services", "insurance - property & casualty"),
    "AIG":  ("Financial Services", "insurance - diversified"),
    "BRK-B": ("Financial Services", "insurance - diversified"),
    # REITs
    "O":    ("Real Estate", "reit - retail"),
    "SPG":  ("Real Estate", "reit - retail"),
    "AMT":  ("Real Estate", "reit - specialty"),
    "PLD":  ("Real Estate", "reit - industrial"),
    "VICI": ("Real Estate", "reit - specialty"),
    "WPC":  ("Real Estate", "reit - diversified"),
    "EQIX": ("Real Estate", "reit - specialty"),
    # Utilities
    "DUK":  ("Utilities", "utilities - regulated electric"),
    "SO":   ("Utilities", "utilities - regulated electric"),
    "NEE":  ("Utilities", "utilities - regulated electric"),
    "AEP":  ("Utilities", "utilities - regulated electric"),
    "D":    ("Utilities", "utilities - regulated electric"),
    "SRE":  ("Utilities", "utilities - diversified"),
    "XEL":  ("Utilities", "utilities - regulated electric"),
    # Energy
    "XOM":  ("Energy", "oil & gas integrated"),
    "CVX":  ("Energy", "oil & gas integrated"),
    "COP":  ("Energy", "oil & gas exploration & production"),
    "SLB":  ("Energy", "oil & gas equipment & services"),
    "EOG":  ("Energy", "oil & gas exploration & production"),
    "PSX":  ("Energy", "oil & gas refining & marketing"),
    "VLO":  ("Energy", "oil & gas refining & marketing"),
    "OXY":  ("Energy", "oil & gas exploration & production"),
    # Healthcare
    "JNJ":  ("Healthcare", "drug manufacturers - general"),
    "UNH":  ("Healthcare", "healthcare plans"),
    "ABBV": ("Healthcare", "drug manufacturers - general"),
    "PFE":  ("Healthcare", "drug manufacturers - general"),
    "LLY":  ("Healthcare", "drug manufacturers - general"),
    "MRK":  ("Healthcare", "drug manufacturers - general"),
    "TMO":  ("Healthcare", "diagnostics & research"),
    "AMGN": ("Healthcare", "drug manufacturers - general"),
    "BMY":  ("Healthcare", "drug manufacturers - general"),
    # Industrials
    "CAT":  ("Industrials", "farm & heavy construction machinery"),
    "HON":  ("Industrials", "specialty industrial machinery"),
    "GE":   ("Industrials", "specialty industrial machinery"),
    "MMM":  ("Industrials", "conglomerates"),
    "RTX":  ("Industrials", "aerospace & defense"),
    "UPS":  ("Industrials", "integrated freight & logistics"),
    "DE":   ("Industrials", "farm & heavy construction machinery"),
    "LMT":  ("Industrials", "aerospace & defense"),
    # Consumer Discretionary
    "TSLA": ("Consumer Cyclical", "auto manufacturers"),
    "AMZN": ("Consumer Cyclical", "internet retail"),
    "HD":   ("Consumer Cyclical", "home improvement retail"),
    "MCD":  ("Consumer Cyclical", "restaurants"),
    "NKE":  ("Consumer Cyclical", "footwear & accessories"),
    "SBUX": ("Consumer Cyclical", "restaurants"),
    "DIS":  ("Communication Services", "entertainment"),
    "TGT":  ("Consumer Cyclical", "discount stores"),
    # Telecom
    "T":    ("Communication Services", "telecom services"),
    "VZ":   ("Communication Services", "telecom services"),
    "TMUS": ("Communication Services", "telecom services"),
    # Other
    "BX":   ("Financial Services", "asset management"),
    "KKR":  ("Financial Services", "asset management"),
    "COIN": ("Technology", "software - infrastructure"),
    "SQ":   ("Technology", "software - infrastructure"),
}

results = {}
errors = []
for ticker, (sector, sub_industry) in COMPANIES.items():
    print(f"Processing {ticker}...", end=" ", flush=True)
    try:
        t = yf.Ticker(ticker)
        std = standardize_yfinance(t.income_stmt, t.balance_sheet, t.cashflow)
        if std is None:
            print("NO DATA")
            errors.append(ticker)
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
        r = ratios[-1] if ratios else {}
        eq = None
        if bs_t:
            eq = bs_t[-1].get("total_equity")
        results[ticker] = {
            "sector": sector,
            "sub_industry": sub_industry,
            "classification": ct.get("type", ""),
            "industry_match": ind_avg.get("industry_name") if ind_avg else None,
            "n_firms": ind_avg.get("n_firms") if ind_avg else None,
            "metrics": {
                "ebit_margin": round(r.get("ebit_margin") or 0, 4) or None,
                "net_margin": round(r.get("net_margin") or 0, 4) or None,
                "debt_ebitda": round(r.get("debt_ebitda") or 0, 2) or None,
                "payout_ratio": round(r.get("payout_ratio") or 0, 4) or None,
                "roe": round(r.get("roe") or 0, 4) or None,
                "fcf_conversion": round(r.get("fcf_conversion") or 0, 4) or None,
                "revenue_growth": round(r.get("revenue_growth") or 0, 4) or None,
                "equity": round(eq / 1e9, 1) if eq else None,
            },
            "flag_count": len(flags),
            "flags": [
                {"severity": f["severity"], "year": f["year"],
                 "category": f["category"], "what": f["what"]}
                for f in flags
            ],
        }
        print(f"OK — {len(flags)} flags")
    except Exception as e:
        print(f"ERROR: {e}")
        errors.append(ticker)
    time.sleep(0.2)

# Save
out_dir = os.path.join(os.path.dirname(__file__), "..", "test_results")
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, "flags_test_85.json"), "w") as f:
    json.dump(results, f, indent=2)

# Summary table
print(f"\n{'='*90}")
print(f"{'TICKER':<7} {'TYPE':<16} {'INDUSTRY':<35} {'FLAGS':>5} {'EQ($B)':>8}")
print(f"{'='*90}")
for ticker, d in results.items():
    eq = d["metrics"].get("equity")
    eq_s = f"{eq:.1f}" if eq else "—"
    print(f"{ticker:<7} {d['classification']:<16} "
          f"{(d['industry_match'] or '?'):<35} {d['flag_count']:>5} {eq_s:>8}")

# Detailed flags
print(f"\n{'='*90}")
print("DETAILED FLAGS")
print(f"{'='*90}")
for ticker, d in results.items():
    if not d.get("flags"):
        continue
    m = d["metrics"]
    print(f"\n{ticker} ({d['classification']}, {d.get('industry_match','?')}):")
    parts = []
    if m.get("ebit_margin"): parts.append(f"EBIT={m['ebit_margin']*100:.1f}%")
    if m.get("debt_ebitda"): parts.append(f"D/EBITDA={m['debt_ebitda']:.1f}x")
    if m.get("payout_ratio"): parts.append(f"Pay={m['payout_ratio']*100:.0f}%")
    if m.get("roe"): parts.append(f"ROE={m['roe']*100:.1f}%")
    if m.get("equity") is not None: parts.append(f"Eq=${m['equity']:.1f}B")
    if parts: print(f"  {', '.join(parts)}")
    for f in d["flags"]:
        print(f"  [{f['severity']:6s}] {f['year']} {f['category']:8s} | {f['what']}")

if errors:
    print(f"\nERRORS/SKIPPED: {', '.join(errors)}")
print(f"\nTotal: {len(results)} companies, {sum(d['flag_count'] for d in results.values())} flags")
