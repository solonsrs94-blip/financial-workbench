"""Reusable placeholder renderer for coming-soon pages.

Standardized "under development" UI used across every not-yet-built page.
Keep one source of truth here; never hand-roll placeholder UI in a page.

Optional kwargs (phase, target_quarter, progress_pct, tier) integrate with
the status dashboard and tier system. Existing callers that pass only the
core args continue to work unchanged.
"""

import streamlit as st

from components.layout import load_css
from components.auth_guard import require_auth, show_user_sidebar


_TIER_LABEL = {
    "personal": ("👤", "Personal"),
    "professional": ("🏦", "Professional"),
}


def render_placeholder(
    title: str,
    icon: str,
    description: str,
    features: list[tuple[str, str]],
    *,
    phase: str | None = None,
    target_quarter: str | None = None,
    progress_pct: int = 0,
    tier: str = "personal",
) -> None:
    """Render a coming-soon placeholder page.

    Parameters
    ----------
    title : page title (no icon — passed separately)
    icon : emoji icon for the header
    description : one-line summary of the page
    features : list of (name, detail) tuples — the planned feature list
    phase : optional roadmap phase identifier (e.g. "Fasi 3a — Discovery")
    target_quarter : optional target delivery quarter (e.g. "Q2 2026")
    progress_pct : 0-100 — shown as a progress bar. 0 = not started.
    tier : "personal" or "professional" — controls badge + auth flow
    """
    load_css()
    require_auth()
    show_user_sidebar()

    st.title(f"{icon} {title}")

    # Tier + description line
    tier_icon, tier_name = _TIER_LABEL.get(tier, _TIER_LABEL["personal"])
    st.caption(f"{description}  •  {tier_icon} {tier_name} tier")

    # Status banner
    if tier == "professional":
        st.info(
            "This Professional tier feature is on the roadmap. "
            "It will become available when this module is implemented.",
            icon="🏦",
        )
    else:
        st.info(
            "This page is under development and will be available in a future update.",
            icon="🚧",
        )

    # Progress bar + phase metadata (only shown if provided)
    if phase or target_quarter or progress_pct:
        with st.container(border=True):
            cols = st.columns([2, 1, 1])
            if phase:
                cols[0].markdown(f"**Phase**  \n{phase}")
            if target_quarter:
                cols[1].markdown(f"**Target**  \n{target_quarter}")
            cols[2].markdown(f"**Progress**  \n`{progress_pct}%`")
            st.progress(progress_pct / 100)

    # Planned features
    st.markdown("#### Planned Features")
    for name, detail in features:
        st.markdown(f"- **{name}** — {detail}")

    st.markdown("---")
    st.caption("See the Guide page for the full feature roadmap and progress.")
