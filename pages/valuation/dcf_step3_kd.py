"""Step 3B: Cost of Debt (Kd) — actual vs. synthetic methods.

Two methods:
  1. Actual: Interest Expense / Total Debt
  2. Synthetic: ICR → Damodaran rating → Rf + spread
Tax rate selector + after-tax Kd display.
"""

import streamlit as st

from lib.analysis.valuation.wacc import (
    cost_of_debt_from_interest,
    synthetic_kd,
)
from lib.data.valuation_data import get_spread
from components.layout import format_large_number


# ── Helpers ────────────────────────────────────────────────────────

_LABEL = "font-size:13px;opacity:0.6"
_INFO = "font-size:13px;padding:8px 12px;background:rgba(28,131,225,0.08);border-radius:6px"


def _pct(val: float) -> str:
    return f"{val * 100:.2f}%"


# ── Main render ────────────────────────────────────────────────────


def render_cost_of_debt(inputs: dict) -> dict:
    """Render Cost of Debt section. Returns kd_result dict."""
    st.markdown("#### B. Cost of Debt (Kd)")
    st.caption("Pre-tax cost of debt, then apply tax shield")

    rf = inputs["rf"]
    interest = inputs["interest_expense"]
    total_debt = inputs["total_debt"]
    ebit = inputs["ebit"]
    eff_tax = inputs["effective_tax_rate"]
    market_cap = inputs["market_cap"]
    company_type = inputs.get("company_type", "normal")

    # ── Compute both methods ──────────────────────────────────
    kd_actual = cost_of_debt_from_interest(interest, total_debt)

    # Synthetic: ICR → rating → spread
    icr = ebit / interest if interest and interest > 0 else None
    firm_type = _get_firm_type(market_cap, company_type)
    spread_result = get_spread(icr, firm_type) if icr else None
    rating = spread_result[0] if spread_result else "N/A"
    spread = spread_result[1] if spread_result else 0.02
    kd_synth = synthetic_kd(rf, spread)

    # ── Method selector ───────────────────────────────────────
    c1, c2 = st.columns([1, 2])
    with c1:
        kd_method = st.selectbox(
            "Kd Method",
            ["Actual (Interest/Debt)", "Synthetic (ICR Rating)"],
            key="wacc_kd_method",
        )

    is_actual = "Actual" in kd_method
    kd_selected = kd_actual if is_actual else kd_synth

    # ── Show both methods side by side ────────────────────────
    m1, m2 = st.columns(2)

    with m1:
        _selected = " **[Selected]**" if is_actual else ""
        st.markdown(f"**Actual Method**{_selected}")
        if interest and total_debt and total_debt > 0:
            st.markdown(
                f'<div style="{_INFO}">'
                f'Interest Expense: {format_large_number(interest)}<br>'
                f'Total Debt: {format_large_number(total_debt)}<br>'
                f'<b>Kd = {_pct(kd_actual)}</b></div>',
                unsafe_allow_html=True,
            )
        else:
            st.warning("Missing interest expense or debt data", icon="⚠️")

    with m2:
        _selected = " **[Selected]**" if not is_actual else ""
        st.markdown(f"**Synthetic Method**{_selected}")
        if icr is not None:
            st.markdown(
                f'<div style="{_INFO}">'
                f'ICR (EBIT/Interest): {icr:.2f}x<br>'
                f'Rating: {rating} | Spread: {_pct(spread)}<br>'
                f'<b>Kd = Rf ({_pct(rf)}) + Spread = {_pct(kd_synth)}</b>'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            st.warning("Cannot compute ICR (no interest expense)", icon="⚠️")

    # ── Tax rate ──────────────────────────────────────────────
    st.markdown("")  # spacer
    t1, t2, t3 = st.columns([1, 1, 1])

    eff_label = f"Effective ({_pct(eff_tax)})" if eff_tax else "Effective (N/A)"
    tax_options = [eff_label, "Marginal (21%)"]

    def _on_tax_choice_change():
        choice = st.session_state.get("wacc_tax_choice", "")
        if "Effective" in choice and eff_tax:
            st.session_state["wacc_tax_rate"] = round(eff_tax * 100, 2)
        else:
            st.session_state["wacc_tax_rate"] = 21.0

    with t1:
        tax_choice = st.selectbox(
            "Tax Rate", tax_options, key="wacc_tax_choice",
            on_change=_on_tax_choice_change,
        )

    default_tax = eff_tax if "Effective" in tax_choice and eff_tax else 0.21
    with t2:
        tax_input = st.number_input(
            "Tax Rate (%)",
            min_value=0.0, max_value=60.0,
            value=default_tax * 100, step=0.5, format="%.1f",
            key="wacc_tax_rate",
        )
        st.markdown(
            f'<div style="{_LABEL}">'
            f'{"Effective" if "Effective" in tax_choice else "Marginal US"}'
            f'</div>',
            unsafe_allow_html=True,
        )
    tax_val = tax_input / 100

    # ── After-tax Kd ──────────────────────────────────────────
    kd_after = kd_selected * (1 - tax_val)
    with t3:
        st.metric("After-tax Kd", _pct(kd_after))

    st.markdown(
        f'<div style="font-size:14px">'
        f'<b>Kd(1-t) = </b>{_pct(kd_selected)} × (1 - {_pct(tax_val)})'
        f' = <b style="color:#1c83e1">{_pct(kd_after)}</b></div>',
        unsafe_allow_html=True,
    )

    return {
        "kd_pretax": kd_selected,
        "kd_method": "actual" if is_actual else "synthetic",
        "tax_rate": tax_val,
        "kd_after_tax": kd_after,
        "kd_actual": kd_actual,
        "kd_synthetic": kd_synth,
        "synthetic_rating": rating,
        "synthetic_spread": spread,
    }


# ── Firm type for spread lookup ───────────────────────────────────


def _get_firm_type(market_cap: float, company_type: str) -> str:
    """Determine firm type for Damodaran spread table."""
    if company_type == "financial":
        return "financial"
    if market_cap and market_cap > 5e9:
        return "large"
    return "small"
