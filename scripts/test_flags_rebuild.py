"""Test rebuilt flagging system on 4 tickers."""

import sys, os, json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.data.historical import get_raw_statements, get_standardized_history
from lib.analysis.historical import (
    build_income_table, build_balance_table,
    build_cashflow_table, build_ratios_table,
)
from lib.analysis.historical_flags import detect_flags

TICKERS = ["AAPL", "GOOG", "XOM", "WMT"]
SECTORS = {"AAPL": "Technology", "GOOG": "Technology",
           "XOM": "Energy", "WMT": "Consumer Defensive"}

results = {}

for ticker in TICKERS:
    print(f"\n{'='*60}")
    print(f"  {ticker}")
    print(f"{'='*60}")
    try:
        raw = get_raw_statements(ticker)
        std = get_standardized_history(ticker, raw_data=raw, force_refresh=True)
        if std is None:
            print("  ERROR: no standardized data")
            results[ticker] = {"error": "no data"}
            continue

        years = std["years"]
        is_t = build_income_table(std, years)
        bs_t = build_balance_table(std, years)
        cf_t = build_cashflow_table(std, years)
        ratios = build_ratios_table(is_t, bs_t, cf_t)

        flags = detect_flags(
            ratios, is_table=is_t, bs_table=bs_t, cf_table=cf_t,
            sector=SECTORS.get(ticker, ""), ticker=ticker,
        )

        print(f"  Total flags: {len(flags)}")
        high = [f for f in flags if f["severity"] == "high"]
        med = [f for f in flags if f["severity"] == "medium"]
        low = [f for f in flags if f["severity"] == "low"]
        print(f"  High: {len(high)}, Medium: {len(med)}, Low: {len(low)}")

        # Count by category
        cats = {}
        for f in flags:
            cats[f["category"]] = cats.get(f["category"], 0) + 1
        print(f"  Categories: {cats}")

        print()
        for f in flags:
            pc = f.get("possible_causes")
            pc_str = f" causes={pc}" if pc else ""
            imp = f.get("impact_mn")
            imp_str = f" impact=${imp:.0f}M" if imp else ""
            print(f"  [{f['severity'].upper():6}] {f['year']} | "
                  f"{f['category']:10} | {f['what']}{imp_str}{pc_str}")

        results[ticker] = {
            "total": len(flags),
            "high": len(high),
            "medium": len(med),
            "low": len(low),
            "categories": cats,
            "flags": flags,
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        results[ticker] = {"error": str(e)}

# Write JSON
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "data", "flags_rebuild_test.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nJSON: {out}")
