"""
Financial Workbench — Main entry point.
Run with: streamlit run app.py

Handles auth, session state initialization, and tier-aware navigation.
After auth + approval, delegates to st.navigation() which runs the
selected page module.
"""

import streamlit as st

from config.settings import APP_NAME, APP_ICON, get_firebase_service_account
from components.layout import load_css
from lib.logger import setup_logging

setup_logging()

st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()

# ── Firebase init (once per session) ─────────────────────────
sa = get_firebase_service_account()
if sa and not st.session_state.get("_firebase_initialized"):
    from lib.auth.firebase_init import init_firebase
    init_firebase(sa)
    st.session_state["_firebase_initialized"] = True

# ── Auth check ───────────────────────────────────────────────
uid = st.session_state.get("auth_uid")

if not uid:
    with st.sidebar:
        st.caption(f"{APP_ICON} {APP_NAME}")
    st.title(f"{APP_ICON} {APP_NAME}")
    st.caption("Your personal financial analysis workbench")
    st.markdown("---")
    from components.auth_forms import render_auth_page
    render_auth_page()
    st.stop()

# ── Approval check ───────────────────────────────────────────
if not st.session_state.get("auth_approved"):
    from lib.auth.firebase_auth import check_user_approved
    if check_user_approved(uid):
        st.session_state["auth_approved"] = True
    else:
        st.title(f"{APP_ICON} {APP_NAME}")
        st.info(
            "Your account is pending admin approval. "
            "Please check back later."
        )
        from components.auth_guard import show_user_sidebar
        show_user_sidebar()
        st.stop()

# ── Session state init (post-auth, once per session) ─────────
# Tier flag — controls which features/pages are accessible.
# Default "personal"; toggled via Settings → Tier tab.
if "user_tier" not in st.session_state:
    st.session_state["user_tier"] = "personal"

# Feature flags — experimental/in-development features.
# Empty by default; toggled via Settings → Feature Flags.
if "feature_flags" not in st.session_state:
    st.session_state["feature_flags"] = {}

# ── Navigation (tier-aware, grouped) ─────────────────────────
from components.tier_guard import is_professional

research_pages = [
    st.Page("pages/0_guide.py",     title="Guide",      icon="📖", default=True),
    st.Page("pages/1_company.py",   title="Company",    icon="🏢"),
    st.Page("pages/3_valuation.py", title="Valuation",  icon="💰"),
    st.Page("pages/4_charts.py",    title="Charts",     icon="📈"),
    st.Page("pages/5_screener.py",  title="Screener",   icon="🔍"),
]

portfolio_pages = [
    st.Page("pages/6_watchlist.py", title="Watchlist",  icon="👁"),
    st.Page("pages/7_portfolio.py", title="Portfolio",  icon="📊"),
    st.Page("pages/2_saved.py",     title="Saved",      icon="💾"),
]

context_pages = [
    st.Page("pages/8_macro.py",       title="Macro",      icon="🌍"),
    st.Page("pages/13_calendars.py",  title="Calendars",  icon="📅"),
    st.Page("pages/14_news.py",       title="News",       icon="📰"),
]

tools_pages = [
    st.Page("pages/11_journal.py",    title="Journal",    icon="📝"),
    st.Page("pages/9_ai.py",          title="AI",         icon="🤖"),
    st.Page("pages/10_academy.py",    title="Academy",    icon="🎓"),
    st.Page("pages/12_settings.py",   title="Settings",   icon="⚙"),
]

nav_dict = {
    "Research":  research_pages,
    "Portfolio": portfolio_pages,
    "Context":   context_pages,
    "Tools":     tools_pages,
}

# Professional tier — group only appears when user_tier == "professional".
# Individual pages still exist regardless; they show an upgrade placeholder
# when navigated to by a personal-tier user.
if is_professional():
    nav_dict["Professional"] = [
        st.Page("pages/20_lbo.py",         title="LBO",         icon="🏦"),
        st.Page("pages/21_ma.py",          title="M&A",         icon="🤝"),
        st.Page("pages/22_precedents.py",  title="Precedents",  icon="📋"),
    ]

pg = st.navigation(nav_dict)
pg.run()
