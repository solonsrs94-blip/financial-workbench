"""Confidence score component — shows data reliability rating for each input."""

import streamlit as st


def confidence_badge(score: int, source: str = "", container=None) -> None:
    """Display a confidence score (1-10) with source info.

    Args:
        score: 1-10 confidence rating
        source: Where the data comes from (e.g., "Yahoo consensus (5 analysts)")
        container: Streamlit container to render in (default: st)
    """
    c = container or st
    filled = "★" * score
    empty = "☆" * (10 - score)
    if score >= 7:
        color = "#2ca02c"
    elif score >= 4:
        color = "#ff9800"
    else:
        color = "#d62728"

    html = (
        f'<span style="color:{color};font-size:11px;letter-spacing:1px;">'
        f'{filled}{empty}</span>'
        f' <span style="color:#888;font-size:11px;">{score}/10</span>'
    )
    if source:
        html += f'<br><span style="color:#666;font-size:10px;">{source}</span>'

    c.markdown(html, unsafe_allow_html=True)
