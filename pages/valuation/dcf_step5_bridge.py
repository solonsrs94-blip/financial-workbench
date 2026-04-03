"""Step 5 sub-renderer — Equity Bridge (EV → Equity Value → per share).

Shows bridge table with override capability for each line item.
All monetary values in millions (matching FCF projections).
"""

import streamlit as st

from components.layout import format_large_number


def render_bridge(result, bridge_inputs: dict, ticker: str) -> dict:
    """Render equity bridge with overridable inputs. Returns final values."""
    st.markdown("#### Equity Bridge")
    st.caption(
        "Enterprise Value to Equity Value. "
        "Override any line item if your estimate differs."
    )

    ev = result.enterprise_value

    # ── Override inputs ────────────────────────────────────────
    c_label, c_default, c_override = st.columns([2, 1, 1.5])
    with c_label:
        st.markdown("**Line Item**")
    with c_default:
        st.markdown("**Auto ($M)**")
    with c_override:
        st.markdown("**Your Value ($M)**")

    net_debt = _bridge_row(
        "Net Debt (Debt − Cash)", bridge_inputs["net_debt"],
        "bridge_net_debt", subtract=True,
    )
    minority = _bridge_row(
        "Minority Interest", bridge_inputs["minority"],
        "bridge_minority", subtract=True,
    )
    preferred = _bridge_row(
        "Preferred Equity", bridge_inputs["preferred"],
        "bridge_preferred", subtract=True,
    )

    # ── Equity Value ───────────────────────────────────────────
    equity_value = ev - net_debt - minority - preferred

    st.markdown(
        '<hr style="margin:8px 0;border-color:rgba(28,131,225,0.3)">',
        unsafe_allow_html=True,
    )

    # Shares override
    shares_default = bridge_inputs["shares"]
    c1, c2, c3 = st.columns([2, 1, 1.5])
    with c1:
        st.markdown("**Diluted Shares (M)**")
    with c2:
        st.markdown(
            f'<div style="font-size:13px;opacity:0.6;padding-top:8px">'
            f'{shares_default:,.1f}M</div>',
            unsafe_allow_html=True,
        )
    with c3:
        shares = st.number_input(
            "Shares", value=round(shares_default, 1),
            min_value=0.1, step=10.0, format="%.1f",
            key="bridge_shares", label_visibility="collapsed",
        )

    implied_price = equity_value / shares if shares > 0 else 0

    # ── Summary ────────────────────────────────────────────────
    st.markdown(
        '<hr style="margin:8px 0;border-color:rgba(28,131,225,0.3)">',
        unsafe_allow_html=True,
    )

    s1, s2, s3 = st.columns(3)
    s1.metric("Enterprise Value", format_large_number(ev * 1e6))
    s2.metric("Equity Value", format_large_number(equity_value * 1e6))
    s3.metric("Implied Price / Share", f"${implied_price:,.2f}")

    # ── Bridge formula ─────────────────────────────────────────
    st.markdown(
        f'<div style="font-size:13px;opacity:0.7;margin-top:4px">'
        f'{format_large_number(ev * 1e6)} EV '
        f'− {format_large_number(net_debt * 1e6)} net debt '
        f'− {format_large_number(minority * 1e6)} minority '
        f'− {format_large_number(preferred * 1e6)} preferred '
        f'= {format_large_number(equity_value * 1e6)} equity '
        f'÷ {shares:,.1f}M shares '
        f'= <b>${implied_price:,.2f}</b></div>',
        unsafe_allow_html=True,
    )

    return {
        "equity_value": equity_value,
        "implied_price": implied_price,
        "net_debt": net_debt,
        "minority": minority,
        "preferred": preferred,
        "shares": shares,
    }


def _bridge_row(
    label: str, default_val: float, key: str, subtract: bool = False,
) -> float:
    """Render one bridge line with auto value + override input."""
    c1, c2, c3 = st.columns([2, 1, 1.5])

    sign = "−" if subtract else "+"
    with c1:
        st.markdown(f"{sign} {label}")
    with c2:
        st.markdown(
            f'<div style="font-size:13px;opacity:0.6;padding-top:8px">'
            f'${default_val:,.0f}M</div>',
            unsafe_allow_html=True,
        )
    with c3:
        val = st.number_input(
            label, value=round(default_val, 0),
            step=100.0, format="%.0f",
            key=key, label_visibility="collapsed",
        )
    return val
