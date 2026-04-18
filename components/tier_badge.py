"""Tier badge — small visual indicator of Personal vs Professional tier."""

import streamlit as st

from components.tier_guard import get_user_tier


_TIER_STYLES = {
    "personal": {
        "label": "Personal",
        "icon": "👤",
        "bg": "#e8f4f8",
        "fg": "#0c5889",
        "border": "#99cce0",
    },
    "professional": {
        "label": "Professional",
        "icon": "🏦",
        "bg": "#fef3e8",
        "fg": "#8b4513",
        "border": "#e0a875",
    },
}


def render_tier_badge(tier: str | None = None) -> None:
    """Render an inline tier badge.

    If tier is None, uses the current user's tier from session state.
    """
    if tier is None:
        tier = get_user_tier()

    style = _TIER_STYLES.get(tier, _TIER_STYLES["personal"])

    st.markdown(
        f"""
        <span style="
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            background-color: {style['bg']};
            color: {style['fg']};
            border: 1px solid {style['border']};
            font-size: 0.75rem;
            font-weight: 500;
        ">{style['icon']} {style['label']}</span>
        """,
        unsafe_allow_html=True,
    )


def tier_label(tier: str | None = None) -> str:
    """Plain-text tier label for headers or captions."""
    if tier is None:
        tier = get_user_tier()
    return _TIER_STYLES.get(tier, _TIER_STYLES["personal"])["label"]
