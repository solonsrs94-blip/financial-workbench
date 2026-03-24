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
    """Format a decimal as percentage. Always treats input as decimal (0.25 → 25.0%)."""
    if value is None:
        return "N/A"
    pct = value * 100
    if abs(pct) >= 100:
        return f"{pct:.0f}%"
    if abs(pct) < 1:
        return f"{pct:.2f}%"
    return f"{pct:.1f}%"


def format_ratio(value: float) -> str:
    """Format a ratio (e.g., 28.50)."""
    if value is None:
        return "N/A"
    return f"{value:.2f}"


def format_volume(value: int) -> str:
    """Format volume with suffix (e.g., 37.4M, 2.1B)."""
    if value is None:
        return "N/A"
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return str(value)


def format_price(value: float) -> str:
    """Format a price (e.g., $288.62)."""
    if value is None:
        return "N/A"
    return f"${value:,.2f}"


def colored_metric(
    container, label: str, value: float,
    formatter: str = "percentage", positive_good: bool = True,
) -> None:
    """Display a metric with green/red color based on value.
    Use for growth rates, margins, and other directional metrics.
    formatter: 'percentage', 'ratio', or 'price'
    """
    if value is None:
        container.metric(label, "N/A")
        return

    if formatter == "percentage":
        text = format_percentage(value)
    elif formatter == "price":
        text = format_price(value)
    else:
        text = format_ratio(value)

    # Determine color
    is_positive = value > 0
    if not positive_good:
        is_positive = not is_positive

    color = "#2ca02c" if is_positive else "#d62728" if value < 0 else "#888"

    container.markdown(
        f'<div style="font-size: 14px; color: #888; margin-bottom: -10px;">{label}</div>'
        f'<div style="font-size: 28px; font-weight: bold; color: {color};">{text}</div>',
        unsafe_allow_html=True,
    )
