"""DDM tab — Dividend Discount Model (Gordon Growth + 2-stage)."""

import streamlit as st


def render(prepared: dict, ticker: str) -> None:
    ctype = prepared.get("company_type", {}).get("type", "normal")
    methods = prepared.get("company_type", {}).get("recommended_methods", [])

    st.subheader("Dividend Discount Model")

    if ctype in ("financial", "dividend_stable"):
        st.success(
            f"**DDM is the recommended method** for this company "
            f"({ctype.replace('_', ' ')}). Under construction."
        )
    else:
        st.info(
            "DDM is not the primary method for this company. "
            "Under construction — Gordon Growth and 2-stage DDM "
            "for dividend-paying stocks."
        )
