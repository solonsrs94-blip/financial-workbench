"""Step 5 scenario orchestration — comparison table + per-scenario output.

Runs the DCF engine once per scenario with scenario-specific assumptions
and the shared WACC. Displays a comparison table and per-scenario details.
"""

import streamlit as st
import pandas as pd

from pages.valuation.dcf_step2_scenarios import _SCENARIOS, _TAB_LABELS
from pages.valuation.dcf_step5_display import (
    render_summary,
    render_ev_breakdown,
    render_implied_price,
)
from pages.valuation.dcf_step5_bridge import render_bridge
from pages.valuation.dcf_step5_sensitivity import render_sensitivity
from lib.analysis.valuation.dcf import run_dcf
from components.layout import format_large_number


def render_scenario_output(
    prepared: dict,
    ticker: str,
    build_fcf_fn,
    to_wacc_fn,
    get_bridge_fn,
    get_proj_fn,
) -> None:
    """Run DCF per scenario and render comparison + details."""
    wacc_data = st.session_state.get("dcf_wacc")
    scenarios = st.session_state.get("dcf_scenarios", {})
    terminals = st.session_state.get("dcf_scenarios_terminal", {})

    wacc_result = to_wacc_fn(wacc_data)
    bridge_inputs = get_bridge_fn(prepared, ticker)
    current_price = bridge_inputs["current_price"]
    pf = bridge_inputs.get("price_factor", 1.0)
    currency = bridge_inputs.get("currency", "USD")

    # ── Run DCF for each scenario ────────────────────────────
    results = {}
    for scenario in _SCENARIOS:
        assumptions = scenarios.get(scenario)
        terminal = terminals.get(scenario)
        if not assumptions or not terminal:
            continue
        proj = get_proj_fn(prepared, assumptions)
        if proj is None:
            continue
        fcf_table = build_fcf_fn(proj, assumptions)
        result = run_dcf(
            fcf_table=fcf_table,
            wacc_result=wacc_result,
            terminal_growth=terminal["terminal_growth"],
            terminal_method=terminal["method"],
            exit_multiple=terminal["exit_multiple"],
            net_debt=bridge_inputs["net_debt"],
            shares=bridge_inputs["shares"],
            current_price=current_price,
            minority_interest=bridge_inputs["minority"],
            preferred_equity=bridge_inputs["preferred"],
        )
        results[scenario] = {
            "result": result,
            "terminal": terminal,
            "assumptions": assumptions,
            "fcf_table": fcf_table,
        }

    if not results.get("base"):
        st.warning("Complete all DCF steps for the Base Case first.")
        return

    # ── Customization warning ─────────────────────────────────
    _render_customization_warning(results)

    # ── Comparison table ──────────────────────────────────────
    _render_comparison_table(results, current_price, pf, currency)
    st.markdown("---")

    # ── Per-scenario detail tabs ──────────────────────────────
    avail = [(s, l) for s, l in zip(_SCENARIOS, _TAB_LABELS) if s in results]
    detail_tabs = st.tabs([l for _, l in avail])

    dcf_output = {}
    for tab, (scenario, label) in zip(detail_tabs, avail):
        with tab:
            r = results[scenario]
            dcf_result = r["result"]
            terminal = r["terminal"]
            fcf_table = r["fcf_table"]

            render_summary(dcf_result, wacc_data, terminal, pf, currency)
            render_ev_breakdown(dcf_result)

            st.markdown("---")
            bridge_result = render_bridge(
                dcf_result, bridge_inputs, ticker, scenario,
            )

            st.markdown("---")
            render_implied_price(bridge_result, current_price, pf, currency)

            st.markdown("---")
            sens_range = render_sensitivity(
                fcf_table, wacc_result, terminal,
                bridge_inputs, current_price, scenario,
            )

            for w in dcf_result.warnings:
                st.warning(w)

            # Build output dict for this scenario
            method_label = ("Gordon Growth" if terminal["method"] == "gordon"
                            else "Exit Multiple")
            implied_listing = bridge_result["implied_price"]
            if pf != 1.0:
                implied_listing = implied_listing / pf
            dcf_output[scenario] = {
                "enterprise_value": dcf_result.enterprise_value,
                "equity_value": bridge_result["equity_value"],
                "implied_price": implied_listing,
                "current_price": current_price,
                "tv_pct_of_ev": dcf_result.tv_pct_of_ev,
                "sensitivity_min": sens_range["min"] / pf if pf != 1.0 else sens_range["min"],
                "sensitivity_max": sens_range["max"] / pf if pf != 1.0 else sens_range["max"],
                "wacc": wacc_data["wacc"],
                "terminal_growth": terminal["terminal_growth"],
                "terminal_method": method_label,
                "projections": _build_projections(
                    fcf_table, dcf_result.pv_fcfs,
                ),
                "sensitivity": _build_sensitivity(
                    fcf_table, wacc_result, terminal,
                    bridge_inputs, current_price, pf,
                ),
            }

    # Save button — only writes to session_state when clicked
    from components.save_button import render_save_button
    render_save_button("dcf_output", "DCF", dcf_output)


# ── Comparison table ──────────────────────────────────────────────


def _render_comparison_table(
    results: dict, current_price: float, pf: float, cur: str,
) -> None:
    """Render Bear|Base|Bull comparison table."""
    st.markdown("#### Scenario Comparison")

    # Order: Bear | Base | Bull
    order = ["bear", "base", "bull"]
    labels = {"bear": "Bear", "base": "Base", "bull": "Bull"}
    colors = {
        "bear": "rgba(248,81,73,0.15)",
        "base": "rgba(128,128,128,0.1)",
        "bull": "rgba(46,160,67,0.15)",
    }

    active = [s for s in order if s in results]
    if not active:
        return

    cols = st.columns(len(active))
    for col, scenario in zip(cols, active):
        r = results[scenario]["result"]
        t = results[scenario]["terminal"]
        implied = r.implied_price / pf if pf != 1.0 else r.implied_price
        upside = (implied / current_price - 1) * 100 if current_price > 0 else 0
        ucolor = "#2ea043" if upside > 0 else "#f85149"
        sym = "$" if cur == "USD" else ""
        bg = colors.get(scenario, "transparent")

        col.markdown(
            f'<div style="background:{bg};padding:12px;border-radius:8px">'
            f'<div style="font-weight:700;font-size:15px;margin-bottom:8px">'
            f'{labels[scenario]} Case</div>'
            f'<div style="font-size:13px;opacity:0.7">Enterprise Value</div>'
            f'<div style="font-size:16px;font-weight:600">'
            f'{format_large_number(r.enterprise_value * 1e6)}</div>'
            f'<div style="font-size:13px;opacity:0.7;margin-top:6px">'
            f'Implied Price</div>'
            f'<div style="font-size:22px;font-weight:700;color:#1c83e1">'
            f'{sym}{implied:,.2f} {cur}</div>'
            f'<div style="font-size:14px;color:{ucolor};font-weight:600">'
            f'{upside:+.1f}%</div>'
            f'<div style="font-size:12px;opacity:0.6;margin-top:6px">'
            f'g={t["terminal_growth"]*100:.1f}%'
            f'</div></div>',
            unsafe_allow_html=True,
        )


def _build_projections(fcf_table, pv_fcfs: list) -> list[dict]:
    """Convert FCF DataFrame + PV list to JSON-serializable projections."""
    rows = []
    for i in range(len(fcf_table)):
        r = fcf_table.iloc[i]
        rows.append({
            "year": int(r["Year"]),
            "revenue": float(r["Revenue"]),
            "growth": float(r["Growth"]),
            "ebit": float(r["EBIT"]),
            "ebit_margin": float(r["EBIT_Margin"]),
            "nopat": float(r["NOPAT"]),
            "da": float(r["D&A"]),
            "capex": float(r["CapEx"]),
            "dnwc": float(r["dNWC"]),
            "sbc": float(r["SBC"]),
            "fcf": float(r["FCF"]),
            "ebitda": float(r["EBITDA"]),
            "pv_fcf": float(pv_fcfs[i]) if i < len(pv_fcfs) else None,
        })
    return rows


def _build_sensitivity(
    fcf_table, wacc_result, terminal, bridge_inputs,
    current_price, pf,
) -> dict | None:
    """Build serializable sensitivity grids."""
    from lib.analysis.valuation.sensitivity import (
        sensitivity_table, exit_sensitivity_table,
    )
    try:
        g = terminal["terminal_growth"]
        mult = terminal["exit_multiple"]
        net_debt = bridge_inputs["net_debt"]
        shares = bridge_inputs["shares"]
        minority = bridge_inputs["minority"]
        preferred = bridge_inputs["preferred"]

        df_g = sensitivity_table(
            fcf_table, wacc_result, g, terminal["method"], mult,
            net_debt, shares, current_price, minority, preferred,
        )
        if pf != 1.0:
            df_g = df_g / pf

        result = {"wacc_vs_growth": _grid_to_dict(df_g)}

        df_m = exit_sensitivity_table(
            fcf_table, wacc_result, g, mult,
            net_debt, shares, current_price, minority, preferred,
        )
        if pf != 1.0:
            df_m = df_m / pf
        result["wacc_vs_multiple"] = _grid_to_dict(df_m)
        return result
    except Exception:
        return None


def _grid_to_dict(df) -> dict:
    """Convert sensitivity DataFrame to JSON-serializable dict."""
    import math
    rows = []
    for idx, row_data in df.iterrows():
        cells = []
        for val in row_data:
            if isinstance(val, (int, float)) and not math.isnan(val) and val > 0:
                cells.append(round(float(val), 2))
            else:
                cells.append(None)
        rows.append(cells)
    return {
        "row_labels": list(df.index),
        "col_labels": list(df.columns),
        "values": rows,
    }


def _render_customization_warning(results: dict) -> None:
    """Warn if bull/bear scenarios are not customized."""
    base_price = None
    if "base" in results:
        base_price = results["base"]["result"].implied_price

    uncustomized = []
    for scenario in ["bull", "bear"]:
        if scenario in results and base_price:
            s_price = results[scenario]["result"].implied_price
            if abs(s_price - base_price) < 0.01:
                uncustomized.append(scenario.title())

    if uncustomized:
        st.info(
            f"**{' and '.join(uncustomized)}** case(s) have not been "
            f"customized — results reflect Base Case assumptions. "
            f"Go to Steps 2 and 4 to enter scenario-specific inputs."
        )
