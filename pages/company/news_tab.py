"""News tab — recent news articles for the company."""

import streamlit as st
from lib.data.providers import yahoo


def render(ticker: str) -> None:
    with st.spinner("Loading news..."):
        news = yahoo.fetch_news(ticker)

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
