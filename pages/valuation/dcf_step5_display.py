"""Step 5 display helpers — summary metrics, EV breakdown, implied price.

Extracted from dcf_step5_output.py to keep files under 300 lines.
Pure display functions — no session state writes.
"""

import streamlit as st

from components.layout import format_large_number


def render_summary(result, wacc_data, terminal, pf=1.0, cur="USD"):
    """Top-line metrics row."""
    ev = result.enterprise_value
    eq = result.bridge.equity_value
    implied = result.implied_price / pf if pf != 1.0 else result.implied_price
    current = result.current_price
    upside = (implied / current - 1) * 100 if current > 0 else 0
    sym = "$" if cur == "USD" else ""

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Enterprise Value", format_large_number(ev * 1e6))
    c2.metric("Equity Value", format_large_number(eq * 1e6))
    c3.metric("Implied Price", f"{sym}{implied:,.2f} {cur}")
    c4.metric("Current Price", f"{sym}{current:,.2f} {cur}")
    color = "#2ea043" if upside > 0 else "#f85149"
    c5.markdown(
        f'<div style="font-size:13px;opacity:0.6">Upside / Downside</div>'
        f'<div style="font-size:24px;font-weight:700;color:{color}">'
        f'{upside:+.1f}%</div>',
        unsafe_allow_html=True,
    )

    method_label = ("Gordon Growth" if terminal["method"] == "gordon"
                    else "Exit Multiple")
    st.markdown(
        f'<div style="font-size:13px;opacity:0.6;margin-top:4px">'
        f'WACC: {wacc_data["wacc"]*100:.2f}% &nbsp;|&nbsp; '
        f'Terminal: {method_label} '
        f'(g={terminal["terminal_growth"]*100:.2f}%, '
        f'multiple={terminal["exit_multiple"]:.1f}x) &nbsp;|&nbsp; '
        f'{terminal["n_years"]}yr projection</div>',
        unsafe_allow_html=True,
    )


def render_ev_breakdown(result) -> None:
    """Show PV of FCFs + PV of TV = EV."""
    pv_fcfs_total = sum(result.pv_fcfs)
    pv_tv = result.pv_terminal
    ev = result.enterprise_value
    tv_pct = result.tv_pct_of_ev

    st.markdown("#### Enterprise Value Breakdown")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("PV of FCFs", format_large_number(pv_fcfs_total * 1e6))
    c2.metric("PV of Terminal Value", format_large_number(pv_tv * 1e6))
    c3.metric("Enterprise Value", format_large_number(ev * 1e6))
    c4.metric("TV as % of EV", f"{tv_pct:.0%}")


def render_implied_price(bridge_result, current_price, pf=1.0, cur="USD"):
    """Large implied price display with upside/downside."""
    implied = bridge_result["implied_price"]
    if pf != 1.0:
        implied = implied / pf
    upside = (implied / current_price - 1) * 100 if current_price > 0 else 0
    color = "#2ea043" if upside > 0 else "#f85149"
    verdict = "UNDERVALUED" if upside > 0 else "OVERVALUED"
    sym = "$" if cur == "USD" else ""

    st.markdown(
        f'<div style="text-align:center;padding:16px 0">'
        f'<div style="font-size:14px;opacity:0.6">Implied Share Price</div>'
        f'<div style="font-size:36px;font-weight:700;color:#1c83e1">'
        f'{sym}{implied:,.2f} {cur}</div>'
        f'<div style="font-size:14px;margin-top:4px">'
        f'vs {sym}{current_price:,.2f} {cur} current → '
        f'<span style="color:{color};font-weight:700">'
        f'{upside:+.1f}% ({verdict})</span></div></div>',
        unsafe_allow_html=True,
    )
