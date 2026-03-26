"""
Valuation models — standardized representations for WACC, DCF, and comps.

Used by lib/analysis/valuation/ and displayed by pages/valuation/.
All percentages in decimal form (0.10 = 10%).
"""

from dataclasses import dataclass, field
from typing import Optional
import pandas as pd


@dataclass
class WACCResult:
    """Complete WACC calculation with all intermediates for display."""
    # Cost of equity
    rf: float = 0.04
    beta: float = 1.0
    erp: float = 0.055
    size_premium: float = 0.0
    crp: float = 0.0
    cost_of_equity: float = 0.10
    # Cost of debt
    cost_of_debt_pretax: float = 0.05
    tax_rate: float = 0.21
    cost_of_debt_aftertax: float = 0.04
    rd_method: str = "interest_debt"  # for display: how was Rd determined
    # Capital structure
    equity_weight: float = 1.0
    debt_weight: float = 0.0
    # Result
    wacc: float = 0.10


@dataclass
class EquityBridge:
    """Enterprise value to equity value bridge."""
    enterprise_value: float = 0.0
    net_debt: float = 0.0
    minority_interest: float = 0.0
    preferred_equity: float = 0.0
    pension_deficit: float = 0.0
    equity_investments: float = 0.0
    equity_value: float = 0.0
    diluted_shares: float = 0.0
    implied_price: float = 0.0


@dataclass
class DCFResult:
    """Output of a DCF valuation."""
    fcf_table: pd.DataFrame = field(default_factory=pd.DataFrame)
    terminal_value: float = 0.0
    pv_fcfs: list = field(default_factory=list)
    pv_terminal: float = 0.0
    enterprise_value: float = 0.0
    bridge: EquityBridge = field(default_factory=EquityBridge)
    wacc_result: WACCResult = field(default_factory=WACCResult)
    implied_price: float = 0.0
    current_price: float = 0.0
    tv_pct_of_ev: float = 0.0
    # Sanity
    implied_exit_multiple: Optional[float] = None
    revenue_cagr: float = 0.0
    terminal_margin: float = 0.0
    warnings: list = field(default_factory=list)
