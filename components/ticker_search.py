"""
Ticker search component — reusable search bar for all pages.
"""

import streamlit as st


def render_ticker_search(
    default: str = "",
    key: str = "ticker_input",
) -> str:
    """
    Render a ticker search input.

    Returns:
        Ticker string (uppercase, stripped) or empty string.
    """
    col1, col2 = st.columns([3, 1])

    with col1:
        ticker = st.text_input(
            "Ticker",
            value=default,
            placeholder="e.g. AAPL, MSFT, TSLA",
            key=key,
            label_visibility="collapsed",
        )

    with col2:
        refresh = st.button("Refresh", key=f"{key}_refresh", use_container_width=True)

    # Store refresh state
    if refresh:
        st.session_state[f"{key}_force_refresh"] = True

    return ticker.upper().strip() if ticker else ""


def is_force_refresh(key: str = "ticker_input") -> bool:
    """Check if user requested a forced refresh."""
    refresh_key = f"{key}_force_refresh"
    if st.session_state.get(refresh_key, False):
        st.session_state[refresh_key] = False
        return True
    return False
