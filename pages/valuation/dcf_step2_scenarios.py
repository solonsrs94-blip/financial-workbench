"""Step 2 scenario orchestration — Bull/Base/Bear tabs for assumptions.

Creates three tabs. Each tab renders the same driver input table
with its own assumptions dict. Bull/Bear copy from Base on first visit.
"""

import copy

import streamlit as st

from pages.valuation.dcf_step2_output import (
    render_projected_revenue,
    render_calculated_output,
)
from components.commentary import render_dcf_step2_commentary

_SCENARIOS = ["base", "bull", "bear"]
_TAB_LABELS = ["Base Case", "Bull Case", "Bear Case"]


# ── Migration ─────────────────────────────────────────────────────


def migrate_legacy() -> None:
    """Move legacy dcf_assumptions into dcf_scenarios['base']."""
    if "dcf_assumptions" in st.session_state and "dcf_scenarios" not in st.session_state:
        st.session_state["dcf_scenarios"] = {
            "base": st.session_state.pop("dcf_assumptions"),
            "bull": None,
            "bear": None,
        }
        st.session_state["dcf_scenarios_initialized"] = {"base"}


# ── Scenario init ─────────────────────────────────────────────────


def _make_empty(n_years: int, nwc_method: str) -> dict:
    """Create a blank assumptions dict."""
    empty = [None] * n_years
    return {
        "n_years": n_years,
        "nwc_method": nwc_method,
        "growth_rates": list(empty),
        "ebit_margins": list(empty),
        "tax_rates": list(empty),
        "capex_pcts": list(empty),
        "da_pcts": list(empty),
        "sbc_pcts": list(empty),
        "dso": list(empty),
        "dio": list(empty),
        "dpo": list(empty),
        "nwc_pcts": list(empty),
    }


def init_scenario(scenario: str, n_years: int, nwc_method: str) -> dict:
    """Get or create a scenario's assumptions dict.

    Bull/Bear copy from Base on first visit only.
    """
    scenarios = st.session_state.setdefault(
        "dcf_scenarios", {"base": None, "bull": None, "bear": None},
    )
    initialized = st.session_state.setdefault(
        "dcf_scenarios_initialized", set(),
    )

    existing = scenarios.get(scenario)

    # Reset if n_years or nwc_method changed
    if existing and (
        existing["n_years"] != n_years
        or existing["nwc_method"] != nwc_method
    ):
        existing = None
        scenarios[scenario] = None
        initialized.discard(scenario)

    if scenario not in initialized:
        if scenario == "base" or scenarios.get("base") is None:
            scenarios[scenario] = _make_empty(n_years, nwc_method)
        else:
            scenarios[scenario] = copy.deepcopy(scenarios["base"])
        initialized.add(scenario)

    if scenarios[scenario] is None:
        scenarios[scenario] = _make_empty(n_years, nwc_method)
        initialized.add(scenario)

    return scenarios[scenario]


def _reset_to_base(scenario: str) -> None:
    """Reset a non-base scenario by clearing its widget keys."""
    # Remove widget keys for this scenario
    for key in list(st.session_state.keys()):
        if key.startswith(f"dcf_{scenario}_"):
            del st.session_state[key]
    # Mark as not initialized so next visit re-copies from Base
    initialized = st.session_state.get("dcf_scenarios_initialized", set())
    initialized.discard(scenario)
    scenarios = st.session_state.get("dcf_scenarios", {})
    scenarios[scenario] = None


# ── Tab rendering ─────────────────────────────────────────────────


def render_scenario_tabs(
    hist: dict,
    n_years: int,
    proj_years: list[int],
    nwc_method: str,
    render_driver_table_fn,
) -> None:
    """Render Base/Bull/Bear tabs with driver tables + calculated output."""
    tabs = st.tabs(_TAB_LABELS)

    for tab, scenario, label in zip(tabs, _SCENARIOS, _TAB_LABELS):
        with tab:
            assumptions = init_scenario(scenario, n_years, nwc_method)

            # Reset button for non-base scenarios
            if scenario != "base":
                if st.button(
                    "Reset to Base Case",
                    key=f"dcf_{scenario}_reset",
                    type="secondary",
                ):
                    _reset_to_base(scenario)
                    st.rerun()

            # Render driver input table (with scenario-prefixed keys)
            render_driver_table_fn(
                hist, assumptions, n_years, proj_years,
                nwc_method, scenario,
            )

            # Calculated output section
            st.markdown("---")
            render_calculated_output(assumptions, hist, proj_years)

            # Per-scenario commentary
            render_dcf_step2_commentary(scenario)
