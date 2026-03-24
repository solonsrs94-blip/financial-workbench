"""About tab — company description, website, employees."""

import streamlit as st
from models.company import Company


def render(company: Company) -> None:
    if company.info.description:
        st.write(company.info.description)

    col1, col2, col3 = st.columns(3)
    with col1:
        if company.info.website:
            st.markdown(f"[{company.info.website}]({company.info.website})")
    with col2:
        if company.info.employees:
            st.metric("Employees", f"{company.info.employees:,}")
    with col3:
        st.metric("Currency", company.info.currency)
