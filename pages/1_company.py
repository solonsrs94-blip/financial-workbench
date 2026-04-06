"""
Company Overview — the main browsing hub.
Search, explore, and get a comprehensive overview before diving deeper.
"""

import streamlit as st
import pandas as pd
from datetime import timedelta

from components.ticker_search import render_ticker_search, is_force_refresh
from components.layout import page_header, data_status_banner, load_css
from components.charts import price_chart, volume_chart
from lib.data.fundamentals import get_company, get_events
from lib.data.market import get_price_history
from config.constants import PERIOD_DAYS, SESSION_CACHE_PREFIXES

# Tab modules
from pages.company import detail_tab, financials_tab, ownership_tab
from pages.company import peers_tab, analysts_tab, news_tab, about_tab
from pages.company.header import render_header, render_key_metrics, calc_peer_medians

from components.auth_guard import require_auth, show_user_sidebar

load_css()
require_auth()
show_user_sidebar()

page_header("Company Overview", "Search for any publicly traded company")

# --- Ticker Search (with URL persistence) ---
params = st.query_params
saved_ticker = params.get("ticker", "").upper()

ticker = render_ticker_search(default=saved_ticker)

if not ticker:
    st.stop()

ticker = ticker.upper()

if ticker != saved_ticker:
    st.query_params["ticker"] = ticker

# --- Load Data ---
force_refresh = is_force_refresh()

# Clear session cache on force refresh or ticker change
if force_refresh or st.session_state.get("_cached_ticker") != ticker:
    for key in list(st.session_state.keys()):
        if key.startswith(SESSION_CACHE_PREFIXES):
            del st.session_state[key]
    st.session_state["_cached_ticker"] = ticker

# Cache company data in session_state
company_key = f"company_{ticker}"
if company_key not in st.session_state:
    with st.spinner(f"Loading {ticker}..."):
        st.session_state[company_key], st.session_state[f"company_status_{ticker}"] = get_company(ticker, force_refresh=force_refresh)

company = st.session_state[company_key]
status = st.session_state.get(f"company_status_{ticker}", "fresh")

data_status_banner(status)

if company is None:
    st.error(f"Could not find data for '{ticker}'. Check the ticker and try again.")
    st.stop()

# === HEADER ===
render_header(company)

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

# Fetch extra data for SMA warmup
sma_extended = {"1mo": "6mo", "3mo": "1y", "6mo": "2y", "1y": "5y", "2y": "5y", "5y": "max", "max": "max"}
fetch_period = sma_extended.get(period, period)

# Cache price data per period+interval combo
price_cache_key = f"price_{ticker}_{fetch_period}_{yf_interval}"
if price_cache_key not in st.session_state:
    st.session_state[price_cache_key], _ = get_price_history(
        ticker, period=fetch_period, interval=yf_interval, force_refresh=force_refresh,
    )
price_df = st.session_state[price_cache_key]

# Cache events
events_key = f"events_{ticker}"
if events_key not in st.session_state:
    st.session_state[events_key], _ = get_events(ticker)
chart_events = st.session_state[events_key]

price_chart(price_df, title="", events=chart_events, interval=yf_interval, visible_period=period)

# Volume — trimmed to visible period
if period in PERIOD_DAYS and price_df is not None and not price_df.empty:
    cutoff = pd.Timestamp.now() - timedelta(days=PERIOD_DAYS[period])
    vol_idx = pd.to_datetime(price_df.index)
    volume_df = price_df[vol_idx >= cutoff]
else:
    volume_df = price_df
volume_chart(volume_df)

# === KEY METRICS ===
_peer_med_key = f"peer_medians_{ticker}"
if _peer_med_key not in st.session_state:
    st.session_state[_peer_med_key] = calc_peer_medians(
        company.info.sector or "", company.info.industry or "", ticker
    )

render_key_metrics(company, st.session_state[_peer_med_key])

# === TABS ===
tab_detail, tab_financials, tab_ownership, tab_peers, tab_analysts, tab_news, tab_about = st.tabs(
    ["Detail", "Financials", "Ownership", "Peers", "Analysts", "News", "About"]
)

with tab_detail:
    detail_tab.render(company, ticker)

with tab_financials:
    financials_tab.render(ticker)

with tab_ownership:
    ownership_tab.render(ticker)

with tab_peers:
    peers_tab.render(company)

with tab_analysts:
    analysts_tab.render(ticker)

with tab_news:
    news_tab.render(ticker)

with tab_about:
    about_tab.render(company)
