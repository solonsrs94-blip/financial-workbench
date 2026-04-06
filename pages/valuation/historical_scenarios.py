"""Historical Multiples scenario orchestration — Bull/Base/Bear tabs.

Each scenario uses the same historical data but different valuation points:
  Bear: defaults to -1 sigma (or at_minus_1std implied value)
  Base: defaults to historical mean implied value
  Bull: defaults to +1 sigma implied value

The analyst can override with any custom multiple value.
"""

import streamlit as st

from components.commentary import (
    render_historical_commentary,
    render_historical_comparison_commentary,
)

_SCENARIOS = ["base", "bull", "bear"]
_TAB_LABELS = ["Base Case", "Bull Case", "Bear Case"]

_MULT_LABELS = {
    "pe": "P/E",
    "ev_ebitda": "EV/EBITDA",
    "ev_revenue": "EV/Revenue",
    "p_book": "P/Book",
    "p_tbv": "P/TBV",
}


def render_scenario_valuation(
    summary: dict,
    implied_values: dict,
    current_price: float,
    currency: str,
    eps_info: dict | None = None,
) -> None:
    """Render scenario tabs for historical implied valuation."""
    # Find available multiples with valid implied values
    mult_options = []
    for key in ["pe", "ev_ebitda", "ev_revenue", "p_book", "p_tbv"]:
        iv = implied_values.get(key)
        s = summary.get(key)
        if iv and s and iv.get("at_mean"):
            mult_options.append((key, _MULT_LABELS.get(key, key)))

    if not mult_options:
        st.info("No valid historical multiples for scenario valuation.")
        return

    # Primary multiple selector (shared)
    selected_mult = st.selectbox(
        "Primary Multiple",
        options=[k for k, _ in mult_options],
        format_func=lambda k: dict(mult_options)[k],
        key="hist_scenario_mult",
        help="Select the historical multiple to use across scenarios.",
    )

    stats = summary.get(selected_mult, {})
    iv = implied_values.get(selected_mult, {})

    if not stats or not iv:
        return

    # Scenario defaults from implied values
    defaults = {
        "bear": iv.get("at_minus_1std", iv.get("at_p10", 0)),
        "base": iv.get("at_mean", iv.get("at_median", 0)),
        "bull": _compute_plus_1std_implied(stats, iv, current_price),
    }

    # Default multiple levels for display
    mult_defaults = {
        "bear": stats.get("minus_1std", stats.get("min", 0)),
        "base": stats.get("mean", stats.get("median", 0)),
        "bull": stats.get("plus_1std", stats.get("max", 0)),
    }

    results = {}
    tabs = st.tabs(_TAB_LABELS)

    for tab, scenario, label in zip(tabs, _SCENARIOS, _TAB_LABELS):
        with tab:
            result = _render_scenario_tab(
                scenario, label, selected_mult, stats, iv,
                defaults, mult_defaults, current_price, currency,
            )
            if result:
                results[scenario] = result

            render_historical_commentary(scenario)

    # ── Comparison + store results ────────────────────────────
    if results:
        _render_comparison(results, current_price, currency)
        hist_output = _build_output(
            results, current_price, summary, implied_values, eps_info,
        )
        from components.save_button import render_save_button
        render_save_button("historical_result", "Historical", hist_output)

    render_historical_comparison_commentary()


def _render_scenario_tab(
    scenario, label, mult_key, stats, iv,
    defaults, mult_defaults, current_price, currency,
) -> dict | None:
    """Render one scenario tab. Returns result dict or None."""
    default_mult = mult_defaults.get(scenario, 0)
    default_price = defaults.get(scenario, 0)

    if not default_mult or default_mult <= 0:
        st.info(f"No data for {label}.")
        return None

    mult_label = _MULT_LABELS.get(mult_key, mult_key)
    anchor_labels = {
        "bear": f"-1\u03c3 ({default_mult:.1f}x)",
        "base": f"Mean ({default_mult:.1f}x)",
        "bull": f"+1\u03c3 ({default_mult:.1f}x)",
    }

    st.caption(f"Default: {anchor_labels.get(scenario, '')}")

    applied = st.number_input(
        f"Applied {mult_label}",
        min_value=0.1, max_value=500.0,
        value=round(default_mult, 1),
        step=0.1, format="%.1f",
        key=f"hist_{scenario}_applied_mult",
    )

    # Compute implied price from the applied multiple
    # Use the ratio between implied price and multiple from the data
    if stats.get("mean") and stats["mean"] > 0 and iv.get("at_mean"):
        price_per_unit = iv["at_mean"] / stats["mean"]
        implied_price = applied * price_per_unit
    else:
        implied_price = default_price

    if implied_price <= 0:
        st.warning("Implied price is non-positive.")
        return None

    upside = (implied_price / current_price - 1) * 100 if current_price > 0 else 0
    color = "#2ea043" if upside > 0 else "#f85149"
    sym = "$" if currency == "USD" else ""

    st.markdown(
        f'<div style="text-align:center;padding:12px 0">'
        f'<div style="font-size:14px;opacity:0.6">Implied Price</div>'
        f'<div style="font-size:28px;font-weight:700;color:#1c83e1">'
        f'{sym}{implied_price:,.2f} {currency}</div>'
        f'<div style="font-size:13px;color:{color};font-weight:600">'
        f'{upside:+.1f}% vs {sym}{current_price:,.2f}</div>'
        f'<div style="font-size:12px;opacity:0.5;margin-top:4px">'
        f'{mult_label}: {applied:.1f}x</div></div>',
        unsafe_allow_html=True,
    )

    return {
        "implied_price": implied_price,
        "applied_mult": applied,
        "mult_key": mult_key,
    }


def _render_comparison(results, current_price, currency):
    """Render Bear|Base|Bull comparison."""
    st.markdown("---")
    st.markdown("#### Scenario Comparison")

    prices = [r["implied_price"] for r in results.values()]
    if len(set(round(p, 2) for p in prices)) == 1 and len(prices) > 1:
        st.info(
            "All scenarios produce identical implied prices. "
            "Adjust the applied multiples in each tab."
        )

    order = ["bear", "base", "bull"]
    labels = {"bear": "Bear", "base": "Base", "bull": "Bull"}
    colors = {
        "bear": "rgba(248,81,73,0.15)",
        "base": "rgba(128,128,128,0.1)",
        "bull": "rgba(46,160,67,0.15)",
    }
    sym = "$" if currency == "USD" else ""

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
            f'{sym}{implied:,.2f}</div>'
            f'<div style="font-size:14px;color:{ucolor};font-weight:600">'
            f'{upside:+.1f}%</div>'
            f'<div style="font-size:12px;opacity:0.6;margin-top:4px">'
            f'Multiple: {r["applied_mult"]:.1f}x</div></div>',
            unsafe_allow_html=True,
        )


def _build_output(results, current_price, summary, implied_values, eps_info=None):
    """Build scenario output dict (does not write to session_state)."""
    hist_output = {}
    for scenario, r in results.items():
        hist_output[scenario] = {
            "implied_price": r["implied_price"],
            "applied_mult": r["applied_mult"],
            "mult_key": r["mult_key"],
        }
    # Also keep legacy format fields for backward compatibility
    hist_output["summary"] = summary
    hist_output["implied_values"] = implied_values
    hist_output["current_price"] = current_price
    if eps_info and eps_info.get("override"):
        hist_output["eps_basis"] = eps_info.get("eps_basis")
        hist_output["eps_used"] = eps_info.get("eps_used")
    return hist_output


def _compute_plus_1std_implied(stats, iv, current_price):
    """Compute implied price at +1 sigma from available data."""
    plus_1std = stats.get("plus_1std")
    mean_mult = stats.get("mean")
    at_mean = iv.get("at_mean")
    if plus_1std and mean_mult and mean_mult > 0 and at_mean:
        return at_mean / mean_mult * plus_1std
    return iv.get("at_p90", iv.get("at_mean", 0))
