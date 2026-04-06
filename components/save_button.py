"""Save-to-Summary button — shared by all valuation modules.

Renders a save button + status indicator. On click, writes module output
to session_state so Summary and JSON export can read it.
"""

import streamlit as st


def _is_scenario_format(data: dict) -> bool:
    """Check if output uses scenario structure (base/bull/bear)."""
    return "base" in data and isinstance(data.get("base"), dict)


def render_save_button(
    module_key: str,
    module_label: str,
    current_data: dict,
    on_save=None,
) -> None:
    """Render a 'Save to Summary' button with status indicator.

    Args:
        module_key: session_state key to write to (e.g. "dcf_output").
        module_label: display name (e.g. "DCF").
        current_data: the computed output dict to save.
        on_save: optional callback invoked instead of default write.
    """
    saved = st.session_state.get(module_key)
    changed = _has_changed(saved, current_data)

    col_btn, col_status = st.columns([1, 2])
    with col_btn:
        if st.button(
            f"Save {module_label} to Summary",
            key=f"_save_{module_key}",
            type="primary",
        ):
            if on_save:
                on_save()
            else:
                st.session_state[module_key] = current_data
            st.toast(f"{module_label} results saved!")
            st.rerun()

    with col_status:
        if saved and not changed:
            st.markdown(
                '<div style="padding:8px 0;color:#2ea043;font-weight:600">'
                '&#10003; Saved to Summary</div>',
                unsafe_allow_html=True,
            )
        elif saved and changed:
            st.markdown(
                '<div style="padding:8px 0;color:#d29922;font-weight:600">'
                '&#9888; Results changed since last save</div>',
                unsafe_allow_html=True,
            )


def _has_changed(saved: dict | None, current: dict | None) -> bool:
    """Check if current output differs from saved (lightweight)."""
    if not saved or not current:
        return True
    # Compare scenario implied prices
    for key in ["bear", "base", "bull"]:
        cur_s = current.get(key, {}) if isinstance(current.get(key), dict) else {}
        sav_s = saved.get(key, {}) if isinstance(saved.get(key), dict) else {}
        cur_p = cur_s.get("implied_price", 0)
        sav_p = sav_s.get("implied_price", 0)
        if abs(cur_p - sav_p) > 0.005:
            return True
    return False
