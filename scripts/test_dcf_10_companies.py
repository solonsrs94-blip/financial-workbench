"""DCF Stress Test — 10 companies end-to-end.

Replicates the exact same data flow as the UI:
  Step 1: standardize_yfinance → build tables → build ratios
  Step 2: compute_projections (assumptions based on historical ratios)
  Step 3: WACC (CAPM + actual Kd + market structure)
  Step 4: Terminal Value (Gordon + Exit Multiple)
  Step 5: run_dcf → DCFResult

Run: PYTHONPATH=. python scripts/test_dcf_10_companies.py
"""

import sys
import warnings
import traceback
warnings.filterwarnings("ignore")

import pandas as pd
import yfinance as yf

from lib.data.yfinance_standardizer import standardize_yfinance
from lib.analysis.historical import (
    build_income_table, build_balance_table, build_cashflow_table,
)
from lib.analysis.historical_ratios import build_ratios_table
from pages.valuation.dcf_step2_table import build_historical_data, compute_projections
from lib.analysis.valuation.dcf import run_dcf, calc_terminal_value
from lib.analysis.valuation.sensitivity import sensitivity_table
from models.valuation import WACCResult

# ═══════════════════════════════════════════════════════════════
# 10 COMPANIES — diverse sectors, all suitable for DCF
# ═══════════════════════════════════════════════════════════════

COMPANIES = [
    ("AAPL", "Technology"),
    ("JNJ", "Healthcare"),
    ("PG", "Consumer Defensive"),
    ("V", "Financial Services"),
    ("HD", "Consumer Cyclical"),
    ("PEP", "Consumer Defensive"),
    ("COST", "Consumer Defensive"),
    ("AMZN", "Consumer Cyclical"),
    ("GOOGL", "Communication Svc"),
    ("UNP", "Industrials"),
]

# Current 10Y Treasury rate (from recent data)
RF = 0.0431
# Damodaran implied ERP (approximate)
ERP = 0.0477

N_YEARS = 5


def safe_float(val, default=0.0):
    """Safe float conversion."""
    if val is None:
        return default
    try:
        v = float(val)
        return default if pd.isna(v) else v
    except (ValueError, TypeError):
        return default


def get_last_ratio(ratios, key, default=None):
    """Get last non-None value for a ratio key."""
    for r in reversed(ratios):
        v = r.get(key)
        if v is not None and not pd.isna(v):
            return v
    return default


def avg_ratio(ratios, key, n=3, default=None):
    """Average of last n non-None values for a ratio key."""
    vals = []
    for r in reversed(ratios):
        v = r.get(key)
        if v is not None and not pd.isna(v):
            vals.append(v)
            if len(vals) >= n:
                break
    return sum(vals) / len(vals) if vals else default


def build_assumptions(ratios, n_years=5):
    """Build reasonable DCF assumptions from historical ratios.

    Strategy: start near recent values, mean-revert slightly over 5yr.
    """
    # Revenue growth: taper from recent toward ~5% long-term
    recent_g = get_last_ratio(ratios, "revenue_growth", 0.08)
    avg_g = avg_ratio(ratios, "revenue_growth", 3, 0.08)
    start_g = min(max(avg_g, 0.02), 0.25)  # Clamp 2-25%
    end_g = max(0.03, start_g * 0.5)  # Fade to ~half
    growth = [start_g + (end_g - start_g) * i / (n_years - 1)
              for i in range(n_years)]

    # EBIT margin: slight expansion from 3yr average
    avg_margin = avg_ratio(ratios, "ebit_margin", 3, 0.15)
    if avg_margin is None or avg_margin <= 0:
        avg_margin = 0.15
    margin_start = min(max(avg_margin, 0.03), 0.60)
    margins = [margin_start + 0.005 * i for i in range(n_years)]

    # Tax rate: use recent effective rate
    tax = avg_ratio(ratios, "effective_tax_rate", 3, 0.21)
    if tax is None or tax <= 0 or tax > 0.50:
        tax = 0.21
    taxes = [tax] * n_years

    # CapEx/Revenue
    capex = avg_ratio(ratios, "capex_pct", 3, 0.05)
    if capex is None or capex <= 0:
        capex = 0.05
    capex = min(capex, 0.30)
    capex_pcts = [capex - 0.005 * i for i in range(n_years)]
    capex_pcts = [max(0.02, c) for c in capex_pcts]

    # D&A/Revenue
    da = avg_ratio(ratios, "da_pct", 3, 0.04)
    if da is None or da <= 0:
        da = 0.04
    da_pcts = [min(da, 0.15)] * n_years

    # SBC/Revenue
    sbc = avg_ratio(ratios, "sbc_pct", 3, 0.02)
    if sbc is None or sbc <= 0:
        sbc = 0.01
    sbc_pcts = [min(sbc, 0.10)] * n_years

    # NWC (simplified)
    nwc = avg_ratio(ratios, "nwc_pct_revenue", 3, 0.05)
    if nwc is None:
        nwc = 0.05
    nwc = max(-0.20, min(0.30, nwc))

    return {
        "n_years": n_years,
        "nwc_method": "simplified",
        "growth_rates": growth,
        "ebit_margins": margins,
        "tax_rates": taxes,
        "capex_pcts": capex_pcts,
        "da_pcts": da_pcts,
        "sbc_pcts": sbc_pcts,
        "nwc_pcts": [nwc] * n_years,
        "dso": [60] * n_years,
        "dio": [30] * n_years,
        "dpo": [40] * n_years,
    }


def compute_wacc(info, val_data):
    """Compute WACC from Yahoo data."""
    beta_raw = safe_float(info.get("beta"), 1.0)
    beta = 0.333 + 0.667 * beta_raw  # Blume adjustment

    ke = RF + beta * ERP

    # Cost of debt
    bs = val_data.get("balance_sheet", {})
    inc = val_data.get("income_detail", {})
    total_debt = safe_float(bs.get("total_debt"), 0)
    interest = safe_float(inc.get("interest_expense"), 0)
    kd_pretax = interest / total_debt if total_debt > 0 else 0.04
    kd_pretax = min(max(kd_pretax, 0.01), 0.15)  # Clamp

    tax = safe_float(inc.get("effective_tax_rate"), 0.21)
    if tax <= 0 or tax > 0.50:
        tax = 0.21
    kd_after = kd_pretax * (1 - tax)

    # Capital structure
    market_cap = safe_float(info.get("marketCap"), 0)
    total_v = market_cap + total_debt
    e_wt = market_cap / total_v if total_v > 0 else 1.0
    d_wt = total_debt / total_v if total_v > 0 else 0.0

    wacc = ke * e_wt + kd_after * d_wt

    return WACCResult(
        rf=RF, beta=beta, erp=ERP,
        cost_of_equity=ke,
        cost_of_debt_pretax=kd_pretax,
        tax_rate=tax,
        cost_of_debt_aftertax=kd_after,
        equity_weight=e_wt, debt_weight=d_wt,
        wacc=wacc,
    )


def run_single_test(ticker, sector_label):
    """Run full DCF for one company. Returns result dict or error str."""
    result = {"ticker": ticker, "sector": sector_label}

    # ── Step 1: Fetch & Standardize ────────────────────────
    stock = yf.Ticker(ticker)
    info = stock.info or {}

    inc_stmt = stock.income_stmt
    bs_stmt = stock.balance_sheet
    cf_stmt = stock.cashflow

    std = standardize_yfinance(inc_stmt, bs_stmt, cf_stmt)
    if std is None:
        return {**result, "error": "standardize_yfinance returned None"}

    years = std.get("years", [])
    if len(years) < 2:
        return {**result, "error": f"Only {len(years)} years of data"}

    # Build tables and ratios (same as preparation.py)
    is_t = build_income_table(std, years)
    bs_t = build_balance_table(std, years)
    cf_t = build_cashflow_table(std, years)
    ratios = build_ratios_table(is_t, bs_t, cf_t)

    # Get base revenue
    last_yr = years[-1]
    last_inc = std["income"].get(last_yr, {})
    base_revenue = (safe_float(last_inc.get("total_revenue"))
                    or safe_float(last_inc.get("revenue")))
    if not base_revenue or base_revenue <= 0:
        return {**result, "error": "No base revenue"}

    # COGS %
    cogs = safe_float(last_inc.get("cost_of_revenue"))
    if cogs and base_revenue > 0:
        base_cogs_pct = abs(cogs) / abs(base_revenue)
    else:
        base_cogs_pct = 0.50

    result["base_revenue_B"] = base_revenue / 1e9

    # ── Step 2: Assumptions & Projections ──────────────────
    assumptions = build_assumptions(ratios, N_YEARS)
    result["assumptions"] = {
        "growth": assumptions["growth_rates"][0],
        "margin": assumptions["ebit_margins"][0],
        "capex": assumptions["capex_pcts"][0],
    }

    proj = compute_projections(assumptions, base_revenue, base_cogs_pct)
    if proj is None:
        return {**result, "error": "compute_projections returned None"}

    # Build FCF DataFrame (same as dcf_step5_output._build_fcf_df)
    rows = []
    for i in range(len(proj["fcf"])):
        ebit = proj["ebit"][i]
        da = proj["da"][i]
        rows.append({
            "Year": i + 1, "Revenue": proj["revenue"][i],
            "Growth": assumptions["growth_rates"][i],
            "EBIT": ebit, "EBIT_Margin": assumptions["ebit_margins"][i],
            "NOPAT": proj["nopat"][i], "D&A": da,
            "CapEx": proj["capex"][i], "dNWC": proj["nwc_change"][i],
            "SBC": proj["sbc"][i], "FCF": proj["fcf"][i],
            "EBITDA": ebit + da,
        })
    fcf_table = pd.DataFrame(rows)
    result["last_fcf_M"] = proj["fcf"][-1]
    result["last_ebitda_M"] = proj["ebit"][-1] + proj["da"][-1]

    # ── Step 3: WACC ──────────────────────────────────────
    from lib.data.providers.yahoo_valuation import fetch_valuation_data
    val_data = fetch_valuation_data(ticker) or {}

    wacc_result = compute_wacc(info, val_data)
    result["wacc"] = wacc_result.wacc

    # ── Step 4: Terminal Value ────────────────────────────
    g = 0.025
    ev_ebitda_yahoo = safe_float(info.get("enterpriseToEbitda"), 12.0)
    if ev_ebitda_yahoo <= 0 or ev_ebitda_yahoo > 100:
        ev_ebitda_yahoo = 12.0
    exit_mult = ev_ebitda_yahoo

    last_fcf = proj["fcf"][-1]
    last_ebitda = proj["ebit"][-1] + proj["da"][-1]

    tv_gordon = calc_terminal_value(last_fcf, last_ebitda, g, wacc_result.wacc, "gordon")
    tv_exit = calc_terminal_value(last_fcf, last_ebitda, g, wacc_result.wacc,
                                  "exit_multiple", exit_mult)

    result["exit_multiple"] = exit_mult

    # ── Step 5: DCF Output ────────────────────────────────
    # Bridge inputs (same as dcf_step5_output._get_bridge_inputs)
    bs_data = val_data.get("balance_sheet", {})
    net_debt_M = safe_float(bs_data.get("net_debt"), 0) / 1e6
    minority_M = safe_float(bs_data.get("minority_interest"), 0) / 1e6
    preferred_M = safe_float(bs_data.get("preferred_equity"), 0) / 1e6

    # Fallback to standardized if val_data missing
    if net_debt_M == 0:
        last_bs = std.get("balance", {}).get(last_yr, {})
        net_debt_M = safe_float(last_bs.get("net_debt"), 0) / 1e6

    shares_raw = (safe_float(val_data.get("shares"))
                  or safe_float(info.get("impliedSharesOutstanding"))
                  or safe_float(info.get("sharesOutstanding"))
                  or 1)
    shares_M = shares_raw / 1e6

    current_price = safe_float(
        info.get("currentPrice") or info.get("regularMarketPrice"), 0)

    # Run DCF — Gordon
    dcf_gordon = run_dcf(
        fcf_table, wacc_result, g, "gordon", exit_mult,
        net_debt_M, shares_M, current_price, minority_M, preferred_M,
    )

    # Run DCF — Exit Multiple
    dcf_exit = run_dcf(
        fcf_table, wacc_result, g, "exit_multiple", exit_mult,
        net_debt_M, shares_M, current_price, minority_M, preferred_M,
    )

    result["ev_gordon_B"] = dcf_gordon.enterprise_value / 1e3
    result["ev_exit_B"] = dcf_exit.enterprise_value / 1e3
    result["price_gordon"] = dcf_gordon.implied_price
    result["price_exit"] = dcf_exit.implied_price
    result["current_price"] = current_price
    result["tv_ev_pct"] = dcf_gordon.tv_pct_of_ev
    result["warnings"] = dcf_gordon.warnings + dcf_exit.warnings

    if current_price > 0:
        result["upside_gordon"] = (dcf_gordon.implied_price / current_price - 1) * 100
        result["upside_exit"] = (dcf_exit.implied_price / current_price - 1) * 100
    else:
        result["upside_gordon"] = 0
        result["upside_exit"] = 0

    return result


# ═══════════════════════════════════════════════════════════════
# MAIN — Run all 10 companies
# ═══════════════════════════════════════════════════════════════

def main():
    print("=" * 90)
    print("DCF STRESS TEST — 10 COMPANIES")
    print("=" * 90)
    print(f"Risk-Free Rate: {RF*100:.2f}% | ERP: {ERP*100:.2f}% | "
          f"Projection: {N_YEARS}yr | Terminal Growth: 2.50%\n")

    results = []
    for ticker, sector in COMPANIES:
        print(f"  Testing {ticker} ({sector})...", end=" ", flush=True)
        try:
            r = run_single_test(ticker, sector)
            if "error" in r:
                print(f"ERROR: {r['error']}")
            else:
                print(f"OK — ${r['price_exit']:,.0f} (exit) / "
                      f"${r['price_gordon']:,.0f} (gordon) vs "
                      f"${r['current_price']:,.0f}")
            results.append(r)
        except Exception as e:
            print(f"CRASH: {e}")
            traceback.print_exc()
            results.append({
                "ticker": ticker, "sector": sector,
                "error": f"Exception: {e}",
            })

    # ── Summary Table ─────────────────────────────────────
    print("\n" + "=" * 90)
    print("SUMMARY TABLE")
    print("=" * 90)

    header = (f"{'Ticker':<7} {'Sector':<18} {'WACC':>6} {'Exit':>5} "
              f"{'$Exit':>8} {'$Gordon':>8} {'$Mkt':>8} "
              f"{'Up(E)':>7} {'Up(G)':>7} {'TV/EV':>6} {'OK?':<4}")
    print(header)
    print("-" * 90)

    ok_count = 0
    for r in results:
        if "error" in r:
            print(f"{r['ticker']:<7} {r['sector']:<18} {'ERROR: ' + r['error']}")
            continue

        wacc_s = f"{r['wacc']*100:.1f}%"
        exit_s = f"{r['exit_multiple']:.1f}x"
        pe = f"${r['price_exit']:,.0f}"
        pg = f"${r['price_gordon']:,.0f}"
        pm = f"${r['current_price']:,.0f}"
        ue = f"{r['upside_exit']:+.0f}%"
        ug = f"{r['upside_gordon']:+.0f}%"
        tv = f"{r['tv_ev_pct']:.0%}"

        # "OK" if exit-multiple implied is within ±50%
        is_ok = abs(r["upside_exit"]) < 50
        ok_str = "Yes" if is_ok else "NO"
        if is_ok:
            ok_count += 1

        print(f"{r['ticker']:<7} {r['sector']:<18} {wacc_s:>6} {exit_s:>5} "
              f"{pe:>8} {pg:>8} {pm:>8} "
              f"{ue:>7} {ug:>7} {tv:>6} {ok_str:<4}")

    total = len([r for r in results if "error" not in r])
    print("-" * 90)
    print(f"{'':>58} {ok_count}/{total} within ±50% (exit multiple)")

    # ── Warnings ──────────────────────────────────────────
    print(f"\nWARNINGS:")
    for r in results:
        if "error" in r:
            continue
        if r.get("warnings"):
            for w in set(r["warnings"]):
                print(f"  {r['ticker']}: {w}")

    # ── Analysis ──────────────────────────────────────────
    print(f"\n{'='*90}")
    print("ANALYSIS")
    print(f"{'='*90}")

    valid = [r for r in results if "error" not in r]
    if valid:
        exit_upsides = [r["upside_exit"] for r in valid]
        gordon_upsides = [r["upside_gordon"] for r in valid]
        print(f"\nExit Multiple method:")
        print(f"  Mean upside: {sum(exit_upsides)/len(exit_upsides):+.1f}%")
        print(f"  Median: {sorted(exit_upsides)[len(exit_upsides)//2]:+.1f}%")
        print(f"  Range: {min(exit_upsides):+.1f}% to {max(exit_upsides):+.1f}%")

        print(f"\nGordon Growth method:")
        print(f"  Mean upside: {sum(gordon_upsides)/len(gordon_upsides):+.1f}%")
        print(f"  Median: {sorted(gordon_upsides)[len(gordon_upsides)//2]:+.1f}%")
        print(f"  Range: {min(gordon_upsides):+.1f}% to {max(gordon_upsides):+.1f}%")

        tv_pcts = [r["tv_ev_pct"] for r in valid]
        print(f"\nTV/EV: {min(tv_pcts):.0%} – {max(tv_pcts):.0%} "
              f"(avg {sum(tv_pcts)/len(tv_pcts):.0%})")


if __name__ == "__main__":
    main()
