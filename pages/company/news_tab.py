"""News tab — recent news articles with basic sentiment indicators."""

import streamlit as st
from lib.data.fundamentals import get_news

# Simple keyword-based sentiment (replaced by AI later)
_POSITIVE = {
    "beat", "beats", "surge", "surges", "rally", "gain", "gains", "record",
    "upgrade", "upgraded", "raises", "raise", "growth", "profit", "strong",
    "bullish", "outperform", "buy", "soar", "soars", "positive", "boom",
    "recover", "recovery", "high", "dividend", "boost", "innovation",
}
_NEGATIVE = {
    "miss", "misses", "drop", "drops", "fall", "falls", "decline", "loss",
    "downgrade", "downgraded", "cut", "cuts", "weak", "bearish", "sell",
    "crash", "plunge", "risk", "warning", "layoff", "layoffs", "lawsuit",
    "investigation", "recall", "debt", "negative", "low", "slump", "fear",
}


def _simple_sentiment(title: str) -> str:
    """Return 🟢, 🔴, or ⚪ based on title keywords."""
    words = set(title.lower().split())
    pos = len(words & _POSITIVE)
    neg = len(words & _NEGATIVE)
    if pos > neg:
        return "🟢"
    if neg > pos:
        return "🔴"
    return "⚪"


def render(ticker: str) -> None:
    cache_key = f"news_{ticker}"
    if cache_key not in st.session_state:
        with st.spinner("Loading news..."):
            st.session_state[cache_key], _ = get_news(ticker)

    news = st.session_state[cache_key]

    if not news:
        st.info("No recent news available.")
        return

    # Sentiment summary
    sentiments = [_simple_sentiment(a.get("title", "")) for a in news]
    pos_count = sentiments.count("🟢")
    neg_count = sentiments.count("🔴")
    neutral_count = sentiments.count("⚪")

    col1, col2, col3 = st.columns(3)
    col1.metric("Positive", f"{pos_count}", delta=None)
    col2.metric("Neutral", f"{neutral_count}", delta=None)
    col3.metric("Negative", f"{neg_count}", delta=None)

    st.caption("Sentiment based on headline keywords — AI-powered analysis coming later.")
    st.markdown("---")

    for article, sentiment in zip(news, sentiments):
        title = article.get("title", "")
        publisher = article.get("publisher", "")
        link = article.get("link", "")
        published = article.get("published", "")

        if title and link:
            st.markdown(f"{sentiment} **[{title}]({link})**")
            st.caption(f"{publisher} · {published[:10] if published else ''}")
            st.markdown("---")
