"""DDM tab — Dividend Discount Model (Gordon Growth + 2-stage)."""

import streamlit as st
from models.company import Company


def render(company: Company, ticker: str) -> None:
    st.subheader("Dividend Discount Model")
    st.info("DDM tab — under construction. Gordon Growth and 2-stage DDM for dividend-paying stocks.")
