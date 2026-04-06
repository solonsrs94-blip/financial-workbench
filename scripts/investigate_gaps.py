"""Investigate remaining gaps: DPO, intangibles, acquisitions, debt, shares."""

import sys, os, warnings
warnings.filterwarnings("ignore", category=FutureWarning)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.data.historical import get_raw_statements, get_standardized_history
from lib.analysis.historical import (
    build_income_table, build_balance_table,
    build_cashflow_table, build_ratios_table,
)
from lib import cache

TICKERS_20 = [
    "AAPL", "MSFT", "GOOG", "AMZN", "META",
    "NVDA", "ADBE", "CRM", "INTC",
    "WMT", "COST", "NKE", "MCD",
    "JNJ", "UNH", "LLY",
    "CAT", "HON", "BA",
    "XOM", "CVX",
]

def v(audit, key):
    info = audit.get(key, {})
    return info.get("value") if isinstance(info, dict) else None

def load(ticker):
    try: cache._delete(f"std_hist:{ticker}")
    except: pass
    raw = get_raw_statements(ticker)
    if not raw: return None
    return get_standardized_history(ticker, raw_data=raw, force_refresh=True)


# ==============================
# 1. DPO Investigation
# ==============================
print("=" * 80)
print("  1. DPO INVESTIGATION")
print("=" * 80)

dpo_tickers = ["META", "AAPL", "MSFT", "GOOG", "AMZN", "WMT", "NKE", "JNJ", "CAT", "XOM"]
for ticker in dpo_tickers:
    std = load(ticker)
    if not std: continue
    years = std["years"]
    is_t = build_income_table(std, years)
    bs_t = build_balance_table(std, years)
    cf_t = build_cashflow_table(std, years)
    ratios = build_ratios_table(is_t, bs_t, cf_t)

    row = f"  {ticker:6s} |"
    for yr in years[-6:]:
        dpo = None
        for r in ratios:
            if r.get("year") == yr:
                dpo = r.get("dpo")
                break
        if dpo is not None:
            row += f" {dpo:>5.0f}d"
        else:
            row += "     —"

    # Also show AP and COGS for latest 2 years
    latest = years[-1]
    prev = years[-2] if len(years) > 1 else None
    bs_l = std["balance_audit"].get(latest, {})
    is_l = std["income_audit"].get(latest, {})
    ap = v(bs_l, "accounts_payable")
    cogs = v(is_l, "cogs")
    ap_s = f"AP={ap/1e6:,.0f}M" if ap else "AP=—"
    cogs_s = f"COGS={cogs/1e6:,.0f}M" if cogs else "COGS=—"
    row += f"  | {ap_s:>15s} {cogs_s:>15s}"
    print(row)


# ==============================
# 2. Intangible Assets
# ==============================
print()
print("=" * 80)
print("  2. INTANGIBLE ASSETS")
print("=" * 80)

int_tickers = ["META", "GOOG", "MSFT", "AAPL", "AMZN", "JNJ", "ADBE", "CRM", "HON", "CAT"]
for ticker in int_tickers:
    std = load(ticker)
    if not std: continue
    years = std["years"]
    row = f"  {ticker:6s} |"
    for yr in years[-5:]:
        bs = std["balance_audit"].get(yr, {})
        ia = v(bs, "intangible_assets")
        gw = v(bs, "goodwill")
        if ia is not None:
            row += f" {ia/1e6:>7,.0f}M"
        else:
            row += "       —"
    print(row)


# ==============================
# 3. Acquisitions
# ==============================
print()
print("=" * 80)
print("  3. ACQUISITIONS")
print("=" * 80)

acq_tickers = ["META", "MSFT", "GOOG", "AMZN", "ADBE", "JNJ"]
for ticker in acq_tickers:
    std = load(ticker)
    if not std: continue
    years = std["years"]
    row = f"  {ticker:6s} |"
    for yr in years:
        cf = std["cashflow_audit"].get(yr, {})
        acq = v(cf, "acquisitions")
        if acq is not None:
            row += f" {acq/1e6:>7,.0f}M"
        else:
            row += "       —"
    print(row)


# ==============================
# 4. Total Debt gaps
# ==============================
print()
print("=" * 80)
print("  4. TOTAL DEBT ($0 vs —)")
print("=" * 80)

debt_tickers = ["META", "GOOG", "NVDA", "AMZN", "ADBE"]
for ticker in debt_tickers:
    std = load(ticker)
    if not std: continue
    years = std["years"]
    row = f"  {ticker:6s} |"
    for yr in years:
        bs = std["balance_audit"].get(yr, {})
        td = v(bs, "total_debt")
        ltd = v(bs, "long_term_debt")
        std_debt = v(bs, "short_term_debt")
        cpltd = v(bs, "current_portion_ltd")
        if td is not None:
            row += f" {td/1e6:>7,.0f}M"
        elif ltd is not None or std_debt is not None:
            # Components exist but total doesn't
            row += " COMPS!"
        else:
            row += "       —"
    print(row)
    # Show components for latest year
    bs_l = std["balance_audit"].get(years[-1], {})
    print(f"         LTD={v(bs_l,'long_term_debt')}, STD={v(bs_l,'short_term_debt')}, CPLTD={v(bs_l,'current_portion_ltd')}")


# ==============================
# 5. Shares Outstanding on BS
# ==============================
print()
print("=" * 80)
print("  5. SHARES OUTSTANDING ON BS")
print("=" * 80)

for ticker in TICKERS_20[:15]:
    std = load(ticker)
    if not std: continue
    years = std["years"]
    latest = years[-1]
    bs = std["balance_audit"].get(latest, {})
    shares = v(bs, "shares_outstanding")
    is_a = std["income_audit"].get(latest, {})
    dil_shares = v(is_a, "diluted_shares")

    shares_s = f"{shares/1e6:,.0f}M" if shares else "MISSING"
    dil_s = f"{dil_shares/1e6:,.0f}M" if dil_shares else "MISSING"
    print(f"  {ticker:6s} | BS shares: {shares_s:>12s} | IS diluted: {dil_s:>12s}")


# ==============================
# 6. FULL GAP AUDIT — 20 companies
# ==============================
print()
print("=" * 80)
print("  6. FULL GAP AUDIT — Template lines that are '—'")
print("=" * 80)

# Template lines that should be present for most companies
EXPECTED_IS = ["revenue", "cogs", "gross_profit", "sga", "rd", "ebit", "ebitda",
               "pretax_income", "tax_provision", "net_income", "diluted_eps", "diluted_shares"]
EXPECTED_BS = ["cash", "accounts_receivable", "inventories", "total_current_assets",
               "pp_and_e", "total_assets", "accounts_payable", "total_current_liabilities",
               "long_term_debt", "total_liabilities", "total_equity", "total_debt", "net_debt"]
EXPECTED_CF = ["operating_cash_flow", "capital_expenditure", "free_cash_flow",
               "depreciation_amortization", "stock_based_compensation",
               "dividends_paid", "investing_cash_flow", "financing_cash_flow"]

all_gaps = []

for ticker in TICKERS_20:
    std = load(ticker)
    if not std:
        print(f"  {ticker}: FAILED TO LOAD")
        continue
    years = std["years"]
    latest = years[-1]

    # Check latest year for gaps
    is_a = std["income_audit"].get(latest, {})
    bs_a = std["balance_audit"].get(latest, {})
    cf_a = std["cashflow_audit"].get(latest, {})

    gaps = []
    for key in EXPECTED_IS:
        if v(is_a, key) is None:
            gaps.append(("IS", key))
    for key in EXPECTED_BS:
        if v(bs_a, key) is None:
            gaps.append(("BS", key))
    for key in EXPECTED_CF:
        if v(cf_a, key) is None:
            gaps.append(("CF", key))

    if gaps:
        gap_str = ", ".join(f"{stmt}:{k}" for stmt, k in gaps)
        print(f"  {ticker:6s} ({latest}) [{len(gaps)} gaps]: {gap_str}")
        for stmt, k in gaps:
            all_gaps.append((ticker, latest, stmt, k))
    else:
        print(f"  {ticker:6s} ({latest}) [0 gaps] ✅")

print()
print(f"  Total gaps across {len(TICKERS_20)} companies: {len(all_gaps)}")
print()

# Aggregate: which lines are most commonly missing?
from collections import Counter
gap_counter = Counter(f"{s}:{k}" for _, _, s, k in all_gaps)
print("  Most common gaps:")
for gap, count in gap_counter.most_common(15):
    tickers_with_gap = [t for t, _, s, k in all_gaps if f"{s}:{k}" == gap]
    print(f"    {gap:30s}: {count:2d} companies — {tickers_with_gap}")
