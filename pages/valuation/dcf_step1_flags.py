"""Step 1b sub-component: Smart anomaly flags with what/why/action + Apply."""

import streamlit as st


_CAT_LABELS = {
    "one_off": "One-off",
    "accounting_change": "Accounting",
    "m_and_a": "M&A",
    "tax": "Tax",
    "investment_cycle": "CapEx Cycle",
    "dilution": "Dilution",
}

# Map flag line_item to the Override dropdown options
_LINE_ITEM_MAP = {
    "ebit": "EBIT",
    "gross_profit": "EBIT",
    "net_income": "Net Income",
    "revenue": "Revenue",
    "cost_of_revenue": "COGS",
    "tax_provision": "Tax",
    "sbc": "Other",
    "capital_expenditure": "Other",
    "total_debt": "Other",
    "selling_general_admin": "SGA",
    "research_development": "R&D",
}


def _get_applied_key(ticker: str) -> str:
    return f"dcf_applied_flags_{ticker}"


def _get_applied(ticker: str) -> list[dict]:
    """Get list of applied flag adjustments from session state."""
    return st.session_state.get(_get_applied_key(ticker), [])


def _apply_flag(ticker: str, flag: dict) -> None:
    """Add a flag's suggested adjustment to session state."""
    key = _get_applied_key(ticker)
    if key not in st.session_state:
        st.session_state[key] = []

    # Don't duplicate
    existing = st.session_state[key]
    for adj in existing:
        if adj["year"] == flag.get("year") and adj["line_item"] == flag.get("line_item"):
            return

    st.session_state[key].append({
        "year": flag.get("year", ""),
        "line_item": _LINE_ITEM_MAP.get(flag.get("line_item", ""), "Other"),
        "reason": flag.get("what", ""),
        "impact_mn": flag.get("impact_mn", 0),
    })


def render_flags_section(flags: list[dict], ticker: str) -> None:
    """Display flags grouped by severity with Apply buttons."""
    if not flags:
        st.success("No anomalies detected in historical data.")
        return

    high = [f for f in flags if f["severity"] == "high"]
    medium = [f for f in flags if f["severity"] == "medium"]

    if high:
        st.markdown(f"**{len(high)} significant anomalies:**")
        for i, f in enumerate(high):
            _render_flag(f, f"high_{ticker}_{i}", "flag-high", ticker)

    if medium:
        with st.expander(f"{len(medium)} minor flags", expanded=False):
            for i, f in enumerate(medium):
                _render_flag(f, f"med_{ticker}_{i}", "flag-medium", ticker)


def _render_flag(flag: dict, key: str, css_class: str, ticker: str) -> None:
    """Render a single flag with what/why/action and Apply button."""
    cat = _CAT_LABELS.get(flag.get("category", ""), "Other")
    year = flag.get("year", "")
    what = flag.get("what", "")
    why = flag.get("why", "")
    action = flag.get("action", "")
    impact = flag.get("impact_mn")
    line_item = flag.get("line_item", "")

    impact_s = ""
    if impact:
        if abs(impact) >= 1000:
            impact_s = f" | Impact: ${impact/1000:.1f}B"
        else:
            impact_s = f" | Impact: ${impact:.0f}M"

    html = (
        f'<div class="{css_class}">'
        f'<strong>{year}</strong> '
        f'<span class="source-tag">{cat}</span>{impact_s}<br>'
        f'<span style="color:rgba(255,255,255,0.9)">{what}</span><br>'
    )
    if why:
        html += f'<span style="color:rgba(255,255,255,0.6);font-size:12px">Why: {why}</span><br>'
    if action:
        html += f'<span style="color:rgba(100,200,255,0.8);font-size:12px">Action: {action}</span>'
    html += '</div>'

    # Flag content + Apply button side by side
    col_flag, col_btn = st.columns([6, 1])
    with col_flag:
        st.markdown(html, unsafe_allow_html=True)
    with col_btn:
        # Check if already applied
        applied = _get_applied(ticker)
        already = any(
            a["year"] == year and a["line_item"] == _LINE_ITEM_MAP.get(line_item, "Other")
            for a in applied
        )
        if already:
            st.markdown(
                '<span style="color:#2ca02c;font-size:12px">Applied</span>',
                unsafe_allow_html=True,
            )
        elif impact and impact != 0:
            if st.button("Apply", key=f"apply_{key}", type="secondary"):
                _apply_flag(ticker, flag)
                st.rerun()
