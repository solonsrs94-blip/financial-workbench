"""Reusable placeholder renderer for coming-soon pages."""

import streamlit as st

from components.layout import load_css
from components.auth_guard import require_auth, show_user_sidebar


def render_placeholder(
    title: str,
    icon: str,
    description: str,
    features: list[tuple[str, str]],
) -> None:
    """Render a coming-soon placeholder page.

    Parameters
    ----------
    title : page title (no icon)
    icon : emoji icon for the header
    description : one-line summary of the page
    features : list of (name, detail) tuples
    """
    load_css()
    require_auth()
    show_user_sidebar()

    st.title(f"{icon} {title}")
    st.caption(description)

    st.info("This page is under development and will be available in a future update.", icon="🚧")

    st.markdown("#### Planned Features")
    for name, detail in features:
        st.markdown(f"- **{name}** — {detail}")
