"""Saved Valuations — browse, load, and manage saved analyses."""

import json
from collections import defaultdict

import streamlit as st

from components.layout import page_header, load_css
from components.auth_guard import require_auth, show_user_sidebar
from lib.storage.firestore_valuations import (
    list_valuations, load_valuation, delete_valuation,
)

load_css()
uid = require_auth()
show_user_sidebar()

page_header("Saved Valuations", "Browse and restore previous analyses")


def _load_entry(doc_id: str) -> None:
    """Load a saved valuation and switch to the valuation page."""
    from lib.exports.session_restorer import restore_valuation_state

    saved = load_valuation(uid, doc_id)
    state_dict, ticker = restore_valuation_state(saved)

    for k, v in state_dict.items():
        st.session_state[k] = v

    st.query_params["ticker"] = ticker
    st.session_state["ticker_input"] = ticker
    st.toast(f"Loaded {ticker} valuation")
    st.switch_page("pages/3_valuation.py")


def _render_delete(doc_id: str) -> None:
    """Render delete button with two-click confirmation."""
    confirm_key = f"_confirm_del_{doc_id}"

    if st.session_state.get(confirm_key):
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("Confirm", key=f"_yes_{doc_id}", type="primary"):
                delete_valuation(uid, doc_id)
                st.session_state.pop(confirm_key, None)
                st.toast("Deleted")
                st.rerun()
        with col_no:
            if st.button("Cancel", key=f"_no_{doc_id}"):
                st.session_state.pop(confirm_key, None)
                st.rerun()
    else:
        if st.button("Delete", key=f"_del_{doc_id}"):
            st.session_state[confirm_key] = True
            st.rerun()


def _format_date(iso_str: str) -> str:
    """Format ISO date string for display."""
    if not iso_str:
        return "\u2014"
    try:
        return iso_str[:16].replace("T", " ")
    except (TypeError, IndexError):
        return str(iso_str)


def _format_price(val) -> str:
    """Format a price value for display."""
    if val is None:
        return "\u2014"
    try:
        return f"${float(val):,.2f}"
    except (TypeError, ValueError):
        return "\u2014"


def _upside_pct(fair_value, share_price) -> str:
    """Calculate and format upside/downside percentage."""
    if not fair_value or not share_price:
        return ""
    try:
        pct = (float(fair_value) / float(share_price) - 1) * 100
        return f"({pct:+.1f}%)"
    except (TypeError, ValueError, ZeroDivisionError):
        return ""


# ── Main page ─────────────────────────────────────────────
valuations = list_valuations(uid)

if not valuations:
    st.info(
        "No saved valuations yet. Complete a valuation and click "
        "'Save Valuation' on the Summary tab."
    )
    st.stop()

# Group by ticker
grouped = defaultdict(list)
for v in valuations:
    grouped[v.get("ticker", "???")].append(v)

# Stats bar
n_companies = len(grouped)
n_valuations = len(valuations)
st.markdown(
    f"**{n_companies}** {'company' if n_companies == 1 else 'companies'}, "
    f"**{n_valuations}** saved "
    f"{'valuation' if n_valuations == 1 else 'valuations'}"
)

st.markdown("---")

# Render each ticker group
for ticker in sorted(grouped.keys()):
    entries = grouped[ticker]
    first = entries[0]
    company_name = first.get("company_name", ticker)
    st.markdown(
        f"### {ticker}" + (f" \u2014 {company_name}" if company_name else "")
    )

    for entry in entries:
        doc_id = entry.get("doc_id", "")
        models = entry.get("models_completed", [])
        fv = entry.get("weighted_fair_value")
        price = entry.get("share_price")
        save_date = _format_date(entry.get("save_date", ""))

        # Summary line
        parts = [f"**{save_date}**"]
        if models:
            parts.append(f"Models: {', '.join(models)}")
        if fv:
            upside = _upside_pct(fv, price)
            parts.append(f"Fair Value: {_format_price(fv)} {upside}")
        elif price:
            parts.append(f"Price: {_format_price(price)}")

        st.markdown(" \u00b7 ".join(parts))

        # Action buttons
        col_load, col_dl, col_del = st.columns([1, 1, 1])
        with col_load:
            if st.button("Load", key=f"load_{doc_id}", type="primary"):
                _load_entry(doc_id)
        with col_dl:
            try:
                full = load_valuation(uid, doc_id)
                raw_json = json.dumps(full, indent=2, default=str)
                st.download_button(
                    "Download JSON",
                    data=raw_json,
                    file_name=f"{ticker}_{doc_id[:8]}.json",
                    mime="application/json",
                    key=f"dl_{doc_id}",
                )
            except Exception:
                st.caption("Could not load")
        with col_del:
            _render_delete(doc_id)

        st.markdown("---")
