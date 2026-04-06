"""Analyst Commentary — guided text areas for each valuation module."""

import streamlit as st

from components.commentary_templates import (
    tech_growth, industrials, consumer,
    healthcare, energy_utilities, real_estate,
    dcf_step4, dcf_step5,
    ddm_financial, ddm_step3,
    ddm_consumer, ddm_utility, ddm_reit, ddm_cyclical,
    comps as comps_templates,
    historical as hist_templates,
    non_dcf,
)

# -- Sector registry (DCF Step 2) ----------------------------------------

SECTOR_OPTIONS = [
    "Technology / Growth",
    "Industrials / Manufacturing",
    "Consumer",
    "Healthcare / Pharma",
    "Energy / Utilities",
    "Real Estate",
]

_SECTOR_MODULES = {
    "Technology / Growth": tech_growth,
    "Industrials / Manufacturing": industrials,
    "Consumer": consumer,
    "Healthcare / Pharma": healthcare,
    "Energy / Utilities": energy_utilities,
    "Real Estate": real_estate,
}

_SCENARIO_ATTRS = {
    "base": "STEP2_BASE",
    "bull": "STEP2_BULL",
    "bear": "STEP2_BEAR",
}

# -- Step 4 templates (not sector-specific) -------------------------------

_STEP4_TEMPLATES = {
    "base": dcf_step4.STEP4_BASE,
    "bull": dcf_step4.STEP4_BULL,
    "bear": dcf_step4.STEP4_BEAR,
}

# -- DDM sector registry --------------------------------------------------

DDM_SECTOR_OPTIONS = [
    "Consumer / Dividend Aristocrat",
    "Financial (Bank / Insurance)",
    "Utility / Infrastructure",
    "REIT",
    "Cyclical Dividend",
]

_DDM_SECTOR_MODULES = {
    "Consumer / Dividend Aristocrat": ddm_consumer,
    "Financial (Bank / Insurance)": ddm_financial,
    "Utility / Infrastructure": ddm_utility,
    "REIT": ddm_reit,
    "Cyclical Dividend": ddm_cyclical,
}

# -- Non-DCF templates ----------------------------------------------------

TEMPLATES: dict[str, str] = {
    "commentary_dcf_step3": non_dcf.STEP3_WACC,
    "commentary_comps": non_dcf.COMPS,
    "commentary_historical": non_dcf.HISTORICAL,
    "commentary_ddm": non_dcf.DDM_LEGACY,
    "commentary_summary": non_dcf.SUMMARY,
}


# -- Public API: standard modules -----------------------------------------


def render_commentary(key: str) -> None:
    """Render a standard Analyst Commentary expander (non-DCF modules)."""
    template = TEMPLATES.get(key, "")
    if not template:
        return
    with st.expander("Analyst Commentary", expanded=False):
        st.text_area(
            label="Analyst Commentary",
            value=st.session_state.get(key, template),
            height=400, key=key,
            placeholder="Enter your analysis here...",
            label_visibility="collapsed",
        )


# -- Public API: DCF per-scenario -----------------------------------------


def get_step2_template(scenario: str) -> str:
    """Get the DCF Step 2 template for a scenario using selected sector."""
    sector = st.session_state.get("dcf_sector_template", SECTOR_OPTIONS[0])
    mod = _SECTOR_MODULES.get(sector, tech_growth)
    attr = _SCENARIO_ATTRS.get(scenario, "STEP2_BASE")
    return getattr(mod, attr, "")


def render_dcf_step2_commentary(scenario: str) -> None:
    """Render per-scenario DCF Step 2 commentary with sector selector."""
    key = f"commentary_dcf_step2_{scenario}"
    template = get_step2_template(scenario)
    with st.expander("Analyst Commentary", expanded=False):
        _render_sector_selector(scenario)
        st.text_area(
            label="Analyst Commentary",
            value=st.session_state.get(key, template),
            height=400, key=key,
            placeholder="Enter your analysis here...",
            label_visibility="collapsed",
        )


def render_dcf_step4_commentary(scenario: str) -> None:
    """Render per-scenario DCF Step 4 commentary."""
    key = f"commentary_dcf_step4_{scenario}"
    template = _STEP4_TEMPLATES.get(scenario, dcf_step4.STEP4_BASE)
    with st.expander("Analyst Commentary", expanded=False):
        st.text_area(
            label="Analyst Commentary",
            value=st.session_state.get(key, template),
            height=300, key=key,
            placeholder="Enter your analysis here...",
            label_visibility="collapsed",
        )


def render_dcf_step5_commentary() -> None:
    """Render shared DCF Step 5 scenario comparison commentary."""
    key = "commentary_dcf_step5"
    template = dcf_step5.STEP5_COMPARISON
    with st.expander("Analyst Commentary", expanded=False):
        st.text_area(
            label="Analyst Commentary",
            value=st.session_state.get(key, template),
            height=400, key=key,
            placeholder="Enter your analysis here...",
            label_visibility="collapsed",
        )


# -- Public API: DDM per-scenario -----------------------------------------


def _get_ddm_step2_template(scenario: str) -> str:
    """Get the DDM Step 2 template for a scenario using selected sector."""
    sector = st.session_state.get("ddm_sector_template", DDM_SECTOR_OPTIONS[0])
    mod = _DDM_SECTOR_MODULES.get(sector, ddm_consumer)
    attr = _SCENARIO_ATTRS.get(scenario, "STEP2_BASE")
    return getattr(mod, attr, "")


def render_ddm_step2_commentary(scenario: str) -> None:
    """Render per-scenario DDM Step 2 commentary with sector selector."""
    key = f"commentary_ddm_step2_{scenario}"
    template = _get_ddm_step2_template(scenario)
    with st.expander("Analyst Commentary", expanded=False):
        _render_ddm_sector_selector(scenario)
        st.text_area(
            label="Analyst Commentary",
            value=st.session_state.get(key, template),
            height=400, key=key,
            placeholder="Enter your analysis here...",
            label_visibility="collapsed",
        )


def render_ddm_step3_commentary() -> None:
    """Render shared DDM Step 3 scenario comparison commentary."""
    key = "commentary_ddm_step3"
    template = ddm_step3.STEP3_COMPARISON
    with st.expander("Analyst Commentary", expanded=False):
        st.text_area(
            label="Analyst Commentary",
            value=st.session_state.get(key, template),
            height=400, key=key,
            placeholder="Enter your analysis here...",
            label_visibility="collapsed",
        )


# -- Public API: Comps per-scenario ---------------------------------------

_COMPS_TEMPLATES = {
    "base": comps_templates.STEP3_BASE,
    "bull": comps_templates.STEP3_BULL,
    "bear": comps_templates.STEP3_BEAR,
}


def render_comps_step3_commentary(scenario: str) -> None:
    """Render per-scenario Comps Step 3 commentary."""
    key = f"commentary_comps_step3_{scenario}"
    template = _COMPS_TEMPLATES.get(scenario, comps_templates.STEP3_BASE)
    with st.expander("Analyst Commentary", expanded=False):
        st.text_area(
            label="Analyst Commentary",
            value=st.session_state.get(key, template),
            height=400, key=key,
            placeholder="Enter your analysis here...",
            label_visibility="collapsed",
        )


def render_comps_comparison_commentary() -> None:
    """Render shared Comps scenario comparison commentary."""
    key = "commentary_comps_comparison"
    template = comps_templates.COMPARISON
    with st.expander("Analyst Commentary", expanded=False):
        st.text_area(
            label="Analyst Commentary",
            value=st.session_state.get(key, template),
            height=400, key=key,
            placeholder="Enter your analysis here...",
            label_visibility="collapsed",
        )


# -- Public API: Historical per-scenario ----------------------------------

_HIST_TEMPLATES = {
    "base": hist_templates.STEP_BASE,
    "bull": hist_templates.STEP_BULL,
    "bear": hist_templates.STEP_BEAR,
}


def render_historical_commentary(scenario: str) -> None:
    """Render per-scenario Historical Multiples commentary."""
    key = f"commentary_historical_{scenario}"
    template = _HIST_TEMPLATES.get(scenario, hist_templates.STEP_BASE)
    with st.expander("Analyst Commentary", expanded=False):
        st.text_area(
            label="Analyst Commentary",
            value=st.session_state.get(key, template),
            height=400, key=key,
            placeholder="Enter your analysis here...",
            label_visibility="collapsed",
        )


def render_historical_comparison_commentary() -> None:
    """Render shared Historical scenario comparison commentary."""
    key = "commentary_historical_comparison"
    template = hist_templates.COMPARISON
    with st.expander("Analyst Commentary", expanded=False):
        st.text_area(
            label="Analyst Commentary",
            value=st.session_state.get(key, template),
            height=400, key=key,
            placeholder="Enter your analysis here...",
            label_visibility="collapsed",
        )


# -- Sector selectors (shared logic) --------------------------------------


def _render_sector_selector(scenario: str) -> None:
    """DCF sector dropdown."""
    _render_template_selector(
        scenario, "dcf", SECTOR_OPTIONS,
        "dcf_sector_template", "commentary_dcf_step2",
    )


def _render_ddm_sector_selector(scenario: str) -> None:
    """DDM sector dropdown."""
    _render_template_selector(
        scenario, "ddm", DDM_SECTOR_OPTIONS,
        "ddm_sector_template", "commentary_ddm_step2",
    )


def _render_template_selector(scenario, prefix, options, state_key, commentary_prefix):
    prev = st.session_state.get(state_key, options[0])
    idx = options.index(prev) if prev in options else 0
    new = st.selectbox("Analysis Template", options=options, index=idx,
                       key=f"_{prefix}_sector_select_{scenario}",
                       help="Sector-specific prompts for your analysis.")
    if new != prev:
        st.warning("Changing template will reset commentary for all scenarios.")
        if st.button("Confirm template change", key=f"_confirm_{prefix}_sector_{scenario}"):
            st.session_state[state_key] = new
            for s in ["base", "bull", "bear"]:
                k = f"{commentary_prefix}_{s}"
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()
