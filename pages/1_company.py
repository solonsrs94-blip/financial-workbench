"""
Company Overview — the main browsing hub.
Search, explore, and get a comprehensive overview before diving deeper.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from components.ticker_search import render_ticker_search, is_force_refresh
from components.layout import (
    page_header, data_status_banner,
    format_large_number, format_percentage, format_ratio,
    format_volume, format_price,
)
from components.charts import price_chart, volume_chart
from lib.data.fundamentals import get_company
from lib.data.market import get_price_history
from lib.data.providers import yahoo


# === Helper Functions (must be defined before use) ===

@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_peers(sector: str, industry: str, exclude_ticker: str) -> list[dict]:
    """Fetch peer companies in the same industry with key metrics.
    Only includes USD-denominated stocks to ensure comparable data."""
    import yfinance as yf
    from yfinance.screener import EquityQuery, screen as yf_screen

    try:
        # Extract base ticker without exchange suffix
        base_exclude = exclude_ticker.split(".")[0] if "." in exclude_ticker else exclude_ticker

        q = EquityQuery("and", [
            EquityQuery("eq", ["sector", sector]),
            EquityQuery("eq", ["industry", industry]),
            EquityQuery("gt", ["intradaymarketcap", 1_000_000_000]),
        ])
        result = yf_screen(q, count=30, sortField="intradaymarketcap", sortAsc=False)

        if not result or "quotes" not in result:
            return []

        seen_names = set()
        tickers = []
        for r in result["quotes"]:
            symbol = r.get("symbol", "")
            name = r.get("longName", r.get("shortName", ""))

            # Extract base ticker for comparison
            base_symbol = symbol.split(".")[0] if "." in symbol else symbol

            # Skip self (any exchange variant)
            if base_symbol == base_exclude:
                continue

            # Skip duplicates by company name
            base_name = name.split(" ")[0].lower() if name else ""
            if base_name in seen_names:
                continue

            seen_names.add(base_name)
            tickers.append(symbol)

            if len(tickers) >= 10:
                break

        peers = []
        for t in tickers:
            try:
                stock = yf.Ticker(t)
                info = stock.info
                if not info or len(info) < 5:
                    continue

                currency = info.get("currency", "")

                div_yield = info.get("dividendYield")
                if div_yield is not None:
                    div_yield = div_yield / 100

                price = info.get("currentPrice", info.get("previousClose"))

                peers.append({
                    "ticker": t,
                    "name": info.get("longName", info.get("shortName", t)),
                    "currency": currency,
                    "price": price,
                    "market_cap": info.get("marketCap"),
                    "pe": info.get("trailingPE"),
                    "pb": info.get("priceToBook"),
                    "profit_margin": info.get("profitMargins"),
                    "roe": info.get("returnOnEquity"),
                    "div_yield": div_yield,
                    "beta": info.get("beta"),
                })
            except Exception:
                continue

            if len(peers) >= 6:
                break

        return peers
    except Exception:
        return []


page_header("Company Overview", "Search for any publicly traded company")

# --- Ticker Search ---
ticker = render_ticker_search()

if not ticker:
    st.stop()

# --- Load Data ---
force_refresh = is_force_refresh()

with st.spinner(f"Loading {ticker}..."):
    company, status = get_company(ticker, force_refresh=force_refresh)

data_status_banner(status)

if company is None:
    st.error(f"Could not find data for '{ticker}'. Check the ticker and try again.")
    st.stop()

# === HEADER ===
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
            delta=f"{company.price.change_pct:.2f}%" if company.price.change_pct else None,
        )

with col_cap:
    st.metric("Market Cap", format_large_number(company.price.market_cap))

# === CHART ===
col_period, col_interval = st.columns([2, 1])

with col_period:
    period = st.segmented_control(
        "Period",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
        default="5y",
        key="price_period",
        label_visibility="collapsed",
    )

with col_interval:
    interval = st.segmented_control(
        "Interval",
        ["Daily", "Weekly", "Monthly"],
        default="Daily",
        key="price_interval",
        label_visibility="collapsed",
    )

interval_map = {"Daily": "1d", "Weekly": "1wk", "Monthly": "1mo"}
yf_interval = interval_map.get(interval, "1d")

price_df, price_status = get_price_history(
    ticker, period=period, interval=yf_interval, force_refresh=force_refresh,
)

price_chart(price_df, title="")
volume_chart(price_df)

# === KEY METRICS ===
st.divider()

col1, col2, col3, col4 = st.columns(4)
col1.metric("P/E (TTM)", format_ratio(company.ratios.pe_trailing))
col2.metric("EV/EBITDA", format_ratio(company.ratios.ev_ebitda))
col3.metric("Profit Margin", format_percentage(company.ratios.profit_margin))
col4.metric("ROE", format_percentage(company.ratios.roe))

col1, col2, col3, col4 = st.columns(4)
col1.metric("P/B", format_ratio(company.ratios.pb))
col2.metric("D/E", format_ratio(company.ratios.debt_to_equity))
col3.metric("Div Yield", format_percentage(company.ratios.dividend_yield))
col4.metric("Beta", format_ratio(company.price.beta))

st.divider()

# === TABS ===
tab_detail, tab_financials, tab_ownership, tab_peers, tab_analysts, tab_news, tab_about = st.tabs(
    ["Detail", "Financials", "Ownership", "Peers", "Analysts", "News", "About"]
)

# --- Detail Tab ---
with tab_detail:
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
    col3.metric("Rev Growth", format_percentage(company.ratios.revenue_growth))
    col4.metric("Earn Growth", format_percentage(company.ratios.earnings_growth))

    st.markdown("**Margins & Returns**")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Gross Margin", format_percentage(company.ratios.gross_margin))
    col2.metric("Op. Margin", format_percentage(company.ratios.operating_margin))
    col3.metric("ROA", format_percentage(company.ratios.roa))
    col4.metric("Payout Ratio", format_percentage(company.ratios.payout_ratio))

    st.markdown("**Trading**")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("52W High", format_price(company.price.high_52w))
    col2.metric("52W Low", format_price(company.price.low_52w))
    col3.metric("Volume", format_volume(company.price.volume))
    col4.metric("Avg Volume", format_volume(company.price.avg_volume))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Ratio", format_ratio(company.ratios.current_ratio))
    col2.metric("Quick Ratio", format_ratio(company.ratios.quick_ratio))
    col3.metric("", "")
    col4.metric("", "")

# --- Financials Tab ---
with tab_financials:
    with st.spinner("Loading financials..."):
        fin_data = yahoo.fetch_financials(ticker)

    if fin_data is None:
        st.info("Financial data not available.")
    else:
        fin_type = st.segmented_control(
            "Statement",
            ["Income", "Balance Sheet", "Cash Flow"],
            default="Income",
            key="fin_type",
            label_visibility="collapsed",
        )

        stmt_map = {
            "Income": fin_data.get("income_statement"),
            "Balance Sheet": fin_data.get("balance_sheet"),
            "Cash Flow": fin_data.get("cash_flow"),
        }

        df = stmt_map.get(fin_type)
        if df is not None and not df.empty:
            df = df.copy()
            # Format column headers as years
            df.columns = [c.strftime("%Y") if hasattr(c, "strftime") else str(c) for c in df.columns]

            # Clean row index names (remove underscores etc.)
            df.index = [str(i).replace("_", " ").title() if isinstance(i, str) else str(i) for i in df.index]

            # Format large numbers for display
            def _fmt_financial(x):
                if not isinstance(x, (int, float)) or pd.isna(x):
                    return ""
                if abs(x) >= 1e9:
                    return f"{x / 1e9:.2f}B"
                if abs(x) >= 1e6:
                    return f"{x / 1e6:.1f}M"
                if abs(x) >= 1e3:
                    return f"{x / 1e3:.1f}K"
                return f"{x:,.0f}"

            display_df = df.map(_fmt_financial)
            st.dataframe(display_df, use_container_width=True, height=500)
        else:
            st.info(f"No {fin_type.lower()} data available.")

# --- Ownership Tab ---
with tab_ownership:
    with st.spinner("Loading ownership data..."):
        holders = yahoo.fetch_holders(ticker)

    if holders is None:
        st.info("Ownership data not available.")
    else:
        if holders.get("institutional") is not None:
            st.markdown("**Top Institutional Holders**")
            inst = holders["institutional"].head(10).copy()

            # Clean up date column
            if "Date Reported" in inst.columns:
                inst["Date Reported"] = pd.to_datetime(inst["Date Reported"]).dt.strftime("%Y-%m-%d")

            # Format percentage
            if "pctHeld" in inst.columns:
                inst["% Held"] = inst["pctHeld"].apply(lambda x: f"{x*100:.2f}%" if pd.notna(x) else "N/A")
                inst = inst.drop(columns=["pctHeld"])

            # Format shares with commas
            if "Shares" in inst.columns:
                inst["Shares"] = inst["Shares"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")

            # Format value
            if "Value" in inst.columns:
                inst["Value"] = inst["Value"].apply(
                    lambda x: f"${x/1e9:.1f}B" if pd.notna(x) and abs(x) >= 1e9
                    else f"${x/1e6:.0f}M" if pd.notna(x) else "N/A"
                )

            # Format pctChange as percentage
            if "pctChange" in inst.columns:
                inst["Change"] = inst["pctChange"].apply(
                    lambda x: f"{x*100:+.1f}%" if pd.notna(x) else "N/A"
                )
                inst = inst.drop(columns=["pctChange"])

            st.dataframe(inst, use_container_width=True, hide_index=True)

        if holders.get("insider_transactions") is not None:
            st.markdown("**Recent Insider Transactions**")
            insider = holders["insider_transactions"].head(10).copy()

            # Clean up date
            for col in insider.columns:
                if "date" in col.lower() or "start" in col.lower():
                    try:
                        insider[col] = pd.to_datetime(insider[col]).dt.strftime("%Y-%m-%d")
                    except Exception:
                        pass

            st.dataframe(insider, use_container_width=True, hide_index=True)

# --- Peers Tab ---
with tab_peers:
    if not company.info.industry:
        st.info("Industry data not available for peer comparison.")
    else:
        with st.spinner("Finding peers..."):
            peers = _fetch_peers(company.info.sector, company.info.industry, company.ticker)

        if not peers:
            st.info("Could not find peer companies.")
        else:
            st.caption(f"Companies in **{company.info.industry}** ({company.info.sector})")

            # Build comparison table
            peer_rows = []
            for p in peers:
                ccy = p.get("currency", "USD")
                price = p.get("price")
                price_str = f"{ccy} {price:,.2f}" if price else "N/A"

                mcap = p.get("market_cap")
                if mcap is not None:
                    if mcap >= 1e12:
                        mcap_str = f"{ccy} {mcap/1e12:.2f}T"
                    elif mcap >= 1e9:
                        mcap_str = f"{ccy} {mcap/1e9:.2f}B"
                    else:
                        mcap_str = f"{ccy} {mcap/1e6:.0f}M"
                else:
                    mcap_str = "N/A"

                peer_rows.append({
                    "Company": f"{p.get('name', '')} ({p.get('ticker', '')})",
                    "Price": price_str,
                    "Mkt Cap": mcap_str,
                    "P/E": format_ratio(p.get("pe")),
                    "P/B": format_ratio(p.get("pb")),
                    "Margin": format_percentage(p.get("profit_margin")),
                    "ROE": format_percentage(p.get("roe")),
                    "Div Yield": format_percentage(p.get("div_yield")),
                })

            peer_df = pd.DataFrame(peer_rows)
            st.dataframe(peer_df, use_container_width=True, hide_index=True)

# --- Analysts Tab ---
with tab_analysts:
    with st.spinner("Loading analyst data..."):
        recs = yahoo.fetch_recommendations(ticker)

    if recs is None:
        st.info("Analyst data not available.")
    else:
        if len(recs) > 0:
            current = recs.iloc[0]
            st.markdown("**Current Analyst Consensus**")

            total = sum([
                int(current.get("strongBuy", 0)),
                int(current.get("buy", 0)),
                int(current.get("hold", 0)),
                int(current.get("sell", 0)),
                int(current.get("strongSell", 0)),
            ])

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Strong Buy", int(current.get("strongBuy", 0)))
            col2.metric("Buy", int(current.get("buy", 0)))
            col3.metric("Hold", int(current.get("hold", 0)))
            col4.metric("Sell", int(current.get("sell", 0)))
            col5.metric("Strong Sell", int(current.get("strongSell", 0)))

            if total > 0:
                st.caption(f"Based on {total} analyst ratings")

            # Trend over months with readable labels
            if len(recs) > 1:
                st.markdown("**Recommendation Trend**")
                trend = recs.head(6).copy()
                period_labels = ["Current", "1 mo ago", "2 mo ago", "3 mo ago", "4 mo ago", "5 mo ago"]
                trend["Period"] = period_labels[:len(trend)]
                trend = trend.drop(columns=["period"], errors="ignore")
                cols = ["Period"] + [c for c in trend.columns if c != "Period"]
                trend = trend[cols]
                st.dataframe(trend, use_container_width=True, hide_index=True)

# --- News Tab ---
with tab_news:
    with st.spinner("Loading news..."):
        news = yahoo.fetch_news(ticker)

    if not news:
        st.info("No recent news available.")
    else:
        for article in news:
            title = article.get("title", "")
            publisher = article.get("publisher", "")
            link = article.get("link", "")
            published = article.get("published", "")

            if title and link:
                st.markdown(f"**[{title}]({link})**")
                st.caption(f"{publisher} · {published[:10] if published else ''}")
                st.markdown("---")

# --- About Tab ---
with tab_about:
    if company.info.description:
        st.write(company.info.description)

    col1, col2, col3 = st.columns(3)
    with col1:
        if company.info.website:
            st.markdown(f"[{company.info.website}]({company.info.website})")
    with col2:
        if company.info.employees:
            st.metric("Employees", f"{company.info.employees:,}")
    with col3:
        st.metric("Currency", company.info.currency)
