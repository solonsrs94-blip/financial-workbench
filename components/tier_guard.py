"""Tier guard helpers for personal vs professional tier gating.

Single source of truth for tier enforcement. Never use ad-hoc if-checks
against session_state["user_tier"] — always go through these helpers.
"""

import streamlit as st


def get_user_tier() -> str:
    """Return current user tier. Defaults to 'personal' if unset."""
    return st.session_state.get("user_tier", "personal")


def is_professional() -> bool:
    """True if current user is on professional tier."""
    return get_user_tier() == "professional"


def require_professional() -> None:
    """Guard for professional-only pages/features.

    If user is on personal tier, renders an upgrade placeholder and halts
    page execution via st.stop(). Safe to call inside a page render flow.
    """
    if is_professional():
        return

    from components.layout import load_css
    from components.auth_guard import require_auth, show_user_sidebar

    load_css()
    require_auth()
    show_user_sidebar()

    st.title("🏦 Professional Tier Feature")
    st.caption("This feature is available in the Professional tier")

    st.info(
        "This module provides deal-oriented tools (LBO, M&A, precedents) "
        "that complement the Personal tier's valuation suite. "
        "Switch to Professional tier in Settings to access.",
        icon="🔒",
    )

    st.markdown("#### Professional Tier Includes")
    st.markdown("""
    - **LBO Modeling** — debt schedules, IRR/MOIC, exit scenarios
    - **M&A Analysis** — accretion/dilution, synergies, pro-forma
    - **M&A Precedents** — transaction comparables database
    - **Pitch-book output** — Excel with live formulas, PDF deck
    - **Collaboration** — share models with teammates
    - **Industry overlays** — SaaS metrics, bank NIM, E&P reserves
    """)

    st.markdown("---")
    st.caption("Go to **Settings → Tier** to switch tiers.")
    st.stop()
