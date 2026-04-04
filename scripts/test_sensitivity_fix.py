"""Sensitivity fix verification — test JNJ, AAPL, 7203.T."""

import sys, os, time, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import warnings
warnings.filterwarnings("ignore")
import numpy as np

from lib.data.valuation_data import get_valuation_data, get_risk_free_rate, get_erp, get_ddm_data
from lib.data.providers import yahoo
from lib.analysis.valuation.wacc import auto_wacc, adjusted_beta, calc_capm, size_premium_bracket
from lib.analysis.valuation.dcf import build_fcf_table, run_dcf
from lib.analysis.valuation.sensitivity import sensitivity_table
from lib.analysis.valuation.ddm import gordon_growth, two_stage_ddm, ddm_sensitivity


def safe_pct(v): return f"{v*100:.1f}%" if v else "N/A"
def safe_dollar(v): return f"${v:,.2f}" if v else "N/A"


TICKERS = [
    {"ticker": "JNJ", "name": "Johnson & Johnson", "test_ddm": True, "test_dcf": False},
    {"ticker": "AAPL", "name": "Apple", "test_ddm": True, "test_dcf": True},
    {"ticker": "7203.T", "name": "Toyota", "test_ddm": True, "test_dcf": True},
]


def main():
    lines = []
    lines.append("# Sensitivity Fix Verification")
    lines.append(f"**Date:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")

    rf = get_risk_free_rate()
    erp = get_erp()
    lines.append(f"**Rf:** {safe_pct(rf)} | **ERP:** {safe_pct(erp)}")
    lines.append("")

    for t in TICKERS:
        ticker = t["ticker"]
        print(f"\n{'='*50}")
        print(f"Testing {ticker}...")

        lines.append(f"## {ticker} - {t['name']}")
        lines.append("")

        info = yahoo.fetch_all_info(ticker)
        if not info:
            lines.append("ERROR: No data\n---\n")
            continue
        current_price = info.get("price", {}).get("price", 0)
        market_cap = info.get("price", {}).get("market_cap", 50e9)
        beta_raw = info.get("price", {}).get("beta", 1.0)
        currency = info.get("info", {}).get("currency", "USD")

        lines.append(f"**Price:** {current_price:,.2f} {currency}")
        lines.append("")

        # DDM
        if t.get("test_ddm"):
            ddm_data = get_ddm_data(ticker)
            if ddm_data and ddm_data.get("has_dividend"):
                d0 = ddm_data.get("current_dps", 0)
                beta = adjusted_beta(beta_raw) if beta_raw and beta_raw > 0 else 1.0
                sp, _ = size_premium_bracket(market_cap)
                ke = calc_capm(rf, beta, erp or 0.055, sp)
                cagr = ddm_data.get("dps_cagr", {})
                g_hist = cagr.get("5y") or cagr.get("3y") or 0.04
                g_gordon = min(g_hist, ke - 0.01, 0.06)
                g_gordon = max(g_gordon, 0.01)
                g1 = min(g_hist, 0.08)
                g2 = min(g_gordon, 0.03)

                # Gordon sensitivity
                sens_g = ddm_sensitivity(d0, ke, g_gordon, model="gordon")
                gv = sens_g.values.flatten()
                gv_valid = [float(v) for v in gv if not np.isnan(v) and v > 0]
                g_nan = sum(1 for v in gv if np.isnan(v))
                g_min = min(gv_valid) if gv_valid else None
                g_max = max(gv_valid) if gv_valid else None

                lines.append("### DDM Gordon Sensitivity")
                lines.append(f"- Ke={safe_pct(ke)}, g={safe_pct(g_gordon)}, d0={d0:.2f}")
                lines.append(f"- Grid: {sens_g.shape[0]}x{sens_g.shape[1]} = {sens_g.size} cells")
                lines.append(f"- Valid cells: {len(gv_valid)}, NaN cells: {g_nan}")
                lines.append(f"- **Range:** {safe_dollar(g_min)} - {safe_dollar(g_max)}")
                low_ok = g_min and g_min > 0
                lines.append(f"- **Low > $0:** {'PASS' if low_ok else 'FAIL'}")
                print(f"  Gordon: {safe_dollar(g_min)} - {safe_dollar(g_max)}, NaN={g_nan}, low>0={'PASS' if low_ok else 'FAIL'}")

                # 2-Stage sensitivity
                sens_t = ddm_sensitivity(d0, ke, g2, model="two_stage", n=5, g1=g1)
                tv = sens_t.values.flatten()
                tv_valid = [float(v) for v in tv if not np.isnan(v) and v > 0]
                t_nan = sum(1 for v in tv if np.isnan(v))
                t_min = min(tv_valid) if tv_valid else None
                t_max = max(tv_valid) if tv_valid else None

                lines.append("")
                lines.append("### DDM 2-Stage Sensitivity")
                lines.append(f"- g1={safe_pct(g1)}, g2={safe_pct(g2)}, n=5")
                lines.append(f"- Grid: {sens_t.shape[0]}x{sens_t.shape[1]} = {sens_t.size} cells")
                lines.append(f"- Valid cells: {len(tv_valid)}, NaN cells: {t_nan}")
                lines.append(f"- **Range:** {safe_dollar(t_min)} - {safe_dollar(t_max)}")
                has_range = t_min is not None and t_max is not None
                lines.append(f"- **Has range (not N/A):** {'PASS' if has_range else 'FAIL'}")
                low_ok2 = t_min and t_min > 0
                lines.append(f"- **Low > $0:** {'PASS' if low_ok2 else 'FAIL'}")
                print(f"  2-Stage: {safe_dollar(t_min)} - {safe_dollar(t_max)}, NaN={t_nan}, has_range={'PASS' if has_range else 'FAIL'}")

        lines.append("")

        # DCF
        if t.get("test_dcf"):
            val_data, _ = get_valuation_data(ticker)
            if val_data:
                inc = val_data.get("income_detail", {})
                bs = val_data.get("balance_sheet", {})
                hist = val_data.get("historical_margins", [])
                base_rev = inc.get("revenue")
                if base_rev and base_rev > 0:
                    avg_ebit = sum(m["ebit_margin"] for m in hist if m.get("ebit_margin")) / max(1, len([m for m in hist if m.get("ebit_margin")]))
                    avg_capex = sum(m["capex_pct"] for m in hist if m.get("capex_pct")) / max(1, len([m for m in hist if m.get("capex_pct")]))
                    avg_da = sum(m["da_pct"] for m in hist if m.get("da_pct")) / max(1, len([m for m in hist if m.get("da_pct")]))
                    avg_sbc = sum(m.get("sbc_pct", 0) for m in hist) / max(1, len(hist))
                    avg_cogs = sum(m["cogs_pct"] for m in hist if m.get("cogs_pct")) / max(1, len([m for m in hist if m.get("cogs_pct")])) or 0.60
                    tax = inc.get("effective_tax_rate") or 0.21
                    wc = val_data.get("working_capital", {})

                    fcf = build_fcf_table(
                        base_revenue=base_rev / 1e6, n_years=5,
                        growth_rates=[0.05, 0.04, 0.04, 0.03, 0.03],
                        ebit_margins=[avg_ebit]*5, tax_rate=tax,
                        capex_pcts=[avg_capex]*5, da_pcts=[avg_da]*5,
                        sbc_pcts=[avg_sbc]*5,
                        dso=[wc.get("dso") or 45]*5,
                        dio=[wc.get("dio") or 30]*5,
                        dpo=[wc.get("dpo") or 40]*5,
                        base_cogs_pct=avg_cogs,
                    )

                    beta_v = val_data.get("beta") or 1.0
                    mcap_v = val_data.get("market_cap") or market_cap
                    wacc_r = auto_wacc(rf, beta_v, mcap_v, bs.get("total_debt", 0),
                                       inc.get("interest_expense", 0), tax, erp or 0.055)
                    net_debt = bs.get("net_debt", 0) / 1e6
                    shares = (val_data.get("shares") or 1e9) / 1e6

                    sens_dcf = sensitivity_table(
                        fcf, wacc_r, 0.025, "gordon", None,
                        net_debt, shares, current_price, 0, 0,
                    )
                    sv = sens_dcf.values.flatten()
                    sv_valid = [float(v) for v in sv if not np.isnan(v) and v > 0]
                    s_nan = sum(1 for v in sv if np.isnan(v))
                    s_min = min(sv_valid) if sv_valid else None
                    s_max = max(sv_valid) if sv_valid else None

                    lines.append("### DCF Sensitivity")
                    lines.append(f"- WACC={safe_pct(wacc_r.wacc)}")
                    lines.append(f"- Grid: {sens_dcf.shape[0]}x{sens_dcf.shape[1]} = {sens_dcf.size} cells")
                    lines.append(f"- Valid cells: {len(sv_valid)}, NaN cells: {s_nan}")
                    lines.append(f"- **Range:** {safe_dollar(s_min)} - {safe_dollar(s_max)}")
                    low_ok = s_min and s_min > 0
                    lines.append(f"- **Low > $0:** {'PASS' if low_ok else 'FAIL'}")
                    print(f"  DCF: {safe_dollar(s_min)} - {safe_dollar(s_max)}, NaN={s_nan}, low>0={'PASS' if low_ok else 'FAIL'}")

        lines.append("")
        lines.append("---")
        lines.append("")

    report_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "test_results", "sensitivity_fix_verification.md",
    )
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nReport: {report_path}")


if __name__ == "__main__":
    main()
