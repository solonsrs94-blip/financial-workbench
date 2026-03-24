"""
Company Overview — the first screen users see after searching.
Shows key info, price chart, metrics, and basic financials.
"""

import streamlit as st

from components.ticker_search import render_ticker_search, is_force_refresh
from components.layout import (
    page_header, data_status_banner,
    format_large_number, format_percentage, format_ratio,
)
from components.charts import price_chart, volume_chart
from lib.data.fundamentals import get_company
from lib.data.market import get_price_history


page_header("Company Overview", "Search for any publicly traded company")

# --- Ticker Search ---
ticker = render_ticker_search()

if not ticker:
    st.info("Enter a ticker symbol above to get started.")
    st.stop()

# --- Load Data ---
force_refresh = is_force_refresh()

with st.spinner(f"Loading {ticker}..."):
    company, status = get_company(ticker, force_refresh=force_refresh)
    price_df, price_status = get_price_history(ticker, force_refresh=force_refresh)

# --- Status Banner ---
data_status_banner(status)

if company is None:
    st.error(f"Could not find data for '{ticker}'. Check the ticker and try again.")
    st.stop()

# --- Company Header ---
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    st.subheader(f"{company.name} ({company.ticker})")
    if company.info.sector:
        st.caption(f"{company.info.sector} · {company.info.industry} · {company.info.country}")

with col2:
    if company.price.price is not None:
        st.metric(
            "Price",
            f"${company.price.price:.2f}",
            delta=f"{company.price.change_pct:.2f}%" if company.price.change_pct else None,
        )

with col3:
    st.metric("Market Cap", format_large_number(company.price.market_cap))

st.divider()

# --- Price Chart ---
period = st.selectbox(
    "Period",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
    index=5,
    key="price_period",
    label_visibility="collapsed",
)

# Reload if period changed
if period != "5y" or force_refresh:
    price_df, price_status = get_price_history(ticker, period=period, force_refresh=force_refresh)

price_chart(price_df, title=f"{company.name} — Price History")
volume_chart(price_df)

st.divider()

# --- Key Metrics ---
st.subheader("Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("P/E (TTM)", format_ratio(company.ratios.pe_trailing))
    st.metric("P/E (Forward)", format_ratio(company.ratios.pe_forward))
    st.metric("PEG Ratio", format_ratio(company.ratios.peg))

with col2:
    st.metric("P/B", format_ratio(company.ratios.pb))
    st.metric("P/S", format_ratio(company.ratios.ps))
    st.metric("EV/EBITDA", format_ratio(company.ratios.ev_ebitda))

with col3:
    st.metric("Profit Margin", format_percentage(company.ratios.profit_margin))
    st.metric("Operating Margin", format_percentage(company.ratios.operating_margin))
    st.metric("ROE", format_percentage(company.ratios.roe))

with col4:
    st.metric("Dividend Yield", format_percentage(company.ratios.dividend_yield))
    st.metric("D/E Ratio", format_ratio(company.ratios.debt_to_equity))
    st.metric("Beta", format_ratio(company.price.beta))

st.divider()

# --- Company Description ---
if company.info.description:
    with st.expander("About", expanded=False):
        st.write(company.info.description)

# --- Quick Stats ---
st.subheader("Quick Stats")
col1, col2 = st.columns(2)

with col1:
    st.metric("52-Week High", f"${company.price.high_52w:.2f}" if company.price.high_52w else "N/A")
    st.metric("52-Week Low", f"${company.price.low_52w:.2f}" if company.price.low_52w else "N/A")
    st.metric("EPS (TTM)", f"${company.ratios.eps_trailing:.2f}" if company.ratios.eps_trailing else "N/A")

with col2:
    st.metric("Avg Volume", f"{company.price.avg_volume:,.0f}" if company.price.avg_volume else "N/A")
    st.metric("Revenue Growth", format_percentage(company.ratios.revenue_growth))
    st.metric("Earnings Growth", format_percentage(company.ratios.earnings_growth))
