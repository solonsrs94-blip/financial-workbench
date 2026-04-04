"""Currency fix verification — test SHEL.L, NESN.SW, AAPL, 7203.T.

Compares historical multiples P/E and implied values before/after fix.
"""

import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import warnings
warnings.filterwarnings("ignore")

from lib.data.valuation_data import (
    get_historical_multiples, get_valuation_data, get_risk_free_rate,
    get_erp, get_ddm_data,
)
from lib.data.providers import yahoo
from lib.analysis.valuation.wacc import auto_wacc, adjusted_beta, calc_capm, size_premium_bracket
from lib.analysis.valuation.dcf import build_fcf_table, run_dcf
from lib.analysis.valuation.ddm import gordon_growth
from models.valuation import WACCResult


def safe_pct(v): return f"{v*100:.1f}%" if v else "N/A"
def safe_dollar(v, cur="USD"):
    if v is None: return "N/A"
    sym = "$" if cur == "USD" else ""
    return f"{sym}{v:,.2f} {cur}"


TICKERS = [
    {"ticker": "SHEL.L", "name": "Shell plc", "expect_pf": True},
    {"ticker": "NESN.SW", "name": "Nestle", "expect_pf": False},
    {"ticker": "AAPL", "name": "Apple", "expect_pf": False},
    {"ticker": "7203.T", "name": "Toyota", "expect_pf": False},
]


def run_tests():
    lines = []
    lines.append("# Currency Fix Verification Report")
    lines.append(f"**Date:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")

    rf = get_risk_free_rate()
    erp = get_erp()
    lines.append(f"**Rf:** {safe_pct(rf)} | **ERP:** {safe_pct(erp)}")
    lines.append("")

    for t in TICKERS:
        ticker = t["ticker"]
        print(f"\n{'='*50}")
        print(f"Testing {ticker} ({t['name']})...")

        lines.append(f"## {ticker} — {t['name']}")
        lines.append("")

        # Get market info
        info = yahoo.fetch_all_info(ticker)
        if not info:
            lines.append("**ERROR:** No market data\n")
            continue

        price_data = info.get("price", {})
        info_data = info.get("info", {})
        current_price = price_data.get("price", 0)
        market_cap = price_data.get("market_cap", 0)
        currency = info_data.get("currency", "USD")

        lines.append(f"**Price:** {safe_dollar(current_price, currency)} | **Market Cap:** {market_cap:,.0f} | **Currency:** {currency}")
        lines.append("")

        # --- Historical Multiples ---
        print(f"  Historical Multiples...")
        t0 = time.time()
        hist = get_historical_multiples(ticker, period_years=3, is_financial=False)
        elapsed = time.time() - t0

        if hist.get("error"):
            lines.append(f"**Historical:** ERROR — {hist['error']}")
        else:
            summary = hist.get("summary", {})
            implied = hist.get("implied_values", {})
            fin_cur = hist.get("financial_currency", currency)

            lines.append(f"### Historical Multiples ({elapsed:.1f}s)")
            lines.append(f"- Data source: {hist.get('data_source')}")
            lines.append(f"- Financial currency: {fin_cur}")
            lines.append("")

            for key in ["pe", "ev_ebitda", "ev_revenue"]:
                s = summary.get(key, {})
                iv = implied.get(key, {})
                if s:
                    cur_m = s.get("current", "N/A")
                    med_m = s.get("median", "N/A")
                    imp_med = iv.get("at_median")
                    lines.append(f"- **{key}:** current={cur_m}, median={med_m} → implied={safe_dollar(imp_med, currency)}")
                    print(f"    {key}: current={cur_m}, median={med_m}, implied_median={safe_dollar(imp_med, currency)}")

            # Sanity check: is implied price in same order of magnitude as current?
            pe_implied = implied.get("pe", {}).get("at_median")
            if pe_implied and current_price:
                ratio = pe_implied / current_price
                sanity = "PASS" if 0.1 < ratio < 10 else f"FAIL (ratio={ratio:.2f})"
                lines.append(f"- **Sanity (P/E implied vs price):** {sanity}")
                print(f"    Sanity: {sanity}")

        lines.append("")

        # --- DCF ---
        print(f"  DCF...")
        val_data, status = get_valuation_data(ticker, force_refresh=True)
        if val_data:
            inc = val_data.get("income_detail", {})
            bs = val_data.get("balance_sheet", {})
            hist_m = val_data.get("historical_margins", [])
            base_rev = inc.get("revenue")
            val_currency = val_data.get("currency", "USD")
            val_fin_cur = val_data.get("financial_currency", val_currency)

            lines.append(f"### DCF")
            lines.append(f"- Valuation data currency: {val_currency} / financial: {val_fin_cur}")

            if base_rev and base_rev > 0:
                # Simple assumptions
                avg_ebit = sum(m["ebit_margin"] for m in hist_m if m.get("ebit_margin")) / max(1, len([m for m in hist_m if m.get("ebit_margin")]))
                avg_capex = sum(m["capex_pct"] for m in hist_m if m.get("capex_pct")) / max(1, len([m for m in hist_m if m.get("capex_pct")]))
                avg_da = sum(m["da_pct"] for m in hist_m if m.get("da_pct")) / max(1, len([m for m in hist_m if m.get("da_pct")]))
                avg_sbc = sum(m.get("sbc_pct", 0) for m in hist_m) / max(1, len(hist_m))
                avg_cogs = sum(m["cogs_pct"] for m in hist_m if m.get("cogs_pct")) / max(1, len([m for m in hist_m if m.get("cogs_pct")])) or 0.60
                tax = inc.get("effective_tax_rate") or 0.21
                wc = val_data.get("working_capital", {})

                # Convert to millions (DCF engine expects $M)
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

                beta = val_data.get("beta") or 1.0
                mcap = val_data.get("market_cap") or market_cap
                wacc_r = auto_wacc(rf, beta, mcap, bs.get("total_debt", 0),
                                   inc.get("interest_expense", 0), tax, erp or 0.055)

                dcf_r = run_dcf(
                    fcf, wacc_r, 0.025, "gordon", 12.0,
                    bs.get("net_debt", 0) / 1e6, (val_data.get("shares") or 1e9) / 1e6,
                    current_price, (bs.get("minority_interest", 0) or 0) / 1e6,
                    (bs.get("preferred_equity", 0) or 0) / 1e6,
                )

                # DCF implied is in financial currency (e.g. USD for SHEL.L).
                # Convert to listing currency: divide by price_factor.
                implied_fin = dcf_r.implied_price
                pf = 1.0
                if val_currency != val_fin_cur and current_price > 0 and mcap and val_data.get("shares"):
                    pf = mcap / (current_price * val_data["shares"])
                # implied_fin is $/share in financial currency
                # To get listing currency: divide by pf (e.g. $79 / 0.01 = 7900 GBp)
                implied_listing = implied_fin / pf if pf != 1.0 else implied_fin

                upside = (implied_listing / current_price - 1) * 100 if current_price > 0 else 0
                lines.append(f"- WACC: {safe_pct(wacc_r.wacc)}")
                lines.append(f"- Implied (financial currency): {implied_fin:,.2f}")
                lines.append(f"- Implied (listing currency): {safe_dollar(implied_listing, val_currency)}")
                lines.append(f"- Upside: {upside:+.1f}%")
                lines.append(f"- price_factor: {pf:.6f}")

                ratio = implied_listing / current_price if current_price > 0 else 0
                sanity = "PASS" if 0.05 < ratio < 20 else f"FAIL (ratio={ratio:.2f})"
                lines.append(f"- **DCF Sanity:** {sanity}")
                print(f"    DCF: implied={safe_dollar(implied_listing, val_currency)}, upside={upside:+.1f}%, sanity={sanity}")
            else:
                lines.append("- No revenue data for DCF")

        lines.append("")

        # --- DDM ---
        print(f"  DDM...")
        ddm_data = get_ddm_data(ticker, force_refresh=True)
        if ddm_data and ddm_data.get("has_dividend"):
            d0 = ddm_data.get("current_dps", 0)
            ddm_cur = ddm_data.get("currency", "USD")
            ddm_fin_cur = ddm_data.get("financial_currency", ddm_cur)

            lines.append(f"### DDM")
            lines.append(f"- DPS: {d0} (currency: {ddm_fin_cur})")

            if d0 > 0:
                beta_raw = price_data.get("beta", 1.0)
                beta_adj = adjusted_beta(beta_raw) if beta_raw and beta_raw > 0 else 1.0
                sp, _ = size_premium_bracket(market_cap)
                ke = calc_capm(rf, beta_adj, erp or 0.055, sp)
                cagr = ddm_data.get("dps_cagr", {})
                g = min(cagr.get("5y") or cagr.get("3y") or 0.04, ke - 0.01, 0.06)
                g = max(g, 0.01)

                gg = gordon_growth(d0, ke, g)
                implied_gg = gg.get("implied_price", 0)

                # Convert from financial to listing currency
                pf_ddm = 1.0
                if ddm_cur != ddm_fin_cur and current_price > 0 and market_cap:
                    shares_est = val_data.get("shares") if val_data else None
                    if shares_est and shares_est > 0:
                        pf_ddm = market_cap / (current_price * shares_est)
                implied_listing = implied_gg / pf_ddm if pf_ddm != 1.0 else implied_gg

                upside = (implied_listing / current_price - 1) * 100 if current_price > 0 else 0
                lines.append(f"- Ke: {safe_pct(ke)}, g: {safe_pct(g)}")
                lines.append(f"- Gordon implied (financial): {implied_gg:,.2f}")
                lines.append(f"- Gordon implied (listing): {safe_dollar(implied_listing, ddm_cur)}")
                lines.append(f"- Upside: {upside:+.1f}%")
                lines.append(f"- price_factor: {pf_ddm:.6f}")

                ratio = implied_listing / current_price if current_price > 0 else 0
                sanity = "PASS" if 0.05 < ratio < 20 else f"FAIL (ratio={ratio:.2f})"
                lines.append(f"- **DDM Sanity:** {sanity}")
                print(f"    DDM: implied={safe_dollar(implied_listing, ddm_cur)}, upside={upside:+.1f}%, sanity={sanity}")

        lines.append("")
        lines.append("---")
        lines.append("")

    # Write report
    report_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "test_results", "currency_fix_verification.md",
    )
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nReport: {report_path}")


if __name__ == "__main__":
    run_tests()
