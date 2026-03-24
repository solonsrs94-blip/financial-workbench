"""Ownership tab — institutional holders and insider transactions."""

import streamlit as st
import pandas as pd
from lib.data.providers import yahoo


def render(ticker: str) -> None:
    with st.spinner("Loading ownership data..."):
        holders = yahoo.fetch_holders(ticker)

    if holders is None:
        st.info("Ownership data not available.")
        return

    if holders.get("institutional") is not None:
        _render_institutional(holders["institutional"])

    if holders.get("insider_transactions") is not None:
        _render_insider(holders["insider_transactions"])


def _render_institutional(df: pd.DataFrame) -> None:
    st.markdown("**Top Institutional Holders**")
    inst = df.head(10).copy()

    if "Date Reported" in inst.columns:
        inst["Date Reported"] = pd.to_datetime(inst["Date Reported"]).dt.strftime("%Y-%m-%d")

    if "pctHeld" in inst.columns:
        inst["% Held"] = inst["pctHeld"].apply(lambda x: f"{x*100:.2f}%" if pd.notna(x) else "N/A")
        inst = inst.drop(columns=["pctHeld"])

    if "Shares" in inst.columns:
        inst["Shares"] = inst["Shares"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")

    if "Value" in inst.columns:
        inst["Value"] = inst["Value"].apply(
            lambda x: f"${x/1e9:.1f}B" if pd.notna(x) and abs(x) >= 1e9
            else f"${x/1e6:.0f}M" if pd.notna(x) else "N/A"
        )

    if "pctChange" in inst.columns:
        inst["Change"] = inst["pctChange"].apply(
            lambda x: f"{x*100:+.1f}%" if pd.notna(x) else "N/A"
        )
        inst = inst.drop(columns=["pctChange"])

    def _color_change(val):
        if isinstance(val, str) and val.startswith("+"):
            return "color: #2ca02c"
        if isinstance(val, str) and val.startswith("-"):
            return "color: #d62728"
        return ""

    styled = inst.style.map(_color_change, subset=["Change"] if "Change" in inst.columns else [])
    st.dataframe(styled, use_container_width=True, hide_index=True)


def _render_insider(df: pd.DataFrame) -> None:
    insider_all = df.copy()

    # Net insider activity summary
    if "Shares" in insider_all.columns and "Text" in insider_all.columns:
        buys = insider_all[insider_all["Text"].str.contains("Purchase|Buy|Acquisition", case=False, na=False)]
        sells = insider_all[insider_all["Text"].str.contains("Sale|Sell|Disposition", case=False, na=False)]
        buy_count = len(buys)
        sell_count = len(sells)

        if buy_count > 0 or sell_count > 0:
            net = buy_count - sell_count
            if net > 0:
                sentiment, color = "Net Buying", "#2ca02c"
            elif net < 0:
                sentiment, color = "Net Selling", "#d62728"
            else:
                sentiment, color = "Neutral", "#888"

            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 15px; padding: 10px 16px; background: rgba(28, 131, 225, 0.04); border-radius: 8px; border: 1px solid rgba(28, 131, 225, 0.1); margin: 10px 0;">
                <span style="color: #888; font-size: 13px;">Insider Activity</span>
                <span style="color: {color}; font-size: 16px; font-weight: bold;">{sentiment}</span>
                <span style="color: #2ca02c; font-size: 13px;">{buy_count} buys</span>
                <span style="color: #888;">·</span>
                <span style="color: #d62728; font-size: 13px;">{sell_count} sells</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("**Recent Insider Transactions**")
    insider = insider_all.head(10).copy()

    for col in insider.columns:
        if "date" in col.lower() or "start" in col.lower():
            try:
                insider[col] = pd.to_datetime(insider[col]).dt.strftime("%Y-%m-%d")
            except Exception:
                pass

    st.dataframe(insider, use_container_width=True, hide_index=True)
