"""Sensitivity analysis — 2D tables for WACC vs terminal growth."""

import pandas as pd
import numpy as np
from typing import Optional
from models.valuation import WACCResult


def sensitivity_table(
    fcf_table: pd.DataFrame,
    wacc_result: WACCResult,
    terminal_growth: float,
    terminal_method: str,
    exit_multiple: Optional[float],
    net_debt: float,
    shares: float,
    current_price: float,
    minority: float = 0.0,
    preferred: float = 0.0,
) -> pd.DataFrame:
    """2D sensitivity: implied price across WACC / terminal growth combos."""
    from lib.analysis.valuation.dcf import run_dcf

    base_wacc = wacc_result.wacc
    wacc_range = np.linspace(base_wacc - 0.02, base_wacc + 0.02, 5)
    g_range = np.linspace(max(0.005, terminal_growth - 0.01),
                          terminal_growth + 0.01, 5)

    data = {}
    for g in g_range:
        col = []
        for w in wacc_range:
            wr = WACCResult(**{**wacc_result.__dict__, "wacc": w})
            r = run_dcf(fcf_table, wr, g, terminal_method, exit_multiple,
                        net_debt, shares, current_price, minority, preferred)
            col.append(r.implied_price)
        data[f"g={g:.1%}"] = col

    return pd.DataFrame(data, index=[f"WACC={w:.1%}" for w in wacc_range])
