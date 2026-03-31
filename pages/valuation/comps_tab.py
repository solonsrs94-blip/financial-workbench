"""Comps tab — peer multiples, operating metrics, implied prices."""

import streamlit as st


def render(prepared: dict, ticker: str) -> None:
    ctype = prepared.get("company_type", {}).get("type", "normal")
    st.subheader("Comparable Companies")
    st.info(
        f"Comps tab — under construction. "
        f"Company classified as **{ctype}**. "
        f"Trading comps with peer selection and football field."
    )
