"""
Valuation — multi-method valuation workbench.

Flow:
1. Ticker input
2. Financial Preparation (standardization, flagging, classification)
3. Valuation tabs: DCF | Comps | DDM | Historical | Summary
   All tabs share prepared_data from step 2.
"""

import streamlit as st

from components.ticker_search import render_ticker_search, is_force_refresh
from components.layout import page_header, data_status_banner, load_css
from lib.data.fundamentals import get_company, get_financials
from lib.data.valuation_data import get_risk_free_rate, get_valuation_data
from config.constants import SESSION_CACHE_PREFIXES

from pages.valuation import (
    preparation, dcf_tab, comps_tab, ddm_tab, historical_tab, summary_tab,
)

from components.auth_guard import require_auth, show_user_sidebar
from lib.storage.autosave import (
    write_autosave, read_autosave, delete_autosave,
    autosave_age_seconds, format_age,
)
from lib.exports.session_restorer import restore_valuation_state

load_css()
require_auth()
show_user_sidebar()

page_header("Valuation", "Multi-method valuation workbench")

# --- Ticker Search (URL persistence) ---
params = st.query_params
saved_ticker = params.get("ticker", "").upper()
ticker = render_ticker_search(default=saved_ticker)

if not ticker:
    st.stop()

ticker = ticker.upper()
if ticker != saved_ticker:
    st.query_params["ticker"] = ticker

force_refresh = is_force_refresh()

# Detect loaded-from-save: skip cache clearing, use pre-loaded state
# Use get() not pop() to survive reruns; clear guard keys only after success
_loaded = st.session_state.get("_loaded_ticker")
if _loaded and _loaded == ticker:
    force_refresh = False
    st.session_state["_val_cached_ticker"] = ticker
    st.session_state.pop("_loaded_ticker", None)
    st.session_state.pop("_loaded_from_save", None)

# --- Auto-restore prompt (once per ticker per session) ---
_autosave_flag = f"_autosave_checked_{ticker}"
if (
    not st.session_state.get(_autosave_flag)
    and not st.session_state.get("_loaded_from_save")
    and st.session_state.get("_val_cached_ticker") != ticker
):
    _age = autosave_age_seconds(ticker)
    if _age is not None:
        _payload = read_autosave(ticker)
        if _payload:
            st.info(
                f"💾 Previous session found for **{ticker}** "
                f"(saved {format_age(_age)}). Restore your work?"
            )
            _c1, _c2, _c3 = st.columns([1, 1, 6])
            with _c1:
                if st.button("Restore", key=f"_autosave_restore_{ticker}"):
                    _state, _t = restore_valuation_state(_payload)
                    for _k, _v in _state.items():
                        st.session_state[_k] = _v
                    st.session_state[_autosave_flag] = True
                    st.rerun()
            with _c2:
                if st.button("Discard", key=f"_autosave_discard_{ticker}"):
                    delete_autosave(ticker)
                    st.session_state[_autosave_flag] = True
                    st.rerun()
            st.stop()
    st.session_state[_autosave_flag] = True

# Clear session cache on ticker change
if force_refresh or st.session_state.get("_val_cached_ticker") != ticker:
    for key in list(st.session_state.keys()):
        if key.startswith(SESSION_CACHE_PREFIXES):
            del st.session_state[key]
    # Also clear prepared data
    for key in list(st.session_state.keys()):
        if key.startswith("prepared_data"):
            del st.session_state[key]
    # Reset fetch-status tracker so warnings don't leak across tickers
    from components.fetch_warnings import clear_fetch_status
    clear_fetch_status()
    st.session_state["_val_cached_ticker"] = ticker

# --- Load Company Data ---
company_key = f"company_{ticker}"
if company_key not in st.session_state:
    with st.spinner(f"Loading {ticker}..."):
        st.session_state[company_key], st.session_state[f"company_status_{ticker}"] = (
            get_company(ticker, force_refresh)
        )

company = st.session_state[company_key]
status = st.session_state.get(f"company_status_{ticker}", "fresh")

data_status_banner(status)

if company is None:
    st.error(f"Could not find data for '{ticker}'.")
    st.stop()

# --- Load Valuation Data (risk-free rate, etc.) ---
vd_key = f"val_data_{ticker}"
if vd_key not in st.session_state:
    with st.spinner("Loading valuation data..."):
        st.session_state[vd_key], _ = get_valuation_data(ticker, force_refresh)

rf_key = "val_risk_free_rate"
if rf_key not in st.session_state:
    st.session_state[rf_key] = get_risk_free_rate()

# === FINANCIAL PREPARATION ===
# Runs BEFORE tabs. Results stored in session_state["prepared_data"].
preparation.render_preparation(ticker, company)

# === VALUATION TABS ===
# Only show if preparation completed successfully.
prepared = st.session_state.get("prepared_data")
if prepared and not prepared.get("error"):
    st.divider()
    st.markdown("## Valuation")

    tab_dcf, tab_comps, tab_ddm, tab_hist, tab_summary = st.tabs(
        ["DCF", "Comps", "DDM", "Historical", "Summary"]
    )

    with tab_dcf:
        dcf_tab.render(prepared, ticker)

    with tab_comps:
        comps_tab.render(prepared, ticker)

    with tab_ddm:
        ddm_tab.render(prepared, ticker)

    with tab_hist:
        historical_tab.render(prepared, ticker)

    with tab_summary:
        summary_tab.render(prepared, ticker)

# --- Auto-save on every rerun (safety net against session loss) ---
if ticker and st.session_state.get("prepared_data"):
    write_autosave(dict(st.session_state), ticker)
