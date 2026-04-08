"""Step 3C: Capital Structure + WACC Output.

Capital structure weights (3 methods) + final WACC metric + summary table.
"""

import streamlit as st

from lib.analysis.valuation.wacc import calc_wacc
from lib.data.valuation_data import get_industry_beta
from components.layout import format_large_number


# ── Helpers ────────────────────────────────────────────────────────

_LABEL = "font-size:13px;opacity:0.6"


def _pct(val: float) -> str:
    return f"{val * 100:.2f}%"


# ── Main render ────────────────────────────────────────────────────


def render_structure_and_output(
    inputs: dict, ke_result: dict, kd_result: dict,
) -> dict:
    """Render Capital Structure + WACC output. Returns full result dict."""

    st.markdown("#### C. Capital Structure")
    st.caption("Equity and debt weights for WACC")

    market_cap = inputs["market_cap"] or 0
    total_debt = inputs["total_debt"] or 0
    industry = inputs["industry"]

    # ── Method selector ───────────────────────────────────────
    methods = [
        "Current Market Values",
        "Industry Average (Damodaran)",
        "Target (Manual)",
    ]
    c_sel, c_info = st.columns([1, 2])
    with c_sel:
        cap_method = st.selectbox(
            "Capital Structure", methods, key="wacc_cap_method",
        )

    e_weight, d_weight = _compute_weights(
        cap_method, market_cap, total_debt, industry, c_info,
    )

    # Show weights
    w1, w2, w3 = st.columns([1, 1, 1])
    with w1:
        st.metric("E/V (Equity Weight)", _pct(e_weight))
    with w2:
        st.metric("D/V (Debt Weight)", _pct(d_weight))
    with w3:
        total_v = market_cap + total_debt
        if total_v > 0 and "Current" in cap_method:
            st.markdown(
                f'<div style="{_LABEL};margin-top:12px">'
                f'Equity: {format_large_number(market_cap)}<br>'
                f'Debt: {format_large_number(total_debt)}</div>',
                unsafe_allow_html=True,
            )

    # ── WACC calculation ──────────────────────────────────────
    st.markdown("---")
    st.markdown("#### D. WACC Result")

    ke = ke_result["ke"]
    kd_pretax = kd_result["kd_pretax"]
    tax = kd_result["tax_rate"]
    kd_after = kd_result["kd_after_tax"]

    can_wacc = all(
        v is not None for v in (ke, kd_pretax, tax, kd_after)
    )
    if not can_wacc:
        st.info(
            "WACC cannot be computed — complete Ke and Kd inputs above.",
            icon="ℹ️",
        )
        return {
            "wacc": None, "ke": ke, "kd_after_tax": kd_after,
            "weight_equity": e_weight, "weight_debt": d_weight,
            "rf": ke_result.get("rf"),
            "beta": ke_result.get("beta"),
            "beta_method": ke_result.get("beta_method"),
            "erp": ke_result.get("erp"),
            "size_premium": ke_result.get("size_premium"),
            "crp": ke_result.get("crp"),
            "kd_pre_tax": kd_pretax,
            "kd_method": kd_result.get("kd_method"),
            "tax_rate": tax,
            "cap_structure_method": "market",
        }

    wacc = calc_wacc(ke, kd_pretax, tax, e_weight, d_weight)

    ke_contrib = ke * e_weight
    kd_contrib = kd_after * d_weight

    # Large WACC display
    wc1, wc2, wc3 = st.columns([1, 1, 1])
    with wc1:
        st.metric("WACC", _pct(wacc))
    with wc2:
        st.metric("Ke Contribution", _pct(ke_contrib))
    with wc3:
        st.metric("Kd(1-t) Contribution", _pct(kd_contrib))

    st.markdown(
        f'<div style="font-size:14px;margin-top:4px">'
        f'<b>WACC = </b>{_pct(ke)} × {_pct(e_weight)}'
        f' + {_pct(kd_pretax)} × (1-{_pct(tax)}) × {_pct(d_weight)}'
        f' = <b style="color:#1c83e1;font-size:16px">{_pct(wacc)}</b>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Summary table ─────────────────────────────────────────
    _render_summary(ke_result, kd_result, e_weight, d_weight, cap_method, wacc)

    # ── Build result dict ─────────────────────────────────────
    cap_key = "market"
    if "Industry" in cap_method:
        cap_key = "industry"
    elif "Target" in cap_method:
        cap_key = "target"

    return {
        "wacc": wacc,
        "ke": ke,
        "kd_after_tax": kd_after,
        "weight_equity": e_weight,
        "weight_debt": d_weight,
        "rf": ke_result["rf"],
        "beta": ke_result["beta"],
        "beta_method": ke_result["beta_method"],
        "erp": ke_result["erp"],
        "size_premium": ke_result["size_premium"],
        "crp": ke_result["crp"],
        "kd_pre_tax": kd_pretax,
        "kd_method": kd_result["kd_method"],
        "tax_rate": tax,
        "cap_structure_method": cap_key,
    }


# ── Weight computation ────────────────────────────────────────────


def _compute_weights(
    method: str, market_cap: float, total_debt: float,
    industry: str, info_col,
) -> tuple[float, float]:
    """Compute E/V and D/V weights based on method."""

    if "Industry" in method:
        ind = get_industry_beta(industry)
        if ind and ind.get("de_ratio") is not None:
            de = ind["de_ratio"]
            d_weight = de / (1 + de)
            e_weight = 1 - d_weight
            with info_col:
                st.markdown(
                    f'<div style="{_LABEL};margin-top:8px">'
                    f'{ind["industry"]}: D/E = {de:.3f}</div>',
                    unsafe_allow_html=True,
                )
            return e_weight, d_weight
        with info_col:
            st.warning("Industry data not found, using market values")

    if "Target" in method:
        with info_col:
            de_target = st.number_input(
                "Target D/E Ratio",
                min_value=0.0, max_value=10.0,
                value=0.3, step=0.05, format="%.2f",
                key="wacc_target_de",
            )
        d_weight = de_target / (1 + de_target)
        return 1 - d_weight, d_weight

    # Default: Current Market Values
    total_v = market_cap + total_debt
    if total_v > 0:
        return market_cap / total_v, total_debt / total_v
    return 1.0, 0.0


# ── Summary ───────────────────────────────────────────────────────


def _render_summary(
    ke_r: dict, kd_r: dict,
    e_wt: float, d_wt: float, cap_method: str, wacc: float,
) -> None:
    """Compact assumptions summary."""
    with st.expander("Assumptions Summary", expanded=False):
        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown("**Cost of Equity**")
            st.markdown(
                f"- Rf: {_pct(ke_r['rf'])}\n"
                f"- Beta: {ke_r['beta']:.3f} ({ke_r['beta_method']})\n"
                f"- ERP: {_pct(ke_r['erp'])}\n"
                f"- Size: {_pct(ke_r['size_premium'])}\n"
                f"- CRP: {_pct(ke_r['crp'])}\n"
                f"- **Ke: {_pct(ke_r['ke'])}**"
            )
        with s2:
            st.markdown("**Cost of Debt**")
            st.markdown(
                f"- Method: {kd_r['kd_method']}\n"
                f"- Kd pre-tax: {_pct(kd_r['kd_pretax'])}\n"
                f"- Tax rate: {_pct(kd_r['tax_rate'])}\n"
                f"- **Kd(1-t): {_pct(kd_r['kd_after_tax'])}**"
            )
            if kd_r["kd_method"] == "synthetic":
                st.markdown(
                    f"- Rating: {kd_r['synthetic_rating']}\n"
                    f"- Spread: {_pct(kd_r['synthetic_spread'])}"
                )
        with s3:
            st.markdown("**Capital Structure**")
            st.markdown(
                f"- Method: {cap_method}\n"
                f"- E/V: {_pct(e_wt)}\n"
                f"- D/V: {_pct(d_wt)}\n"
                f"- **WACC: {_pct(wacc)}**"
            )
