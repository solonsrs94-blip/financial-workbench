"""DDM Step 2 projection builders + shared display helpers.

Extracted from ddm_step2_assumptions.py to keep that file under the
300-line limit. Pure presentation/calculation helpers — no state.
"""

import pandas as pd
import streamlit as st

from lib.data.valuation_data import get_ddm_data


def build_dps_projection(d0, g1, g2, ke, n):
    rows, dps = [], d0
    for t in range(1, n + 1):
        dps = dps * (1 + g1)
        pv_f = 1 / (1 + ke) ** t
        rows.append({"Year": t, "DPS": f"${dps:.2f}",
                      "PV Factor": f"{pv_f:.4f}",
                      "PV of Dividend": f"${dps*pv_f:.2f}"})
    if g2 < ke:
        td = dps * (1 + g2)
        tv = td / (ke - g2)
        pvtv = tv / (1 + ke) ** n
        rows.append({"Year": f"TV (Yr {n})", "DPS": f"${td:.2f}",
                      "PV Factor": f"{(1/(1+ke)**n):.4f}",
                      "PV of Dividend": f"${pvtv:,.2f}"})
    return rows


def build_eps_projection(eps0, eg1, eg2, po1, po2, ke, n):
    rows, eps = [], eps0
    for t in range(1, n + 1):
        eps = eps * (1 + eg1)
        dps = eps * po1
        pv_f = 1 / (1 + ke) ** t
        rows.append({"Year": t, "EPS": f"${eps:.2f}", "Payout": f"{po1:.0%}",
                      "DPS": f"${dps:.2f}", "PV Factor": f"{pv_f:.4f}",
                      "PV of Dividend": f"${dps*pv_f:.2f}"})
    if eg2 < ke:
        te = eps * (1 + eg2)
        td = te * po2
        tv = td / (ke - eg2)
        pvtv = tv / (1 + ke) ** n
        rows.append({"Year": f"TV (Yr {n})", "EPS": f"${te:.2f}",
                      "Payout": f"{po2:.0%}", "DPS": f"${td:.2f}",
                      "PV Factor": f"{(1/(1+ke)**n):.4f}",
                      "PV of Dividend": f"${pvtv:,.2f}"})
    return rows


def show_projection_table(rows):
    if not rows:
        return
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True,
                 height=min(400, 40 + len(rows) * 35))


def show_gordon_result(d1, ke, g) -> None:
    """Show live Gordon Growth implied price."""
    if g >= ke:
        st.error("Growth rate must be less than cost of equity (Ke).")
        return
    if ke - g < 0.02:
        st.warning(
            f"Growth rate ({g*100:.1f}%) is within 2pp of Ke "
            f"({ke*100:.1f}%). Small denominator produces extreme valuations."
        )
    implied = d1 / (ke - g)
    st.markdown(
        f'<div style="font-size:14px;margin-top:8px;padding:8px 12px;'
        f'background:rgba(28,131,225,0.08);border-radius:6px">'
        f'D\u2081 = ${d1:,.2f} &nbsp;|&nbsp; '
        f'Ke = {ke*100:.2f}% &nbsp;|&nbsp; '
        f'g = {g*100:.2f}% &nbsp;\u2192&nbsp; '
        f'<b>Implied Price = ${implied:,.2f}</b></div>',
        unsafe_allow_html=True,
    )


def get_ddm_data_cached(ticker):
    key = f"ddm_data_{ticker}"
    if key in st.session_state:
        return st.session_state[key]
    data = get_ddm_data(ticker)
    if data:
        st.session_state[key] = data
    return data
