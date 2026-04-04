"""
DCF calculation engine — shared by Simple and Complex modes.

Same FCF formula for both. Simple auto-populates inputs, Complex lets user override.
Pure Python — NO Streamlit imports.
"""

import pandas as pd
import numpy as np
from typing import Optional
from models.valuation import DCFResult, EquityBridge, WACCResult


def build_fcf_table(
    base_revenue: float,
    n_years: int,
    growth_rates: list,
    ebit_margins: list,
    tax_rate: float,
    capex_pcts: list,
    da_pcts: list,
    sbc_pcts: list,
    dso: list, dio: list, dpo: list,
    base_cogs_pct: float = 0.60,
) -> pd.DataFrame:
    """Build FCF projection table using the same formula for Simple and Complex.

    All list inputs should have length n_years.
    Returns DataFrame with full line items per year.
    """
    rows = []
    prev_revenue = base_revenue
    prev_nwc = 0.0  # Will be set from year 0

    for i in range(n_years):
        growth = growth_rates[i] if i < len(growth_rates) else growth_rates[-1]
        revenue = prev_revenue * (1 + growth)

        # Cost structure — derive from EBIT margin
        margin = ebit_margins[i] if i < len(ebit_margins) else ebit_margins[-1]
        da_pct = da_pcts[i] if i < len(da_pcts) else da_pcts[-1]
        ebit = revenue * margin
        da = revenue * da_pct

        # Tax
        nopat = ebit * (1 - tax_rate)

        # CapEx
        capex_pct = capex_pcts[i] if i < len(capex_pcts) else capex_pcts[-1]
        capex = revenue * capex_pct

        # Working capital from days
        cogs = revenue * base_cogs_pct
        rec = revenue * (dso[i] if i < len(dso) else dso[-1]) / 365
        inv = cogs * (dio[i] if i < len(dio) else dio[-1]) / 365
        pay = cogs * (dpo[i] if i < len(dpo) else dpo[-1]) / 365
        nwc = rec + inv - pay

        if i == 0:
            # Estimate base NWC from base revenue
            base_cogs = base_revenue * base_cogs_pct
            prev_nwc = (base_revenue * dso[0] / 365 +
                        base_cogs * dio[0] / 365 -
                        base_cogs * dpo[0] / 365)

        d_nwc = nwc - prev_nwc

        # SBC
        sbc_pct = sbc_pcts[i] if i < len(sbc_pcts) else sbc_pcts[-1]
        sbc = revenue * sbc_pct

        # FCF
        fcf = nopat + da - capex - d_nwc - sbc

        rows.append({
            "Year": i + 1,
            "Revenue": revenue,
            "Growth": growth,
            "EBIT": ebit,
            "EBIT_Margin": margin,
            "NOPAT": nopat,
            "D&A": da,
            "CapEx": capex,
            "dNWC": d_nwc,
            "SBC": sbc,
            "FCF": fcf,
            "EBITDA": ebit + da,
        })

        prev_revenue = revenue
        prev_nwc = nwc

    return pd.DataFrame(rows)


def calc_terminal_value(
    last_fcf: float, last_ebitda: float,
    terminal_growth: float, wacc: float,
    method: str = "gordon",
    exit_multiple: Optional[float] = None,
) -> float:
    """Calculate terminal value. method: 'gordon' | 'exit_multiple' | 'average'."""
    tv_gordon = 0.0
    if wacc > terminal_growth:
        tv_gordon = last_fcf * (1 + terminal_growth) / (wacc - terminal_growth)

    tv_exit = last_ebitda * exit_multiple if exit_multiple and exit_multiple > 0 else 0.0

    if method == "gordon":
        return tv_gordon
    elif method == "exit_multiple":
        return tv_exit
    else:  # average
        vals = [v for v in [tv_gordon, tv_exit] if v > 0]
        return sum(vals) / len(vals) if vals else 0.0


def run_dcf(
    fcf_table: pd.DataFrame,
    wacc_result: WACCResult,
    terminal_growth: float,
    terminal_method: str,
    exit_multiple: Optional[float],
    net_debt: float,
    shares: float,
    current_price: float,
    minority_interest: float = 0.0,
    preferred_equity: float = 0.0,
) -> DCFResult:
    """Run DCF from a built FCF table. Returns DCFResult."""
    wacc = wacc_result.wacc
    n = len(fcf_table)

    last = fcf_table.iloc[-1]
    tv = calc_terminal_value(
        last["FCF"], last["EBITDA"], terminal_growth, wacc,
        terminal_method, exit_multiple,
    )

    # Discount
    discount = [1 / (1 + wacc) ** t for t in range(1, n + 1)]
    pv_fcfs = [float(fcf_table["FCF"].iloc[i] * discount[i]) for i in range(n)]
    pv_terminal = tv * discount[-1]
    ev = sum(pv_fcfs) + pv_terminal

    # Equity bridge (guard against None values)
    net_debt = net_debt or 0
    minority_interest = minority_interest or 0
    preferred_equity = preferred_equity or 0
    equity_value = ev - net_debt - minority_interest - preferred_equity
    implied_price = equity_value / shares if shares and shares > 0 else 0.0

    bridge = EquityBridge(
        enterprise_value=ev, net_debt=net_debt,
        minority_interest=minority_interest,
        preferred_equity=preferred_equity,
        equity_value=equity_value,
        diluted_shares=shares,
        implied_price=implied_price,
    )

    # Sanity
    tv_pct = pv_terminal / ev if ev > 0 else 0.0
    implied_exit = tv / last["EBITDA"] if last["EBITDA"] > 0 else None
    base_rev = fcf_table["Revenue"].iloc[0] / (1 + fcf_table["Growth"].iloc[0])
    final_rev = fcf_table["Revenue"].iloc[-1]
    cagr = (final_rev / base_rev) ** (1 / n) - 1 if base_rev > 0 else 0.0

    warnings = []
    if tv_pct > 0.85:
        warnings.append(
            f"Terminal value is {tv_pct:.0%} of EV — consider whether "
            f"growth/WACC assumptions are realistic"
        )
    elif tv_pct > 0.75:
        warnings.append(f"Terminal value is {tv_pct:.0%} of EV — high forecast uncertainty")
    if implied_exit and implied_exit > 25:
        warnings.append(f"Implied exit multiple of {implied_exit:.1f}x is very high")
    if terminal_growth > 0.04:
        warnings.append(f"Terminal growth of {terminal_growth:.1%} exceeds typical GDP growth")

    return DCFResult(
        fcf_table=fcf_table,
        terminal_value=tv,
        pv_fcfs=pv_fcfs,
        pv_terminal=pv_terminal,
        enterprise_value=ev,
        bridge=bridge,
        wacc_result=wacc_result,
        implied_price=implied_price,
        current_price=current_price,
        tv_pct_of_ev=tv_pct,
        implied_exit_multiple=implied_exit,
        revenue_cagr=cagr,
        terminal_margin=float(last["EBIT_Margin"]),
        warnings=warnings,
    )


# Sensitivity analysis — see lib/analysis/valuation/sensitivity.py
