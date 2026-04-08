"""
WACC calculation engine.

Pure Python — NO Streamlit imports. Functions return ``None`` when
required inputs are missing; callers must surface a warning instead of
silently substituting a hardcoded default.
"""

from typing import Optional

from models.valuation import WACCResult
from config.constants import DEFAULT_TAX_RATE


# ── Beta ──────────────────────────────────────────────────────────


def adjusted_beta(raw_beta: float) -> float:
    """Blume adjustment: 2/3 * raw + 1/3 * 1.0."""
    return (2 / 3) * raw_beta + (1 / 3) * 1.0


def unlever_beta(
    levered_beta: float, de_ratio: float, tax_rate: float,
) -> float:
    """Hamada: strip leverage from a levered (equity) beta.

    β_U = β_L / (1 + (1 - t) × D/E)
    """
    return levered_beta / (1 + (1 - tax_rate) * de_ratio)


def relever_beta(
    unlevered_beta: float, de_ratio: float, tax_rate: float,
) -> float:
    """Relever an unlevered (asset) beta with company D/E and tax.

    β_L = β_U × (1 + (1 - t) × D/E)
    """
    return unlevered_beta * (1 + (1 - tax_rate) * de_ratio)


# ── Cost of Equity ────────────────────────────────────────────────


def calc_capm(rf: float, beta: float, erp: float,
              size_premium: float = 0.0, crp: float = 0.0) -> float:
    """Cost of equity: Re = Rf + β×ERP + size_premium + CRP."""
    return rf + beta * erp + size_premium + crp


def size_premium_bracket(market_cap: float) -> tuple[float, str]:
    """Size premium based on market cap bracket.

    Returns (premium_decimal, label).
    """
    if market_cap and market_cap > 20e9:
        return 0.0, "Large/Mega Cap (>$20B)"
    if market_cap and market_cap > 2e9:
        return 0.01, "Mid Cap ($2–20B)"
    if market_cap and market_cap > 300e6:
        return 0.02, "Small Cap ($300M–$2B)"
    return 0.035, "Micro Cap (<$300M)"


# ── Cost of Debt ──────────────────────────────────────────────────


def cost_of_debt_from_interest(
    interest_expense: Optional[float],
    total_debt: Optional[float],
) -> Optional[float]:
    """Method A: Interest Expense / Total Debt.

    Returns ``None`` when either input is missing — callers must
    surface a warning instead of applying a hardcoded fallback.
    """
    if total_debt and total_debt > 0 and interest_expense:
        return interest_expense / total_debt
    return None


def synthetic_kd(rf: float, spread: float) -> float:
    """Method B: Kd = Rf + default spread from Damodaran ratings."""
    return rf + spread


# ── WACC ──────────────────────────────────────────────────────────


def calc_wacc(
    ke: float, kd_pretax: float, tax_rate: float,
    e_weight: float, d_weight: float,
) -> float:
    """WACC = Ke × (E/V) + Kd×(1-t) × (D/V)."""
    return ke * e_weight + kd_pretax * (1 - tax_rate) * d_weight


def auto_wacc(rf: float, raw_beta: float, market_cap: float,
              total_debt: float, interest_expense: float,
              erp: float,
              tax_rate: float = DEFAULT_TAX_RATE) -> WACCResult:
    """Calculate WACC with smart defaults.

    Uses: adjusted beta, interest/debt for Rd, market weights.
    Caller must supply ``erp`` explicitly — no silent fallback.
    Returns WACCResult with all intermediates for display.
    """
    if erp is None:
        raise ValueError("auto_wacc: erp is required (no silent fallback)")
    # Beta
    beta = adjusted_beta(raw_beta) if raw_beta and raw_beta > 0 else 1.0

    # Cost of equity
    re = calc_capm(rf, beta, erp)

    # Cost of debt — no silent fallback. If interest/debt is missing
    # the caller is expected to use the synthetic-spread path instead.
    rd_pretax = cost_of_debt_from_interest(interest_expense, total_debt)
    rd_method = "interest_debt"
    if rd_pretax is None:
        rd_method = "unavailable"
        rd_pretax = 0.0
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
