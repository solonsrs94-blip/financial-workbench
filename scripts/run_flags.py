"""Run detect_flags() on multiple tickers and dump results as JSON."""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.data.historical import get_raw_statements, get_standardized_history
from lib.analysis.historical import (
    build_income_table, build_balance_table,
    build_cashflow_table, build_ratios_table,
)
from lib.analysis.historical_flags import detect_flags

TICKERS = ["AAPL", "GOOG", "XOM", "WMT"]

# Map ticker to sector (approximate)
SECTORS = {
    "AAPL": "Technology",
    "GOOG": "Technology",
    "XOM": "Energy",
    "WMT": "Consumer Defensive",
}

results = {}

for ticker in TICKERS:
    print(f"\n{'='*60}")
    print(f"Processing {ticker}...")
    print(f"{'='*60}")
    try:
        raw = get_raw_statements(ticker)
        if raw is None:
            print(f"  ERROR: No raw statements for {ticker}")
            results[ticker] = {"error": "No raw statements"}
            continue

        std = get_standardized_history(ticker, raw_data=raw)
        if std is None:
            print(f"  ERROR: No standardized history for {ticker}")
            results[ticker] = {"error": "No standardized history"}
            continue

        years = std["years"]
        is_t = build_income_table(std, years)
        bs_t = build_balance_table(std, years)
        cf_t = build_cashflow_table(std, years)
        ratios = build_ratios_table(is_t, bs_t, cf_t)

        sector = SECTORS.get(ticker, "")
        flags = detect_flags(
            ratios, is_table=is_t, bs_table=bs_t, cf_table=cf_t,
            sector=sector, ticker=ticker,
        )

        print(f"  Found {len(flags)} flags")
        results[ticker] = {
            "flags": flags,
            "years": years,
            "sector": sector,
        }
    except Exception as e:
        print(f"  EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        results[ticker] = {"error": str(e)}

# Write to JSON for processing
output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "data", "flag_results.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults written to {output_path}")
