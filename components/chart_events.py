"""Chart event markers — earnings, dividends, splits on price charts."""

import logging
import plotly.graph_objects as go
import pandas as pd

logger = logging.getLogger(__name__)

# Event visual configuration
EVENT_CONFIGS = {
    "earnings": {
        "color": "rgba(255, 127, 14, 0.2)", "dash": "dot",
        "icon": "▲", "hover_color": "#ff7f0e", "show_line": True,
    },
    "dividends": {
        "color": "rgba(44, 160, 44, 0.15)", "dash": "dash",
        "icon": "◆", "hover_color": "#2ca02c", "show_line": False,
    },
    "splits": {
        "color": "rgba(227, 119, 194, 0.3)", "dash": "solid",
        "icon": "★", "hover_color": "#e377c2", "show_line": True,
    },
}


def add_event_markers(
    fig: go.Figure,
    events: dict,
    date_min: pd.Timestamp,
    date_max: pd.Timestamp,
) -> None:
    """Add earnings, dividend, and split markers as vertical lines on the x-axis."""
    for event_type, config in EVENT_CONFIGS.items():
        items = events.get(event_type, [])
        if not items:
            continue

        for item in items:
            try:
                d = pd.to_datetime(item["date"]).tz_localize(None)
            except Exception:
                logger.warning("Could not parse event date: %s", item.get("date"))
                continue

            if d < date_min or d > date_max:
                continue

            label = item.get("label", event_type)
            d_str = d.strftime("%Y-%m-%d")

            if config["show_line"]:
                fig.add_shape(
                    type="line",
                    x0=d_str, x1=d_str,
                    y0=0, y1=1,
                    yref="paper",
                    line=dict(color=config["color"], width=1, dash=config["dash"]),
                )

            fig.add_annotation(
                x=d_str, y=-0.02, yref="paper",
                text=config["icon"],
                showarrow=False,
                font=dict(size=13, color=config["hover_color"]),
                hovertext=label,
                opacity=0.8,
            )


def build_event_legend(events: dict) -> str:
    """Build HTML legend string for events present in the data."""
    parts = []
    if events.get("earnings"):
        parts.append('<span style="color: #ff7f0e;">▲ Earnings</span>')
    if events.get("dividends"):
        parts.append('<span style="color: #2ca02c;">◆ Dividend</span>')
    if events.get("splits"):
        parts.append('<span style="color: #e377c2;">★ Split</span>')
    return " &nbsp;&nbsp; ".join(parts)
