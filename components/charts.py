"""
Standardized chart components — consistent look across all pages.
Uses Plotly for interactive charts.
"""

import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from typing import Optional

from config.constants import CHART_COLORS, CHART_HEIGHT, CHART_TEMPLATE, PERIOD_DAYS
from components.chart_events import add_event_markers, build_event_legend


def price_chart(
    df: pd.DataFrame,
    title: str = "Price History",
    height: int = CHART_HEIGHT,
    chart_key: str = "price_chart",
    events: Optional[dict] = None,
    interval: str = "1d",
    visible_period: Optional[str] = None,
) -> None:
    """Render an interactive price chart with type selector and event markers."""
    if df is None or df.empty:
        st.info("No price data available.")
        return

    # Chart controls
    col_type, col_sma = st.columns([2, 1])

    with col_type:
        chart_type = st.segmented_control(
            "Chart Type",
            ["Line", "Candlestick", "Area"],
            default="Line",
            key=f"{chart_key}_type",
            label_visibility="collapsed",
        )

    with col_sma:
        show_sma = st.toggle("SMA 50/200", value=False, key=f"{chart_key}_sma")

    x = df["Date"] if "Date" in df.columns else df.index
    x_dates = pd.to_datetime(x)
    date_min = x_dates.min()
    date_max = x_dates.max()

    fig = go.Figure()

    # OHLC validation — fall back to Line if columns missing
    has_ohlc = all(col in df.columns for col in ["Open", "High", "Low", "Close"])

    if chart_type == "Candlestick" and has_ohlc:
        fig.add_trace(go.Candlestick(
            x=x, open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"],
            increasing_line_color=CHART_COLORS["positive"],
            decreasing_line_color=CHART_COLORS["negative"],
            name="OHLC",
        ))
        fig.update_layout(xaxis_rangeslider_visible=False)
    elif chart_type == "Candlestick" and not has_ohlc:
        st.caption("OHLC data not available — showing line chart.")
        _add_line_trace(fig, x, df["Close"])
    elif chart_type == "Area":
        fig.add_trace(go.Scatter(
            x=x, y=df["Close"], mode="lines", name="Close",
            line=dict(color=CHART_COLORS["primary"], width=2),
            fill="tozeroy", fillcolor="rgba(31, 119, 180, 0.15)",
        ))
    else:
        _add_line_trace(fig, x, df["Close"])

    if show_sma:
        _add_sma_overlays(fig, df, x, interval)

    # Add event markers
    has_events = events and any(events.get(k) for k in ["earnings", "dividends", "splits"])
    if events:
        add_event_markers(fig, events, date_min, date_max)

    fig.update_layout(
        title=title, template=CHART_TEMPLATE, height=height,
        xaxis_title="", yaxis_title="Price", hovermode="x unified",
        margin=dict(l=0, r=0, t=40, b=25 if has_events else 0),
    )

    # Zoom to visible period
    if visible_period and visible_period != "max":
        from datetime import timedelta
        days = PERIOD_DAYS.get(visible_period)
        if days:
            x_end = date_max
            x_start = x_end - timedelta(days=days)
            fig.update_xaxes(range=[x_start.strftime("%Y-%m-%d"), x_end.strftime("%Y-%m-%d")])

    st.plotly_chart(fig, use_container_width=True)

    # Event legend
    if has_events:
        legend_html = build_event_legend(events)
        if legend_html:
            st.markdown(
                f'<div style="text-align: center; font-size: 12px; color: #888; margin-top: -10px;">'
                f'{legend_html}</div>',
                unsafe_allow_html=True,
            )


def volume_chart(df: pd.DataFrame, height: int = 200) -> None:
    """Render a volume bar chart with green/red coloring."""
    if df is None or df.empty:
        return

    x = df["Date"] if "Date" in df.columns else df.index

    has_ohlc = "Open" in df.columns and "Close" in df.columns
    if has_ohlc:
        colors = [
            CHART_COLORS["positive"] if c >= o else CHART_COLORS["negative"]
            for c, o in zip(df["Close"], df["Open"])
        ]
    else:
        colors = CHART_COLORS["primary"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=x, y=df["Volume"], name="Volume",
        marker_color=colors, opacity=0.5,
    ))
    fig.update_layout(
        template=CHART_TEMPLATE, height=height,
        xaxis_title="", yaxis_title="Volume",
        margin=dict(l=0, r=0, t=10, b=0), showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def _add_line_trace(fig: go.Figure, x, close: pd.Series) -> None:
    """Add a simple line trace."""
    fig.add_trace(go.Scatter(
        x=x, y=close, mode="lines", name="Close",
        line=dict(color=CHART_COLORS["primary"], width=2),
    ))


def _add_sma_overlays(fig: go.Figure, df: pd.DataFrame, x, interval: str) -> None:
    """Add SMA overlays adjusted for interval."""
    close = df["Close"]

    if interval == "1wk":
        short_window, long_window = 10, 40
        short_label, long_label = "SMA 10w", "SMA 40w"
    elif interval == "1mo":
        short_window, long_window = 3, 10
        short_label, long_label = "SMA 3m", "SMA 10m"
    else:
        short_window, long_window = 50, 200
        short_label, long_label = "SMA 50", "SMA 200"

    if len(df) > short_window:
        sma_short = close.rolling(window=short_window).mean()
        fig.add_trace(go.Scatter(
            x=x, y=sma_short, mode="lines", name=short_label,
            line=dict(color="#ff7f0e", width=1.5), opacity=0.7,
        ))

    if len(df) > long_window:
        sma_long = close.rolling(window=long_window).mean()
        fig.add_trace(go.Scatter(
            x=x, y=sma_long, mode="lines", name=long_label,
            line=dict(color="#e377c2", width=1.5), opacity=0.7,
        ))
