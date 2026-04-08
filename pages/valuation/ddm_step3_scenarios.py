"""DDM Step 3 scenario orchestration — comparison table + per-scenario output.

Runs the DDM engine once per scenario with scenario-specific assumptions
and the shared Ke. Displays a comparison table and per-scenario details.
"""

import streamlit as st

from pages.valuation.ddm_step2_scenarios import _SCENARIOS, _TAB_LABELS
from components.layout import format_large_number


def render_scenario_output(
    prepared: dict,
    ticker: str,
    run_gordon_fn,
    run_two_stage_fn,
    render_implied_fn,
    render_breakdown_fn,
    render_sensitivity_fn,
    render_football_fn,
    store_alt_fn,
    get_price_fn,
    get_pf_fn,
) -> None:
    """Run DDM per scenario and render comparison + details."""
    ke_data = st.session_state.get("ddm_ke")
    scenarios = st.session_state.get("ddm_scenarios", {})
    ke = ke_data["ke"]
    current_price = get_price_fn(ticker)
    pf = get_pf_fn(ticker, current_price)

    # ── Run DDM for each scenario ────────────────────────────
    results = {}
    for scenario in _SCENARIOS:
        a = scenarios.get(scenario)
        if not a or not a.get("model"):
            continue
        d0 = a["d0"]
        model = a["model"]
        if model == "gordon":
            r = run_gordon_fn(d0, ke, a)
        else:
            r = run_two_stage_fn(d0, ke, a)
        if r is None or r.get("error"):
            continue
        implied_fin = r["implied_price"]
        implied = implied_fin / pf if pf != 1.0 else implied_fin
        results[scenario] = {
            "result": r,
            "assumptions": a,
            "implied": implied,
            "model": model,
        }

    if not results.get("base"):
        st.warning("Complete Steps 1 and 2 for the Base Case first.")
        return

    # ── Customization warning ─────────────────────────────────
    _render_customization_warning(results)

    # ── Comparison table ──────────────────────────────────────
    _render_comparison_table(results, current_price, ke)
    st.markdown("---")

    # ── Per-scenario detail tabs ──────────────────────────────
    avail = [(s, l) for s, l in zip(_SCENARIOS, _TAB_LABELS) if s in results]
    detail_tabs = st.tabs([l for _, l in avail])

    ddm_output = {}
    for tab, (scenario, label) in zip(detail_tabs, avail):
        with tab:
            r = results[scenario]
            implied = r["implied"]
            a = r["assumptions"]
            d0 = a["d0"]
            model = a["model"]

            render_implied_fn(implied, current_price)
            if model != "gordon":
                render_breakdown_fn(r["result"])

            st.markdown("---")
            render_sensitivity_fn(d0, ke, a, current_price, scenario)

            st.markdown("---")
            ff_range = render_football_fn(d0, ke, a, current_price, scenario)

            g_label = a.get("g") if model == "gordon" else a.get("g2")
            ddm_output[scenario] = {
                "implied_price": implied,
                "current_price": current_price,
                "model": model,
                "ke": ke,
                "g": g_label,
                "sensitivity_min": ff_range.get("min", implied),
                "sensitivity_max": ff_range.get("max", implied),
                "projections": _build_ddm_projections(r["result"], model),
                "sensitivity": _build_ddm_sensitivity(
                    d0, ke, a, current_price,
                ),
            }

    # Save button — only writes to session_state when clicked
    def _on_save():
        st.session_state["ddm_output"] = ddm_output
        base_a = scenarios.get("base")
        if base_a:
            store_alt_fn(
                base_a["d0"], ke, base_a,
                base_a["model"], pf, current_price,
            )

    from components.save_button import render_save_button
    render_save_button("ddm_output", "DDM", ddm_output, on_save=_on_save)


def _build_ddm_projections(result: dict, model: str) -> dict:
    """Extract DDM projection data for export."""
    if model == "gordon":
        return {
            "model": "gordon",
            "d0": result.get("d0"),
            "d1": result.get("d1"),
        }
    # 2-Stage: extract projection table
    proj_df = result.get("projection")
    years = []
    if proj_df is not None and len(proj_df) > 0:
        for _, row in proj_df.iterrows():
            entry = {
                "year": int(row["Year"]),
                "dps": round(float(row["DPS"]), 4),
                "pv_factor": round(float(row["PV Factor"]), 6),
                "pv_dividend": round(float(row["PV of Dividend"]), 4),
            }
            if "EPS" in row.index:
                entry["eps"] = round(float(row["EPS"]), 4)
            if "Payout" in row.index:
                entry["payout"] = round(float(row["Payout"]), 4)
            years.append(entry)
    return {
        "model": "two_stage",
        "years": years,
        "pv_stage1": result.get("pv_stage1"),
        "pv_terminal": result.get("pv_terminal"),
        "terminal_value": result.get("terminal_value"),
        "terminal_dps": result.get("terminal_dps"),
    }


def _build_ddm_sensitivity(d0, ke, a, current_price) -> dict | None:
    """Build DDM sensitivity grid for export."""
    import math
    from lib.analysis.valuation.ddm import ddm_sensitivity
    try:
        model = a["model"]
        g_base = a.get("g") if model == "gordon" else a.get("g2")
        df = ddm_sensitivity(
            d0=d0, ke_base=ke, g_base=g_base, model=model,
            n=a.get("n", 5), g1=a.get("g1"),
            eps0=a.get("eps0"), eps_growth1=a.get("eps_growth1"),
            payout1=a.get("payout1"), eps_growth2=a.get("eps_growth2"),
            payout2=a.get("payout2"), use_eps_method=a.get("use_eps", False),
        )
        cap = current_price * 100 if current_price > 0 else float("inf")
        rows = []
        for _, row_data in df.iterrows():
            cells = []
            for val in row_data:
                if isinstance(val, (int, float)) and not math.isnan(val) and 0 < val < cap:
                    cells.append(round(float(val), 2))
                else:
                    cells.append(None)
            rows.append(cells)
        return {
            "row_header": "ke",
            "col_header": "growth",
            "row_labels": list(df.index),
            "col_labels": list(df.columns),
            "values": rows,
        }
    except Exception:
        return None


# ── Comparison table ──────────────────────────────────────────────


def _render_comparison_table(
    results: dict, current_price: float, ke: float,
) -> None:
    """Render Bear|Base|Bull comparison table."""
    st.markdown("#### Scenario Comparison")

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
        r = results[scenario]
        implied = r["implied"]
        a = r["assumptions"]
        model = a.get("model", "gordon")
        upside = (implied / current_price - 1) * 100 if current_price > 0 else 0
        ucolor = "#2ea043" if upside > 0 else "#f85149"
        bg = colors.get(scenario, "transparent")
        ml = "Gordon" if model == "gordon" else "2-Stage"
        g = a.get("g", a.get("g2", 0))

        col.markdown(
            f'<div style="background:{bg};padding:12px;border-radius:8px">'
            f'<div style="font-weight:700;font-size:15px;margin-bottom:8px">'
            f'{labels[scenario]} Case</div>'
            f'<div style="font-size:13px;opacity:0.7">Model: {ml}</div>'
            f'<div style="font-size:22px;font-weight:700;color:#1c83e1">'
            f'${implied:,.2f}</div>'
            f'<div style="font-size:14px;color:{ucolor};font-weight:600">'
            f'{upside:+.1f}%</div>'
            f'<div style="font-size:12px;opacity:0.6;margin-top:6px">'
            f'Ke={ke*100:.1f}%, g={g*100:.1f}%'
            f'</div></div>',
            unsafe_allow_html=True,
        )


def _render_customization_warning(results: dict) -> None:
    """Warn if bull/bear scenarios are not customized."""
    base_price = results.get("base", {}).get("implied")
    if not base_price:
        return
    uncustomized = []
    for scenario in ["bull", "bear"]:
        if scenario in results:
            s_price = results[scenario]["implied"]
            if abs(s_price - base_price) < 0.01:
                uncustomized.append(scenario.title())
    if uncustomized:
        st.info(
            f"**{' and '.join(uncustomized)}** case(s) have not been "
            f"customized — results reflect Base Case assumptions. "
            f"Go to Step 2 to enter scenario-specific inputs."
        )
