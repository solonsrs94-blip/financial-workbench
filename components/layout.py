"""
Shared layout component — common header and page setup.
"""

import streamlit as st
from config.settings import APP_NAME, APP_ICON


def page_header(title: str, subtitle: str = "") -> None:
    """Render a consistent page header."""
    st.title(f"{title}")
    if subtitle:
        st.caption(subtitle)


def data_status_banner(status: str) -> None:
    """Show a banner indicating data freshness."""
    if status == "stale":
        st.warning(
            "Showing cached data — could not fetch latest. "
            "Click Refresh to try again.",
            icon="⚠️",
        )
    elif status == "error":
        st.error(
            "Could not load data. Check your internet connection "
            "or try a different ticker.",
            icon="🚫",
        )


def format_large_number(value: float) -> str:
    """Format large numbers with suffix (e.g., 2.8T, 150B, 45M)."""
    if value is None:
        return "N/A"

    abs_value = abs(value)
    if abs_value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"
    elif abs_value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    elif abs_value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    elif abs_value >= 1_000:
        return f"${value / 1_000:.2f}K"
    else:
        return f"${value:.2f}"


def format_percentage(value: float) -> str:
    """Format a decimal as percentage (e.g., 0.25 → 25.00%)."""
    if value is None:
        return "N/A"
    return f"{value * 100:.2f}%" if abs(value) < 1 else f"{value:.2f}%"


def format_ratio(value: float) -> str:
    """Format a ratio (e.g., 28.50)."""
    if value is None:
        return "N/A"
    return f"{value:.2f}"
