"""End-to-end DCF test on MSFT."""

import pandas as pd
from lib.analysis.valuation.dcf import run_dcf, calc_terminal_value
from lib.analysis.valuation.sensitivity import sensitivity_table, exit_sensitivity_table
from models.valuation import WACCResult
import yfinance as yf

ticker = "MSFT"
stock = yf.Ticker(ticker)
info = stock.info or {}

print("=" * 60)
print("MSFT DCF END-TO-END TEST")
print("=" * 60)

# ── STEP 1: Financial Preparation ──────────────
current_price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
market_cap = info.get("marketCap", 0)
shares_raw = info.get("impliedSharesOutstanding") or info.get("sharesOutstanding", 0)
print(f"\nStep 1: Financial Preparation")
print(f"  Current Price: ${current_price:,.2f}")
print(f"  Market Cap: ${market_cap/1e9:,.1f}B")
print(f"  Shares: {shares_raw/1e9:,.2f}B")

inc = stock.income_stmt
if inc is not None and not inc.empty:
    last_rev = float(inc.loc["Total Revenue"].iloc[0])
    print(f"  Last Revenue: ${last_rev/1e9:,.1f}B")
else:
    last_rev = 245e9
    print(f"  Last Revenue (fallback): ${last_rev/1e9:,.1f}B")

bs = stock.balance_sheet
total_debt = cash = minority = preferred = 0
if bs is not None and not bs.empty:
    if "Total Debt" in bs.index:
        total_debt = float(bs.loc["Total Debt"].iloc[0])
    cash_row = "Cash And Cash Equivalents"
    if cash_row in bs.index:
        cash = float(bs.loc[cash_row].iloc[0])
    if "Minority Interest" in bs.index:
        v = bs.loc["Minority Interest"].iloc[0]
        minority = float(v) if str(v) != "nan" else 0
    if "Preferred Stock" in bs.index:
        v = bs.loc["Preferred Stock"].iloc[0]
        preferred = float(v) if str(v) != "nan" else 0

net_debt_raw = total_debt - cash
print(f"  Total Debt: ${total_debt/1e9:,.1f}B")
print(f"  Cash: ${cash/1e9:,.1f}B")
print(f"  Net Debt: ${net_debt_raw/1e9:,.1f}B")
print(f"  Minority Interest: ${minority/1e9:,.1f}B")

# ── STEP 2: Assumptions ───────────────────────
print(f"\nStep 2: Assumptions")
n_years = 5
base_revenue_M = last_rev / 1e6

growth_rates = [0.13, 0.12, 0.10, 0.09, 0.08]
ebit_margins = [0.45, 0.455, 0.46, 0.46, 0.46]
tax_rates = [0.18, 0.18, 0.18, 0.18, 0.18]
capex_pcts = [0.20, 0.19, 0.18, 0.17, 0.16]
da_pcts = [0.07, 0.07, 0.07, 0.07, 0.07]
sbc_pcts = [0.04, 0.04, 0.04, 0.04, 0.04]

print(f"  Base Revenue: ${base_revenue_M:,.0f}M (${base_revenue_M/1e3:,.1f}B)")
print(f"  Growth: {[f'{g*100:.0f}%' for g in growth_rates]}")
print(f"  EBIT Margins: {[f'{m*100:.1f}%' for m in ebit_margins]}")
print(f"  Tax: {tax_rates[0]*100:.0f}% | CapEx: {[f'{c*100:.0f}%' for c in capex_pcts]}")
print(f"  D&A: {da_pcts[0]*100:.0f}% | SBC: {sbc_pcts[0]*100:.0f}%")

# Build FCF table
prev_rev = base_revenue_M
rows = []
for i in range(n_years):
    rev = prev_rev * (1 + growth_rates[i])
    ebit = rev * ebit_margins[i]
    da = rev * da_pcts[i]
    nopat = ebit * (1 - tax_rates[i])
    capex = rev * capex_pcts[i]
    sbc = rev * sbc_pcts[i]
    # Simplified NWC (small for MSFT)
    d_nwc = rev * 0.005  # ~0.5% of revenue
    fcf = nopat + da - capex - sbc - d_nwc

    rows.append({
        "Year": i + 1, "Revenue": rev, "Growth": growth_rates[i],
        "EBIT": ebit, "EBIT_Margin": ebit_margins[i],
        "NOPAT": nopat, "D&A": da, "CapEx": capex,
        "dNWC": d_nwc, "SBC": sbc, "FCF": fcf,
        "EBITDA": ebit + da,
    })
    prev_rev = rev

fcf_table = pd.DataFrame(rows)

print(f"\n  Projected (in $M):")
print(f"  {'Year':>6} {'Revenue':>12} {'EBIT':>12} {'FCF':>12} {'EBITDA':>12}")
for _, r in fcf_table.iterrows():
    print(f"  {int(r['Year']):>6} ${r['Revenue']:>11,.0f} ${r['EBIT']:>11,.0f} "
          f"${r['FCF']:>11,.0f} ${r['EBITDA']:>11,.0f}")

# ── STEP 3: WACC ──────────────────────────────
print(f"\nStep 3: WACC")
ke = 0.0431 + 1.072 * 0.0477  # Rf + Beta*ERP
kd_pretax = 0.0394
tax = 0.18
kd_after = kd_pretax * (1 - tax)

total_v = market_cap + total_debt
e_wt = market_cap / total_v if total_v > 0 else 1.0
d_wt = total_debt / total_v if total_v > 0 else 0.0
wacc = ke * e_wt + kd_after * d_wt

wacc_result = WACCResult(
    rf=0.0431, beta=1.072, erp=0.0477,
    cost_of_equity=ke,
    cost_of_debt_pretax=kd_pretax,
    tax_rate=tax,
    cost_of_debt_aftertax=kd_after,
    equity_weight=e_wt, debt_weight=d_wt,
    wacc=wacc,
)

print(f"  Ke = {ke*100:.2f}%")
print(f"  Kd(1-t) = {kd_after*100:.2f}%")
print(f"  E/V = {e_wt*100:.1f}%, D/V = {d_wt*100:.1f}%")
print(f"  WACC = {wacc*100:.2f}%")

# ── STEP 4: Terminal Value ────────────────────
print(f"\nStep 4: Terminal Value")
g = 0.025
ev_ebitda_yahoo = info.get("enterpriseToEbitda") or 25.0
exit_mult = ev_ebitda_yahoo

last_fcf = fcf_table.iloc[-1]["FCF"]
last_ebitda = fcf_table.iloc[-1]["EBITDA"]

tv_gordon = calc_terminal_value(last_fcf, last_ebitda, g, wacc, "gordon")
tv_exit = calc_terminal_value(last_fcf, last_ebitda, g, wacc, "exit_multiple", exit_mult)

print(f"  Terminal Growth: {g*100:.1f}%")
print(f"  Exit Multiple (Yahoo): {exit_mult:.1f}x")
print(f"  Gordon TV: ${tv_gordon:,.0f}M (${tv_gordon/1e3:,.0f}B)")
print(f"  Exit TV: ${tv_exit:,.0f}M (${tv_exit/1e3:,.0f}B)")
print(f"  Gordon implied exit: {tv_gordon/last_ebitda:.1f}x")
if tv_exit > 0 and last_fcf > 0:
    k = last_fcf / tv_exit
    impl_g = (wacc - k) / (1 + k)
    print(f"  Exit implied growth: {impl_g*100:.2f}%")

# ── STEP 5: DCF Output ───────────────────────
print(f"\nStep 5: DCF Output")
net_debt_M = net_debt_raw / 1e6
minority_M = minority / 1e6
preferred_M = preferred / 1e6
shares_M = shares_raw / 1e6

result = run_dcf(
    fcf_table, wacc_result, g, "gordon", exit_mult,
    net_debt_M, shares_M, current_price, minority_M, preferred_M,
)

pv_fcfs_total = sum(result.pv_fcfs)
print(f"\n  === RESULTS ===")
print(f"  PV of FCFs:  ${pv_fcfs_total:,.0f}M (${pv_fcfs_total/1e3:,.0f}B)")
print(f"  PV of TV:    ${result.pv_terminal:,.0f}M (${result.pv_terminal/1e3:,.0f}B)")
print(f"  Enterpr. V:  ${result.enterprise_value:,.0f}M (${result.enterprise_value/1e3:,.0f}B)")
print(f"  TV/EV:       {result.tv_pct_of_ev:.0%}")
print(f"")
print(f"  Equity Bridge:")
print(f"    EV:         ${result.enterprise_value:,.0f}M")
print(f"    - Net Debt: ${net_debt_M:,.0f}M")
print(f"    - Minority: ${minority_M:,.0f}M")
print(f"    - Preferred:${preferred_M:,.0f}M")
print(f"    = Equity:   ${result.bridge.equity_value:,.0f}M (${result.bridge.equity_value/1e3:,.0f}B)")
print(f"")
print(f"  Shares: {shares_M:,.0f}M ({shares_raw/1e9:,.2f}B)")
print(f"  Implied Price:  ${result.implied_price:,.2f}")
print(f"  Current Price:  ${current_price:,.2f}")
upside = (result.implied_price / current_price - 1) * 100 if current_price > 0 else 0
print(f"  Upside/Downside: {upside:+.1f}%")

print(f"\n  === SANITY CHECKS ===")
print(f"  TV/EV: {result.tv_pct_of_ev:.0%} {'OK' if 0.5 <= result.tv_pct_of_ev <= 0.85 else 'WARNING'}")
if result.implied_exit_multiple:
    print(f"  Implied Exit: {result.implied_exit_multiple:.1f}x")
print(f"  Rev CAGR: {result.revenue_cagr:.1%}")
price_ratio = result.implied_price / current_price if current_price > 0 else 0
print(f"  Price ratio: {price_ratio:.2f}x {'OK' if 0.5 < price_ratio < 2.0 else 'WARNING'}")
for w in result.warnings:
    print(f"  WARNING: {w}")

# ── SENSITIVITY ───────────────────────────────
print(f"\n  === SENSITIVITY: WACC vs Terminal Growth ===")
sens_g = sensitivity_table(
    fcf_table, wacc_result, g, "gordon", exit_mult,
    net_debt_M, shares_M, current_price, minority_M, preferred_M,
)
print(sens_g.map(lambda x: f"${x:,.0f}").to_string())

print(f"\n  === SENSITIVITY: WACC vs Exit Multiple ===")
sens_m = exit_sensitivity_table(
    fcf_table, wacc_result, g, exit_mult,
    net_debt_M, shares_M, current_price, minority_M, preferred_M,
)
print(sens_m.map(lambda x: f"${x:,.0f}").to_string())
