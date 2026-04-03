"""DDM Step 3: Output — implied price, value breakdown, sensitivity, football.

Runs the DDM engine with Step 1 (Ke) and Step 2 (assumptions),
renders results with sensitivity table and football field chart.
"""

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

    # ── Run DDM engine ──────────────────────────────────────
    if model == "gordon":
        result = _run_gordon(d0, ke, assumptions)
    else:
        result = _run_two_stage(d0, ke, assumptions)

    if result is None or result.get("error"):
        st.error(result.get("error", "Calculation error."))
        return

    implied = result["implied_price"]

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
    _render_football(d0, ke, assumptions, current_price)

    # ── Store output ────────────────────────────────────────
    st.session_state["ddm_output"] = {
        "implied_price": implied,
        "current_price": current_price,
        "model": model,
    }


# ── Engine runners ───────────────────────────────────────────


def _run_gordon(d0: float, ke: float, a: dict) -> dict:
    """Run Gordon Growth with either DPS or EPS method."""
    if a.get("use_eps"):
        d1 = a["d1"]
        g = a["g"]
        if g >= ke:
            return {"error": "Growth rate must be less than Ke."}
        return {"implied_price": d1 / (ke - g), "d1": d1}
    return gordon_growth(d0, ke, a["g"])


def _run_two_stage(d0: float, ke: float, a: dict) -> dict:
    """Run 2-Stage DDM."""
    return two_stage_ddm(
        d0=d0, ke=ke,
        g1=a.get("g1", 0.05),
        g2=a.get("g2", 0.025),
        n=a.get("n", 5),
        eps0=a.get("eps0"),
        eps_growth1=a.get("eps_growth1"),
        payout1=a.get("payout1"),
        eps_growth2=a.get("eps_growth2"),
        payout2=a.get("payout2"),
        use_eps_method=a.get("use_eps", False),
    )


# ── Renderers ────────────────────────────────────────────────


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
    """Value breakdown for 2-stage: PV stage 1 + PV terminal."""
    pv1 = result.get("pv_stage1", 0)
    pv_tv = result.get("pv_terminal", 0)
    total = result.get("implied_price", 0)

    pct1 = pv1 / total * 100 if total > 0 else 0
    pct_tv = pv_tv / total * 100 if total > 0 else 0

    st.markdown("#### Value Breakdown")
    c1, c2, c3 = st.columns(3)
    c1.metric("PV of Stage 1 Dividends", f"${pv1:,.2f}", f"{pct1:.0f}%")
    c2.metric("PV of Terminal Value", f"${pv_tv:,.2f}", f"{pct_tv:.0f}%")
    c3.metric("Total DDM Value", f"${total:,.2f}")


def _render_sensitivity(
    d0: float, ke: float, a: dict, current_price: float,
) -> None:
    """Sensitivity table: Ke vs growth → implied price."""
    st.markdown("#### Sensitivity Analysis")
    st.caption(
        "Ke (rows) vs growth rate (columns). "
        "Green = upside, red = downside."
    )

    model = a["model"]
    g_base = a.get("g") if model == "gordon" else a.get("g2", 0.025)

    df = ddm_sensitivity(
        d0=d0, ke_base=ke, g_base=g_base, model=model,
        n=a.get("n", 5), g1=a.get("g1"),
        eps0=a.get("eps0"), eps_growth1=a.get("eps_growth1"),
        payout1=a.get("payout1"), eps_growth2=a.get("eps_growth2"),
        payout2=a.get("payout2"), use_eps_method=a.get("use_eps", False),
    )

    # Format and color
    formatted = df.map(lambda x: f"${x:,.2f}" if x else "—")

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


def _render_football(
    d0: float, ke: float, a: dict, current_price: float,
) -> None:
    """Football field chart from sensitivity range."""
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

    all_vals = df.values.flatten()
    valid = [v for v in all_vals if v > 0]
    if not valid:
        st.info("Not enough data for football field chart.")
        return

    low = min(valid)
    high = max(valid)
    import numpy as np
    median = float(np.median(valid))

    label = "DDM"
    bar_color = "rgba(28, 131, 225, 0.5)"
    median_color = "#1c83e1"
    current_color = "#f85149"

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=[label], x=[high - low], base=[low],
        orientation="h", marker_color=bar_color,
        marker_line=dict(color=median_color, width=1),
        hovertemplate=(
            f"Low: ${low:,.0f}<br>High: ${high:,.0f}<br>"
            f"Median: ${median:,.0f}<extra></extra>"
        ),
        showlegend=False,
    ))

    fig.add_trace(go.Scatter(
        y=[label], x=[median], mode="markers",
        marker=dict(symbol="diamond", size=12, color=median_color,
                    line=dict(width=1, color="white")),
        hovertemplate=f"Median: ${median:,.0f}<extra></extra>",
        name="Median",
    ))

    fig.add_vline(
        x=current_price,
        line=dict(color=current_color, width=2, dash="dash"),
        annotation=dict(
            text=f"Current: ${current_price:,.0f}",
            font=dict(color=current_color, size=11), yshift=10,
        ),
    )

    x_cap = max(high * 1.3, current_price * 2)
    fig.update_layout(
        template=CHART_TEMPLATE,
        height=180,
        margin=dict(l=10, r=20, t=30, b=40),
        xaxis=dict(
            title="Implied Share Price ($)",
            tickprefix="$", tickformat=",",
            gridcolor="rgba(128,128,128,0.15)",
            range=[0, x_cap],
        ),
        yaxis=dict(automargin=True),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=11),
        ),
        bargap=0.3,
    )

    st.plotly_chart(fig, use_container_width=True)


# ── Helpers ──────────────────────────────────────────────────


def _get_current_price(ticker: str) -> float:
    """Get current share price from session state."""
    company = st.session_state.get(f"company_{ticker}")
    if company:
        price_obj = getattr(company, "price", None)
        return getattr(price_obj, "price", 0) or 0
    return 0.0
