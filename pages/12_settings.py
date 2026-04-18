"""Settings — tier toggle works; other settings coming soon."""

import streamlit as st

from components.layout import load_css
from components.auth_guard import require_auth, show_user_sidebar
from components.tier_badge import render_tier_badge
from components.tier_guard import get_user_tier


load_css()
require_auth()
show_user_sidebar()


st.title("⚙ Settings")
st.caption("Manage your profile, data sources, tier, and preferences")

# ── Tier toggle (working) ────────────────────────────────────
st.markdown("---")
st.subheader("Tier")

st.markdown("Current tier:")
render_tier_badge()

st.markdown(
    """
**Personal tier** — Full analytical toolkit for individual investors.
DCF, Comps, DDM, Historical Multiples, Screener, Watchlist, Portfolio,
Macro, Journal, AI assistant, Academy.

**Professional tier** — Adds deal-oriented tools: LBO modeling,
M&A accretion/dilution, SOTP mode, M&A precedents database,
pitch-book output, industry overlays.
"""
)

current = get_user_tier()
selected = st.radio(
    "Switch tier",
    options=["personal", "professional"],
    index=0 if current == "personal" else 1,
    format_func=lambda t: "Personal" if t == "personal" else "Professional",
    horizontal=True,
    key="_settings_tier_radio",
)

if selected != current:
    st.session_state["user_tier"] = selected
    st.success(
        f"Tier switched to **{selected.title()}**. "
        "Reload the page to see navigation update."
    )
    if st.button("Reload now"):
        st.rerun()

# ── Other settings (placeholder) ──────────────────────────────
st.markdown("---")
st.subheader("Other settings")

st.info(
    "Full settings UI is under development. For now, only the tier "
    "toggle above is functional.",
    icon="🚧",
)

st.markdown(
    """
**Coming soon:**

- **Profile** — Name, email, timezone, display preferences
- **Data sources** — API key management (FRED, Anthropic, SimFin, FMP, Finnhub)
- **Preferences** — Default currency, default scenario count, UI theme (dark mode)
- **Feature flags** — Toggle experimental features
- **Data export** — Full user data export (portfolios, watchlists, journal, saved valuations)
- **Account management** — Change password, delete account
"""
)
