"""Summary tab — football field, all results combined, workspace."""

import streamlit as st
from models.company import Company


def render(company: Company, ticker: str) -> None:
    st.subheader("Valuation Summary")
    st.info("Summary tab — under construction. Football field chart combining all methods + workspace.")
