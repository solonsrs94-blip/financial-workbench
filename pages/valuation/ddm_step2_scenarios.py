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
    _cleanup_legacy_025_defaults()


def _cleanup_legacy_025_defaults() -> None:
    """One-shot: wipe widget keys still carrying the old 0.025 default.

    Wave 1 moved growth inputs to value=None but users with pre-Wave-1
    saves may still have 2.5 sitting in their session_state widget keys.
    Runs once per session (guarded by flag).
    """
    if st.session_state.get("_ddm_025_cleanup_done"):
        return
    stale_keys = ("_g2", "_gordon_g", "_eps_g2")
    for key in list(st.session_state.keys()):
        if not key.startswith("ddm_"):
            continue
        if not any(key.endswith(s) for s in stale_keys):
            continue
        val = st.session_state.get(key)
        if isinstance(val, (int, float)) and abs(val - 2.5) < 1e-9:
            del st.session_state[key]
    st.session_state["_ddm_025_cleanup_done"] = True


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


def store_ddm_scenario(scenario: str, assumptions: dict) -> None:
    """Store a scenario's assumptions dict."""
    scenarios = st.session_state.setdefault(
        "ddm_scenarios", {"base": None, "bull": None, "bear": None},
    )
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

            store_ddm_scenario(scenario, result)

            # Per-scenario commentary
            render_ddm_step2_commentary(scenario)
