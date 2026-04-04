"""Step 4 sub-renderers — Gordon Growth + Exit Multiple method UIs.

Pure rendering + calculation display. Called by dcf_step4_terminal.py.
"""

import streamlit as st

from lib.analysis.valuation.dcf import calc_terminal_value
from config.constants import DEFAULT_TERMINAL_GROWTH


# ── Gordon Growth ──────────────────────────────────────────────


def render_gordon(
    fcf_final: float, ebitda_final: float, wacc: float,
    is_primary: bool,
    scenario: str = "base",
) -> tuple[float, float]:
    """Render Gordon Growth inputs + output. Returns (tv, g)."""
    label = "A. Gordon Growth Model"
    if is_primary:
        label += " *(primary)*"
    st.markdown(f"#### {label}")

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        g_pct = st.number_input(
            "Terminal Growth Rate (%)",
            min_value=-2.0, max_value=8.0,
            value=DEFAULT_TERMINAL_GROWTH * 100,
            step=0.25, format="%.2f",
            key=f"dcf_{scenario}_terminal_g",
            help="Long-run perpetual growth. ~2-3% = inflation + real GDP.",
        )
    g = g_pct / 100

    with c2:
        st.markdown(
            f'<div style="font-size:13px;opacity:0.6;margin-top:28px">'
            f'WACC: {wacc * 100:.2f}% &nbsp;|&nbsp; '
            f'Spread: {(wacc - g) * 100:.2f}%</div>',
            unsafe_allow_html=True,
        )

    tv = calc_terminal_value(fcf_final, ebitda_final, g, wacc, "gordon")
    implied_exit = tv / ebitda_final if ebitda_final > 0 else 0

    with c3:
        st.markdown(
            f'<div style="margin-top:8px;font-size:14px">'
            f'TV = ${fcf_final:,.0f}M × (1 + {g_pct:.2f}%) / '
            f'({wacc * 100:.2f}% − {g_pct:.2f}%)<br>'
            f'<b style="color:#1c83e1;font-size:18px">'
            f'= ${tv:,.0f}M</b>'
            f'<br><span style="opacity:0.6;font-size:12px">'
            f'Implied Exit Multiple: {implied_exit:.1f}x EV/EBITDA'
            f'</span></div>',
            unsafe_allow_html=True,
        )
    return tv, g


# ── Exit Multiple ──────────────────────────────────────────────


def render_exit_multiple(
    ebitda_final: float, fcf_final: float, wacc: float,
    current_ev_ebitda: float | None,
    sector: str, sector_multiple: float | None,
    is_primary: bool,
    scenario: str = "base",
) -> tuple[float, float]:
    """Render Exit Multiple inputs + output. Returns (tv, multiple)."""
    label = "B. Exit Multiple"
    if is_primary:
        label += " *(primary)*"
    st.markdown(f"#### {label}")

    default = current_ev_ebitda or sector_multiple or 12.0

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        multiple = st.number_input(
            "EV/EBITDA Multiple",
            min_value=1.0, max_value=50.0,
            value=round(default, 1),
            step=0.5, format="%.1f",
            key=f"dcf_{scenario}_exit_multiple",
            help="Applied to final-year EBITDA.",
        )

    with c2:
        refs = []
        if current_ev_ebitda:
            refs.append(f"Current: {current_ev_ebitda:.1f}x")
        if sector_multiple:
            refs.append(f"{sector}: {sector_multiple:.1f}x")
        if refs:
            st.markdown(
                f'<div style="font-size:13px;opacity:0.6;margin-top:28px">'
                + " &nbsp;|&nbsp; ".join(refs) + "</div>",
                unsafe_allow_html=True,
            )

    tv = calc_terminal_value(
        fcf_final, ebitda_final, 0, wacc, "exit_multiple", multiple,
    )
    implied_g = implied_growth(fcf_final, tv, wacc)

    with c3:
        st.markdown(
            f'<div style="margin-top:8px;font-size:14px">'
            f'TV = ${ebitda_final:,.0f}M × {multiple:.1f}x<br>'
            f'<b style="color:#1c83e1;font-size:18px">'
            f'= ${tv:,.0f}M</b>'
            f'<br><span style="opacity:0.6;font-size:12px">'
            f'Implied Growth Rate: {implied_g * 100:.2f}%'
            f'</span></div>',
            unsafe_allow_html=True,
        )
    return tv, multiple


# ── Shared helpers ─────────────────────────────────────────────


def implied_growth(fcf: float, tv: float, wacc: float) -> float:
    """Back-calculate implied perpetuity growth from TV.

    From TV = FCF(1+g)/(WACC-g):  g = (WACC - FCF/TV) / (1 + FCF/TV)
    """
    if tv <= 0 or fcf <= 0:
        return 0.0
    k = fcf / tv
    return (wacc - k) / (1 + k)
