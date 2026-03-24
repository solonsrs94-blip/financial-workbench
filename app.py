"""
Financial Workbench — Main entry point.
Run with: streamlit run app.py
"""

import streamlit as st
from config.settings import APP_NAME, APP_ICON

st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
)

st.title(f"{APP_ICON} {APP_NAME}")
st.caption("Your personal financial analysis workbench")

st.markdown("---")

st.markdown("""
### Getting Started

Use the **sidebar** to navigate between pages:

- **Company Overview** — Search any publicly traded company and see key metrics, price charts, and financials

More pages coming soon.
""")
