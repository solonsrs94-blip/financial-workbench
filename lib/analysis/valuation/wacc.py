"""
WACC calculation engine — auto-calculates with smart defaults.

Pure Python — NO Streamlit imports.
"""

from models.valuation import WACCResult
from config.constants import DEFAULT_MRP, DEFAULT_TAX_RATE


def adjusted_beta(raw_beta: float) -> float:
    """Blume adjustment: 2/3 * raw + 1/3 * 1.0."""
    return (2 / 3) * raw_beta + (1 / 3) * 1.0


def calc_capm(rf: float, beta: float, erp: float,
              size_premium: float = 0.0, crp: float = 0.0) -> float:
    """Cost of equity: Re = Rf + β×ERP + size_premium + CRP."""
    return rf + beta * erp + size_premium + crp


def cost_of_debt_from_interest(interest_expense: float, total_debt: float) -> float:
    """Method A: Interest Expense / Total Debt."""
    if total_debt and total_debt > 0 and interest_expense:
        return interest_expense / total_debt
    return 0.05  # fallback


def auto_wacc(rf: float, raw_beta: float, market_cap: float,
              total_debt: float, interest_expense: float,
              tax_rate: float = DEFAULT_TAX_RATE,
              erp: float = DEFAULT_MRP) -> WACCResult:
    """Calculate WACC with smart defaults.

    Uses: adjusted beta, interest/debt for Rd, market weights.
    Returns WACCResult with all intermediates for display.
    """
    # Beta
    beta = adjusted_beta(raw_beta) if raw_beta and raw_beta > 0 else 1.0

    # Cost of equity
    re = calc_capm(rf, beta, erp)

    # Cost of debt
    rd_pretax = cost_of_debt_from_interest(interest_expense, total_debt)
    rd_method = "interest_debt"
    if not interest_expense or not total_debt or total_debt <= 0:
        rd_pretax = rf + 0.02  # fallback: Rf + 200bps
        rd_method = "estimated"
    rd_aftertax = rd_pretax * (1 - tax_rate)

    # Capital structure (market weights)
    equity = market_cap or 0
    debt = total_debt or 0
    total_capital = equity + debt
    if total_capital > 0:
        e_weight = equity / total_capital
        d_weight = debt / total_capital
    else:
        e_weight, d_weight = 1.0, 0.0

    # WACC
    wacc = e_weight * re + d_weight * rd_aftertax

    return WACCResult(
        rf=rf, beta=beta, erp=erp,
        cost_of_equity=re,
        cost_of_debt_pretax=rd_pretax,
        tax_rate=tax_rate,
        cost_of_debt_aftertax=rd_aftertax,
        rd_method=rd_method,
        equity_weight=e_weight,
        debt_weight=d_weight,
        wacc=wacc,
    )
