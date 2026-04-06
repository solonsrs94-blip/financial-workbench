"""Professional check — compare standardized output against known values."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from lib.data.historical import get_raw_statements, get_standardized_history
from lib import cache

TICKERS = ["GOOG", "AAPL", "MSFT", "XOM"]

for ticker in TICKERS:
    print(f"\n{'='*80}")
    print(f"  {ticker}")
    print(f"{'='*80}")

    try:
        cache._delete(f"std_hist:{ticker}")
    except:
        pass

    raw = get_raw_statements(ticker)
    std = get_standardized_history(ticker, raw_data=raw, force_refresh=True)
    if not std:
        print("  FAILED")
        continue

    years = std["years"]
    latest = years[-1]

    is_a = std.get("income_audit", {}).get(latest, {})
    bs_a = std.get("balance_audit", {}).get(latest, {})
    cf_a = std.get("cashflow_audit", {}).get(latest, {})

    def v(audit, key):
        info = audit.get(key, {})
        return info.get("value") if isinstance(info, dict) else None

    def fmt(val):
        if val is None:
            return "     — MISSING"
        if abs(val) < 100:
            return f"     {val:>10.2f}"
        return f"     {val/1e6:>10,.0f}M"

    def src(audit, key):
        info = audit.get(key, {})
        if isinstance(info, dict):
            return info.get("raw_label", "?")[:45]
        return "?"

    lines = [
        ("Revenue",              is_a, "revenue"),
        ("COGS",                 is_a, "cogs"),
        ("Gross Profit",         is_a, "gross_profit"),
        ("SGA (combined)",       is_a, "sga"),
        ("  S&M",                is_a, "selling_and_marketing"),
        ("  G&A",                is_a, "general_and_administrative"),
        ("R&D",                  is_a, "rd"),
        ("Total OpEx",           is_a, "total_opex"),
        ("EBIT",                 is_a, "ebit"),
        ("EBITDA",               is_a, "ebitda"),
        ("Interest Expense",     is_a, "interest_expense"),
        ("Other Non-Op",        is_a, "other_non_operating"),
        ("Pretax Income",        is_a, "pretax_income"),
        ("Tax Provision",        is_a, "tax_provision"),
        ("Net Income",           is_a, "net_income"),
        ("Diluted EPS",          is_a, "diluted_eps"),
        ("Diluted Shares",       is_a, "diluted_shares"),
        ("---", None, None),
        ("Total Assets",         bs_a, "total_assets"),
        ("Total Liabilities",    bs_a, "total_liabilities"),
        ("Total Equity",         bs_a, "total_equity"),
        ("Cash",                 bs_a, "cash"),
        ("STI",                  bs_a, "short_term_investments"),
        ("Total Debt",           bs_a, "total_debt"),
        ("Net Debt",             bs_a, "net_debt"),
        ("Goodwill",             bs_a, "goodwill"),
        ("Intangible Assets",    bs_a, "intangible_assets"),
        ("Inventories",          bs_a, "inventories"),
        ("Shares Outstanding",   bs_a, "shares_outstanding"),
        ("---", None, None),
        ("OCF",                  cf_a, "operating_cash_flow"),
        ("CapEx",                cf_a, "capital_expenditure"),
        ("FCF",                  cf_a, "free_cash_flow"),
        ("D&A",                  cf_a, "depreciation_amortization"),
        ("SBC",                  cf_a, "stock_based_compensation"),
        ("Dividends",            cf_a, "dividends_paid"),
        ("Stock Repurchases",    cf_a, "stock_repurchases"),
    ]

    print(f"  {'Line':<22s} {'Value':>15s}  {'Source'}")
    print(f"  {'-'*22} {'-'*15}  {'-'*45}")
    for name, audit, key in lines:
        if audit is None:
            print(f"  {'-'*80}")
            continue
        val = v(audit, key)
        source = src(audit, key)
        print(f"  {name:<22s} {fmt(val)}  {source}")

    # Cross-checks
    print(f"\n  Cross-checks ({latest}):")
    rev = v(is_a, "revenue")
    cogs = v(is_a, "cogs")
    gp = v(is_a, "gross_profit")
    ebit = v(is_a, "ebit")
    sga = v(is_a, "sga")
    rd = v(is_a, "rd")
    ta = v(bs_a, "total_assets")
    tl = v(bs_a, "total_liabilities")
    te = v(bs_a, "total_equity")
    ocf = v(cf_a, "operating_cash_flow")
    capex = v(cf_a, "capital_expenditure")
    fcf = v(cf_a, "free_cash_flow")
    da = v(cf_a, "depreciation_amortization")
    ebitda = v(is_a, "ebitda")

    if rev and cogs and gp:
        calc = rev - abs(cogs)
        ok = abs(calc - gp) < abs(rev) * 0.01
        print(f"    Rev - COGS = GP: {calc/1e6:,.0f}M vs {gp/1e6:,.0f}M {'✅' if ok else '❌'}")

    if ta and tl and te:
        calc = tl + te
        ok = abs(ta - calc) < abs(ta) * 0.01
        print(f"    A = L + E: {ta/1e6:,.0f}M vs {calc/1e6:,.0f}M {'✅' if ok else '❌'}")

    if ocf and capex and fcf:
        calc = ocf - abs(capex)
        ok = abs(calc - fcf) < abs(ocf) * 0.01
        print(f"    OCF - CapEx = FCF: {calc/1e6:,.0f}M vs {fcf/1e6:,.0f}M {'✅' if ok else '❌'}")

    if ebit and da and ebitda:
        calc = ebit + abs(da)
        ok = abs(calc - ebitda) < abs(ebit) * 0.01
        print(f"    EBIT + D&A = EBITDA: {calc/1e6:,.0f}M vs {ebitda/1e6:,.0f}M {'✅' if ok else '❌'}")

    # OpEx check: Revenue - EBIT should ≈ Total OpEx
    if rev and ebit:
        calc_opex = rev - ebit
        top = v(is_a, "total_opex")
        if top:
            ok = abs(calc_opex - top) < abs(rev) * 0.01
            print(f"    Rev - EBIT = OpEx: {calc_opex/1e6:,.0f}M vs {top/1e6:,.0f}M {'✅' if ok else '❌'}")
        else:
            print(f"    Rev - EBIT = OpEx: {calc_opex/1e6:,.0f}M (total_opex MISSING)")

    # SGA check: S&M + G&A
    sm = v(is_a, "selling_and_marketing")
    ga = v(is_a, "general_and_administrative")
    if sm and ga:
        calc_sga = sm + ga
        print(f"    S&M + G&A = SGA: {abs(sm)/1e6:,.0f} + {abs(ga)/1e6:,.0f} = {abs(calc_sga)/1e6:,.0f}M vs SGA {abs(sga)/1e6:,.0f}M {'✅' if sga and abs(abs(calc_sga) - abs(sga)) < 1e6 else '❌'}")
