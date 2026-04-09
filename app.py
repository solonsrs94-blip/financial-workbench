"""
Financial Workbench — Main entry point.
Run with: streamlit run app.py
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

# ── Authenticated landing page ───────────────────────────────
from components.auth_guard import show_user_sidebar
show_user_sidebar()

st.title(f"{APP_ICON} {APP_NAME}")
st.caption("Your personal financial analysis workbench")

st.markdown("---")

st.markdown("""
### Getting Started

Use the **sidebar** to navigate between pages:

**Live now:**
- **Company Overview** — Search any company, see key metrics, price charts, and financials
- **Saved Valuations** — Browse and load your previously saved analyses
- **Valuation** — Full valuation workbench (DCF, Comps, Historical Multiples, DDM, Summary)

**Coming soon:**
- **Technical Charts** — Candlestick charts with indicators and drawing tools
- **Stock Screener** — Filter the market by any financial metric
- **Watchlists** — Track companies and set price alerts
- **Portfolio & Risk** — Holdings, returns, VaR, stress tests, backtesting
- **Macro Overview** — Interest rates, inflation, economic calendar
- **AI Assistant** — Chat with your data, sandbox experiments, AI reports
- **Academy** — Learning paths, exercises, and AI tutor
""")
