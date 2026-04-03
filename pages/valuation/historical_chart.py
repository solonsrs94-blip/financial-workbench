"""Historical Multiples — time series charts.

One Plotly chart per selected multiple with mean/median lines,
±1σ band, and current value marker.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config.constants import CHART_TEMPLATE

# ── Labels ────────────────────────────────────────────────────

_LABELS = {
    "pe": "P/E — Trailing 12 Months",
    "ev_ebitda": "EV/EBITDA — Trailing 12 Months",
    "ev_revenue": "EV/Revenue — Trailing 12 Months",
    "p_book": "P/Book — Trailing 12 Months",
    "p_tbv": "P/TBV — Trailing 12 Months",
}

_COLORS = {
    "line": "#1c83e1",
    "mean": "#ff7f0e",
    "median": "#2ca02c",
    "band": "rgba(28,131,225,0.08)",
    "current": "#f85149",
}


# ── Public ────────────────────────────────────────────────────


def render_historical_charts(
    daily: pd.DataFrame,
    summary: dict,
    selected: list[str],
) -> None:
    """Render one stacked chart per selected multiple."""
    for key in selected:
        if key not in daily.columns or key not in summary:
            continue
        stats = summary[key]
        _render_single_chart(daily, key, stats)


# ── Single chart ──────────────────────────────────────────────


def _render_single_chart(
    daily: pd.DataFrame, key: str, stats: dict,
) -> None:
    """Render a single historical multiple chart."""
    series = daily[key].dropna()
    if series.empty:
        return

    current = stats["current"]
    label = _LABELS.get(key, key)
    title = f"{label} — Current: {current:.1f}x"

    fig = go.Figure()

    # ±1σ band
    mean = stats["mean"]
    std = stats["std"]
    x_dates = list(series.index)
    fig.add_trace(go.Scatter(
        x=x_dates + x_dates[::-1],
        y=[mean + std] * len(x_dates) + [mean - std] * len(x_dates),
        fill="toself",
        fillcolor=_COLORS["band"],
        line=dict(width=0),
        hoverinfo="skip",
        showlegend=True,
        name="±1σ",
    ))

    # Main line
    fig.add_trace(go.Scatter(
        x=series.index,
        y=series.values,
        mode="lines",
        line=dict(color=_COLORS["line"], width=1.5),
        name=key.upper().replace("_", "/"),
        hovertemplate="%{x|%b %Y}: %{y:.1f}x<extra></extra>",
    ))

    # Mean line
    fig.add_hline(
        y=mean,
        line=dict(color=_COLORS["mean"], width=1.5, dash="dash"),
        annotation=dict(
            text=f"Mean: {mean:.1f}x",
            font=dict(color=_COLORS["mean"], size=10),
            xanchor="left",
        ),
    )

    # Median line
    median = stats["median"]
    fig.add_hline(
        y=median,
        line=dict(color=_COLORS["median"], width=1.5, dash="dot"),
        annotation=dict(
            text=f"Median: {median:.1f}x",
            font=dict(color=_COLORS["median"], size=10),
            xanchor="left", yshift=-12,
        ),
    )

    # Current value marker (rightmost point)
    fig.add_trace(go.Scatter(
        x=[series.index[-1]],
        y=[current],
        mode="markers+text",
        marker=dict(color=_COLORS["current"], size=8),
        text=[f"{current:.1f}x"],
        textposition="middle right",
        textfont=dict(color=_COLORS["current"], size=11),
        showlegend=False,
        hoverinfo="skip",
    ))

    fig.update_layout(
        template=CHART_TEMPLATE,
        title=dict(text=title, font=dict(size=14)),
        height=300,
        margin=dict(l=10, r=60, t=40, b=30),
        xaxis=dict(gridcolor="rgba(128,128,128,0.15)"),
        yaxis=dict(
            title="Multiple (x)",
            gridcolor="rgba(128,128,128,0.15)",
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=10),
        ),
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)
