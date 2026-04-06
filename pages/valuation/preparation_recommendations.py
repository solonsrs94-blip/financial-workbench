"""Preparation Recommendations — rich analyst briefing panel.

Renders the output of lib/analysis/recommendations.generate_recommendations()
as a structured guidance panel within Financial Preparation.

Uses Streamlit native components where possible for automatic theme support.
Custom HTML uses `inherit` / `currentColor` instead of hardcoded colors.
"""
import streamlit as st


# ── Fit badge colors (work on both light and dark) ──────────────────

_FIT_STYLE = {
    "strong": ("rgba(52,199,89,0.15)", "#2da44e", "Strong Fit"),
    "moderate": ("rgba(234,179,8,0.15)", "#b58105", "Moderate"),
    "weak": ("rgba(255,59,48,0.15)", "#cf222e", "Limited"),
}

_MODEL_LABELS = {
    "dcf": "DCF",
    "ddm": "DDM",
    "comps": "Comps",
    "historical": "Historical Multiples",
}


def render_recommendations(recs: dict) -> None:
    """Render the 4-section recommendation panel."""
    if not recs:
        return

    with st.expander("Recommendations & Considerations", expanded=True):
        _render_model_suitability(recs.get("model_suitability", []))
        _render_limited_models(recs.get("limited_value_models", []))
        _render_attention_items(recs.get("attention_items", []))
        _render_risks(recs.get("risks", []))


# ── Section renderers ───────────────────────────────────────────────

def _render_model_suitability(models: list[dict]) -> None:
    """Render model suitability cards in columns."""
    if not models:
        return

    st.markdown("#### Model Suitability")
    cols = st.columns(len(models))

    for col, m in zip(cols, models):
        with col:
            _render_model_card(m)


def _render_model_card(m: dict) -> None:
    """Render a single model card with fit badge."""
    fit = m.get("fit", "moderate")
    bg, color, label = _FIT_STYLE.get(fit, _FIT_STYLE["moderate"])
    model_name = _MODEL_LABELS.get(m["model"], m["model"].upper())

    badge = (f'<span style="background:{bg};color:{color};'
             f'padding:2px 8px;border-radius:3px;font-size:11px;'
             f'font-weight:600">{label}</span>')

    # Header + badge
    st.markdown(f"**{model_name}** {badge}", unsafe_allow_html=True)

    # Headline
    st.caption(m["headline"])

    # Reasons as bullet list
    reasons = m.get("reasons", [])
    if reasons:
        md = "\n".join(f"- {r}" for r in reasons)
        st.markdown(f'<div style="font-size:12px">\n\n{md}\n\n</div>',
                    unsafe_allow_html=True)

    # Caveats
    caveats = m.get("caveats", [])
    if caveats:
        for c in caveats:
            st.markdown(
                f'<div style="font-size:11px;color:#b58105;'
                f'margin:1px 0">&#9888; {c}</div>',
                unsafe_allow_html=True)


def _render_limited_models(models: list[dict]) -> None:
    """Render models with limited value as compact callouts."""
    if not models:
        return

    st.markdown("---")
    for m in models:
        model_name = _MODEL_LABELS.get(m["model"], m["model"].upper())
        reasons = " ".join(m.get("reasons", []))
        st.caption(f"**{model_name}**: {m['headline']}. {reasons}")


def _render_attention_items(items: list[dict]) -> None:
    """Render attention items with severity indicators."""
    st.markdown("---")
    st.markdown("#### Key Attention Items")

    if not items:
        st.success("No significant attention items identified")
        return

    for item in items:
        sev = item.get("severity", "medium")
        src = item.get("source", "")
        tag = f" `{src}`" if src else ""

        if sev == "high":
            st.warning(f"**{item['title']}**{tag}\n\n{item['detail']}")
        else:
            st.info(f"**{item['title']}**{tag}\n\n{item['detail']}")


def _render_risks(risks: list[dict]) -> None:
    """Render risks and considerations."""
    if not risks:
        return

    st.markdown("---")
    st.markdown("#### Risks & Considerations")

    for r in risks:
        cat = r.get("category", "")
        tag = f" `{cat}`" if cat else ""
        st.markdown(f"**{r['title']}**{tag}")
        st.caption(r["detail"])
