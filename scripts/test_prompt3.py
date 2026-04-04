"""Prompt 3 verification: multi-currency Rf, Comps peers, TV% warning."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import warnings
warnings.filterwarnings("ignore")

import numpy as np
from lib.data.valuation_data import (
    get_risk_free_rate, get_valuation_data, get_erp,
    get_comps_candidate_info, get_peer_universe, filter_peer_universe,
    get_comps_row, get_suggested_peers,
)
from lib.data.providers import yahoo
from lib.analysis.valuation.wacc import auto_wacc
from lib.analysis.valuation.dcf import build_fcf_table, run_dcf


def main():
    lines = []
    lines.append("# Prompt 3 Verification Report")
    lines.append(f"**Date:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")

    # === 1. Multi-currency Rf ===
    lines.append("## 1. Multi-Currency Rf")
    lines.append("")
    currencies = ["USD", "EUR", "GBP", "JPY", "CHF", "KRW", "HKD"]
    lines.append("| Currency | Rf | Label | Source |")
    lines.append("|----------|-----|-------|--------|")
    for cur in currencies:
        rf, label = get_risk_free_rate(currency=cur)
        source = "yfinance" if cur in ("USD", "HKD") else "static default"
        lines.append(f"| {cur} | {rf*100:.2f}% | {label} | {source} |")
        print(f"  Rf {cur}: {rf*100:.2f}% ({label})")
    lines.append("")

    # Test specific tickers
    lines.append("### Rf per company")
    lines.append("")
    test_tickers = [
        ("AAPL", "USD"), ("7203.T", "JPY"), ("NESN.SW", "CHF"),
        ("SAP.DE", "EUR"), ("SHEL.L", "GBP"), ("0700.HK", "HKD"),
    ]
    for ticker, expected_cur in test_tickers:
        val_data, _ = get_valuation_data(ticker, force_refresh=True)
        if val_data:
            fin_cur = val_data.get("financial_currency", "USD")
            rf, label = get_risk_free_rate(currency=fin_cur)
            lines.append(f"- **{ticker}:** financialCurrency={fin_cur}, Rf={rf*100:.2f}% ({label})")
            ok = "PASS" if fin_cur.upper().replace("GBP", "GBP").replace("GBX", "GBP") == expected_cur else f"UNEXPECTED ({fin_cur})"
            lines.append(f"  - Currency match: {ok}")
            print(f"  {ticker}: fin_cur={fin_cur}, Rf={rf*100:.2f}%, match={ok}")
    lines.append("")

    # === 2. Comps Peer Selection ===
    lines.append("## 2. Comps Peer Selection (GICS vs Yahoo)")
    lines.append("")

    comps_tickers = ["KO", "XOM", "SAP.DE"]
    universe = get_peer_universe()

    for ticker in comps_tickers:
        yahoo_peers = get_suggested_peers(ticker, max_peers=6)
        target_info = get_comps_candidate_info(ticker)
        industry = target_info.get("industry", "") if target_info else ""

        gics_peers = []
        if universe and industry:
            mcap = target_info.get("market_cap", 0) if target_info else 0
            gics_peers = filter_peer_universe(universe, ticker, industry, mcap)

        lines.append(f"### {ticker} ({industry})")
        lines.append(f"- Yahoo recommended: {yahoo_peers}")
        lines.append(f"- GICS-filtered ({len(gics_peers)}): {gics_peers[:8]}")
        # Check if GICS peers are same industry
        if gics_peers:
            same_industry = 0
            for p in gics_peers[:6]:
                pi = get_comps_candidate_info(p)
                if pi and pi.get("industry") == industry:
                    same_industry += 1
            lines.append(f"- Same industry (of top 6): {same_industry}/6")
        lines.append("")
        print(f"  {ticker}: yahoo={yahoo_peers[:4]}, gics={gics_peers[:4]}")

    # === 3. TV% Warning ===
    lines.append("## 3. TV% Warning")
    lines.append("")

    # Test with Toyota (known high TV%)
    rf_jpy, _ = get_risk_free_rate(currency="JPY")
    erp = get_erp() or 0.055
    val_data, _ = get_valuation_data("7203.T")
    if val_data:
        inc = val_data.get("income_detail", {})
        bs = val_data.get("balance_sheet", {})
        hist = val_data.get("historical_margins", [])
        base_rev = inc.get("revenue", 0) / 1e6

        if base_rev > 0 and hist:
            avg_ebit = sum(m["ebit_margin"] for m in hist if m.get("ebit_margin")) / max(1, len([m for m in hist if m.get("ebit_margin")]))
            avg_capex = sum(m["capex_pct"] for m in hist if m.get("capex_pct")) / max(1, len([m for m in hist if m.get("capex_pct")]))
            avg_da = sum(m["da_pct"] for m in hist if m.get("da_pct")) / max(1, len([m for m in hist if m.get("da_pct")]))
            avg_sbc = sum(m.get("sbc_pct", 0) for m in hist) / max(1, len(hist))
            avg_cogs = sum(m["cogs_pct"] for m in hist if m.get("cogs_pct")) / max(1, len([m for m in hist if m.get("cogs_pct")])) or 0.60
            tax = inc.get("effective_tax_rate") or 0.25
            wc = val_data.get("working_capital", {})

            fcf = build_fcf_table(
                base_revenue=base_rev, n_years=5,
                growth_rates=[0.05, 0.04, 0.04, 0.03, 0.03],
                ebit_margins=[avg_ebit]*5, tax_rate=tax,
                capex_pcts=[avg_capex]*5, da_pcts=[avg_da]*5,
                sbc_pcts=[avg_sbc]*5,
                dso=[wc.get("dso") or 45]*5,
                dio=[wc.get("dio") or 30]*5,
                dpo=[wc.get("dpo") or 40]*5,
                base_cogs_pct=avg_cogs,
            )

            beta = val_data.get("beta") or 1.0
            mcap = val_data.get("market_cap") or 42e12
            wacc_r = auto_wacc(rf_jpy, beta, mcap, bs.get("total_debt", 0),
                               inc.get("interest_expense", 0), tax, erp)

            dcf_r = run_dcf(
                fcf, wacc_r, 0.025, "gordon", 12.0,
                bs.get("net_debt", 0) / 1e6, (val_data.get("shares") or 1e9) / 1e6,
                3255, 0, 0,
            )

            lines.append(f"### 7203.T (Toyota) with JPY Rf={rf_jpy*100:.2f}%")
            lines.append(f"- WACC: {wacc_r.wacc*100:.2f}%")
            lines.append(f"- TV as % of EV: {dcf_r.tv_pct_of_ev:.0%}")
            lines.append(f"- Warnings: {dcf_r.warnings}")

            has_85_warning = any("consider" in w.lower() for w in dcf_r.warnings)
            has_75_warning = any("uncertainty" in w.lower() for w in dcf_r.warnings)
            if dcf_r.tv_pct_of_ev > 0.85:
                lines.append(f"- **85% warning triggered:** {'PASS' if has_85_warning else 'FAIL'}")
                print(f"  Toyota TV%={dcf_r.tv_pct_of_ev:.0%}, 85% warning={'PASS' if has_85_warning else 'FAIL'}")
            elif dcf_r.tv_pct_of_ev > 0.75:
                lines.append(f"- **75% warning triggered:** {'PASS' if has_75_warning else 'FAIL'}")
                print(f"  Toyota TV%={dcf_r.tv_pct_of_ev:.0%}, 75% warning={'PASS' if has_75_warning else 'FAIL'}")
            else:
                lines.append(f"- TV% is {dcf_r.tv_pct_of_ev:.0%} (below 75%, no warning expected)")

    lines.append("")

    # Write report
    report_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "test_results", "prompt3_verification.md",
    )
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nReport: {report_path}")


if __name__ == "__main__":
    main()
