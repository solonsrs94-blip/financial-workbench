"""Analysts tab — consensus ratings and recommendation trend."""

import streamlit as st
from lib.data.providers import yahoo


def render(ticker: str) -> None:
    with st.spinner("Loading analyst data..."):
        recs = yahoo.fetch_recommendations(ticker)

    if recs is None:
        st.info("Analyst data not available.")
        return

    if len(recs) == 0:
        st.info("No analyst recommendations available.")
        return

    current = recs.iloc[0]
    sb = int(current.get("strongBuy", 0))
    b = int(current.get("buy", 0))
    h = int(current.get("hold", 0))
    s = int(current.get("sell", 0))
    ss = int(current.get("strongSell", 0))
    total = sb + b + h + s + ss

    # Visual consensus bar
    if total > 0:
        sb_pct = sb / total * 100
        b_pct = b / total * 100
        h_pct = h / total * 100
        s_pct = s / total * 100
        ss_pct = ss / total * 100

        st.markdown("**Analyst Consensus**")
        st.markdown(f"""
        <div style="display: flex; height: 32px; border-radius: 6px; overflow: hidden; margin: 10px 0;">
            <div style="width: {sb_pct}%; background: #0d6e3f; display: flex; align-items: center; justify-content: center; color: white; font-size: 12px; font-weight: bold;">{sb if sb else ''}</div>
            <div style="width: {b_pct}%; background: #2ca02c; display: flex; align-items: center; justify-content: center; color: white; font-size: 12px; font-weight: bold;">{b if b else ''}</div>
            <div style="width: {h_pct}%; background: #ff7f0e; display: flex; align-items: center; justify-content: center; color: white; font-size: 12px; font-weight: bold;">{h if h else ''}</div>
            <div style="width: {s_pct}%; background: #d62728; display: flex; align-items: center; justify-content: center; color: white; font-size: 12px; font-weight: bold;">{s if s else ''}</div>
            <div style="width: {ss_pct}%; background: #8b0000; display: flex; align-items: center; justify-content: center; color: white; font-size: 12px; font-weight: bold;">{ss if ss else ''}</div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 11px; color: #888; margin-bottom: 15px;">
            <span>Strong Buy</span><span>Buy</span><span>Hold</span><span>Sell</span><span>Strong Sell</span>
        </div>
        """, unsafe_allow_html=True)

        st.caption(f"Based on {total} analyst ratings")

    # Metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Strong Buy", sb)
    col2.metric("Buy", b)
    col3.metric("Hold", h)
    col4.metric("Sell", s)
    col5.metric("Strong Sell", ss)

    # Trend
    if len(recs) > 1:
        st.markdown("**Recommendation Trend**")
        trend = recs.head(6).copy()
        period_labels = ["Current", "1 mo ago", "2 mo ago", "3 mo ago", "4 mo ago", "5 mo ago"]
        trend["Period"] = period_labels[:len(trend)]
        trend = trend.drop(columns=["period"], errors="ignore")
        cols = ["Period"] + [c for c in trend.columns if c != "Period"]
        trend = trend[cols]
        st.dataframe(trend, use_container_width=True, hide_index=True)
