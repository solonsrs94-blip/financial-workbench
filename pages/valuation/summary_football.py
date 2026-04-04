"""Summary — Combined Football Field chart.

Single Plotly horizontal bar chart combining all valuation methods.
Each bar spans the method's range with a diamond at base case / median.
Vertical dashed line at current market price.

Color scheme:
  DCF        — blue
  Comps      — green
  Historical — orange
  DDM        — purple
"""

import plotly.graph_objects as go
import streamlit as st

from config.constants import CHART_TEMPLATE


def render_combined_football(
    bars: list[dict], current_price: float,
) -> None:
    """Render combined football field chart.

    Each bar dict has: label, low, high, mid, color, marker_color.
    """
    st.markdown("#### Combined Football Field")
    st.caption(
        "Implied share price range from each valuation method. "
        "Diamond = base case / median. Dashed line = current price."
    )

    if not bars:
        st.info("No data for football field chart.")
        return

    # Build traces — reverse order so first bar appears on top
    labels = [b["label"] for b in bars]
    lows = [b["low"] for b in bars]
    highs = [b["high"] for b in bars]
    mids = [b["mid"] for b in bars]
    colors = [b["color"] for b in bars]
    marker_colors = [b["marker_color"] for b in bars]

    fig = go.Figure()

    # One bar trace per method (for individual colors)
    for i, b in enumerate(bars):
        width = b["high"] - b["low"]
        fig.add_trace(go.Bar(
            y=[b["label"]],
            x=[width],
            base=[b["low"]],
            orientation="h",
            marker_color=b["color"],
            marker_line=dict(color=b["marker_color"], width=1),
            hovertemplate=(
                f"<b>{b['label']}</b><br>"
                f"Low: ${b['low']:,.0f}<br>"
                f"High: ${b['high']:,.0f}<br>"
                f"Base: ${b['mid']:,.0f}"
                "<extra></extra>"
            ),
            showlegend=False,
        ))

    # Diamond markers at base case / median
    fig.add_trace(go.Scatter(
        y=labels,
        x=mids,
        mode="markers",
        marker=dict(
            symbol="diamond",
            size=10,
            color=marker_colors,
            line=dict(width=1, color="white"),
        ),
        hovertemplate="Base: $%{x:,.0f}<extra></extra>",
        name="Base Case",
    ))

    # Current price vertical line
    if current_price > 0:
        fig.add_vline(
            x=current_price,
            line=dict(color="#f85149", width=2, dash="dash"),
            annotation=dict(
                text=f"Current: ${current_price:,.0f}",
                font=dict(color="#f85149", size=11),
                yshift=10,
            ),
        )

    # X-axis cap
    all_vals = lows + highs + mids
    if current_price > 0:
        all_vals.append(current_price)
    x_cap = sorted(all_vals)[int(len(all_vals) * 0.85)] * 1.6
    x_cap = max(x_cap, (current_price or max(all_vals)) * 1.5)

    fig.update_layout(
        template=CHART_TEMPLATE,
        height=max(250, len(bars) * 55 + 80),
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

    st.caption(
        "Blue = DCF · Green = Comps · "
        "Orange = Historical · Purple = DDM"
    )
