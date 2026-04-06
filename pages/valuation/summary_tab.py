"""Summary tab — combined valuation overview from all models."""

import json
from datetime import date

import streamlit as st

from pages.valuation.summary_table import render_valuation_table
from pages.valuation.summary_football import render_combined_football
from pages.valuation.summary_helpers import (
    is_scenario_format,
    collect_dcf_rows,
    collect_dcf_bars,
    collect_ddm_rows,
    collect_ddm_bars,
    collect_comps_rows,
    collect_comps_bars,
    collect_historical_rows,
    collect_historical_bars,
    render_summary_stats,
    render_weight_inputs,
)
from components.commentary import render_commentary
from lib.exports.analysis_export import build_export_json


def render(prepared: dict, ticker: str) -> None:
    """Render Summary tab."""
    st.subheader("Valuation Summary")
    st.caption(
        "Executive summary combining results from all completed "
        "valuation models. Uncheck a model to exclude it from the "
        "consensus."
    )

    current_price = _get_current_price(ticker)
    all_rows = _collect_rows(current_price)
    all_bars = _collect_bars()

    if not all_rows:
        st.info(
            "No valuation models have been completed yet. "
            "Complete at least one model (DCF, Comps, Historical, or DDM) "
            "to see the summary."
        )
        return

    # ── Model selector ─────────────────────────────────────
    available = _available_groups(all_rows)
    included = _render_model_selector(available)
    weights = render_weight_inputs(included)
    rows = [r for r in all_rows if _row_group(r) in included]
    bars = [b for b in all_bars if _bar_group(b) in included]
    excluded = [r for r in all_rows if _row_group(r) not in included]

    # ── Section 1: Current price reference ─────────────────
    if current_price > 0:
        st.markdown(
            f'<div style="font-size:13px;opacity:0.6">'
            f'Current Market Price: <b>${current_price:,.2f}</b>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Section 2: Valuation overview table ────────────────
    if rows:
        render_valuation_table(rows, current_price)
    else:
        st.info("All models excluded. Check at least one above.")

    # ── Section 3: Combined football field ─────────────────
    st.markdown("---")
    if bars:
        render_combined_football(bars, current_price)

    # ── Section 4: Summary statistics ──────────────────────
    if len(rows) > 1:
        st.markdown("---")
        render_summary_stats(rows, current_price, weights)

    # ── Section 5: Excluded models (grayed out) ────────────
    if excluded:
        st.markdown("---")
        _render_excluded(excluded, current_price)

    # ── Export Analysis ────────────────────────────────────────────
    st.markdown("---")
    _render_export(ticker, included)

    # ── Analyst Commentary ────────────────────────────────────────
    render_commentary("commentary_summary")


_GROUP_ORDER = ["DCF", "Comps", "Historical", "DDM"]


def _row_group(row: dict) -> str:
    """Map a row's method name to its model group."""
    m = row["method"]
    if m.startswith("DCF"):
        return "DCF"
    if m.startswith("Comps"):
        return "Comps"
    if m.startswith("Historical"):
        return "Historical"
    if m.startswith("DDM"):
        return "DDM"
    return m


def _bar_group(bar: dict) -> str:
    """Map a bar's label to its model group."""
    return _row_group({"method": bar["label"]})


def _available_groups(rows: list[dict]) -> list[str]:
    """Return ordered list of model groups present in rows."""
    present = {_row_group(r) for r in rows}
    return [g for g in _GROUP_ORDER if g in present]


def _render_model_selector(available: list[str]) -> set[str]:
    """Render checkboxes and return set of included model groups."""
    cols = st.columns(len(available))
    included = set()
    for i, group in enumerate(available):
        key = f"summary_include_{group}"
        default = st.session_state.get(key, True)
        checked = cols[i].checkbox(
            group, value=default, key=key,
        )
        if checked:
            included.add(group)
    return included


def _render_excluded(rows: list[dict], current_price: float):
    """Show excluded models in a muted style."""
    parts = ["#### Excluded from Consensus"]
    for r in rows:
        imp = r["implied"]
        up = (imp / current_price - 1) * 100 if current_price > 0 else 0
        parts.append(f"- ~~{r['method']}~~: ${imp:,.2f} ({up:+.1f}%)")
    st.markdown(
        f'<div style="opacity:0.45">\n\n' + "\n".join(parts) + "\n</div>",
        unsafe_allow_html=True,
    )


def _collect_rows(current_price: float) -> list[dict]:
    """Collect implied price rows from all completed models."""
    rows = []
    dcf = st.session_state.get("dcf_output")
    if dcf:
        collect_dcf_rows(dcf, rows)
    comps = st.session_state.get("comps_valuation")
    if comps:
        collect_comps_rows(comps, rows)

    hist = st.session_state.get("historical_result")
    if hist:
        collect_historical_rows(hist, rows)
    # DDM — scenario or legacy format
    ddm = st.session_state.get("ddm_output")
    if ddm:
        collect_ddm_rows(ddm, rows)
    # Alt model (legacy only — skip when scenario output exists)
    ddm_alt = st.session_state.get("ddm_output_alt")
    if (ddm_alt and ddm_alt.get("implied_price") and ddm_alt["implied_price"] > 0
            and not (ddm and is_scenario_format(ddm))):
        ml = "Gordon Growth" if ddm_alt.get("model") == "gordon" else "2-Stage"
        ke, g = ddm_alt.get("ke", 0), ddm_alt.get("g", 0)
        rows.append({"method": f"DDM ({ml})", "implied": ddm_alt["implied_price"],
                      "notes": f"Ke: {ke*100:.1f}%, g: {g*100:.1f}%"})
    return rows


def _collect_bars() -> list[dict]:
    """Collect football field bar data from all completed models."""
    bars = []

    # DCF — scenario range or single sensitivity range
    dcf = st.session_state.get("dcf_output")
    if dcf:
        collect_dcf_bars(dcf, bars)

    # Comps — scenario range or per-multiple range
    comps = st.session_state.get("comps_valuation")
    if comps:
        collect_comps_bars(comps, bars)

    # Historical — scenario range or per-multiple range
    hist = st.session_state.get("historical_result")
    if hist:
        collect_historical_bars(hist, bars)

    # DDM — scenario or legacy format
    ddm = st.session_state.get("ddm_output")
    if ddm:
        collect_ddm_bars(ddm, bars)
    # Alt model (legacy only — skip when scenario output exists)
    ddm_alt = st.session_state.get("ddm_output_alt")
    if (ddm_alt and ddm_alt.get("implied_price") and ddm_alt["implied_price"] > 0
            and not (ddm and is_scenario_format(ddm))):
        lo = ddm_alt.get("sensitivity_min", ddm_alt["implied_price"])
        hi = ddm_alt.get("sensitivity_max", ddm_alt["implied_price"])
        ml = "Gordon" if ddm_alt.get("model") == "gordon" else "2-Stage"
        bars.append({
            "label": f"DDM ({ml})",
            "low": lo, "high": hi, "mid": ddm_alt["implied_price"],
            "color": "rgba(163, 113, 247, 0.5)",
            "marker_color": "#a371f7",
        })

    return bars


def _get_current_price(ticker: str) -> float:
    """Get current share price from session state."""
    company = st.session_state.get(f"company_{ticker}")
    if company:
        price_obj = getattr(company, "price", None)
        return getattr(price_obj, "price", 0) or 0
    return 0.0


def _render_export(ticker: str, included: set) -> None:
    """Render Export Analysis download button."""
    included_modules = {
        g: (g in included) for g in _GROUP_ORDER
    }

    defaults = _build_default_templates()
    state_copy = dict(st.session_state)

    export_data = build_export_json(
        state_copy, ticker, included_modules, defaults,
    )
    json_str = json.dumps(export_data, indent=2, default=str)
    today = date.today().isoformat()

    st.download_button(
        "Export Analysis",
        data=json_str,
        file_name=f"{ticker}_analysis_{today}.json",
        mime="application/json",
        type="secondary",
    )


def _build_default_templates() -> dict:
    """Build map of commentary key -> default template for comparison."""
    from components.commentary import (
        TEMPLATES, get_step2_template,
        _STEP4_TEMPLATES, _DDM_STEP2_TEMPLATES,
        _COMPS_TEMPLATES, _HIST_TEMPLATES,
    )
    from components.commentary_templates import dcf_step5, ddm_step3
    from components.commentary_templates import (
        comps as comps_t, historical as hist_t,
    )

    defaults = dict(TEMPLATES)
    # DCF Step 2 (sector-specific)
    for s in ["base", "bull", "bear"]:
        defaults[f"commentary_dcf_step2_{s}"] = get_step2_template(s)
    # DCF Step 4
    for s, tmpl in _STEP4_TEMPLATES.items():
        defaults[f"commentary_dcf_step4_{s}"] = tmpl
    # DCF Step 5
    defaults["commentary_dcf_step5"] = dcf_step5.STEP5_COMPARISON
    # DDM Step 2
    for s, tmpl in _DDM_STEP2_TEMPLATES.items():
        defaults[f"commentary_ddm_step2_{s}"] = tmpl
    # DDM Step 3
    defaults["commentary_ddm_step3"] = ddm_step3.STEP3_COMPARISON
    # Comps
    for s, tmpl in _COMPS_TEMPLATES.items():
        defaults[f"commentary_comps_step3_{s}"] = tmpl
    defaults["commentary_comps_comparison"] = comps_t.COMPARISON
    # Historical
    for s, tmpl in _HIST_TEMPLATES.items():
        defaults[f"commentary_historical_{s}"] = tmpl
    defaults["commentary_historical_comparison"] = hist_t.COMPARISON
    return defaults
