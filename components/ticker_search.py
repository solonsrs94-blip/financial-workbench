"""
Ticker search component — search by name or ticker, with suggestions.
Also provides a browse/explore mode for discovery.
"""

import streamlit as st
from lib.data.search import search_companies


def render_ticker_search(
    default: str = "",
    key: str = "ticker_input",
) -> str:
    """
    Render a ticker search with autocomplete suggestions and browse mode.

    Returns:
        Ticker string (uppercase, stripped) or empty string.
    """
    # Check if a ticker was selected from browse/search
    if st.session_state.get(f"{key}_selected"):
        selected = st.session_state[f"{key}_selected"]
        st.session_state[f"{key}_selected"] = ""
        return selected

    search_tab, browse_tab = st.tabs(["Search", "Browse"])

    with search_tab:
        ticker = _render_search(default, key)
        if ticker:
            return ticker

    with browse_tab:
        ticker = _render_browse(key)
        if ticker:
            return ticker

    return ""


def _render_search(default: str, key: str) -> str:
    """Search by name or ticker."""
    col1, col2 = st.columns([4, 1])

    with col1:
        query = st.text_input(
            "Search",
            value=default,
            placeholder="Search by name or ticker (e.g. Apple, AAPL, Microsoft)",
            key=key,
            label_visibility="collapsed",
        )

    with col2:
        refresh = st.button("Refresh", key=f"{key}_refresh", use_container_width=True)

    if refresh:
        st.session_state[f"{key}_force_refresh"] = True

    if not query:
        return ""

    query = query.strip()

    # If it looks like a ticker (all caps, short), use directly
    if query.isupper() and len(query) <= 5 and query.isalpha():
        return query.upper()

    results = _search_with_cache(query)

    if not results:
        return query.upper()

    # If exact ticker match found, use it directly
    for r in results:
        if r["ticker"].upper() == query.upper():
            return r["ticker"].upper()

    # Show search results for user to pick
    for r in results:
        label = f"**{r['name']}** ({r['ticker']}) · {r['sector']} · {r['exchange']}"
        if st.button(label, key=f"pick_{r['ticker']}", use_container_width=True):
            st.session_state[f"{key}_selected"] = r["ticker"]
            st.rerun()

    return ""


def _render_browse(key: str) -> str:
    """Browse companies by category — basic version.
    Full filter-by-region/country/sector/exchange version comes in React frontend.
    """
    import yfinance as yf

    st.caption(
        "Explore popular lists. "
        "Full filtering by region, country, sector and exchange coming soon."
    )

    from config.constants import SCREENER_CATEGORIES
    categories = SCREENER_CATEGORIES

    selected_cat = st.segmented_control(
        "Category",
        list(categories.keys()),
        default="Most Active",
        key=f"{key}_browse_cat",
        label_visibility="collapsed",
    )

    screener_id = categories.get(selected_cat, "most_actives")

    results = _screener_with_cache(screener_id)

    if not results:
        st.info("Could not load data. Try again later.")
        return ""

    for r in results:
        symbol = r.get("symbol", "")
        name = r.get("longName", r.get("shortName", symbol))
        price = r.get("regularMarketPrice", 0)
        change_pct = r.get("regularMarketChangePercent", 0)

        delta_color = "green" if change_pct >= 0 else "red"
        delta_str = f":{delta_color}[{change_pct:+.2f}%]" if change_pct else ""

        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(
                f"**{name}** ({symbol})",
                key=f"browse_{symbol}",
                use_container_width=True,
            ):
                st.session_state[f"{key}_selected"] = symbol
                st.rerun()
        with col2:
            st.markdown(f"${price:.2f} {delta_str}" if price else "")

    return ""


@st.cache_data(ttl=300, show_spinner=False)
def _search_with_cache(query: str) -> list[dict]:
    """Cached search to avoid hitting API on every keystroke."""
    return search_companies(query, max_results=8)


@st.cache_data(ttl=600, show_spinner="Loading...")
def _screener_with_cache(screener_id: str) -> list[dict]:
    """Cached screener results."""
    import yfinance as yf
    try:
        result = yf.screen(screener_id, count=15)
        if result and "quotes" in result:
            return result["quotes"]
        return []
    except Exception:
        return []


def is_force_refresh(key: str = "ticker_input") -> bool:
    """Check if user requested a forced refresh."""
    refresh_key = f"{key}_force_refresh"
    if st.session_state.get(refresh_key, False):
        st.session_state[refresh_key] = False
        return True
    return False
