"""Detail tab — valuation, earnings, margins, trading metrics."""

import streamlit as st
from components.layout import format_ratio, format_price, format_percentage, format_volume, format_large_number, colored_metric
from lib.data.fundamentals import get_financials
from models.company import Company


def render(company: Company, ticker: str) -> None:
    st.markdown("**Valuation**")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("P/E (Fwd)", format_ratio(company.ratios.pe_forward))
    col2.metric("PEG", format_ratio(company.ratios.peg))
    col3.metric("P/S", format_ratio(company.ratios.ps))
    col4.metric("EV/Revenue", format_ratio(company.ratios.ev_revenue))

    st.markdown("**Earnings**")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("EPS (TTM)", format_price(company.ratios.eps_trailing))
    col2.metric("EPS (Fwd)", format_price(company.ratios.eps_forward))
    colored_metric(col3, "Rev Growth", company.ratios.revenue_growth)
    colored_metric(col4, "Earn Growth", company.ratios.earnings_growth)

    st.markdown("**Margins & Returns**")
    col1, col2, col3, col4 = st.columns(4)
    colored_metric(col1, "Gross Margin", company.ratios.gross_margin)
    colored_metric(col2, "Op. Margin", company.ratios.operating_margin)
    colored_metric(col3, "ROA", company.ratios.roa)
    col4.metric("Payout Ratio", format_percentage(company.ratios.payout_ratio))

    st.markdown("**Trading & Liquidity**")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("52W High", format_price(company.price.high_52w))
    col2.metric("52W Low", format_price(company.price.low_52w))
    col3.metric("Volume", format_volume(company.price.volume))
    col4.metric("Avg Volume", format_volume(company.price.avg_volume))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Ratio", format_ratio(company.ratios.current_ratio))
    col2.metric("Quick Ratio", format_ratio(company.ratios.quick_ratio))
    col3.metric("Short % Float", format_percentage(company.ratios.short_pct_float))
    col4.metric("Shares Out", format_large_number(company.ratios.shares_outstanding))

    # Margin trend chart — reuse cached financials from session_state
    _render_margin_trends(ticker)


def _render_margin_trends(ticker: str) -> None:
    # Reuse cached financials instead of fetching again
    cache_key = f"fin_data_{ticker}"
    if cache_key in st.session_state:
        fin_data = st.session_state[cache_key]
    else:
        fin_data, _ = get_financials(ticker)
        st.session_state[cache_key] = fin_data

    if not fin_data or fin_data.get("income_statement") is None:
        return

    inc = fin_data["income_statement"]
    years = [c.strftime("%Y") if hasattr(c, "strftime") else str(c) for c in inc.columns]
    years_rev = list(reversed(years))

    import plotly.graph_objects as go
    from config.constants import CHART_TEMPLATE

    margin_data = {}
    for label, num_rows, den_rows in [
        ("Gross Margin", ["Gross Profit", "GrossProfit"], ["Total Revenue", "TotalRevenue"]),
        ("Op. Margin", ["Operating Income", "OperatingIncome", "EBIT"], ["Total Revenue", "TotalRevenue"]),
        ("Net Margin", ["Net Income", "NetIncome"], ["Total Revenue", "TotalRevenue"]),
    ]:
        num = den = None
        for r in num_rows:
            if r in inc.index:
                num = inc.loc[r]
                break
        for r in den_rows:
            if r in inc.index:
                den = inc.loc[r]
                break
        if num is not None and den is not None:
            margins = [(num[y] / den[y] * 100) if den[y] and den[y] != 0 else None for y in inc.columns]
            margin_data[label] = list(reversed(margins))

    if not margin_data:
        return

    st.markdown("**Margin Trends**")
    fig = go.Figure()
    colors = {"Gross Margin": "#2ca02c", "Op. Margin": "#ff7f0e", "Net Margin": "#1f77b4"}
    for name, vals in margin_data.items():
        fig.add_trace(go.Scatter(
            x=years_rev, y=vals, mode="lines+markers",
            name=name, line=dict(color=colors.get(name, "#888"), width=2),
        ))
    fig.update_layout(
        template=CHART_TEMPLATE, height=280,
        yaxis_title="%", margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)
