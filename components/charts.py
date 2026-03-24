"""
Standardized chart components — consistent look across all pages.
Uses Plotly for interactive charts.
"""

import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from typing import Optional

from config.constants import CHART_COLORS, CHART_HEIGHT, CHART_TEMPLATE


def price_chart(
    df: pd.DataFrame,
    title: str = "Price History",
    height: int = CHART_HEIGHT,
    chart_key: str = "price_chart",
    events: Optional[dict] = None,
) -> None:
    """Render an interactive price chart with type selector and event markers.

    events: dict with optional keys:
        - earnings: list of {"date": datetime, "label": str}
        - dividends: list of {"date": datetime, "label": str}
        - splits: list of {"date": datetime, "label": str}
    """
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

    # Get date range for filtering events
    x_dates = pd.to_datetime(x)
    date_min = x_dates.min()
    date_max = x_dates.max()

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

    # Add event markers
    if events:
        _add_event_markers(fig, events, df, date_min, date_max)

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


def _add_event_markers(
    fig: go.Figure,
    events: dict,
    df: pd.DataFrame,
    date_min: pd.Timestamp,
    date_max: pd.Timestamp,
) -> None:
    """Add earnings, dividend, and split markers as vertical lines on the x-axis."""
    event_configs = {
        "earnings": {"color": "rgba(255, 127, 14, 0.4)", "dash": "dot", "name": "Earnings", "icon": "E"},
        "dividends": {"color": "rgba(44, 160, 44, 0.4)", "dash": "dash", "name": "Dividends", "icon": "D"},
        "splits": {"color": "rgba(227, 119, 194, 0.6)", "dash": "solid", "name": "Splits", "icon": "S"},
    }

    for event_type, config in event_configs.items():
        items = events.get(event_type, [])
        if not items:
            continue

        for item in items:
            d = pd.to_datetime(item["date"]).tz_localize(None)
            if d < date_min or d > date_max:
                continue

            label = item.get("label", config["name"])
            d_str = d.strftime("%Y-%m-%d")

            fig.add_shape(
                type="line",
                x0=d_str, x1=d_str,
                y0=0, y1=1,
                yref="paper",
                line=dict(color=config["color"], width=1, dash=config["dash"]),
            )
            fig.add_annotation(
                x=d_str, y=0, yref="paper",
                text=config["icon"],
                showarrow=False,
                font=dict(size=9, color=config["color"].replace("0.4", "0.9").replace("0.6", "0.9")),
                bgcolor="rgba(0,0,0,0.5)",
                borderpad=2,
                hovertext=label,
            )


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
