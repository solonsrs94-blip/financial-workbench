"""Historical Multiples — football field chart (implied price).

Horizontal bar chart: one bar per multiple spanning implied price at
10th–90th percentile. Current market price as vertical dashed line.
Color coded by cheap/fair/expensive vs median implied price.

Uses implied share price ($) on x-axis — same approach as Comps
football field (comps_step3_football.py).
"""

import plotly.graph_objects as go
import streamlit as st

from config.constants import CHART_TEMPLATE

# ── Labels ────────────────────────────────────────────────────

_LABELS = {
    "pe": "P/E",
    "ev_ebitda": "EV/EBITDA",
    "ev_revenue": "EV/Revenue",
    "p_book": "P/Book",
    "p_tbv": "P/TBV",
}

# Display order (bottom to top)
_ORDER = ["ev_revenue", "ev_ebitda", "p_tbv", "p_book", "pe"]

_MEDIAN_COLOR = "#1c83e1"
_CURRENT_COLOR = "#f85149"


# ── Public ────────────────────────────────────────────────────


def render_historical_football(
    summary: dict,
    implied: dict,
    current_price: float,
    currency: str,
) -> None:
    """Render football field chart using implied share prices."""
    st.markdown("#### Historical Range (Football Field)")

    if not summary or not implied or not current_price:
        st.info("No data for football field chart.")
        return

    sym = "$" if currency == "USD" else currency + " "

    labels = []
    lows = []
    highs = []
    medians = []
    colors = []

    for key in _ORDER:
        iv = implied.get(key)
        if not iv:
            continue
        lo = iv.get("at_p10")
        hi = iv.get("at_p90")
        med = iv.get("at_median")
        if lo is None or hi is None or med is None:
            continue
        if lo <= 0 or hi <= 0:
            continue

        # Color: green (cheap), red (expensive), yellow (fair)
        if current_price < med * 0.90:
            color = "rgba(63, 185, 80, 0.5)"   # green — cheap
        elif current_price > med * 1.10:
            color = "rgba(248, 81, 73, 0.5)"   # red — expensive
        else:
            color = "rgba(210, 153, 34, 0.5)"  # yellow — fair

        labels.append(_LABELS.get(key, key))
        lows.append(lo)
        highs.append(hi)
        medians.append(med)
        colors.append(color)

    if not labels:
        st.info("Not enough data for football field chart.")
        return

    fig = go.Figure()

    # Bars: implied price at p10 → p90
    widths = [h - l for l, h in zip(lows, highs)]
    fig.add_trace(go.Bar(
        y=labels,
        x=widths,
        base=lows,
        orientation="h",
        marker_color=colors,
        marker_line=dict(color="rgba(128,128,128,0.4)", width=1),
        hovertemplate=(
            "<b>%{y}</b><br>"
            f"10th: {sym}" "%{base:,.0f}<br>"
            f"90th: {sym}" "%{customdata[0]:,.0f}<br>"
            f"Median: {sym}" "%{customdata[1]:,.0f}"
            "<extra></extra>"
        ),
        customdata=list(zip(highs, medians)),
        showlegend=False,
    ))

    # Median markers
    fig.add_trace(go.Scatter(
        y=labels,
        x=medians,
        mode="markers",
        marker=dict(
            symbol="diamond", size=10,
            color=_MEDIAN_COLOR,
            line=dict(width=1, color="white"),
        ),
        hovertemplate=f"Median: {sym}" "%{x:,.0f}<extra></extra>",
        name="Median",
    ))

    # Current price vertical line
    fig.add_vline(
        x=current_price,
        line=dict(color=_CURRENT_COLOR, width=2, dash="dash"),
        annotation=dict(
            text=f"Current: {sym}{current_price:,.0f}",
            font=dict(color=_CURRENT_COLOR, size=11),
            yshift=10,
        ),
    )

    # Cap x-axis
    all_vals = lows + highs + medians + [current_price]
    x_cap = sorted(all_vals)[int(len(all_vals) * 0.85)] * 1.6
    x_cap = max(x_cap, current_price * 2)

    fig.update_layout(
        template=CHART_TEMPLATE,
        height=max(200, len(labels) * 60 + 80),
        margin=dict(l=10, r=20, t=10, b=40),
        xaxis=dict(
            title=f"Implied Share Price ({sym.strip()})",
            tickprefix=sym,
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
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=11),
        ),
        bargap=0.35,
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Green = current below median (cheap) · "
        "Red = current above median (expensive) · "
        "Yellow = near median (fair value) · "
        "Range: 10th–90th percentile implied price"
    )
