"""DDM Step 3: Output — implied price, sensitivity, football field."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from lib.analysis.valuation.ddm import gordon_growth, two_stage_ddm, ddm_sensitivity
from config.constants import CHART_TEMPLATE


def render(prepared: dict, ticker: str) -> None:
    """Render DDM output step."""
    st.markdown("### Step 3: DDM Output")

    ke_data = st.session_state.get("ddm_ke")
    assumptions = st.session_state.get("ddm_assumptions")

    if not ke_data or not assumptions:
        st.warning("Complete Steps 1 and 2 first.")
        return

    ke = ke_data["ke"]
    d0 = assumptions["d0"]
    model = assumptions["model"]
    use_eps = assumptions.get("use_eps", False)
    current_price = _get_current_price(ticker)

    # Currency alignment: d0 (dividendRate) is in financialCurrency,
    # current_price is in listing currency. Compute price_factor.
    ddm_data = st.session_state.get(f"ddm_data_{ticker}") or {}
    currency = ddm_data.get("currency", "USD")
    fin_currency = ddm_data.get("financial_currency", currency)
    pf = 1.0
    if currency != fin_currency:
        val_data = st.session_state.get(f"val_data_{ticker}") or {}
        company = st.session_state.get(f"company_{ticker}")
        mcap = val_data.get("market_cap")
        shares = val_data.get("shares")
        if mcap and shares and current_price and current_price > 0:
            pf = mcap / (current_price * shares)

    # ── Run DDM engine ──────────────────────────────────────
    if model == "gordon":
        result = _run_gordon(d0, ke, assumptions)
    else:
        result = _run_two_stage(d0, ke, assumptions)

    if result is None or result.get("error"):
        st.error(result.get("error", "Calculation error."))
        return

    implied_fin = result["implied_price"]
    implied = implied_fin / pf if pf != 1.0 else implied_fin

    # ── Implied price ───────────────────────────────────────
    _render_implied_price(implied, current_price)

    # ── Value breakdown (2-stage only) ──────────────────────
    if model != "gordon":
        _render_breakdown(result)

    # ── Sensitivity table ───────────────────────────────────
    st.markdown("---")
    _render_sensitivity(d0, ke, assumptions, current_price)

    # ── Football field ──────────────────────────────────────
    st.markdown("---")
    ff_range = _render_football(d0, ke, assumptions, current_price)

    # ── Store output (both models when possible) ─────────────
    g_label = assumptions.get("g") if model == "gordon" else assumptions.get("g2", 0.025)
    primary = {
        "implied_price": implied,
        "current_price": current_price,
        "model": model,
        "ke": ke,
        "g": g_label,
        "sensitivity_min": ff_range.get("min", implied),
        "sensitivity_max": ff_range.get("max", implied),
    }
    st.session_state["ddm_output"] = primary

    # Also compute the other model silently for Summary
    _store_alt_model(d0, ke, assumptions, model, pf, current_price)



def _run_gordon(d0, ke, a):
    """Run Gordon Growth."""
    if a.get("use_eps"):
        d1, g = a["d1"], a["g"]
        if g >= ke:
            return {"error": "Growth rate must be less than Ke."}
        return {"implied_price": d1 / (ke - g), "d1": d1}
    return gordon_growth(d0, ke, a["g"])


def _run_two_stage(d0, ke, a):
    """Run 2-Stage DDM."""
    return two_stage_ddm(
        d0=d0, ke=ke, g1=a.get("g1", 0.05), g2=a.get("g2", 0.025),
        n=a.get("n", 5), eps0=a.get("eps0"),
        eps_growth1=a.get("eps_growth1"), payout1=a.get("payout1"),
        eps_growth2=a.get("eps_growth2"), payout2=a.get("payout2"),
        use_eps_method=a.get("use_eps", False),
    )



def _render_implied_price(implied: float, current: float) -> None:
    """Large implied price display."""
    upside = (implied / current - 1) * 100 if current > 0 else 0
    color = "#2ea043" if upside > 0 else "#f85149"
    verdict = "UNDERVALUED" if upside > 0 else "OVERVALUED"

    st.markdown(
        f'<div style="text-align:center;padding:16px 0">'
        f'<div style="font-size:14px;opacity:0.6">DDM Implied Share Price</div>'
        f'<div style="font-size:36px;font-weight:700;color:#1c83e1">'
        f'${implied:,.2f}</div>'
        f'<div style="font-size:14px;margin-top:4px">'
        f'vs ${current:,.2f} current → '
        f'<span style="color:{color};font-weight:700">'
        f'{upside:+.1f}% ({verdict})</span></div></div>',
        unsafe_allow_html=True,
    )


def _render_breakdown(result: dict) -> None:
    """Value breakdown for 2-stage."""
    pv1, pv_tv = result.get("pv_stage1", 0), result.get("pv_terminal", 0)
    total = result.get("implied_price", 0)
    p1 = pv1 / total * 100 if total > 0 else 0
    pt = pv_tv / total * 100 if total > 0 else 0
    st.markdown("#### Value Breakdown")
    c1, c2, c3 = st.columns(3)
    c1.metric("PV Stage 1", f"${pv1:,.2f}", f"{p1:.0f}%")
    c2.metric("PV Terminal", f"${pv_tv:,.2f}", f"{pt:.0f}%")
    c3.metric("Total", f"${total:,.2f}")


def _render_sensitivity(d0, ke, a, current_price):
    """Sensitivity table: Ke vs growth."""
    st.markdown("#### Sensitivity Analysis")
    st.caption("Ke (rows) vs growth rate (columns).")

    model = a["model"]
    g_base = a.get("g") if model == "gordon" else a.get("g2", 0.025)

    df = ddm_sensitivity(
        d0=d0, ke_base=ke, g_base=g_base, model=model,
        n=a.get("n", 5), g1=a.get("g1"),
        eps0=a.get("eps0"), eps_growth1=a.get("eps_growth1"),
        payout1=a.get("payout1"), eps_growth2=a.get("eps_growth2"),
        payout2=a.get("payout2"), use_eps_method=a.get("use_eps", False),
    )

    # Format and color (NaN or asymptotic → dash)
    import math
    cap = current_price * 100 if current_price > 0 else float("inf")
    formatted = df.map(
        lambda x: f"${x:,.2f}" if isinstance(x, (int, float))
        and not math.isnan(x) and 0 < x < cap else "—"
    )

    def _style(val):
        try:
            price = float(str(val).replace("$", "").replace(",", ""))
        except (ValueError, TypeError):
            return ""
        if price > current_price:
            return "background-color: rgba(46, 160, 67, 0.25); color: #2ea043"
        return "background-color: rgba(248, 81, 73, 0.2); color: #f85149"

    styled = formatted.style.applymap(_style)

    g_label = "Growth Rate" if model == "gordon" else "Terminal Growth"
    st.markdown(
        f'<div style="font-size:12px;opacity:0.5;margin-bottom:4px">'
        f'Rows: Ke &nbsp;|&nbsp; Columns: {g_label}'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.dataframe(
        styled, use_container_width=True,
        height=min(350, 50 + len(df) * 40),
    )


def _render_football(d0, ke, a, current_price) -> dict:
    """Football field chart. Returns {min, max, median}."""
    st.markdown("#### Football Field")

    model = a["model"]
    g_base = a.get("g") if model == "gordon" else a.get("g2", 0.025)

    df = ddm_sensitivity(
        d0=d0, ke_base=ke, g_base=g_base, model=model,
        n=a.get("n", 5), g1=a.get("g1"),
        eps0=a.get("eps0"), eps_growth1=a.get("eps_growth1"),
        payout1=a.get("payout1"), eps_growth2=a.get("eps_growth2"),
        payout2=a.get("payout2"), use_eps_method=a.get("use_eps", False),
        ke_steps=5, g_steps=5,
    )

    import numpy as np
    all_vals = df.values.flatten()
    # Cap at 100x current price to exclude asymptotic cells
    cap = current_price * 100 if current_price > 0 else float("inf")
    valid = [float(v) for v in all_vals
             if not np.isnan(v) and 0 < v < cap]
    if not valid:
        st.info("Not enough data for football field chart.")
        return {"min": 0, "max": 0, "median": 0}

    low = min(valid)
    high = max(valid)
    median = float(np.median(valid))

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=["DDM"], x=[high - low], base=[low], orientation="h",
        marker_color="rgba(28,131,225,0.5)",
        marker_line=dict(color="#1c83e1", width=1),
        hovertemplate=f"${low:,.0f} – ${high:,.0f}<extra></extra>",
        showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        y=["DDM"], x=[median], mode="markers",
        marker=dict(symbol="diamond", size=12, color="#1c83e1",
                    line=dict(width=1, color="white")),
        name="Median",
    ))
    if current_price > 0:
        fig.add_vline(x=current_price,
                      line=dict(color="#f85149", width=2, dash="dash"),
                      annotation=dict(text=f"Current: ${current_price:,.0f}",
                                      font=dict(color="#f85149", size=11),
                                      yshift=10))
    fig.update_layout(
        template=CHART_TEMPLATE, height=180,
        margin=dict(l=10, r=20, t=30, b=40),
        xaxis=dict(title="Implied Share Price ($)", tickprefix="$",
                   tickformat=",", gridcolor="rgba(128,128,128,0.15)",
                   range=[0, max(high * 1.3, current_price * 2)]),
        yaxis=dict(automargin=True), bargap=0.3,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1, font=dict(size=11)),
    )
    st.plotly_chart(fig, use_container_width=True)
    return {"min": low, "max": high, "median": median}



def _store_alt_model(d0, ke, assumptions, primary_model, pf, current_price):
    """Compute the other DDM model silently and store for Summary."""
    try:
        if primary_model == "gordon":
            # Also compute 2-Stage
            g1 = assumptions.get("g1") or assumptions.get("g", 0.05)
            g2 = assumptions.get("g2") or min(assumptions.get("g", 0.03), 0.03)
            r = two_stage_ddm(d0, ke, g1=g1, g2=g2, n=assumptions.get("n", 5))
            if r and not r.get("error") and r.get("implied_price", 0) > 0:
                imp = r["implied_price"] / pf if pf != 1.0 else r["implied_price"]
                st.session_state["ddm_output_alt"] = {
                    "implied_price": imp, "model": "two_stage",
                    "ke": ke, "g": g2,
                    "current_price": current_price,
                }
            else:
                st.session_state.pop("ddm_output_alt", None)
        else:
            # Also compute Gordon
            g = assumptions.get("g") or assumptions.get("g2", 0.03)
            if g >= ke:
                g = min(ke - 0.005, 0.06)
            r = gordon_growth(d0, ke, g)
            if r and not r.get("error") and r.get("implied_price", 0) > 0:
                imp = r["implied_price"] / pf if pf != 1.0 else r["implied_price"]
                st.session_state["ddm_output_alt"] = {
                    "implied_price": imp, "model": "gordon",
                    "ke": ke, "g": g,
                    "current_price": current_price,
                }
            else:
                st.session_state.pop("ddm_output_alt", None)
    except Exception:
        st.session_state.pop("ddm_output_alt", None)


def _get_current_price(ticker: str) -> float:
    """Get current share price from session state."""
    company = st.session_state.get(f"company_{ticker}")
    if company:
        price_obj = getattr(company, "price", None)
        return getattr(price_obj, "price", 0) or 0
    return 0.0
