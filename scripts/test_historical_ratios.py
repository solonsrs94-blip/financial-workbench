"""Test ratios across all years for GOOG, AAPL, MSFT, XOM."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.data.historical import get_raw_statements, get_standardized_history
from lib.analysis.historical import (
    build_income_table, build_balance_table,
    build_cashflow_table, build_ratios_table,
)
from lib import cache

TICKERS = ["GOOG", "AAPL", "MSFT", "XOM"]

for ticker in TICKERS:
    print(f"\n{'='*120}")
    print(f"  {ticker}")
    print(f"{'='*120}")

    try:
        cache._delete(f"std_hist:{ticker}")
    except:
        pass

    raw = get_raw_statements(ticker)
    std = get_standardized_history(ticker, raw_data=raw, force_refresh=True)
    if not std:
        print("  ERROR")
        continue

    years = std["years"]
    is_t = build_income_table(std, years)
    bs_t = build_balance_table(std, years)
    cf_t = build_cashflow_table(std, years)
    ratios = build_ratios_table(is_t, bs_t, cf_t)

    # Key ratios to check
    ratio_keys = [
        "revenue_growth", "ebitda_margin", "gross_margin", "ebit_margin",
        "net_margin", "fcf_margin", "effective_tax_rate",
        "dso", "dpo", "capex_pct", "da_pct",
        "debt_ebitda", "roic", "roe", "fcf_conversion",
    ]

    # Print header
    header = f"{'Ratio':<22s}"
    for yr in years:
        header += f" {yr:>7s}"
    print(header)
    print("-" * len(header))

    for rk in ratio_keys:
        row = f"{rk:<22s}"
        for yr in years:
            # Find ratio for this year
            val = None
            for r in ratios:
                if r.get("year") == yr:
                    val = r.get(rk)
                    break
            if val is not None:
                if rk in ("dso", "dpo"):
                    row += f" {val:>6.0f}d"
                elif rk == "debt_ebitda":
                    row += f" {val:>6.1f}x"
                else:
                    row += f" {val*100:>6.1f}%"
            else:
                row += "      —"
        print(row)

    # Count gaps
    total_cells = len(ratio_keys) * len(years)
    filled = 0
    for rk in ratio_keys:
        for yr in years:
            for r in ratios:
                if r.get("year") == yr and r.get(rk) is not None:
                    filled += 1
                    break
    gaps = total_cells - filled
    print(f"\n  Coverage: {filled}/{total_cells} ({filled/total_cells*100:.1f}%) — {gaps} gaps")

    # Verify latest year key values
    latest = years[-1]
    is_a = std.get("income_audit", {}).get(latest, {})
    cf_a = std.get("cashflow_audit", {}).get(latest, {})
    def v(a, k):
        info = a.get(k, {})
        return info.get("value") if isinstance(info, dict) else None

    rev = v(is_a, "revenue")
    ocf = v(cf_a, "operating_cash_flow")
    fcf = v(cf_a, "free_cash_flow")
    da = v(cf_a, "depreciation_amortization") or v(cf_a, "depreciation")
    eps = v(is_a, "diluted_eps")

    print(f"  Latest ({latest}): Rev={rev/1e6:,.0f}M OCF={ocf/1e6:,.0f}M FCF={fcf/1e6:,.0f}M", end="")
    if da:
        print(f" D&A={da/1e6:,.0f}M", end="")
    if eps:
        print(f" EPS={eps:.2f}", end="")
    print()

    # Cross-checks
    checks = std.get("cross_checks", [])
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        print(f"  Cross-check failures: {len(failed)}")
        for c in failed[:3]:
            print(f"    {c['year']} {c['check']}: diff={c.get('diff',0)/1e6:,.0f}M")

    # Layer 4 count for latest year
    l4_count = 0
    for stmt_name in ["income_audit", "balance_audit", "cashflow_audit"]:
        audit = std.get(stmt_name, {}).get(latest, {})
        for k, val in audit.items():
            if isinstance(val, dict) and val.get("layer") == 4:
                l4_count += 1
    print(f"  Layer 4 items ({latest}): {l4_count}")
