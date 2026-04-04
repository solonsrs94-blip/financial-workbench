"""Comps Step 3 scenario orchestration — Bull/Base/Bear valuation tabs.

Each scenario uses the same peer data but different applied multiples:
  Bear: defaults to 25th percentile
  Base: defaults to median
  Bull: defaults to 75th percentile

The analyst can override with any custom value.
"""

import statistics

import streamlit as st

from components.commentary import (
    render_comps_step3_commentary,
    render_comps_comparison_commentary,
)
from components.layout import format_large_number

_SCENARIOS = ["base", "bull", "bear"]
_TAB_LABELS = ["Base Case", "Bull Case", "Bear Case"]


def render_scenario_valuation(
    summary: dict,
    target: dict,
    multiples: list,
    net_debt: float,
    shares: float,
    current_price: float,
    is_financial: bool,
) -> None:
    """Render scenario tabs for Comps implied valuation."""
    peers = st.session_state.get("comps_table", {}).get("peers", [])
    excluded = st.session_state.get("comps_table", {}).get("excluded", set())

    # Compute percentiles from included peers
    included = [p for p in peers if p["ticker"] not in excluded]
    percentiles = _compute_percentiles(included, multiples)

    # Primary multiple selector (shared across scenarios)
    mult_options = [
        (k, lbl) for k, lbl, _, _ in multiples
        if summary.get("median", {}).get(k) is not None
    ]
    if not mult_options:
        st.warning("No valid multiples available for valuation.")
        return

    selected_mult = st.selectbox(
        "Primary Multiple",
        options=[k for k, _ in mult_options],
        format_func=lambda k: dict(mult_options)[k],
        key="comps_scenario_mult",
        help="Select the multiple to apply across all scenarios.",
    )

    # Find basis and metric for the selected multiple
    mult_meta = {k: (mk, b) for k, _, mk, b in multiples}
    metric_key, basis = mult_meta.get(selected_mult, ("", "ev"))
    target_metric = target.get(metric_key)

    if not target_metric or target_metric <= 0:
        st.warning(f"Target metric for {selected_mult} is not available.")
        return

    # Scenario defaults
    defaults = {
        "bear": percentiles.get(selected_mult, {}).get("p25",
                summary.get("low", {}).get(selected_mult)),
        "base": summary.get("median", {}).get(selected_mult),
        "bull": percentiles.get(selected_mult, {}).get("p75",
                summary.get("high", {}).get(selected_mult)),
    }

    # Init scenarios
    initialized = st.session_state.setdefault(
        "comps_scenarios_initialized", set(),
    )

    # ── Comparison table ──────────────────────────────────────
    results = {}
    tabs = st.tabs(_TAB_LABELS)

    for tab, scenario, label in zip(tabs, _SCENARIOS, _TAB_LABELS):
        with tab:
            result = _render_scenario_tab(
                scenario, label, selected_mult, defaults,
                target_metric, basis, net_debt, shares,
                current_price, summary, initialized,
                dict(mult_options),
            )
            if result:
                results[scenario] = result

            render_comps_step3_commentary(scenario)

    # ── Store results ─────────────────────────────────────────
    if results:
        _render_comparison(results, current_price)
        _store_results(results, current_price)

    render_comps_comparison_commentary()


def _render_scenario_tab(
    scenario, label, mult_key, defaults,
    target_metric, basis, net_debt, shares,
    current_price, summary, initialized, mult_labels,
) -> dict | None:
    """Render one scenario tab. Returns result dict or None."""
    default_val = defaults.get(scenario)
    if default_val is None:
        st.info(f"No peer data available for {label}.")
        return None

    c1, c2 = st.columns(2)
    with c1:
        applied = st.number_input(
            f"Applied {mult_labels.get(mult_key, mult_key)}",
            min_value=0.1, max_value=200.0,
            value=round(default_val, 1),
            step=0.1, format="%.1f",
            key=f"comps_{scenario}_applied_mult",
        )
    with c2:
        prem_pct = st.number_input(
            "Premium / Discount (%)",
            min_value=-50.0, max_value=100.0,
            value=0.0, step=1.0, format="%.1f",
            key=f"comps_{scenario}_premium",
            help="Positive = premium, Negative = discount",
        )

    final_mult = applied * (1 + prem_pct / 100)

    # Compute implied price
    if basis == "ev":
        implied_ev = final_mult * target_metric
        implied_eq = implied_ev - net_debt
        implied_price = implied_eq / shares if implied_eq > 0 and shares > 0 else 0
    else:
        implied_price = final_mult * target_metric

    if implied_price <= 0:
        st.warning("Implied price is non-positive with these inputs.")
        return None

    upside = (implied_price / current_price - 1) * 100 if current_price > 0 else 0
    color = "#2ea043" if upside > 0 else "#f85149"

    st.markdown(
        f'<div style="text-align:center;padding:12px 0">'
        f'<div style="font-size:14px;opacity:0.6">Implied Price</div>'
        f'<div style="font-size:28px;font-weight:700;color:#1c83e1">'
        f'${implied_price:,.2f}</div>'
        f'<div style="font-size:13px;color:{color};font-weight:600">'
        f'{upside:+.1f}% vs ${current_price:,.2f}</div>'
        f'<div style="font-size:12px;opacity:0.5;margin-top:4px">'
        f'Multiple: {final_mult:.1f}x'
        f'{f" ({prem_pct:+.1f}% adj)" if prem_pct else ""}'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    return {
        "implied_price": implied_price,
        "applied_mult": applied,
        "premium": prem_pct,
        "final_mult": final_mult,
    }


def _render_comparison(results: dict, current_price: float) -> None:
    """Render Bear|Base|Bull comparison."""
    st.markdown("---")
    st.markdown("#### Scenario Comparison")

    # Customization warning
    prices = [r["implied_price"] for r in results.values()]
    if len(set(round(p, 2) for p in prices)) == 1 and len(prices) > 1:
        st.info(
            "All scenarios produce identical implied prices. "
            "Adjust the applied multiples in each tab to differentiate."
        )

    order = ["bear", "base", "bull"]
    labels = {"bear": "Bear", "base": "Base", "bull": "Bull"}
    colors = {
        "bear": "rgba(248,81,73,0.15)",
        "base": "rgba(128,128,128,0.1)",
        "bull": "rgba(46,160,67,0.15)",
    }

    active = [s for s in order if s in results]
    cols = st.columns(len(active))
    for col, scenario in zip(cols, active):
        r = results[scenario]
        implied = r["implied_price"]
        upside = (implied / current_price - 1) * 100 if current_price > 0 else 0
        ucolor = "#2ea043" if upside > 0 else "#f85149"
        bg = colors.get(scenario, "transparent")
        col.markdown(
            f'<div style="background:{bg};padding:12px;border-radius:8px">'
            f'<div style="font-weight:700;font-size:15px;margin-bottom:8px">'
            f'{labels[scenario]} Case</div>'
            f'<div style="font-size:22px;font-weight:700;color:#1c83e1">'
            f'${implied:,.2f}</div>'
            f'<div style="font-size:14px;color:{ucolor};font-weight:600">'
            f'{upside:+.1f}%</div>'
            f'<div style="font-size:12px;opacity:0.6;margin-top:4px">'
            f'Multiple: {r["final_mult"]:.1f}x</div></div>',
            unsafe_allow_html=True,
        )


def _store_results(results: dict, current_price: float) -> None:
    """Store scenario results in session state."""
    comps_output = {}
    for scenario, r in results.items():
        comps_output[scenario] = {
            "implied_price": r["implied_price"],
            "applied_mult": r["applied_mult"],
            "premium": r["premium"],
            "final_mult": r["final_mult"],
        }
    comps_output["current_price"] = current_price
    st.session_state["comps_valuation"] = comps_output


def _compute_percentiles(
    peers: list[dict], multiples: list,
) -> dict:
    """Compute 25th and 75th percentiles per multiple."""
    result = {}
    for mult_key, _, _, _ in multiples:
        vals = sorted([
            p[mult_key] for p in peers
            if p.get(mult_key) is not None
            and isinstance(p[mult_key], (int, float)) and p[mult_key] > 0
        ])
        if len(vals) >= 4:
            n = len(vals)
            p25_idx = max(0, int(n * 0.25) - 1)
            p75_idx = min(n - 1, int(n * 0.75))
            result[mult_key] = {
                "p25": vals[p25_idx],
                "p75": vals[p75_idx],
            }
        elif vals:
            result[mult_key] = {
                "p25": vals[0],
                "p75": vals[-1],
            }
    return result
