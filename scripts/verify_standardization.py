"""Full standardization verification — extract all data for comparison."""

import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.data.historical import get_raw_statements, get_standardized_history
from lib.analysis.historical import (
    build_income_table, build_balance_table,
    build_cashflow_table, build_ratios_table,
)

TICKERS = ["AAPL", "MSFT", "XOM"]

all_results = {}

for ticker in TICKERS:
    print(f"\n{'='*60}")
    print(f"  {ticker}")
    print(f"{'='*60}")

    raw = get_raw_statements(ticker)
    if raw is None:
        print("  ERROR: no raw data")
        continue

    std = get_standardized_history(ticker, raw_data=raw, force_refresh=True)
    if std is None:
        print("  ERROR: standardization failed")
        continue

    years = std["years"]
    is_t = build_income_table(std, years)
    bs_t = build_balance_table(std, years)
    cf_t = build_cashflow_table(std, years)

    # Collect raw EDGAR labels + values for latest 2 years
    result = {
        "source": std.get("source"),
        "years": years,
        "raw_labels": {},
        "standardized": {},
        "audit": {},
        "tables": {},
    }

    # Raw DataFrames — show all labels and values
    for stmt_name in ["income", "balance", "cashflow"]:
        df = raw.get(stmt_name)
        if df is not None:
            raw_data = {}
            for yr_col in df.columns:
                yr = str(yr_col)[:4]
                raw_data[yr] = {}
                for label in df.index:
                    val = df.loc[label, yr_col]
                    if val is not None and str(val) != "nan":
                        raw_data[yr][str(label)] = float(val)
            result["raw_labels"][stmt_name] = raw_data

    # Standardized audit data for latest years
    for stmt_name in ["income_audit", "balance_audit", "cashflow_audit"]:
        audit = std.get(stmt_name, {})
        result["audit"][stmt_name] = {}
        for yr in years[-3:]:  # Last 3 years
            if yr in audit:
                yr_data = {}
                for k, v in audit[yr].items():
                    if isinstance(v, dict):
                        yr_data[k] = {
                            "value": v.get("value"),
                            "raw_label": v.get("raw_label"),
                            "layer": v.get("layer"),
                        }
                result["audit"][stmt_name][yr] = yr_data

    # Built tables for latest years
    for name, table in [("income", is_t), ("balance", bs_t), ("cashflow", cf_t)]:
        result["tables"][name] = {}
        if table:
            for row in table[-3:]:
                yr = row.get("year", "?")
                result["tables"][name][yr] = {
                    k: v for k, v in row.items()
                    if k != "source" and v is not None
                }

    all_results[ticker] = result
    print(f"  Years: {len(years)} ({years[0]}-{years[-1]})")
    print(f"  Source: {std.get('source')}")

    # Print IS for latest year
    latest = years[-1]
    print(f"\n  IS ({latest}):")
    is_audit = std.get("income_audit", {}).get(latest, {})
    for k in sorted(is_audit.keys()):
        v = is_audit[k]
        if isinstance(v, dict):
            val = v.get("value", 0)
            raw = v.get("raw_label", "?")
            layer = v.get("layer", "?")
            if val and abs(val) > 1:
                print(f"    {k:30s} = {val/1e6:>12,.0f}M  L{layer}  <- \"{raw}\"")
            else:
                print(f"    {k:30s} = {val:>12}  L{layer}  <- \"{raw}\"")

    print(f"\n  BS ({latest}):")
    bs_audit = std.get("balance_audit", {}).get(latest, {})
    for k in sorted(bs_audit.keys()):
        v = bs_audit[k]
        if isinstance(v, dict):
            val = v.get("value", 0)
            raw = v.get("raw_label", "?")
            layer = v.get("layer", "?")
            if val and abs(val) > 1:
                print(f"    {k:30s} = {val/1e6:>12,.0f}M  L{layer}  <- \"{raw}\"")
            else:
                print(f"    {k:30s} = {val:>12}  L{layer}  <- \"{raw}\"")

    print(f"\n  CF ({latest}):")
    cf_audit = std.get("cashflow_audit", {}).get(latest, {})
    for k in sorted(cf_audit.keys()):
        v = cf_audit[k]
        if isinstance(v, dict):
            val = v.get("value", 0)
            raw = v.get("raw_label", "?")
            layer = v.get("layer", "?")
            if val and abs(val) > 1:
                print(f"    {k:30s} = {val/1e6:>12,.0f}M  L{layer}  <- \"{raw}\"")
            else:
                print(f"    {k:30s} = {val:>12}  L{layer}  <- \"{raw}\"")

    # Cross checks
    checks = std.get("cross_checks", [])
    failed = [c for c in checks if not c.get("ok")]
    print(f"\n  Cross-checks: {len(checks)} total, {len(failed)} failed")
    for c in failed:
        print(f"    FAIL: {c}")

# Write JSON
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "data", "verification_data.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=2, default=str)
print(f"\nJSON: {out}")
