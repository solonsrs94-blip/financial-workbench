"""Step 4: Terminal Value — Gordon Growth Model + Exit Multiple.

Both methods always computed. Analyst selects primary method for Step 5.
Cross-check (implied metrics from the other method) always visible.
All inputs auto-populated with sensible defaults, fully overridable.

Split into:
  - dcf_step4_terminal.py (this) — orchestrator + cross-checks + warnings
  - dcf_step4_methods.py — Gordon + Exit Multiple renderers
"""

import streamlit as st

from pages.valuation.dcf_step2_table import compute_projections, build_historical_data
from pages.valuation.dcf_step4_methods import (
    render_gordon,
    render_exit_multiple,
    implied_growth,
)
from config.constants import SECTOR_EXIT_MULTIPLES


def render(prepared: dict, ticker: str) -> None:
    """Render terminal value step."""
    st.markdown("### Step 4: Terminal Value")
    st.caption(
        "Value of all cash flows beyond the projection period. "
        "Both methods computed — select primary for Step 5."
    )

    # ── Prerequisites ──────────────────────────────────────────
    wacc_data = st.session_state.get("dcf_wacc")
    assumptions = st.session_state.get("dcf_assumptions")

    if not wacc_data or not assumptions:
        st.warning("Complete Steps 2 and 3 first.")
        return

    wacc = wacc_data.get("wacc", 0.10)
    proj = _get_projections(prepared, assumptions)
    if proj is None:
        st.info("Complete all Step 2 assumptions to calculate Terminal Value.")
        return

    n_years = assumptions["n_years"]
    fcf_final = proj["fcf"][-1]
    ebitda_final = proj["ebit"][-1] + proj["da"][-1]

    # ── Defaults ───────────────────────────────────────────────
    company = st.session_state.get(f"company_{ticker}")
    current_ev_ebitda = _get_current_ev_ebitda(company, ticker)
    sector = _get_sector(company)
    sector_multiple = SECTOR_EXIT_MULTIPLES.get(sector)

    # ── Method selector ────────────────────────────────────────
    method = st.radio(
        "Primary Method",
        ["Gordon Growth Model", "Exit Multiple"],
        horizontal=True,
        key="dcf_tv_method",
        help="Both methods are always calculated. "
             "Select which one drives the valuation in Step 5.",
    )
    is_gordon = method == "Gordon Growth Model"

    _hr()

    # ── Compute both methods ───────────────────────────────────
    gordon_tv, g = render_gordon(fcf_final, ebitda_final, wacc, is_gordon)
    exit_tv, multiple = render_exit_multiple(
        ebitda_final, fcf_final, wacc, current_ev_ebitda,
        sector, sector_multiple, not is_gordon,
    )

    primary_tv = gordon_tv if is_gordon else exit_tv

    # ── Cross-checks ───────────────────────────────────────────
    _hr()
    _render_cross_checks(
        gordon_tv, exit_tv, fcf_final, ebitda_final, wacc,
    )

    # ── Sanity warnings ────────────────────────────────────────
    _render_warnings(g, multiple, wacc, sector_multiple)

    # ── Store for Step 5 ───────────────────────────────────────
    st.session_state["dcf_terminal"] = {
        "method": "gordon" if is_gordon else "exit_multiple",
        "terminal_value": primary_tv,
        "terminal_growth": g,
        "exit_multiple": multiple,
        "gordon_tv": gordon_tv,
        "exit_tv": exit_tv,
        "fcf_final": fcf_final,
        "ebitda_final": ebitda_final,
        "n_years": n_years,
    }


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


def _hr():
    st.markdown(
        '<hr style="margin:12px 0;border-color:rgba(128,128,128,0.2)">',
        unsafe_allow_html=True,
    )


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
