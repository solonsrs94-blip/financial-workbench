"""
Company Overview — the main browsing hub.
Search, explore, and get a comprehensive overview before diving deeper.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from components.ticker_search import render_ticker_search, is_force_refresh
from components.layout import (
    page_header, data_status_banner,
    format_large_number, format_percentage, format_ratio,
    format_volume, format_price,
)
from components.charts import price_chart, volume_chart
from lib.data.fundamentals import get_company
from lib.data.market import get_price_history
from lib.data.providers import yahoo


page_header("Company Overview", "Search for any publicly traded company")

# --- Ticker Search ---
ticker = render_ticker_search()

if not ticker:
    st.stop()

# --- Load Data ---
force_refresh = is_force_refresh()

with st.spinner(f"Loading {ticker}..."):
    company, status = get_company(ticker, force_refresh=force_refresh)

data_status_banner(status)

if company is None:
    st.error(f"Could not find data for '{ticker}'. Check the ticker and try again.")
    st.stop()

# === HEADER ===
col_name, col_price, col_cap = st.columns([3, 1, 1])

with col_name:
    st.subheader(f"{company.name} ({company.ticker})")
    if company.info.sector:
        st.caption(
            f"{company.info.sector} · {company.info.industry} · "
            f"{company.info.exchange} · {company.info.country}"
        )

with col_price:
    if company.price.price is not None:
        st.metric(
            "Price",
            f"${company.price.price:.2f}",
            delta=f"{company.price.change_pct:.2f}%" if company.price.change_pct else None,
        )

with col_cap:
    st.metric("Market Cap", format_large_number(company.price.market_cap))

# === CHART ===
col_period, col_interval = st.columns([2, 1])

with col_period:
    period = st.segmented_control(
        "Period",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
        default="5y",
        key="price_period",
        label_visibility="collapsed",
    )

with col_interval:
    interval = st.segmented_control(
        "Interval",
        ["Daily", "Weekly", "Monthly"],
        default="Daily",
        key="price_interval",
        label_visibility="collapsed",
    )

interval_map = {"Daily": "1d", "Weekly": "1wk", "Monthly": "1mo"}
yf_interval = interval_map.get(interval, "1d")

price_df, price_status = get_price_history(
    ticker, period=period, interval=yf_interval, force_refresh=force_refresh,
)

price_chart(price_df, title="")
volume_chart(price_df)

# === KEY METRICS ===
st.divider()

col1, col2, col3, col4 = st.columns(4)
col1.metric("P/E (TTM)", format_ratio(company.ratios.pe_trailing))
col2.metric("EV/EBITDA", format_ratio(company.ratios.ev_ebitda))
col3.metric("Profit Margin", format_percentage(company.ratios.profit_margin))
col4.metric("ROE", format_percentage(company.ratios.roe))

col1, col2, col3, col4 = st.columns(4)
col1.metric("P/B", format_ratio(company.ratios.pb))
col2.metric("D/E", format_ratio(company.ratios.debt_to_equity))
col3.metric("Div Yield", format_percentage(company.ratios.dividend_yield))
col4.metric("Beta", format_ratio(company.price.beta))

st.divider()

# === TABS ===
tab_detail, tab_financials, tab_ownership, tab_peers, tab_analysts, tab_news, tab_about = st.tabs(
    ["Detail", "Financials", "Ownership", "Peers", "Analysts", "News", "About"]
)

# --- Detail Tab ---
with tab_detail:
    st.markdown("**Valuation**")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("P/E (Fwd)", format_ratio(company.ratios.pe_forward))
    col2.metric("PEG", format_ratio(company.ratios.peg))
    col3.metric("P/S", format_ratio(company.ratios.ps))
    col4.metric("EV/Revenue", format_ratio(company.ratios.ev_revenue))

    st.markdown("**Earnings**")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("EPS (TTM)", format_price(company.ratios.eps_trailing))
    col2.metric("EPS (Fwd)", format_price(company.ratios.eps_forward))
    col3.metric("Rev Growth", format_percentage(company.ratios.revenue_growth))
    col4.metric("Earn Growth", format_percentage(company.ratios.earnings_growth))

    st.markdown("**Margins & Returns**")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Gross Margin", format_percentage(company.ratios.gross_margin))
    col2.metric("Op. Margin", format_percentage(company.ratios.operating_margin))
    col3.metric("ROA", format_percentage(company.ratios.roa))
    col4.metric("Payout Ratio", format_percentage(company.ratios.payout_ratio))

    st.markdown("**Trading**")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("52W High", format_price(company.price.high_52w))
    col2.metric("52W Low", format_price(company.price.low_52w))
    col3.metric("Volume", format_volume(company.price.volume))
    col4.metric("Avg Volume", format_volume(company.price.avg_volume))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Ratio", format_ratio(company.ratios.current_ratio))
    col2.metric("Quick Ratio", format_ratio(company.ratios.quick_ratio))
    col3.metric("", "")
    col4.metric("", "")

# --- Financials Tab ---
with tab_financials:
    with st.spinner("Loading financials..."):
        fin_data = yahoo.fetch_financials(ticker)

    if fin_data is None:
        st.info("Financial data not available.")
    else:
        fin_type = st.segmented_control(
            "Statement",
            ["Income", "Balance Sheet", "Cash Flow"],
            default="Income",
            key="fin_type",
            label_visibility="collapsed",
        )

        stmt_map = {
            "Income": fin_data.get("income_statement"),
            "Balance Sheet": fin_data.get("balance_sheet"),
            "Cash Flow": fin_data.get("cash_flow"),
        }

        df = stmt_map.get(fin_type)
        if df is not None and not df.empty:
            # Format column headers as years
            df.columns = [c.strftime("%Y") if hasattr(c, "strftime") else str(c) for c in df.columns]

            # Format large numbers
            display_df = df.map(
                lambda x: f"{x / 1e9:.2f}B" if isinstance(x, (int, float)) and abs(x) >= 1e9
                else f"{x / 1e6:.1f}M" if isinstance(x, (int, float)) and abs(x) >= 1e6
                else f"{x:,.0f}" if isinstance(x, (int, float))
                else x
            )
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info(f"No {fin_type.lower()} data available.")

# --- Ownership Tab ---
with tab_ownership:
    with st.spinner("Loading ownership data..."):
        holders = yahoo.fetch_holders(ticker)

    if holders is None:
        st.info("Ownership data not available.")
    else:
        if holders.get("institutional") is not None:
            st.markdown("**Top Institutional Holders**")
            inst = holders["institutional"].head(10).copy()
            if "pctHeld" in inst.columns:
                inst["pctHeld"] = inst["pctHeld"].apply(lambda x: f"{x*100:.2f}%" if pd.notna(x) else "N/A")
            if "Value" in inst.columns:
                inst["Value"] = inst["Value"].apply(lambda x: f"${x/1e9:.1f}B" if pd.notna(x) and x >= 1e9 else f"${x/1e6:.0f}M" if pd.notna(x) else "N/A")
            st.dataframe(inst, use_container_width=True, hide_index=True)

        if holders.get("insider_transactions") is not None:
            st.markdown("**Recent Insider Transactions**")
            insider = holders["insider_transactions"].head(10)
            st.dataframe(insider, use_container_width=True, hide_index=True)

# --- Peers Tab ---
with tab_peers:
    st.info("Peer comparison coming soon — will show how this company compares to others in its sector.")

# --- Analysts Tab ---
with tab_analysts:
    with st.spinner("Loading analyst data..."):
        recs = yahoo.fetch_recommendations(ticker)

    if recs is None:
        st.info("Analyst data not available.")
    else:
        # Current consensus
        if len(recs) > 0:
            current = recs.iloc[0]
            st.markdown("**Current Analyst Consensus**")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Strong Buy", int(current.get("strongBuy", 0)))
            col2.metric("Buy", int(current.get("buy", 0)))
            col3.metric("Hold", int(current.get("hold", 0)))
            col4.metric("Sell", int(current.get("sell", 0)))
            col5.metric("Strong Sell", int(current.get("strongSell", 0)))

            # Trend over months
            if len(recs) > 1:
                st.markdown("**Recommendation Trend**")
                st.dataframe(recs.head(6), use_container_width=True, hide_index=True)

# --- News Tab ---
with tab_news:
    with st.spinner("Loading news..."):
        news = yahoo.fetch_news(ticker)

    if not news:
        st.info("No recent news available.")
    else:
        for article in news:
            title = article.get("title", "")
            publisher = article.get("publisher", "")
            link = article.get("link", "")
            published = article.get("published", "")

            if title and link:
                st.markdown(f"**[{title}]({link})**")
                st.caption(f"{publisher} · {published[:10] if published else ''}")
                st.markdown("---")

# --- About Tab ---
with tab_about:
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
