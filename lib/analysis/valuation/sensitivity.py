"""Sensitivity analysis — 2D tables for WACC vs terminal growth / exit multiple.

Pure Python — NO Streamlit imports.
"""

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
            # NaN for invalid cells (negative price, WACC <= g)
            col.append(r.implied_price if r.implied_price > 0 else np.nan)
        data[f"g={g:.1%}"] = col

    return pd.DataFrame(data, index=[f"{w:.1%}" for w in wacc_range])


def exit_sensitivity_table(
    fcf_table: pd.DataFrame,
    wacc_result: WACCResult,
    terminal_growth: float,
    exit_multiple: float,
    net_debt: float,
    shares: float,
    current_price: float,
    minority: float = 0.0,
    preferred: float = 0.0,
) -> pd.DataFrame:
    """2D sensitivity: implied price across WACC / exit multiple combos."""
    from lib.analysis.valuation.dcf import run_dcf

    base_wacc = wacc_result.wacc
    wacc_range = np.linspace(base_wacc - 0.02, base_wacc + 0.02, 5)
    mult_range = np.linspace(max(2.0, exit_multiple - 4), exit_multiple + 4, 5)

    data = {}
    for m in mult_range:
        col = []
        for w in wacc_range:
            wr = WACCResult(**{**wacc_result.__dict__, "wacc": w})
            r = run_dcf(fcf_table, wr, terminal_growth, "exit_multiple", m,
                        net_debt, shares, current_price, minority, preferred)
            col.append(r.implied_price if r.implied_price > 0 else np.nan)
        data[f"{m:.1f}x"] = col

    return pd.DataFrame(data, index=[f"{w:.1%}" for w in wacc_range])
