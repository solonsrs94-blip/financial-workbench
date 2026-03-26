"""
Valuation calculations — CAPM, WACC, DCF.

Pure Python — NO Streamlit imports.
All percentages in decimal form (0.10 = 10%).
"""

import pandas as pd
import numpy as np
from models.valuation import WACCInputs, DCFAssumptions, DCFResult


def calc_capm(rf: float, beta: float, mrp: float) -> float:
    """Cost of equity via CAPM: rE = Rf + beta * MRP."""
    return rf + beta * mrp


def calc_wacc(inputs: WACCInputs) -> float:
    """Weighted average cost of capital."""
    cost_of_equity = calc_capm(
        inputs.risk_free_rate, inputs.beta, inputs.market_risk_premium,
    )
    after_tax_debt = inputs.cost_of_debt * (1 - inputs.tax_rate)
    return inputs.equity_ratio * cost_of_equity + inputs.debt_ratio * after_tax_debt


def build_fcf_table(
    base_revenue: float,
    base_da: float,
    assumptions: DCFAssumptions,
) -> pd.DataFrame:
    """Build projected FCF table for n_years.

    Returns DataFrame with columns:
    Year, Revenue, EBIT, NOPAT, D&A, CapEx, dNWC, FCF
    """
    rows = []
    prev_revenue = base_revenue
    da_pct = assumptions.da_pct if assumptions.da_pct > 0 else 0.03

    for i in range(assumptions.n_years):
        growth = assumptions.revenue_growth_rates[i] if i < len(
            assumptions.revenue_growth_rates
        ) else assumptions.revenue_growth_rates[-1]

        revenue = prev_revenue * (1 + growth)
        ebit = revenue * assumptions.ebit_margin
        nopat = ebit * (1 - assumptions.tax_rate)
        da = revenue * da_pct
        capex = revenue * assumptions.capex_pct
        d_nwc = (revenue - prev_revenue) * assumptions.nwc_pct
        fcf = nopat + da - capex - d_nwc

        rows.append({
            "Year": i + 1,
            "Revenue": revenue,
            "EBIT": ebit,
            "NOPAT": nopat,
            "D&A": da,
            "CapEx": capex,
            "dNWC": d_nwc,
            "FCF": fcf,
        })
        prev_revenue = revenue

    return pd.DataFrame(rows)


def calc_terminal_value(
    last_fcf: float,
    last_ebitda: float,
    assumptions: DCFAssumptions,
) -> float:
    """Calculate terminal value using selected method."""
    method = assumptions.terminal_method

    tv_gordon = 0.0
    if assumptions.wacc > assumptions.terminal_growth:
        tv_gordon = last_fcf * (1 + assumptions.terminal_growth) / (
            assumptions.wacc - assumptions.terminal_growth
        )

    tv_exit = 0.0
    if assumptions.exit_multiple and assumptions.exit_multiple > 0:
        tv_exit = last_ebitda * assumptions.exit_multiple

    if method == "gordon":
        return tv_gordon
    elif method == "exit_multiple":
        return tv_exit
    else:  # average
        values = [v for v in [tv_gordon, tv_exit] if v > 0]
        return sum(values) / len(values) if values else 0.0


def run_dcf(
    base_revenue: float,
    base_da: float,
    net_debt: float,
    shares_outstanding: float,
    current_price: float,
    assumptions: DCFAssumptions,
) -> DCFResult:
    """Run full DCF valuation. Returns DCFResult."""
    fcf_table = build_fcf_table(base_revenue, base_da, assumptions)

    last_row = fcf_table.iloc[-1]
    last_fcf = last_row["FCF"]
    last_ebitda = last_row["EBIT"] + last_row["D&A"]

    tv = calc_terminal_value(last_fcf, last_ebitda, assumptions)

    # Discount FCFs and terminal value
    discount_factors = [1 / (1 + assumptions.wacc) ** t for t in range(1, assumptions.n_years + 1)]
    pv_fcfs = [fcf_table["FCF"].iloc[i] * discount_factors[i] for i in range(assumptions.n_years)]
    pv_terminal = tv * discount_factors[-1]

    ev = sum(pv_fcfs) + pv_terminal
    equity_value = ev - net_debt
    implied_price = equity_value / shares_outstanding if shares_outstanding > 0 else 0.0

    tv_pct = pv_terminal / ev if ev > 0 else 0.0

    return DCFResult(
        fcf_table=fcf_table,
        terminal_value=tv,
        pv_fcfs=pv_fcfs,
        pv_terminal=pv_terminal,
        enterprise_value=ev,
        net_debt=net_debt,
        equity_value=equity_value,
        shares_outstanding=shares_outstanding,
        implied_price=implied_price,
        current_price=current_price,
        tv_pct_of_ev=tv_pct,
    )


def sensitivity_table(
    base_revenue: float,
    base_da: float,
    net_debt: float,
    shares: float,
    current_price: float,
    assumptions: DCFAssumptions,
    wacc_steps: int = 5,
    growth_steps: int = 5,
) -> pd.DataFrame:
    """2D sensitivity: implied price at various WACC / terminal growth combos."""
    base_wacc = assumptions.wacc
    base_g = assumptions.terminal_growth
    wacc_range = np.linspace(base_wacc - 0.02, base_wacc + 0.02, wacc_steps)
    growth_range = np.linspace(max(0.005, base_g - 0.01), base_g + 0.01, growth_steps)

    data = {}
    for g in growth_range:
        col = []
        for w in wacc_range:
            a = DCFAssumptions(**{
                **assumptions.__dict__,
                "wacc": w,
                "terminal_growth": g,
                "revenue_growth_rates": list(assumptions.revenue_growth_rates),
            })
            result = run_dcf(base_revenue, base_da, net_debt, shares, current_price, a)
            col.append(result.implied_price)
        data[f"g={g:.1%}"] = col

    index = [f"WACC={w:.1%}" for w in wacc_range]
    return pd.DataFrame(data, index=index)
