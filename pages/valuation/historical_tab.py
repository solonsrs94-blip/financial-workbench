"""Historical tab — historical multiples over time (P/E, EV/EBITDA, P/B)."""

import streamlit as st
from models.company import Company


def render(company: Company, ticker: str) -> None:
    st.subheader("Historical Multiples")
    st.info("Historical tab — under construction. P/E, EV/EBITDA, P/B trends over 3-5 years.")
