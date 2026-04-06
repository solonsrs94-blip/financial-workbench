"""Comps Step 3 — Football Field chart (horizontal bar ranges).

Plotly horizontal bar chart showing implied value range per multiple.
Each bar spans Low → High, with Median marked.
Vertical line at current share price.

Split from comps_step3_valuation.py for file size compliance.
"""

import plotly.graph_objects as go
import streamlit as st

from config.constants import CHART_TEMPLATE


# ── Labels for display ─────────────────────────────────────────

_MULT_LABELS = {
    "ev_revenue": "EV / Revenue",
    "ev_ebitda": "EV / EBITDA",
    "ev_ebit": "EV / EBIT",
    "trailing_pe": "P / E",
    "forward_pe": "Fwd P / E",
    "fwd_ev_revenue": "Fwd EV / Rev",
    "fwd_ev_ebitda": "Fwd EV / EBITDA*",
    "price_to_book": "P / Book",
    "price_to_tbv": "P / TBV",
    "dividend_yield": "Div Yield",
}

# Preferred display order (bottom to top on chart).
# Keys not present in `implied` are silently skipped,
# so both normal and financial sets work with one list.
_ORDER = [
    "fwd_ev_ebitda", "fwd_ev_revenue", "dividend_yield",
    "forward_pe", "price_to_tbv", "price_to_book",
    "trailing_pe", "ev_ebit", "ev_ebitda", "ev_revenue",
]

_BAR_COLOR = "rgba(28, 131, 225, 0.5)"
_MEDIAN_COLOR = "#1c83e1"
_CURRENT_COLOR = "#f85149"


# ── Main renderer ──────────────────────────────────────────────


def render_football_field(
    implied: dict, current_price: float,
) -> None:
    """Render football field chart using Plotly."""
    # Collect valid multiples
    labels = []
    lows = []
    highs = []
    medians = []

    for key in _ORDER:
        data = implied.get(key)
        if data is None:
            continue
        lo = data.get("low")
        hi = data.get("high")
        med = data.get("median")
        if lo is None or hi is None or med is None:
            continue
        if lo <= 0 or hi <= 0:
            continue

        labels.append(_MULT_LABELS.get(key, key))
        lows.append(lo)
        highs.append(hi)
        medians.append(med)

    if not labels:
        st.info("Not enough data for football field chart.")
        return

    fig = go.Figure()

    # Bars: base at Low, width = High - Low
    widths = [h - l for l, h in zip(lows, highs)]
    fig.add_trace(go.Bar(
        y=labels,
        x=widths,
        base=lows,
        orientation="h",
        marker_color=_BAR_COLOR,
        marker_line=dict(color=_MEDIAN_COLOR, width=1),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Low: $%{base:,.0f}<br>"
            "High: $%{customdata[0]:,.0f}<br>"
            "Median: $%{customdata[1]:,.0f}"
            "<extra></extra>"
        ),
        customdata=list(zip(highs, medians)),
        name="Range",
        showlegend=False,
    ))

    # Median markers
    fig.add_trace(go.Scatter(
        y=labels,
        x=medians,
        mode="markers",
        marker=dict(
            symbol="diamond",
            size=10,
            color=_MEDIAN_COLOR,
            line=dict(width=1, color="white"),
        ),
        hovertemplate="Median: $%{x:,.0f}<extra></extra>",
        name="Median",
        showlegend=True,
    ))

    # Current price vertical line
    fig.add_vline(
        x=current_price,
        line=dict(color=_CURRENT_COLOR, width=2, dash="dash"),
        annotation=dict(
            text=f"Current: ${current_price:,.0f}",
            font=dict(color=_CURRENT_COLOR, size=11),
            yshift=10,
        ),
    )

    # Cap x-axis to avoid outlier bars stretching the chart
    all_vals = lows + highs + medians + [current_price]
    x_cap = sorted(all_vals)[int(len(all_vals) * 0.85)] * 1.6
    x_cap = max(x_cap, current_price * 2)  # at least 2× current price

    # Layout
    fig.update_layout(
        template=CHART_TEMPLATE,
        height=max(250, len(labels) * 50 + 80),
        margin=dict(l=10, r=20, t=30, b=40),
        xaxis=dict(
            title="Implied Share Price ($)",
            tickprefix="$",
            tickformat=",",
            gridcolor="rgba(128,128,128,0.15)",
            range=[0, x_cap],
        ),
        yaxis=dict(
            automargin=True,
            categoryorder="array",
            categoryarray=labels,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            font=dict(size=11),
        ),
        bargap=0.3,
    )

    st.plotly_chart(fig, use_container_width=True)
