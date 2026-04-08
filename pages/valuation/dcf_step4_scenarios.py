"""Step 4 scenario orchestration — Bull/Base/Bear terminal value tabs.

Each scenario gets its own terminal growth rate and exit multiple.
WACC is shared across all scenarios (from Step 3).
"""

import copy

import streamlit as st

from pages.valuation.dcf_step2_scenarios import _SCENARIOS, _TAB_LABELS
from pages.valuation.dcf_step4_methods import (
    render_gordon,
    render_exit_multiple,
)
from config.constants import SECTOR_EXIT_MULTIPLES
from components.commentary import render_dcf_step4_commentary


def render_terminal_scenarios(
    prepared: dict,
    ticker: str,
    wacc: float,
    proj_fn,
    get_ev_ebitda_fn,
    get_sector_fn,
    render_cross_checks_fn,
    render_warnings_fn,
) -> None:
    """Render Base/Bull/Bear terminal value tabs."""
    company = st.session_state.get(f"company_{ticker}")
    current_ev_ebitda = get_ev_ebitda_fn(company, ticker)
    sector = get_sector_fn(company)
    sector_multiple = SECTOR_EXIT_MULTIPLES.get(sector)

    scenarios_terminal = st.session_state.setdefault(
        "dcf_scenarios_terminal",
        {"base": None, "bull": None, "bear": None},
    )
    initialized = st.session_state.setdefault(
        "dcf_scenarios_terminal_init", set(),
    )

    tabs = st.tabs(_TAB_LABELS)

    for tab, scenario, label in zip(tabs, _SCENARIOS, _TAB_LABELS):
        with tab:
            assumptions = _get_scenario_assumptions(scenario)
            if assumptions is None:
                st.info(f"Complete Step 2 {label} assumptions first.")
                continue

            proj = proj_fn(prepared, assumptions)
            if proj is None:
                st.info(f"Complete all Step 2 {label} assumptions first.")
                continue

            n_years = assumptions["n_years"]
            fcf_final = proj["fcf"][-1]
            ebitda_final = proj["ebit"][-1] + proj["da"][-1]

            # Reset button for non-base
            if scenario != "base":
                if st.button(
                    "Reset to Base Case",
                    key=f"dcf_{scenario}_tv_reset",
                    type="secondary",
                ):
                    _reset_terminal(scenario)
                    st.rerun()

            # Method selector
            method = st.radio(
                "Primary Method",
                ["Gordon Growth Model", "Exit Multiple"],
                horizontal=True,
                key=f"dcf_{scenario}_tv_method",
                help="Both methods always calculated. "
                     "Select which drives Step 5.",
            )
            is_gordon = method == "Gordon Growth Model"

            _hr()

            # Compute both methods
            gordon_tv, g = render_gordon(
                fcf_final, ebitda_final, wacc, is_gordon, scenario,
            )
            exit_tv, multiple = render_exit_multiple(
                ebitda_final, fcf_final, wacc, current_ev_ebitda,
                sector, sector_multiple, not is_gordon, scenario,
            )

            primary_tv = gordon_tv if is_gordon else exit_tv

            _hr()
            if gordon_tv is not None and exit_tv is not None:
                render_cross_checks_fn(
                    gordon_tv, exit_tv, fcf_final, ebitda_final, wacc,
                )
                render_warnings_fn(g, multiple, wacc, sector_multiple)

            # Store terminal only when primary method has valid inputs
            if primary_tv is None:
                scenarios_terminal[scenario] = None
                st.warning("Fill in all required fields to compute terminal value.")
            else:
                scenarios_terminal[scenario] = {
                    "method": "gordon" if is_gordon else "exit_multiple",
                    "terminal_value": primary_tv,
                    "terminal_growth": g if g is not None else 0.0,
                    "exit_multiple": multiple if multiple is not None else 0.0,
                    "gordon_tv": gordon_tv,
                    "exit_tv": exit_tv,
                    "fcf_final": fcf_final,
                    "ebitda_final": ebitda_final,
                    "n_years": n_years,
                }
                initialized.add(scenario)

            # Per-scenario commentary
            render_dcf_step4_commentary(scenario)


def _get_scenario_assumptions(scenario: str) -> dict | None:
    """Get assumptions for a scenario from dcf_scenarios."""
    scenarios = st.session_state.get("dcf_scenarios", {})
    return scenarios.get(scenario)


def _reset_terminal(scenario: str) -> None:
    """Reset terminal value for a non-base scenario."""
    for key in list(st.session_state.keys()):
        if key.startswith(f"dcf_{scenario}_terminal") or \
           key.startswith(f"dcf_{scenario}_exit_multiple") or \
           key.startswith(f"dcf_{scenario}_tv_"):
            del st.session_state[key]
    init = st.session_state.get("dcf_scenarios_terminal_init", set())
    init.discard(scenario)
    terminals = st.session_state.get("dcf_scenarios_terminal", {})
    terminals[scenario] = None


def _hr():
    st.markdown(
        '<hr style="margin:12px 0;border-color:rgba(128,128,128,0.2)">',
        unsafe_allow_html=True,
    )
