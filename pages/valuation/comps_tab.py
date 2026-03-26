"""Comps tab — peer multiples, operating metrics, implied prices."""

import streamlit as st
from models.company import Company
from typing import Optional


def render(company: Company, fin_data: Optional[dict], ticker: str) -> None:
    st.subheader("Comparable Companies")
    st.info("Comps tab — under construction. Trading comps with peer selection and football field.")
