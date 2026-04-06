"""Test standardizer v2 on 10 tickers."""

import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.data.historical import get_raw_statements, get_standardized_history
from lib import cache

TICKERS = ["AAPL", "MSFT", "GOOG", "AMZN", "XOM", "WMT", "PG", "JNJ", "META", "NVDA"]

results = {}

for ticker in TICKERS:
    print(f"\n{'='*70}")
    print(f"  {ticker}")
    print(f"{'='*70}")

    try:
        cache._delete(f"std_hist:{ticker}")
    except:
        pass

    raw = get_raw_statements(ticker)
    if not raw:
        print("  ERROR: no raw data")
        results[ticker] = {"error": "no raw data"}
        continue

    std = get_standardized_history(ticker, raw_data=raw, force_refresh=True)
    if not std:
        print("  ERROR: standardization failed")
        results[ticker] = {"error": "standardization failed"}
        continue

    years = std["years"]
    latest = years[-1]

    def val(audit, k):
        info = audit.get(k, {})
        return info.get("value") if isinstance(info, dict) else None

    def fmt(v):
        if v is None: return "MISSING"
        if abs(v) < 1000: return f"{v:.2f}"
        return f"${v/1e6:,.0f}M"

    is_a = std.get("income_audit", {}).get(latest, {})
    bs_a = std.get("balance_audit", {}).get(latest, {})
    cf_a = std.get("cashflow_audit", {}).get(latest, {})

    # IS top-line
    rev = val(is_a, "revenue")
    ebit = val(is_a, "ebit")
    ni = val(is_a, "net_income")
    eps = val(is_a, "diluted_eps")
    sga = val(is_a, "sga")
    sm = val(is_a, "selling_and_marketing")
    ga = val(is_a, "general_and_administrative")
    print(f"  Revenue: {fmt(rev)}  EBIT: {fmt(ebit)}  NI: {fmt(ni)}")
    print(f"  EPS: {fmt(eps)}  SGA: {fmt(sga)}")
    if sm: print(f"    S&M: {fmt(sm)}  G&A: {fmt(ga)}")

    # BS totals
    ta = val(bs_a, "total_assets")
    tl = val(bs_a, "total_liabilities")
    te = val(bs_a, "total_equity")
    tei = val(bs_a, "total_equity_incl_minority")
    balance_ok = False
    if ta and tl and te:
        diff = abs(ta - tl - te)
        if tei and diff > 1e6:
            diff2 = abs(ta - tl - tei)
            balance_ok = diff2 < 1e6
        else:
            balance_ok = diff < 1e6
    print(f"  Assets: {fmt(ta)}  Liab: {fmt(tl)}  Equity: {fmt(te)}  Balance: {'✅' if balance_ok else '❌'}")

    # CF
    ocf = val(cf_a, "operating_cash_flow")
    icf = val(cf_a, "investing_cash_flow")
    fcf_d = val(cf_a, "free_cash_flow")
    capex = val(cf_a, "capital_expenditure")
    da = val(cf_a, "depreciation_amortization")
    sbc = val(cf_a, "stock_based_compensation")
    div = val(cf_a, "dividends_paid")
    buyback = val(cf_a, "stock_repurchases")
    recv = val(cf_a, "change_in_receivables")
    pay = val(cf_a, "change_in_payables")
    inv = val(cf_a, "change_in_inventory")
    taxes = val(cf_a, "cash_taxes_paid")

    fcf_calc = (ocf - abs(capex)) if ocf and capex else None
    print(f"  OCF: {fmt(ocf)}  CapEx: {fmt(capex)}  FCF: {fmt(fcf_d)} (calc: {fmt(fcf_calc)})")
    print(f"  D&A: {fmt(da)}  SBC: {fmt(sbc)}")
    print(f"  Dividends: {fmt(div)}  Buybacks: {fmt(buyback)}")
    print(f"  ΔRecv: {fmt(recv)}  ΔPay: {fmt(pay)}  ΔInv: {fmt(inv)}")
    if taxes: print(f"  Cash taxes: {fmt(taxes)}")

    # Derived fields
    ebitda = val(is_a, "ebitda")
    td = val(bs_a, "total_debt")
    nd = val(bs_a, "net_debt")
    print(f"  EBITDA: {fmt(ebitda)}  Total Debt: {fmt(td)}  Net Debt: {fmt(nd)}")

    # Layer 4 count
    l4_items = {}
    for stmt_name in ["income_audit", "balance_audit", "cashflow_audit"]:
        audit = std.get(stmt_name, {}).get(latest, {})
        l4 = [(k, v) for k, v in audit.items()
               if isinstance(v, dict) and v.get("layer") == 4]
        l4_items[stmt_name[:2]] = l4
        if l4:
            for k, v in l4:
                val_str = f"{v['value']/1e6:,.0f}M" if abs(v['value']) > 1e6 else str(v['value'])
                print(f"    L4 [{stmt_name[:2].upper()}] {k:30s} = {val_str:>12s}  <- \"{v['raw_label'][:60]}\"")

    l4_count = sum(len(v) for v in l4_items.values())
    print(f"  Layer 4 total: {l4_count}")

    # Cross-checks
    checks = std.get("cross_checks", [])
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        for c in failed:
            print(f"  XCHECK FAIL: {c['year']} {c['check']} diff={c.get('diff',0)/1e6:,.0f}M")

    results[ticker] = {
        "revenue": rev, "ebit": ebit, "net_income": ni, "eps": eps,
        "sga": sga, "sm": sm, "ga": ga,
        "total_assets": ta, "total_liabilities": tl, "total_equity": te,
        "balance": balance_ok,
        "ocf": ocf, "capex": capex, "fcf": fcf_d, "fcf_calc": fcf_calc,
        "da": da, "sbc": sbc, "dividends": div, "buybacks": buyback,
        "recv": recv, "pay": pay, "inv": inv, "taxes": taxes,
        "ebitda": ebitda, "total_debt": td, "net_debt": nd,
        "l4_count": l4_count,
        "xcheck_fails": len(failed),
    }

# Summary table
print("\n" + "="*120)
print("SUMMARY")
print("="*120)
print(f"{'Ticker':8s} {'Revenue':>12s} {'EBIT':>12s} {'NI':>10s} {'OCF':>12s} {'FCF':>12s} {'EPS':>8s} {'BS?':>4s} {'L4':>4s} {'XC':>3s}")
print("-"*100)
for t in TICKERS:
    r = results.get(t, {})
    if "error" in r:
        print(f"{t:8s} ERROR: {r['error']}")
        continue
    def s(v):
        if v is None: return "--"
        if abs(v) < 1000: return f"{v:.2f}"
        return f"{v/1e6:,.0f}M"
    print(f"{t:8s} {s(r.get('revenue')):>12s} {s(r.get('ebit')):>12s} {s(r.get('net_income')):>10s} "
          f"{s(r.get('ocf')):>12s} {s(r.get('fcf')):>12s} {s(r.get('eps')):>8s} "
          f"{'✅' if r.get('balance') else '❌':>4s} {r.get('l4_count',0):>4d} {r.get('xcheck_fails',0):>3d}")
