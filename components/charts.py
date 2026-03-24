"""
Standardized chart components — consistent look across all pages.
Uses Plotly for interactive charts.
"""

import plotly.graph_objects as go
import pandas as pd
import streamlit as st

from config.constants import CHART_COLORS, CHART_HEIGHT, CHART_TEMPLATE


def price_chart(
    df: pd.DataFrame,
    title: str = "Price History",
    height: int = CHART_HEIGHT,
    chart_key: str = "price_chart",
) -> None:
    """Render an interactive price chart with type selector."""
    if df is None or df.empty:
        st.info("No price data available.")
        return

    # Chart type selector
    chart_type = st.segmented_control(
        "Chart Type",
        ["Line", "Candlestick", "Area"],
        default="Line",
        key=f"{chart_key}_type",
        label_visibility="collapsed",
    )

    # Handle both index-based and column-based dates
    if "Date" in df.columns:
        x = df["Date"]
    else:
        x = df.index

    fig = go.Figure()

    if chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=x,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            increasing_line_color=CHART_COLORS["positive"],
            decreasing_line_color=CHART_COLORS["negative"],
            name="OHLC",
        ))
        fig.update_layout(xaxis_rangeslider_visible=False)

    elif chart_type == "Area":
        fig.add_trace(go.Scatter(
            x=x,
            y=df["Close"],
            mode="lines",
            name="Close",
            line=dict(color=CHART_COLORS["primary"], width=2),
            fill="tozeroy",
            fillcolor="rgba(31, 119, 180, 0.15)",
        ))

    else:  # Line (default)
        fig.add_trace(go.Scatter(
            x=x,
            y=df["Close"],
            mode="lines",
            name="Close",
            line=dict(color=CHART_COLORS["primary"], width=2),
        ))

    fig.update_layout(
        title=title,
        template=CHART_TEMPLATE,
        height=height,
        xaxis_title="",
        yaxis_title="Price",
        hovermode="x unified",
        margin=dict(l=0, r=0, t=40, b=0),
    )

    st.plotly_chart(fig, use_container_width=True)


def volume_chart(
    df: pd.DataFrame,
    height: int = 200,
) -> None:
    """Render a volume bar chart."""
    if df is None or df.empty:
        return

    if "Date" in df.columns:
        x = df["Date"]
    else:
        x = df.index

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=x,
        y=df["Volume"],
        name="Volume",
        marker_color=CHART_COLORS["neutral"],
        opacity=0.6,
    ))

    fig.update_layout(
        template=CHART_TEMPLATE,
        height=height,
        xaxis_title="",
        yaxis_title="Volume",
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)
