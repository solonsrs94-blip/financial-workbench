"""Data freshness indicator — show users how fresh/stale the data they see is.

Critical for user trust. Every non-trivial data display should surface
its age so users know if they're looking at live, recent, or stale data.
"""

from datetime import datetime, timedelta, timezone

import streamlit as st


def _humanize_age(seconds: float) -> str:
    """Convert age in seconds to human-readable string."""
    if seconds < 60:
        return "just now"
    if seconds < 3600:
        mins = int(seconds // 60)
        return f"{mins} min ago" if mins == 1 else f"{mins} mins ago"
    if seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} hour ago" if hours == 1 else f"{hours} hours ago"
    days = int(seconds // 86400)
    return f"{days} day ago" if days == 1 else f"{days} days ago"


def render_freshness(
    fetched_at: datetime | None,
    source: str | None = None,
    stale_threshold_hours: float = 24,
    critical_threshold_hours: float = 72,
) -> None:
    """Render inline freshness badge.

    Parameters
    ----------
    fetched_at : when the data was fetched (timezone-aware). None → "unknown".
    source : optional data source name (e.g. "yfinance", "EDGAR", "Damodaran")
    stale_threshold_hours : yellow warning above this age
    critical_threshold_hours : red warning above this age
    """
    if fetched_at is None:
        st.caption("⚠ Data freshness unknown")
        return

    now = datetime.now(timezone.utc)
    if fetched_at.tzinfo is None:
        fetched_at = fetched_at.replace(tzinfo=timezone.utc)

    age_seconds = (now - fetched_at).total_seconds()
    age_label = _humanize_age(age_seconds)
    age_hours = age_seconds / 3600

    source_suffix = f" • {source}" if source else ""

    if age_hours >= critical_threshold_hours:
        icon = "🔴"
        msg = f"{icon} Data fetched {age_label} — may be significantly stale{source_suffix}"
    elif age_hours >= stale_threshold_hours:
        icon = "🟡"
        msg = f"{icon} Data fetched {age_label}{source_suffix}"
    else:
        icon = "🟢"
        msg = f"{icon} Data fetched {age_label}{source_suffix}"

    st.caption(msg)


def render_stale_cache_warning(
    fetched_at: datetime,
    source: str | None = None,
) -> None:
    """Prominent warning banner when using stale cache as fallback.

    Use this when the live API call failed and the app served cached data
    instead. User must know.
    """
    age = _humanize_age((datetime.now(timezone.utc) - fetched_at).total_seconds())
    source_suffix = f" from {source}" if source else ""
    st.warning(
        f"⚠ Live data fetch failed. Showing cached data{source_suffix} "
        f"(fetched {age}). Results may not reflect latest market conditions.",
        icon="⚠️",
    )


def render_delay_disclosure(delay_minutes: int = 15) -> None:
    """Display standard market-data delay disclosure (yfinance is 15-min delayed)."""
    st.caption(f"ℹ Market data is delayed {delay_minutes} minutes")
