"""
Financial Workbench — Main entry point.
Run with: streamlit run app.py
"""

import streamlit as st
from pathlib import Path
from config.settings import APP_NAME, APP_ICON, ROOT_DIR
from lib.logger import setup_logging

setup_logging()

st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load custom CSS
css_path = ROOT_DIR / "assets" / "styles" / "custom.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

st.title(f"{APP_ICON} {APP_NAME}")
st.caption("Your personal financial analysis workbench")

st.markdown("---")

st.markdown("""
### Getting Started

Use the **sidebar** to navigate between pages:

- **Company Overview** — Search any publicly traded company and see key metrics, price charts, and financials

More pages coming soon.
""")
