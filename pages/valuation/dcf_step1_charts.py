"""Step 1 charts — margin trends and revenue/FCF bar chart."""

import streamlit as st
import plotly.graph_objects as go


def render_margin_chart(ratios: list[dict]) -> None:
    """Plotly line chart showing margin trends over time."""
    years = [r["year"] for r in ratios]
    fig = go.Figure()

    for key, name, color in [
        ("gross_margin", "Gross Margin", "#2ca02c"),
        ("ebit_margin", "EBIT Margin", "#1f77b4"),
        ("net_margin", "Net Margin", "#ff7f0e"),
        ("fcf_margin", "FCF Margin", "#9467bd"),
    ]:
        vals = [r.get(key) for r in ratios]
        pct_vals = [v * 100 if v is not None else None for v in vals]
        fig.add_trace(go.Scatter(
            x=years, y=pct_vals, name=name,
            mode="lines+markers", line=dict(color=color, width=2),
            marker=dict(size=5),
        ))

    fig.update_layout(
        title="Margin Trends",
        yaxis_title="%",
        height=350,
        margin=dict(l=40, r=20, t=40, b=30),
        legend=dict(orientation="h", y=-0.15),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_revenue_fcf_chart(
    is_table: list[dict], cf_table: list[dict],
) -> None:
    """Bar chart: revenue with FCF line overlay."""
    years = [r["year"] for r in is_table]
    rev = [r.get("revenue") for r in is_table]
    fcf = [r.get("free_cash_flow") for r in cf_table]

    rev_b = [v / 1e9 if v else None for v in rev]
    fcf_b = [v / 1e9 if v else None for v in fcf]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=years, y=rev_b, name="Revenue",
        marker_color="rgba(28, 131, 225, 0.6)",
    ))
    fig.add_trace(go.Scatter(
        x=years, y=fcf_b, name="FCF",
        mode="lines+markers", line=dict(color="#2ca02c", width=2),
        marker=dict(size=6),
    ))

    fig.update_layout(
        title="Revenue & Free Cash Flow ($B)",
        yaxis_title="$B",
        height=350,
        margin=dict(l=40, r=20, t=40, b=30),
        legend=dict(orientation="h", y=-0.15),
        hovermode="x unified",
        barmode="group",
    )
    st.plotly_chart(fig, use_container_width=True)
