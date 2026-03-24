"""Peers tab — compare company to others in the same industry."""

import streamlit as st
import pandas as pd
from components.layout import format_large_number, format_ratio, format_percentage
from models.company import Company


def render(company: Company) -> None:
    if not company.info.industry:
        st.info("Industry data not available for peer comparison.")
        return

    with st.spinner("Finding peers..."):
        peers = _fetch_peers_cached(company.info.sector, company.info.industry, company.ticker)

    if not peers:
        st.info("Could not find peer companies.")
        return

    st.caption(f"Companies in **{company.info.industry}** ({company.info.sector})")
    st.caption("All values converted to USD")

    peer_rows = []
    for p in peers:
        peer_rows.append({
            "Company": f"{p.get('name', '')} ({p.get('ticker', '')})",
            "Price (USD)": f"${p.get('price', 0):,.2f}" if p.get("price") else "N/A",
            "Mkt Cap": format_large_number(p.get("market_cap")),
            "P/E": format_ratio(p.get("pe")),
            "P/B": format_ratio(p.get("pb")),
            "Margin": format_percentage(p.get("profit_margin")),
            "ROE": format_percentage(p.get("roe")),
            "Div Yield": format_percentage(p.get("div_yield")),
        })

    peer_df = pd.DataFrame(peer_rows)
    st.dataframe(peer_df, use_container_width=True, hide_index=True)


@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_peers_cached(sector: str, industry: str, exclude_ticker: str) -> list[dict]:
    from lib.analysis.peers import fetch_peers
    return fetch_peers(sector, industry, exclude_ticker)
