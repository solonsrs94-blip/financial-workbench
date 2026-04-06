"""Broad verification — 20 companies, full ratios + OCF/FCF check."""

import sys, os, json, warnings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings("ignore", category=FutureWarning)

from lib.data.historical import get_raw_statements, get_standardized_history
from lib.analysis.historical import (
    build_income_table, build_balance_table,
    build_cashflow_table, build_ratios_table,
)
from lib import cache

TICKERS = [
    "AAPL", "MSFT", "GOOG", "AMZN",
    "NVDA", "ADBE", "CRM", "INTC",
    "WMT", "COST", "NKE", "MCD",
    "JNJ", "UNH", "LLY",
    "CAT", "HON", "BA",
    "XOM", "CVX",
]

RATIO_KEYS = [
    "revenue_growth", "ebitda_growth",
    "gross_margin", "ebit_margin", "ebitda_margin", "net_margin", "fcf_margin",
    "effective_tax_rate",
    "dso", "dio", "dpo",
    "capex_pct", "da_pct",
    "debt_ebitda",
    "roic", "roe",
    "fcf_conversion",
]

all_results = {}

for ticker in TICKERS:
    print(f"\n{'='*60} {ticker} {'='*60}")

    try:
        cache._delete(f"std_hist:{ticker}")
    except:
        pass

    try:
        raw = get_raw_statements(ticker)
        if not raw:
            print(f"  ERROR: no raw data")
            all_results[ticker] = {"error": "no raw data"}
            continue

        std = get_standardized_history(ticker, raw_data=raw, force_refresh=True)
        if not std:
            print(f"  ERROR: standardization failed")
            all_results[ticker] = {"error": "standardization failed"}
            continue

        years = std["years"]
        is_t = build_income_table(std, years)
        bs_t = build_balance_table(std, years)
        cf_t = build_cashflow_table(std, years)
        ratios = build_ratios_table(is_t, bs_t, cf_t)

        # Build ratios grid
        grid = {}
        for rk in RATIO_KEYS:
            grid[rk] = {}
            for yr in years:
                for r in ratios:
                    if r.get("year") == yr:
                        grid[rk][yr] = r.get(rk)
                        break

        # Count coverage
        total_cells = len(RATIO_KEYS) * len(years)
        filled = sum(1 for rk in RATIO_KEYS for yr in years if grid[rk].get(yr) is not None)
        gaps = total_cells - filled

        # Print ratios table
        header = f"{'Ratio':<22s}"
        for yr in years:
            header += f" {yr:>7s}"
        print(header)
        print("-" * len(header))

        for rk in RATIO_KEYS:
            row_str = f"{rk:<22s}"
            for yr in years:
                val = grid[rk].get(yr)
                if val is not None:
                    if rk in ("dso", "dio", "dpo"):
                        row_str += f" {val:>6.0f}d"
                    elif rk == "debt_ebitda":
                        row_str += f" {val:>6.1f}x"
                    else:
                        row_str += f" {val*100:>6.1f}%"
                else:
                    row_str += "      —"
            print(row_str)

        print(f"\n  Coverage: {filled}/{total_cells} ({filled/total_cells*100:.1f}%) — {gaps} gaps")

        # OCF/FCF for latest year
        latest = years[-1]
        cf_a = std.get("cashflow_audit", {}).get(latest, {})
        is_a = std.get("income_audit", {}).get(latest, {})
        bs_a = std.get("balance_audit", {}).get(latest, {})

        def v(a, k):
            info = a.get(k, {})
            return info.get("value") if isinstance(info, dict) else None

        ocf = v(cf_a, "operating_cash_flow")
        fcf = v(cf_a, "free_cash_flow")
        capex = v(cf_a, "capital_expenditure")
        rev = v(is_a, "revenue")
        ni = v(is_a, "net_income")
        ebit = v(is_a, "ebit")
        sga = v(is_a, "sga")
        ta = v(bs_a, "total_assets")
        te = v(bs_a, "total_equity")

        print(f"  Latest ({latest}):")
        print(f"    Revenue:  {rev/1e6:>12,.0f}M" if rev else "    Revenue:  MISSING")
        print(f"    EBIT:     {ebit/1e6:>12,.0f}M" if ebit else "    EBIT:     MISSING")
        print(f"    NI:       {ni/1e6:>12,.0f}M" if ni else "    NI:       MISSING")
        print(f"    OCF:      {ocf/1e6:>12,.0f}M" if ocf else "    OCF:      MISSING")
        print(f"    CapEx:    {capex/1e6:>12,.0f}M" if capex else "    CapEx:    MISSING")
        print(f"    FCF:      {fcf/1e6:>12,.0f}M" if fcf else "    FCF:      MISSING")
        print(f"    SGA:      {sga/1e6:>12,.0f}M" if sga else "    SGA:      MISSING")
        print(f"    Assets:   {ta/1e6:>12,.0f}M" if ta else "    Assets:   MISSING")
        print(f"    Equity:   {te/1e6:>12,.0f}M" if te else "    Equity:   MISSING")

        # Identify gap reasons
        gap_reasons = {"structural": 0, "data": 0, "mapping": 0}
        gap_details = []
        for rk in RATIO_KEYS:
            for yr in years:
                if grid[rk].get(yr) is None:
                    # Structural: first year for growth ratios
                    if "growth" in rk and yr == years[0]:
                        gap_reasons["structural"] += 1
                    elif yr == years[0] and rk in ("dso", "dio", "dpo", "roic", "roe", "debt_ebitda"):
                        gap_reasons["structural"] += 1
                    else:
                        gap_reasons["data"] += 1
                        gap_details.append(f"{rk} {yr}")

        print(f"    Gap reasons: structural={gap_reasons['structural']}, data={gap_reasons['data']}")
        if gap_details and len(gap_details) <= 10:
            for g in gap_details:
                print(f"      - {g}")

        all_results[ticker] = {
            "years": years,
            "n_years": len(years),
            "coverage": filled,
            "total": total_cells,
            "coverage_pct": filled / total_cells * 100,
            "gaps": gaps,
            "ocf": ocf, "fcf": fcf, "revenue": rev, "ni": ni,
            "gap_structural": gap_reasons["structural"],
            "gap_data": gap_reasons["data"],
        }

    except Exception as e:
        print(f"  EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        all_results[ticker] = {"error": str(e)}

# Summary table
print(f"\n{'='*120}")
print(f"  SUMMARY")
print(f"{'='*120}")
print(f"{'Ticker':<8s} {'Years':>5s} {'Coverage':>10s} {'Gaps':>5s} {'Structural':>11s} {'Data':>5s} {'OCF':>12s} {'FCF':>12s}")
print(f"{'-'*8} {'-'*5} {'-'*10} {'-'*5} {'-'*11} {'-'*5} {'-'*12} {'-'*12}")
for ticker in TICKERS:
    r = all_results.get(ticker, {})
    if "error" in r:
        print(f"{ticker:<8s} ERROR: {r['error']}")
        continue
    ocf_str = f"{r['ocf']/1e6:>10,.0f}M" if r.get("ocf") else "    MISSING"
    fcf_str = f"{r['fcf']/1e6:>10,.0f}M" if r.get("fcf") else "    MISSING"
    print(f"{ticker:<8s} {r['n_years']:>5d} {r['coverage_pct']:>8.1f}% {r['gaps']:>5d} {r['gap_structural']:>11d} {r['gap_data']:>5d} {ocf_str} {fcf_str}")

# Save JSON
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "data", "broad_verification.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=2, default=str)
print(f"\nJSON saved to {out}")
