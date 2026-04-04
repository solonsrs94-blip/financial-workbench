"""Comps Step 3: Implied Valuation — apply peer multiples to target.

EV-based multiples:  Implied EV -> minus Net Debt -> Equity -> / Shares -> Price
Equity-based (P/E):  Peer P/E x Target EPS -> Implied Price directly

Football field chart rendered by comps_step3_football.py.
Scenario tabs rendered by comps_step3_scenarios.py.
"""

import statistics

import streamlit as st

from pages.valuation.comps_step3_football import render_football_field
from pages.valuation.comps_step3_scenarios import render_scenario_valuation

# ── Multiple definitions ───────────────────────────────────────

_MULTIPLES_NORMAL = [
    ("ev_revenue", "EV / Revenue", "revenue", "ev"),
    ("ev_ebitda", "EV / EBITDA", "ebitda", "ev"),
    ("ev_ebit", "EV / EBIT", "ebit", "ev"),
    ("trailing_pe", "P / E", "eps", "equity"),
    ("forward_pe", "Fwd P / E", "fwd_eps", "equity"),
    ("fwd_ev_revenue", "Fwd EV / Rev", "fwd_revenue", "ev"),
    ("fwd_ev_ebitda", "Fwd EV / EBITDA*", "fwd_ebitda", "ev"),
]

_MULTIPLES_FINANCIAL = [
    ("trailing_pe", "P / E", "eps", "equity"),
    ("forward_pe", "Fwd P / E", "fwd_eps", "equity"),
    ("price_to_book", "P / Book", "book_value_ps", "equity"),
    ("price_to_tbv", "P / TBV", "tangible_book_ps", "equity"),
]


# ── Main render ────────────────────────────────────────────────


def render(prepared: dict, ticker: str) -> None:
    """Render Step 3: Implied Valuation with scenario tabs."""
    st.subheader("Step 3 - Implied Valuation")

    comps = st.session_state.get("comps_table")
    if not comps or not comps.get("target") or not comps.get("summary"):
        st.info("Complete Step 2 to see implied valuation.")
        return

    target = comps["target"]
    summary = comps["summary"]
    is_fin = comps.get("is_financial", False)
    multiples = _MULTIPLES_FINANCIAL if is_fin else _MULTIPLES_NORMAL

    net_debt = _net_debt(target)
    shares = target.get("shares_outstanding")
    current_price = target.get("price")

    if not shares or not current_price:
        st.error("Missing shares outstanding or current price for target.")
        return

    _enrich_forward_eps(target)

    # ── Reference table (all multiples at median/mean) ─────
    method = st.radio(
        "Summary statistic for reference table",
        ["Median", "Mean"], horizontal=True, key="comps_val_method",
    )
    method_key = method.lower()

    implied_legacy = _compute_all_implied(
        summary, target, net_debt, shares, current_price, multiples,
    )
    _render_implied_table(
        implied_legacy, summary, method_key, current_price, target,
        multiples,
    )

    # Football field (per-multiple range)
    st.markdown("---")
    st.markdown("#### Comps Football Field")
    render_football_field(implied_legacy, current_price)

    # ── Scenario valuation ─────────────────────────────────
    st.markdown("---")
    st.markdown("#### Scenario Valuation")
    st.caption(
        "Select a primary multiple and set bear/base/bull applied "
        "values to derive scenario-specific implied prices."
    )
    render_scenario_valuation(
        summary, target, multiples, net_debt, shares,
        current_price, is_fin,
    )


# ── Implied price computation ──────────────────────────────────


def _compute_all_implied(
    summary, target, net_debt, shares, current_price, multiples=None,
) -> dict:
    if multiples is None:
        multiples = _MULTIPLES_NORMAL
    result = {}
    for mult_key, label, metric_key, basis in multiples:
        target_metric = target.get(metric_key)
        if target_metric is None or target_metric <= 0:
            result[mult_key] = None
            continue
        prices = {}
        for stat in ["low", "median", "mean", "high"]:
            mult_val = summary.get(stat, {}).get(mult_key)
            if mult_val is None or mult_val <= 0:
                prices[stat] = None
                continue
            if basis == "ev":
                impl_ev = mult_val * target_metric
                impl_eq = impl_ev - net_debt
                prices[stat] = impl_eq / shares if impl_eq > 0 else None
            else:
                prices[stat] = mult_val * target_metric
        if prices.get("median") or prices.get("mean"):
            prices["target_metric"] = target_metric
            prices["label"] = label
            prices["basis"] = basis
            prices["net_debt"] = net_debt
            result[mult_key] = prices
        else:
            result[mult_key] = None
    return result


def _net_debt(target: dict) -> float:
    return (target.get("total_debt") or 0) - (target.get("cash") or 0)


def _enrich_forward_eps(target: dict) -> None:
    if target.get("fwd_eps"):
        return
    fwd_pe = target.get("forward_pe")
    price = target.get("price")
    if fwd_pe and price and fwd_pe > 0:
        target["fwd_eps"] = price / fwd_pe


# ── Implied table renderer ─────────────────────────────────────


def _render_implied_table(
    implied, summary, method_key, current_price, target, multiples=None,
) -> None:
    if multiples is None:
        multiples = _MULTIPLES_NORMAL
    has_ev = any(basis == "ev" for _, _, _, basis in multiples)
    html = _TBL_CSS + '<table class="impl-tbl"><thead><tr>'
    headers = ["Multiple", f"Peer {method_key.capitalize()}", "Target Metric"]
    if has_ev:
        headers += ["Implied EV", "Implied Equity"]
    headers += ["Implied Price", "Current", "Prem / Disc"]
    for h in headers:
        html += f"<th>{h}</th>"
    html += "</tr></thead><tbody>"
    shares = target.get("shares_outstanding", 1)
    net_debt = _net_debt(target)
    na = lambda n: "<td>N/A</td>" * n

    for mult_key, label, metric_key, basis in multiples:
        data = implied.get(mult_key)
        nc = len(headers) - 1
        if data is None:
            html += f'<tr><td>{label}</td>{na(nc)}</tr>'
            continue
        peer_mult = summary.get(method_key, {}).get(mult_key)
        tm = data.get("target_metric")
        ip = data.get(method_key)
        if peer_mult is None or tm is None:
            html += f'<tr><td>{label}</td>{na(nc)}</tr>'
            continue
        ie = iq = None
        if basis == "ev":
            ie = peer_mult * tm
            iq = ie - net_debt
        ph = "N/A"
        if ip and current_price:
            p = ip / current_price - 1
            c = "#2ea043" if p >= 0 else "#f85149"
            s = "+" if p >= 0 else ""
            ph = f'<span style="color:{c};font-weight:600">{s}{p*100:.1f}%</span>'
        html += "<tr>"
        html += f"<td>{label}</td>"
        html += f'<td class="r">{peer_mult:.1f}x</td>'
        html += f'<td class="r">{_fmt_m(tm, basis)}</td>'
        if has_ev:
            html += f'<td class="r">{_fmt_ev(ie)}</td>'
            html += f'<td class="r">{_fmt_ev(iq)}</td>'
        html += f'<td class="r b">{_fmt_p(ip)}</td>'
        html += f'<td class="r">${current_price:,.0f}</td>'
        html += f'<td class="r">{ph}</td></tr>'
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)


def _fmt_ev(v):
    if v is None: return "\u2014"
    a = abs(v)
    if a >= 1e12: return f"${v/1e12:.2f}T"
    if a >= 1e9: return f"${v/1e9:.1f}B"
    if a >= 1e6: return f"${v/1e6:.0f}M"
    return f"${v:,.0f}"

def _fmt_p(v): return f"${v:,.0f}" if v else "N/A"

def _fmt_m(v, b):
    if v is None: return "N/A"
    return f"${v:,.2f}" if b == "equity" else _fmt_ev(v)

_TBL_CSS = (
    '<style>.impl-tbl{width:100%;border-collapse:collapse;font-size:12px;'
    'margin:8px 0}'
    '.impl-tbl th{font-size:11px;font-weight:600;padding:6px 8px;'
    'text-align:right;border-bottom:2px solid rgba(128,128,128,0.4)}'
    '.impl-tbl th:first-child{text-align:left}'
    '.impl-tbl td{padding:5px 8px;text-align:left;'
    'border-bottom:1px solid rgba(128,128,128,0.1)}'
    '.impl-tbl td.r{text-align:right}'
    '.impl-tbl td.b{font-weight:700;color:#1c83e1}</style>'
)
