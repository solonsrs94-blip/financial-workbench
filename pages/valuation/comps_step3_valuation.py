"""Comps Step 3: Implied Valuation — apply peer multiples to target.

EV-based multiples:  Implied EV → minus Net Debt → Equity → ÷ Shares → Price
Equity-based (P/E):  Peer P/E × Target EPS → Implied Price directly

Football field chart rendered by comps_step3_football.py.
"""

import statistics

import streamlit as st

from pages.valuation.comps_step3_football import render_football_field

# ── Multiple definitions ───────────────────────────────────────

# (key, label, target_metric_key, basis)
# basis: "ev" = EV-based, "equity" = direct price
_MULTIPLES = [
    ("ev_revenue", "EV / Revenue", "revenue", "ev"),
    ("ev_ebitda", "EV / EBITDA", "ebitda", "ev"),
    ("ev_ebit", "EV / EBIT", "ebit", "ev"),
    ("trailing_pe", "P / E", "eps", "equity"),
    ("forward_pe", "Fwd P / E", "fwd_eps", "equity"),
    ("fwd_ev_revenue", "Fwd EV / Rev", "fwd_revenue", "ev"),
    ("fwd_ev_ebitda", "Fwd EV / EBITDA*", "fwd_ebitda", "ev"),
]


# ── Main render ────────────────────────────────────────────────


def render(prepared: dict, ticker: str) -> None:
    """Render Step 3: Implied Valuation."""
    st.subheader("Step 3 - Implied Valuation")

    comps = st.session_state.get("comps_table")
    if not comps or not comps.get("target") or not comps.get("summary"):
        st.info("Complete Step 2 to see implied valuation.")
        return

    target = comps["target"]
    summary = comps["summary"]

    # Extract bridge inputs from target
    net_debt = _net_debt(target)
    shares = target.get("shares_outstanding")
    current_price = target.get("price")

    if not shares or not current_price:
        st.error("Missing shares outstanding or current price for target.")
        return

    # Add forward EPS to target (from info["forwardEps"] via forwardPE)
    _enrich_forward_eps(target)

    # Method selector
    method = st.radio(
        "Summary statistic for implied value",
        ["Median", "Mean"],
        horizontal=True,
        key="comps_val_method",
    )
    method_key = method.lower()

    # Compute implied prices
    implied = _compute_all_implied(
        summary, target, net_debt, shares, current_price,
    )

    # Store in session state
    st.session_state["comps_valuation"] = {
        "method": method_key,
        "implied_prices": implied,
        "current_price": current_price,
    }

    # Render implied valuation table
    _render_implied_table(
        implied, summary, method_key, current_price, target,
    )

    # Football field chart
    st.markdown("---")
    st.markdown("#### Comps Football Field")
    render_football_field(implied, current_price)

    # Summary box
    _render_summary_box(implied, method_key, current_price)


# ── Implied price calculations ─────────────────────────────────


def _compute_all_implied(
    summary: dict,
    target: dict,
    net_debt: float,
    shares: float,
    current_price: float,
) -> dict:
    """Compute implied prices for all multiples at low/median/mean/high."""
    result = {}
    for mult_key, label, metric_key, basis in _MULTIPLES:
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
                implied_ev = mult_val * target_metric
                implied_equity = implied_ev - net_debt
                if implied_equity <= 0:
                    prices[stat] = None
                else:
                    prices[stat] = implied_equity / shares
            else:  # equity-based (P/E)
                prices[stat] = mult_val * target_metric

        # Store if at least median or mean is valid
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
    """Calculate net debt = Total Debt - Cash."""
    debt = target.get("total_debt") or 0
    cash = target.get("cash") or 0
    return debt - cash


def _enrich_forward_eps(target: dict) -> None:
    """Add forward EPS to target dict from forward P/E and price."""
    if target.get("fwd_eps"):
        return
    fwd_pe = target.get("forward_pe")
    price = target.get("price")
    if fwd_pe and price and fwd_pe > 0:
        target["fwd_eps"] = price / fwd_pe


# ── Implied valuation table ───────────────────────────────────


def _render_implied_table(
    implied: dict, summary: dict, method_key: str,
    current_price: float, target: dict,
) -> None:
    """Render implied valuation table as HTML."""
    html = _TBL_CSS + '<table class="impl-tbl"><thead><tr>'
    headers = [
        "Multiple", "Peer " + method_key.capitalize(),
        "Target Metric", "Implied EV", "Implied Equity",
        "Implied Price", "Current", "Premium / Discount",
    ]
    for h in headers:
        html += f"<th>{h}</th>"
    html += "</tr></thead><tbody>"

    shares = target.get("shares_outstanding", 1)
    net_debt = _net_debt(target)

    for mult_key, label, metric_key, basis in _MULTIPLES:
        data = implied.get(mult_key)
        if data is None:
            html += (
                f'<tr><td>{label}</td>'
                + "<td>N/A</td>" * 7 + "</tr>"
            )
            continue

        # Get the RAW multiple from summary (e.g. 23.3x), NOT implied price
        peer_mult = summary.get(method_key, {}).get(mult_key)
        target_metric = data.get("target_metric")
        impl_price = data.get(method_key)  # already-computed implied price

        if peer_mult is None or target_metric is None:
            html += (
                f'<tr><td>{label}</td>'
                + "<td>N/A</td>" * 7 + "</tr>"
            )
            continue

        # Calculate implied EV/equity for display (EV-based only)
        if basis == "ev":
            impl_ev = peer_mult * target_metric
            impl_eq = impl_ev - net_debt
        else:
            impl_ev = None
            impl_eq = None

        prem = None
        prem_html = "N/A"
        if impl_price and current_price:
            prem = (impl_price / current_price - 1)
            color = "#2ea043" if prem >= 0 else "#f85149"
            sign = "+" if prem >= 0 else ""
            prem_html = (
                f'<span style="color:{color};font-weight:600">'
                f"{sign}{prem * 100:.1f}%</span>"
            )

        html += "<tr>"
        html += f"<td>{label}</td>"
        html += f'<td class="r">{peer_mult:.1f}x</td>'
        html += f'<td class="r">{_fmt_metric(target_metric, basis)}</td>'
        html += f'<td class="r">{_fmt_ev(impl_ev)}</td>'
        html += f'<td class="r">{_fmt_ev(impl_eq)}</td>'
        html += f'<td class="r b">{_fmt_price(impl_price)}</td>'
        html += f'<td class="r">${current_price:,.0f}</td>'
        html += f'<td class="r">{prem_html}</td>'
        html += "</tr>"

    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)


# ── Summary box ────────────────────────────────────────────────


def _render_summary_box(
    implied: dict, method_key: str, current_price: float,
) -> None:
    """Render summary box with overall range and median."""
    all_prices = []
    for data in implied.values():
        if data and data.get(method_key):
            all_prices.append(data[method_key])

    if not all_prices:
        return

    low = min(all_prices)
    high = max(all_prices)
    med = statistics.median(all_prices)

    prem = (med / current_price - 1) if current_price else 0
    color = "#2ea043" if prem >= 0 else "#f85149"
    sign = "+" if prem >= 0 else ""

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("Comps Range", f"${low:,.0f} — ${high:,.0f}")
    c2.metric(
        f"{method_key.capitalize()} Implied",
        f"${med:,.0f}",
        f"{sign}{prem * 100:.1f}% vs current",
    )
    c3.metric("Current Price", f"${current_price:,.0f}")


# ── Formatters ─────────────────────────────────────────────────

def _fmt_ev(val) -> str:
    if val is None: return "—"
    av = abs(val)
    if av >= 1e12: return f"${val / 1e12:.2f}T"
    if av >= 1e9: return f"${val / 1e9:.1f}B"
    if av >= 1e6: return f"${val / 1e6:.0f}M"
    return f"${val:,.0f}"

def _fmt_price(val) -> str:
    return f"${val:,.0f}" if val else "N/A"

def _fmt_metric(val, basis: str) -> str:
    if val is None: return "N/A"
    return f"${val:,.2f}" if basis == "equity" else _fmt_ev(val)

_TBL_CSS = (
    '<style>.impl-tbl{width:100%;border-collapse:collapse;font-size:12px;margin:8px 0}'
    '.impl-tbl th{font-size:11px;font-weight:600;padding:6px 8px;text-align:right;'
    'border-bottom:2px solid rgba(128,128,128,0.4)}'
    '.impl-tbl th:first-child{text-align:left}'
    '.impl-tbl td{padding:5px 8px;text-align:left;border-bottom:1px solid rgba(128,128,128,0.1)}'
    '.impl-tbl td.r{text-align:right}'
    '.impl-tbl td.b{font-weight:700;color:#1c83e1}</style>'
)
