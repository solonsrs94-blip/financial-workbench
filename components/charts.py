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
    interval: str = "1d",
    visible_period: Optional[str] = None,
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

    # Add SMA overlays — adjust window for interval
    if show_sma:
        close = df["Close"]

        # Convert 50/200 day SMA to equivalent periods for the interval
        if interval == "1wk":
            short_window, long_window = 10, 40   # ~50 and ~200 trading days
            short_label, long_label = "SMA 10w", "SMA 40w"
        elif interval == "1mo":
            short_window, long_window = 3, 10    # ~3 and ~10 months
            short_label, long_label = "SMA 3m", "SMA 10m"
        else:
            short_window, long_window = 50, 200
            short_label, long_label = "SMA 50", "SMA 200"

        if len(df) > short_window:
            sma_short = close.rolling(window=short_window).mean()
            fig.add_trace(go.Scatter(
                x=x, y=sma_short, mode="lines", name=short_label,
                line=dict(color="#ff7f0e", width=1.5),
                opacity=0.7,
            ))

        if len(df) > long_window:
            sma_long = close.rolling(window=long_window).mean()
            fig.add_trace(go.Scatter(
                x=x, y=sma_long, mode="lines", name=long_label,
                line=dict(color="#e377c2", width=1.5),
                opacity=0.7,
            ))

    # Add event markers
    if events:
        _add_event_markers(fig, events, df, date_min, date_max)

    has_events = events and any(events.get(k) for k in ["earnings", "dividends", "splits"])

    fig.update_layout(
        title=title,
        template=CHART_TEMPLATE,
        height=height,
        xaxis_title="",
        yaxis_title="Price",
        hovermode="x unified",
        margin=dict(l=0, r=0, t=40, b=25 if has_events else 0),
    )

    # Zoom x-axis to the requested visible period (data may be longer for SMA warmup)
    if visible_period and visible_period != "max":
        from datetime import timedelta
        period_days = {
            "1mo": 30, "3mo": 90, "6mo": 180,
            "1y": 365, "2y": 730, "5y": 1825,
        }
        days = period_days.get(visible_period)
        if days:
            x_end = date_max
            x_start = x_end - timedelta(days=days)
            fig.update_xaxes(range=[x_start.strftime("%Y-%m-%d"), x_end.strftime("%Y-%m-%d")])

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
        "earnings": {"color": "rgba(255, 127, 14, 0.2)", "dash": "dot", "icon": "▲", "hover_color": "#ff7f0e", "show_line": True},
        "dividends": {"color": "rgba(44, 160, 44, 0.15)", "dash": "dash", "icon": "◆", "hover_color": "#2ca02c", "show_line": False},
        "splits": {"color": "rgba(227, 119, 194, 0.3)", "dash": "solid", "icon": "★", "hover_color": "#e377c2", "show_line": True},
    }

    for event_type, config in event_configs.items():
        items = events.get(event_type, [])
        if not items:
            continue

        for item in items:
            d = pd.to_datetime(item["date"]).tz_localize(None)
            if d < date_min or d > date_max:
                continue

            label = item.get("label", event_type)
            d_str = d.strftime("%Y-%m-%d")

            # Vertical line only for earnings and splits
            if config["show_line"]:
                fig.add_shape(
                    type="line",
                    x0=d_str, x1=d_str,
                    y0=0, y1=1,
                    yref="paper",
                    line=dict(color=config["color"], width=1, dash=config["dash"]),
                )

            # Icon at bottom
            fig.add_annotation(
                x=d_str, y=-0.02, yref="paper",
                text=config["icon"],
                showarrow=False,
                font=dict(size=13, color=config["hover_color"]),
                hovertext=label,
                opacity=0.8,
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

    # Color bars: green if close >= open (up day), red if close < open (down day)
    colors = [
        CHART_COLORS["positive"] if c >= o else CHART_COLORS["negative"]
        for c, o in zip(df["Close"], df["Open"])
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=x,
        y=df["Volume"],
        name="Volume",
        marker_color=colors,
        opacity=0.5,
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
