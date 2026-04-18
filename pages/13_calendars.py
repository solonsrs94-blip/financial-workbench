"""Calendars — coming soon."""

from components.placeholder import render_placeholder

render_placeholder(
    title="Calendars",
    icon="📅",
    description="Earnings, economic releases, SEC filings, and dividend dates",
    phase="Fasi 3c — Calendars & events",
    target_quarter="Q4 2026",
    progress_pct=0,
    tier="personal",
    features=[
        ("Earnings calendar", "Upcoming earnings with expected EPS/revenue, before/after market"),
        ("Economic calendar", "Fed meetings, CPI, NFP, GDP, PMI — sourced from FRED"),
        ("SEC filings feed", "8-K, 10-K, 10-Q, insider Form 4 alerts for your watchlist"),
        ("Ex-dividend calendar", "Upcoming ex-dividend dates for your holdings"),
        ("IPO calendar", "Upcoming IPOs and recent S-1 filings"),
        ("Watchlist integration", "Filter all calendars to your watchlist tickers"),
    ],
)
