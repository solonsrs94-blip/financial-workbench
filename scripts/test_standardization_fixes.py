"""Test standardization fixes on AAPL, MSFT, GOOG."""

import sys, os, json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Clear cache to force re-standardization
from lib import cache
for ticker in ["AAPL", "MSFT", "GOOG"]:
    cache_key = f"std_hist:{ticker}"
    try:
        cache._delete(cache_key)
    except Exception:
        pass

from lib.data.historical import get_raw_statements, get_standardized_history

TICKERS = ["AAPL", "MSFT", "GOOG"]

results = {}

for ticker in TICKERS:
    print(f"\n{'='*60}")
    print(f"Processing {ticker}...")
    print(f"{'='*60}")
    try:
        raw = get_raw_statements(ticker)
        if raw is None:
            print(f"  ERROR: No raw data for {ticker}")
            results[ticker] = {"error": "No raw data"}
            continue

        std = get_standardized_history(ticker, raw_data=raw, force_refresh=True)
        if std is None:
            print(f"  ERROR: Standardization returned None for {ticker}")
            results[ticker] = {"error": "Standardization returned None"}
            continue

        years = std["years"]
        latest_yr = max(years)

        # Collect Layer 4 items across all statements
        layer4_items = []
        for stmt_key in ["income_audit", "balance_audit", "cashflow_audit"]:
            for yr, fields in std[stmt_key].items():
                for k, v in fields.items():
                    if isinstance(v, dict) and v.get("layer") == 4:
                        layer4_items.append({
                            "statement": stmt_key.replace("_audit", ""),
                            "year": yr, "key": k,
                            "raw_label": v.get("raw_label", "?"),
                            "value": v.get("value"),
                        })

        # Check specific fixes for latest year
        is_data = std["income_audit"].get(latest_yr, {})
        bs_data = std["balance_audit"].get(latest_yr, {})
        cf_data = std["cashflow_audit"].get(latest_yr, {})

        def _v(d, k):
            info = d.get(k)
            if isinstance(info, dict):
                return info.get("value"), info.get("layer"), info.get("raw_label", "?")
            return None, None, "?"

        # IS checks
        eps_val, eps_layer, eps_raw = _v(is_data, "diluted_eps")
        ebitda_val, ebitda_layer, ebitda_raw = _v(is_data, "ebitda")
        ebit_val = _v(is_data, "ebit")[0]
        int_exp_val, int_exp_layer, int_exp_raw = _v(is_data, "interest_expense")

        # BS checks
        deferred_rev_val, dr_layer, dr_raw = _v(bs_data, "deferred_revenue_current")
        accrued_val = _v(bs_data, "accrued_expenses")[0]
        net_debt_val, nd_layer, nd_raw = _v(bs_data, "net_debt")
        total_debt_val = _v(bs_data, "total_debt")[0]
        cash_val = _v(bs_data, "cash")[0]
        sti_val = _v(bs_data, "short_term_investments")[0]

        # CF checks
        div_paid_val, dp_layer, dp_raw = _v(cf_data, "dividends_paid")
        chg_pay_val, cp_layer, cp_raw = _v(cf_data, "change_in_payables")
        chg_rec_val, cr_layer, cr_raw = _v(cf_data, "change_in_receivables")
        chg_inv_val, ci_layer, ci_raw = _v(cf_data, "change_in_inventory")
        inv_purch_val, ip_layer, ip_raw = _v(cf_data, "investment_purchases")
        tax_settle_val, ts_layer, ts_raw = _v(cf_data, "tax_on_share_settlement")
        cash_tax_val, ct_layer, ct_raw = _v(cf_data, "cash_taxes_paid")
        old_def_tax_val = _v(cf_data, "deferred_income_tax")[0]

        print(f"\n  Latest year: {latest_yr}")
        print(f"  Layer 4 items total: {len(layer4_items)}")

        # Unique layer 4 keys
        l4_keys = set(f"{i['statement']}/{i['key']}" for i in layer4_items)
        print(f"  Unique Layer 4 keys: {len(l4_keys)}")
        for k in sorted(l4_keys):
            # Get one example
            ex = next(i for i in layer4_items if f"{i['statement']}/{i['key']}" == k)
            print(f"    {k}: \"{ex['raw_label']}\"")

        print(f"\n  IS FIXES ({latest_yr}):")
        print(f"    diluted_eps: val={eps_val}, layer={eps_layer}, raw=\"{eps_raw}\"")
        print(f"    ebitda: val={ebitda_val}, layer={ebitda_layer}, raw=\"{ebitda_raw}\"")
        print(f"    interest_expense: val={int_exp_val}, layer={int_exp_layer}, raw=\"{int_exp_raw}\"")

        print(f"\n  BS FIXES ({latest_yr}):")
        print(f"    deferred_revenue_current: val={deferred_rev_val}, layer={dr_layer}, raw=\"{dr_raw}\"")
        print(f"    accrued_expenses: val={accrued_val}")
        print(f"    total_debt: val={total_debt_val}")
        print(f"    cash: val={cash_val}")
        print(f"    short_term_investments: val={sti_val}")
        print(f"    net_debt: val={net_debt_val}, layer={nd_layer}, raw=\"{nd_raw}\"")
        if total_debt_val and cash_val:
            expected = total_debt_val - (cash_val or 0) - (sti_val or 0)
            print(f"    net_debt check: {total_debt_val} - {cash_val} - {sti_val or 0} = {expected} (actual: {net_debt_val}) {'OK' if abs(expected - (net_debt_val or 0)) < 1 else 'MISMATCH'}")

        print(f"\n  CF FIXES ({latest_yr}):")
        print(f"    dividends_paid: val={div_paid_val}, layer={dp_layer}, raw=\"{dp_raw}\"")
        print(f"    change_in_payables: val={chg_pay_val}, layer={cp_layer}, raw=\"{cp_raw}\"")
        print(f"    change_in_receivables: val={chg_rec_val}, layer={cr_layer}, raw=\"{cr_raw}\"")
        print(f"    change_in_inventory: val={chg_inv_val}, layer={ci_layer}, raw=\"{ci_raw}\"")
        print(f"    investment_purchases: val={inv_purch_val}, layer={ip_layer}, raw=\"{ip_raw}\"")
        print(f"    cash_taxes_paid: val={cash_tax_val}, layer={ct_layer}, raw=\"{ct_raw}\"")
        print(f"    deferred_income_tax (old key): val={old_def_tax_val}")

        # EBITDA verification
        if ebitda_val and ebit_val:
            da_cf = _v(cf_data, "depreciation_amortization")[0]
            print(f"\n  EBITDA CHECK: ebit={ebit_val}, D&A(CF)={da_cf}")
            if da_cf:
                expected_ebitda = ebit_val + abs(da_cf)
                print(f"    Expected: {expected_ebitda}, Actual: {ebitda_val}, {'OK' if abs(expected_ebitda - ebitda_val) < 1 else 'MISMATCH'}")

        # Cross checks
        print(f"\n  CROSS CHECKS:")
        for c in std.get("cross_checks", []):
            if c["year"] == latest_yr:
                status = "PASS" if c["ok"] else f"FAIL (diff={c['diff']})"
                print(f"    {c['check']}: {status}")

        results[ticker] = {
            "years": years,
            "latest": latest_yr,
            "layer4_count": len(layer4_items),
            "layer4_unique_keys": len(l4_keys),
            "layer4_keys": sorted(l4_keys),
            "has_diluted_eps": eps_val is not None,
            "has_ebitda": ebitda_val is not None,
            "has_dividends_paid": div_paid_val is not None,
            "has_change_in_payables": chg_pay_val is not None,
            "has_change_in_receivables": chg_rec_val is not None,
            "has_investment_purchases": inv_purch_val is not None,
            "net_debt": net_debt_val,
            "total_debt": total_debt_val,
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
        print(f"  {t}: ERROR — {r['error']}")
    else:
        print(f"  {t}: L4={r['layer4_count']} ({r['layer4_unique_keys']} unique keys), eps={r['has_diluted_eps']}, ebitda={r['has_ebitda']}, div_paid={r['has_dividends_paid']}, chg_pay={r['has_change_in_payables']}, inv_purch={r['has_investment_purchases']}")

out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "standardization_fixes_test.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nJSON written to {out_path}")
