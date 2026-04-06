"""Test refactored Financial Preparation on 5 tickers."""

import sys, os, json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.data.historical import get_raw_statements, get_standardized_history
from lib.analysis.historical import (
    build_income_table, build_balance_table,
    build_cashflow_table, build_ratios_table,
)
from lib.analysis.historical_flags import detect_flags, compute_averages
from lib.analysis.company_classifier import classify_company

TICKERS = {
    "AAPL": ("Technology", "Consumer Electronics", "normal"),
    "JPM":  ("Financial Services", "Diversified Banks", "financial"),
    "NEE":  ("Utilities", "Electric Utilities", "dividend_stable"),
    "GOOG": ("Technology", "Internet Content & Information", "normal"),
    "O":    ("Real Estate", "REIT - Retail", "dividend_stable"),
}

results = {}

for ticker, (sector, sub_ind, expected_type) in TICKERS.items():
    print(f"\n{'='*60}")
    print(f"  {ticker} (expected: {expected_type})")
    print(f"{'='*60}")
    try:
        raw = get_raw_statements(ticker)
        if raw is None:
            print(f"  ERROR: no raw data")
            results[ticker] = {"error": "no raw data"}
            continue

        source = raw.get("source", "unknown")
        std = get_standardized_history(ticker, raw_data=raw, force_refresh=True)
        if std is None:
            print(f"  ERROR: standardization failed")
            results[ticker] = {"error": "standardization failed"}
            continue

        years = std["years"]
        is_t = build_income_table(std, years)
        bs_t = build_balance_table(std, years)
        cf_t = build_cashflow_table(std, years)
        ratios = build_ratios_table(is_t, bs_t, cf_t)
        flags = detect_flags(
            ratios, is_table=is_t, bs_table=bs_t, cf_table=cf_t,
            sector=sector, ticker=ticker,
        )
        avgs = compute_averages(ratios)
        ctype = classify_company(ticker, sector, sub_ind, ratios)

        # Check derived fields
        latest_is = is_t[-1] if is_t else {}
        latest_bs = bs_t[-1] if bs_t else {}
        latest_cf = cf_t[-1] if cf_t else {}

        ebitda = latest_is.get("ebitda")
        net_debt = latest_bs.get("net_debt")
        fcf = latest_cf.get("free_cash_flow")

        print(f"  Source: {source}")
        print(f"  Years: {len(years)} ({years[0]}-{years[-1]})")
        print(f"  Classification: {ctype['type']} (expected: {expected_type}) {'OK' if ctype['type'] == expected_type else 'MISMATCH'}")
        print(f"  Reason: {ctype['reason']}")
        print(f"  Methods: {ctype['recommended_methods']}")
        print(f"  Flags: {len(flags)}")
        for f in flags:
            print(f"    {f['year']} [{f['severity']}] {f['category']}: {f['what'][:70]}")
        print(f"  EBITDA: {'${:.1f}B'.format(ebitda/1e9) if ebitda else 'None'}")
        print(f"  Net Debt: {'${:.1f}B'.format(net_debt/1e9) if net_debt else 'None'}")
        print(f"  FCF: {'${:.1f}B'.format(fcf/1e9) if fcf else 'None'}")

        results[ticker] = {
            "source": source,
            "years": len(years),
            "year_range": f"{years[0]}-{years[-1]}",
            "classification": ctype,
            "expected_type": expected_type,
            "type_match": ctype["type"] == expected_type,
            "flags": len(flags),
            "ebitda": ebitda,
            "net_debt": net_debt,
            "fcf": fcf,
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        results[ticker] = {"error": str(e)}

# Summary
print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
for t, r in results.items():
    if "error" in r:
        print(f"  {t}: ERROR - {r['error']}")
    else:
        match = "OK" if r["type_match"] else "MISMATCH"
        print(f"  {t}: {r['classification']['type']} ({match}) | "
              f"{r['source']} {r['years']}yr | "
              f"{r['flags']} flags | "
              f"EBITDA={'${:.0f}B'.format(r['ebitda']/1e9) if r['ebitda'] else '-'} "
              f"NetDebt={'${:.0f}B'.format(r['net_debt']/1e9) if r['net_debt'] else '-'} "
              f"FCF={'${:.0f}B'.format(r['fcf']/1e9) if r['fcf'] else '-'}")

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "data", "refactoring_test.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nJSON: {out}")
