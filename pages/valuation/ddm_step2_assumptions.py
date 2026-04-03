"""DDM Step 2: Dividend Assumptions — model selection, projections.

Auto-fetches dividend data, shows warnings, lets analyst choose
Gordon Growth vs 2-Stage and DPS Growth vs EPS × Payout.

Sub-renderers:
  ddm_step2_reference.py → warnings, reference data, history
"""

import streamlit as st
import pandas as pd

from lib.data.valuation_data import get_ddm_data
from pages.valuation.ddm_step2_reference import render_warnings, render_reference


def render(prepared: dict, ticker: str) -> dict | None:
    """Render DDM Step 2. Returns assumptions dict or None."""
    st.markdown("### Step 2: Dividend Assumptions")

    # ── Fetch dividend data ─────────────────────────────────
    ddm_data = _get_ddm_data(ticker)
    if ddm_data is None:
        st.error("Could not load dividend data.")
        return None

    # ── Warnings + reference data ───────────────────────────
    render_warnings(ddm_data)
    render_reference(ddm_data)

    st.markdown("---")

    # ── Model selection ─────────────────────────────────────
    c_model, c_method = st.columns(2)
    with c_model:
        model = st.radio(
            "Model", ["Gordon Growth", "2-Stage DDM"],
            key="ddm_model", horizontal=True,
        )
    with c_method:
        method = st.radio(
            "Projection Method",
            ["Direct DPS Growth", "EPS × Payout Ratio"],
            key="ddm_method", horizontal=True,
        )

    is_gordon = model == "Gordon Growth"
    use_eps = method == "EPS × Payout Ratio"
    d0 = ddm_data["current_dps"]
    eps0 = ddm_data["trailing_eps"]
    cagr = ddm_data["dps_cagr"]

    # ── Inputs ──────────────────────────────────────────────
    if is_gordon:
        result = _render_gordon(d0, eps0, cagr, ddm_data, use_eps)
    else:
        result = _render_two_stage(d0, eps0, cagr, ddm_data, use_eps)

    if result is None:
        return None

    result["model"] = "gordon" if is_gordon else "two_stage"
    result["use_eps"] = use_eps
    result["d0"] = d0
    result["eps0"] = eps0

    st.session_state["ddm_assumptions"] = result
    return result


# ── Gordon Growth inputs ─────────────────────────────────────


def _render_gordon(
    d0: float, eps0: float, cagr: dict, ddm_data: dict, use_eps: bool,
) -> dict | None:
    """Gordon Growth inputs. Returns assumptions dict."""
    ke_data = st.session_state.get("ddm_ke")
    ke = ke_data["ke"] if ke_data else 0.10

    if use_eps:
        default_eps_g = cagr.get("5y", 0.03)
        default_payout = ddm_data["payout_ratio"] or 0.40

        c1, c2 = st.columns(2)
        with c1:
            eps_g = st.number_input(
                "EPS Growth Rate (%)", min_value=-20.0, max_value=30.0,
                value=default_eps_g * 100, step=0.5, format="%.2f",
                key="ddm_gordon_eps_g",
            )
        with c2:
            payout = st.number_input(
                "Payout Ratio (%)", min_value=0.0, max_value=200.0,
                value=default_payout * 100, step=1.0, format="%.1f",
                key="ddm_gordon_payout",
            )

        eps_g_dec = eps_g / 100
        payout_dec = payout / 100
        d1 = eps0 * (1 + eps_g_dec) * payout_dec

        _show_gordon_result(d1, ke, eps_g_dec)
        return {"g": eps_g_dec, "d1": d1, "eps_growth": eps_g_dec, "payout": payout_dec}
    else:
        default_g = cagr.get("5y", 0.03)
        g_input = st.number_input(
            "Perpetual DPS Growth Rate (%)",
            min_value=-10.0, max_value=20.0,
            value=default_g * 100, step=0.25, format="%.2f",
            key="ddm_gordon_g",
            help="Long-term dividend growth rate",
        )
        g = g_input / 100
        d1 = d0 * (1 + g)
        _show_gordon_result(d1, ke, g)
        return {"g": g, "d1": d1}


def _show_gordon_result(d1: float, ke: float, g: float) -> None:
    """Show live Gordon Growth implied price."""
    if g >= ke:
        st.error("Growth rate must be less than cost of equity (Ke).")
        return
    implied = d1 / (ke - g)
    st.markdown(
        f'<div style="font-size:14px;margin-top:8px;padding:8px 12px;'
        f'background:rgba(28,131,225,0.08);border-radius:6px">'
        f'D₁ = ${d1:,.2f} &nbsp;|&nbsp; '
        f'Ke = {ke*100:.2f}% &nbsp;|&nbsp; '
        f'g = {g*100:.2f}% &nbsp;→&nbsp; '
        f'<b>Implied Price = ${implied:,.2f}</b></div>',
        unsafe_allow_html=True,
    )


# ── 2-Stage inputs ───────────────────────────────────────────


def _render_two_stage(
    d0: float, eps0: float, cagr: dict, ddm_data: dict, use_eps: bool,
) -> dict | None:
    """2-Stage DDM inputs with projection table."""
    ke_data = st.session_state.get("ddm_ke")
    ke = ke_data["ke"] if ke_data else 0.10

    n = st.number_input(
        "High-Growth Period (years)", min_value=1, max_value=15,
        value=5, step=1, key="ddm_n_years",
    )

    if use_eps:
        return _two_stage_eps(d0, eps0, cagr, ddm_data, ke, n)
    return _two_stage_dps(d0, cagr, ke, n)


def _two_stage_dps(d0: float, cagr: dict, ke: float, n: int) -> dict:
    """2-Stage with Direct DPS Growth."""
    default_g1 = cagr.get("3y", cagr.get("5y", 0.05))

    c1, c2 = st.columns(2)
    with c1:
        g1_input = st.number_input(
            "Stage 1 DPS Growth (%)", min_value=-10.0, max_value=30.0,
            value=default_g1 * 100, step=0.5, format="%.2f", key="ddm_g1",
        )
    with c2:
        g2_input = st.number_input(
            "Terminal Growth (%)", min_value=-5.0, max_value=10.0,
            value=2.50, step=0.25, format="%.2f", key="ddm_g2",
        )

    g1, g2 = g1_input / 100, g2_input / 100

    rows = _build_dps_projection(d0, g1, g2, ke, n)
    _show_projection_table(rows)
    return {"g1": g1, "g2": g2, "n": n}


def _two_stage_eps(
    d0: float, eps0: float, cagr: dict, ddm_data: dict,
    ke: float, n: int,
) -> dict:
    """2-Stage with EPS × Payout Ratio."""
    default_eg1 = cagr.get("3y", 0.05)
    default_po1 = ddm_data["payout_ratio"] or 0.40

    c1, c2 = st.columns(2)
    with c1:
        eg1 = st.number_input(
            "Stage 1 EPS Growth (%)", min_value=-20.0, max_value=40.0,
            value=default_eg1 * 100, step=0.5, format="%.2f", key="ddm_eps_g1",
        )
        po1 = st.number_input(
            "Stage 1 Payout Ratio (%)", min_value=0.0, max_value=200.0,
            value=default_po1 * 100, step=1.0, format="%.1f", key="ddm_payout1",
        )
    with c2:
        eg2 = st.number_input(
            "Terminal EPS Growth (%)", min_value=-5.0, max_value=10.0,
            value=2.50, step=0.25, format="%.2f", key="ddm_eps_g2",
        )
        po2 = st.number_input(
            "Terminal Payout Ratio (%)", min_value=0.0, max_value=200.0,
            value=default_po1 * 100, step=1.0, format="%.1f", key="ddm_payout2",
        )

    eg1_d, eg2_d = eg1 / 100, eg2 / 100
    po1_d, po2_d = po1 / 100, po2 / 100

    rows = _build_eps_projection(eps0, eg1_d, eg2_d, po1_d, po2_d, ke, n)
    _show_projection_table(rows)

    return {
        "g1": eg1_d, "g2": eg2_d, "n": n,
        "eps_growth1": eg1_d, "payout1": po1_d,
        "eps_growth2": eg2_d, "payout2": po2_d,
    }


# ── Projection builders ─────────────────────────────────────


def _build_dps_projection(
    d0: float, g1: float, g2: float, ke: float, n: int,
) -> list[dict]:
    """Build DPS projection rows for display."""
    rows = []
    dps = d0
    for t in range(1, n + 1):
        dps = dps * (1 + g1)
        pv_f = 1 / (1 + ke) ** t
        rows.append({
            "Year": t, "DPS": f"${dps:.2f}",
            "PV Factor": f"{pv_f:.4f}", "PV of Dividend": f"${dps*pv_f:.2f}",
        })
    if g2 < ke:
        term_dps = dps * (1 + g2)
        tv = term_dps / (ke - g2)
        pv_tv = tv / (1 + ke) ** n
        rows.append({
            "Year": f"TV (Yr {n})", "DPS": f"${term_dps:.2f}",
            "PV Factor": f"{(1/(1+ke)**n):.4f}",
            "PV of Dividend": f"${pv_tv:,.2f}",
        })
    return rows


def _build_eps_projection(
    eps0: float, eg1: float, eg2: float,
    po1: float, po2: float, ke: float, n: int,
) -> list[dict]:
    """Build EPS × Payout projection rows."""
    rows = []
    eps = eps0
    for t in range(1, n + 1):
        eps = eps * (1 + eg1)
        dps = eps * po1
        pv_f = 1 / (1 + ke) ** t
        rows.append({
            "Year": t, "EPS": f"${eps:.2f}", "Payout": f"{po1:.0%}",
            "DPS": f"${dps:.2f}", "PV Factor": f"{pv_f:.4f}",
            "PV of Dividend": f"${dps*pv_f:.2f}",
        })
    if eg2 < ke:
        term_eps = eps * (1 + eg2)
        term_dps = term_eps * po2
        tv = term_dps / (ke - eg2)
        pv_tv = tv / (1 + ke) ** n
        rows.append({
            "Year": f"TV (Yr {n})", "EPS": f"${term_eps:.2f}",
            "Payout": f"{po2:.0%}", "DPS": f"${term_dps:.2f}",
            "PV Factor": f"{(1/(1+ke)**n):.4f}",
            "PV of Dividend": f"${pv_tv:,.2f}",
        })
    return rows


# ── Shared helpers ───────────────────────────────────────────


def _show_projection_table(rows: list[dict]) -> None:
    if not rows:
        return
    df = pd.DataFrame(rows)
    st.dataframe(
        df, use_container_width=True, hide_index=True,
        height=min(400, 40 + len(rows) * 35),
    )


def _get_ddm_data(ticker: str) -> dict | None:
    """Get DDM data with session caching."""
    key = f"ddm_data_{ticker}"
    if key in st.session_state:
        return st.session_state[key]
    data = get_ddm_data(ticker)
    if data:
        st.session_state[key] = data
    return data
