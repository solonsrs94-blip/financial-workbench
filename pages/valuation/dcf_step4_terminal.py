"""Step 4: Terminal Value — Gordon Growth Model + Exit Multiple.

Both methods always computed. Analyst selects primary method for Step 5.
Cross-check (implied metrics from the other method) always visible.
All inputs auto-populated with sensible defaults, fully overridable.

Split into:
  - dcf_step4_terminal.py (this) — orchestrator + cross-checks + warnings
  - dcf_step4_methods.py — Gordon + Exit Multiple renderers
  - dcf_step4_scenarios.py — Bull/Base/Bear tab orchestration
"""

import streamlit as st

from pages.valuation.dcf_step2_table import compute_projections, build_historical_data
from pages.valuation.dcf_step4_methods import implied_growth
from pages.valuation.dcf_step4_scenarios import render_terminal_scenarios


def render(prepared: dict, ticker: str) -> None:
    """Render terminal value step with scenario tabs."""
    st.markdown("### Step 4: Terminal Value")
    st.caption(
        "Value of all cash flows beyond the projection period. "
        "Both methods computed — select primary for Step 5."
    )

    # ── Prerequisites ──────────────────────────────────────────
    wacc_data = st.session_state.get("dcf_wacc")
    scenarios = st.session_state.get("dcf_scenarios")

    if not wacc_data or not scenarios:
        st.warning("Complete Steps 2 and 3 first.")
        return

    # Check at least base scenario has assumptions
    base = scenarios.get("base")
    if not base:
        st.warning("Complete Step 2 Base Case first.")
        return

    wacc = wacc_data.get("wacc", 0.10)

    # Render scenario tabs (each computes its own terminal value)
    render_terminal_scenarios(
        prepared, ticker, wacc,
        proj_fn=lambda p, a: _get_projections(p, a),
        get_ev_ebitda_fn=_get_current_ev_ebitda,
        get_sector_fn=_get_sector,
        render_cross_checks_fn=_render_cross_checks,
        render_warnings_fn=_render_warnings,
    )



# ── Cross-checks ───────────────────────────────────────────────


def _render_cross_checks(
    gordon_tv: float, exit_tv: float,
    fcf_final: float, ebitda_final: float, wacc: float,
) -> None:
    """Show comparison table and implied metrics."""
    st.markdown("#### Cross-Check")

    implied_exit = gordon_tv / ebitda_final if ebitda_final > 0 else 0
    implied_g = implied_growth(fcf_final, exit_tv, wacc)
    diff_pct = (
        (gordon_tv - exit_tv) / exit_tv * 100 if exit_tv > 0 else 0
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Gordon Growth TV", f"${gordon_tv:,.0f}M")
    with c2:
        st.metric("Exit Multiple TV", f"${exit_tv:,.0f}M")
    with c3:
        st.metric("Difference", f"{diff_pct:+.1f}%")

    st.markdown(
        f'<div style="font-size:13px;opacity:0.7;margin-top:4px">'
        f'Gordon → implied exit: <b>{implied_exit:.1f}x</b> EV/EBITDA '
        f'&nbsp;|&nbsp; '
        f'Exit Multiple → implied growth: <b>{implied_g * 100:.2f}%</b>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── Warnings ───────────────────────────────────────────────────


def _render_warnings(
    g: float, multiple: float,
    wacc: float, sector_multiple: float | None,
) -> None:
    """Show sanity-check warnings."""
    warnings = []
    if g > 0.04:
        warnings.append(
            f"Terminal growth ({g*100:.1f}%) exceeds typical "
            f"long-term GDP growth (3-4%)."
        )
    if g < 0:
        warnings.append(
            f"Negative terminal growth ({g*100:.1f}%) implies "
            f"the business is shrinking forever."
        )
    if g >= wacc:
        warnings.append(
            "Terminal growth >= WACC makes Gordon model invalid "
            "(infinite value)."
        )
    if sector_multiple and abs(multiple - sector_multiple) > 5:
        warnings.append(
            f"Exit multiple ({multiple:.1f}x) differs significantly "
            f"from sector median ({sector_multiple:.1f}x)."
        )
    if multiple > 25:
        warnings.append(f"Exit multiple of {multiple:.1f}x is very high.")
    for w in warnings:
        st.warning(w)


# ── Helpers ────────────────────────────────────────────────────


def _get_projections(prepared: dict, assumptions: dict) -> dict | None:
    """Recompute Step 2 projections to get final-year FCF/EBITDA."""
    standardized = prepared.get("standardized", {})
    years = prepared.get("years", [])
    ratios = prepared.get("ratios", [])
    if not years:
        return None
    hist = build_historical_data(ratios, standardized, years)
    raw_revs = hist.get("revenue_raw", [])
    base_revenue = raw_revs[-1] if raw_revs else None
    if base_revenue is None:
        return None
    base_cogs_pct = hist.get("base_cogs_pct", 0.60)
    return compute_projections(assumptions, base_revenue, base_cogs_pct)


def _get_current_ev_ebitda(company, ticker: str) -> float | None:
    """Get current EV/EBITDA from company model or val_data."""
    if company:
        val = getattr(getattr(company, "ratios", None), "ev_ebitda", None)
        if val and val > 0:
            return val
    val_data = st.session_state.get(f"val_data_{ticker}") or {}
    inc = val_data.get("income_detail", {})
    ev = val_data.get("enterprise_value")
    ebitda = inc.get("ebitda")
    if ev and ebitda and ebitda > 0:
        return ev / ebitda
    return None


def _get_sector(company) -> str:
    """Get sector from company model."""
    if company:
        info = getattr(company, "info", None)
        return getattr(info, "sector", "") or ""
    return ""
