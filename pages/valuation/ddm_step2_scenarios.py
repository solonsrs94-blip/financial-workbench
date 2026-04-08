"""DDM Step 2 scenario orchestration — Bull/Base/Bear dividend assumptions.

Creates three tabs. Each tab renders the same dividend assumption inputs
with its own assumptions dict. Bull/Bear copy from Base on first visit.
"""

import copy

import streamlit as st

from components.commentary import render_ddm_step2_commentary

_SCENARIOS = ["base", "bull", "bear"]
_TAB_LABELS = ["Base Case", "Bull Case", "Bear Case"]


# ── Migration ─────────────────────────────────────────────────────


def migrate_ddm_legacy() -> None:
    """Move legacy ddm_assumptions into ddm_scenarios['base']."""
    if ("ddm_assumptions" in st.session_state
            and "ddm_scenarios" not in st.session_state):
        st.session_state["ddm_scenarios"] = {
            "base": st.session_state.pop("ddm_assumptions"),
            "bull": None,
            "bear": None,
        }
        st.session_state["ddm_scenarios_initialized"] = {"base"}


# ── Scenario init ─────────────────────────────────────────────────


def init_ddm_scenario(scenario: str) -> dict | None:
    """Get or create a scenario's assumptions dict.

    Bull/Bear copy from Base on first visit only.
    Returns None if Base hasn't been filled yet.
    """
    scenarios = st.session_state.setdefault(
        "ddm_scenarios", {"base": None, "bull": None, "bear": None},
    )
    initialized = st.session_state.setdefault(
        "ddm_scenarios_initialized", set(),
    )

    if scenario not in initialized:
        if scenario == "base":
            # Base starts empty — filled by render_assumptions_fn
            pass
        else:
            base = scenarios.get("base")
            if base:
                scenarios[scenario] = copy.deepcopy(base)
            # else: will be filled later
        initialized.add(scenario)

    return scenarios.get(scenario)


def store_ddm_scenario(scenario: str, assumptions: dict | None) -> None:
    """Store a scenario's assumptions dict.

    Never overwrites an existing good value with None — a transient
    None result (missing widget during partial render) must not wipe
    previously-filled scenario data.
    """
    scenarios = st.session_state.setdefault(
        "ddm_scenarios", {"base": None, "bull": None, "bear": None},
    )
    if assumptions is None:
        return
    scenarios[scenario] = assumptions


def _reset_to_base(scenario: str) -> None:
    """Reset a non-base scenario by clearing its widget keys."""
    for key in list(st.session_state.keys()):
        if key.startswith(f"ddm_{scenario}_"):
            del st.session_state[key]
    initialized = st.session_state.get("ddm_scenarios_initialized", set())
    initialized.discard(scenario)
    scenarios = st.session_state.get("ddm_scenarios", {})
    scenarios[scenario] = None


# ── Tab rendering ─────────────────────────────────────────────────


def render_scenario_tabs(
    render_assumptions_fn,
    prepared: dict,
    ticker: str,
) -> None:
    """Render Base/Bull/Bear tabs with dividend assumption inputs."""
    tabs = st.tabs(_TAB_LABELS)

    for tab, scenario, label in zip(tabs, _SCENARIOS, _TAB_LABELS):
        with tab:
            # Reset button for non-base scenarios
            if scenario != "base":
                if st.button(
                    "Reset to Base Case",
                    key=f"ddm_{scenario}_reset",
                    type="secondary",
                ):
                    _reset_to_base(scenario)
                    st.rerun()

            # Render assumption inputs — returns dict or None
            result = render_assumptions_fn(
                prepared, ticker, scenario,
            )

            # Explicit commit: user clicks Generate to write the current
            # inputs into ddm_scenarios[scenario]. Step 3 gates on that
            # dict, so this button is what "unlocks" Step 3.
            stored = st.session_state.get("ddm_scenarios", {}).get(scenario)
            already_matches = (
                result is not None
                and stored is not None
                and stored.get("model") == result.get("model")
                and stored.get("g1") == result.get("g1")
                and stored.get("g2") == result.get("g2")
                and stored.get("g") == result.get("g")
                and stored.get("n") == result.get("n")
            )
            btn_label = (
                "Regenerate" if already_matches else "Generate DDM Valuation"
            )
            if st.button(
                btn_label,
                key=f"ddm_{scenario}_generate",
                type="primary",
                disabled=(result is None),
            ):
                store_ddm_scenario(scenario, result)
                st.rerun()

            if result is None:
                st.caption("Fill in all required inputs above, then click Generate.")
            elif already_matches:
                st.caption("✓ Current inputs saved to scenario.")
            else:
                st.caption("Inputs changed — click Regenerate to update.")

            # Per-scenario commentary
            render_ddm_step2_commentary(scenario)
