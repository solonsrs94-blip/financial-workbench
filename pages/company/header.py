"""Company header — name, price, analyst target, key dates, 52-week range."""

import streamlit as st
import statistics
from components.layout import format_large_number, format_percentage, format_ratio, colored_metric
from models.company import Company


def render_header(company: Company) -> None:
    """Render the company header section."""
    col_name, col_price, col_cap = st.columns([3, 1, 1])

    with col_name:
        st.subheader(f"{company.name} ({company.ticker})")
        if company.info.sector:
            st.caption(
                f"{company.info.sector} · {company.info.industry} · "
                f"{company.info.exchange} · {company.info.country}"
            )

    with col_price:
        if company.price.price is not None:
            st.metric(
                "Price",
                f"${company.price.price:.2f}",
                delta=f"{company.price.change_pct:.2f}%" if company.price.change_pct is not None else None,
            )

    with col_cap:
        st.metric("Market Cap", format_large_number(company.price.market_cap))

    _render_analyst_target(company)
    _render_key_dates(company)
    _render_52w_range(company)


def render_key_metrics(company: Company, peer_medians: dict) -> None:
    """Render key metrics with peer comparison."""
    st.divider()

    def _metric_vs(col, label, value, fmt_func, median_key):
        formatted = fmt_func(value) if value is not None else "N/A"
        med_val = peer_medians.get(median_key)
        if value is not None and med_val is not None and med_val != 0:
            col.metric(label, formatted, delta=f"peers: {med_val:.1f}", delta_color="off")
        else:
            col.metric(label, formatted)

    col1, col2, col3, col4 = st.columns(4)
    _metric_vs(col1, "P/E (TTM)", company.ratios.pe_trailing, format_ratio, "pe")
    _metric_vs(col2, "EV/EBITDA", company.ratios.ev_ebitda, format_ratio, "ev_ebitda")
    colored_metric(col3, "Profit Margin", company.ratios.profit_margin)
    colored_metric(col4, "ROE", company.ratios.roe)

    col1, col2, col3, col4 = st.columns(4)
    _metric_vs(col1, "P/B", company.ratios.pb, format_ratio, "pb")
    col2.metric("D/E", format_ratio(company.ratios.debt_to_equity))
    col3.metric("Div Yield", format_percentage(company.ratios.dividend_yield))
    col4.metric("Beta", format_ratio(company.price.beta))

    st.divider()


@st.cache_data(ttl=3600, show_spinner=False)
def calc_peer_medians(sector: str, industry: str, ticker: str) -> dict:
    """Calculate median valuation metrics from industry peers."""
    try:
        from lib.analysis.peers import fetch_peers
        peers = fetch_peers(sector, industry, ticker)
        if not peers:
            return {}

        pe_vals = [p["pe"] for p in peers if p.get("pe") and 0 < p["pe"] < 500]
        pb_vals = [p["pb"] for p in peers if p.get("pb") and 0 < p["pb"] < 500]

        return {
            "pe": statistics.median(pe_vals) if pe_vals else None,
            "ev_ebitda": None,
            "pb": statistics.median(pb_vals) if pb_vals else None,
        }
    except Exception:
        return {}


def _render_analyst_target(company: Company) -> None:
    """Render analyst price target banner."""
    if not (company.price.target_mean and company.price.price):
        return

    target = company.price.target_mean
    price = company.price.price
    upside = ((target - price) / price) * 100
    color = "#2ca02c" if upside > 0 else "#d62728"
    rating = company.price.analyst_rating or ""
    count = company.price.analyst_count or 0

    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 20px; padding: 8px 16px; background: rgba(28, 131, 225, 0.04); border-radius: 8px; border: 1px solid rgba(28, 131, 225, 0.1); margin: 5px 0;">
        <span style="color: #888; font-size: 13px;">Analyst Target</span>
        <span style="font-size: 18px; font-weight: bold;">${target:,.2f}</span>
        <span style="color: {color}; font-size: 15px; font-weight: bold;">{upside:+.1f}%</span>
        <span style="color: #888; font-size: 13px;">({rating})</span>
        <span style="color: #666; font-size: 12px; margin-left: auto;">Range: ${company.price.target_low:,.2f} — ${company.price.target_high:,.2f} · {count} analysts</span>
    </div>
    """, unsafe_allow_html=True)


def _render_key_dates(company: Company) -> None:
    """Render dividend and earnings date info."""
    items = []
    if company.price.dividend_rate and company.price.ex_dividend_date:
        items.append(
            f'<span style="color: #2ca02c;">◆</span> '
            f'<span style="color: #888;">Dividend:</span> '
            f'<b>${company.price.dividend_rate:.2f}/yr</b> · '
            f'<span style="color: #888;">Ex-date: {company.price.ex_dividend_date}</span>'
        )
    if company.price.next_earnings_date:
        items.append(
            f'<span style="color: #ff7f0e;">▲</span> '
            f'<span style="color: #888;">Next Earnings:</span> '
            f'<b>{company.price.next_earnings_date}</b>'
        )
    if items:
        st.markdown(
            '<div style="display: flex; gap: 30px; padding: 6px 16px; '
            'background: rgba(28, 131, 225, 0.02); border-radius: 8px; '
            'border: 1px solid rgba(28, 131, 225, 0.06); margin: 5px 0; font-size: 14px;">'
            + " &nbsp;|&nbsp; ".join(items) + '</div>',
            unsafe_allow_html=True,
        )


def _render_52w_range(company: Company) -> None:
    """Render 52-week range bar."""
    if not (company.price.low_52w and company.price.high_52w and company.price.price):
        return

    low = company.price.low_52w
    high = company.price.high_52w
    price = company.price.price
    if high <= low:
        return

    pct = max(0.0, min(1.0, (price - low) / (high - low)))
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 10px; margin: 5px 0 15px 0;">
        <span style="color: #888; font-size: 13px;">${low:,.2f}</span>
        <div style="flex: 1; height: 8px; background: linear-gradient(to right, #d62728, #ff7f0e, #2ca02c); border-radius: 4px; position: relative;">
            <div style="position: absolute; left: {pct*100:.1f}%; top: -4px; width: 3px; height: 16px; background: white; border-radius: 2px; box-shadow: 0 0 3px rgba(0,0,0,0.5);"></div>
        </div>
        <span style="color: #888; font-size: 13px;">${high:,.2f}</span>
    </div>
    <div style="text-align: center; color: #888; font-size: 11px; margin-top: -10px;">52-Week Range</div>
    """, unsafe_allow_html=True)
