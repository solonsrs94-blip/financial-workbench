"""News tab — recent news articles for the company."""

import streamlit as st
from lib.data.fundamentals import get_news


def render(ticker: str) -> None:
    with st.spinner("Loading news..."):
        news, _ = get_news(ticker)

    if not news:
        st.info("No recent news available.")
        return

    for article in news:
        title = article.get("title", "")
        publisher = article.get("publisher", "")
        link = article.get("link", "")
        published = article.get("published", "")

        if title and link:
            st.markdown(f"**[{title}]({link})**")
            st.caption(f"{publisher} · {published[:10] if published else ''}")
            st.markdown("---")
