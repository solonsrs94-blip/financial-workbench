"""Watchlists — coming soon."""

from components.placeholder import render_placeholder

render_placeholder(
    title="Watchlists",
    icon="👁",
    description="Track the companies you care about in one place",
    features=[
        ("Multiple watchlists", "Organize by theme — dividends, growth, earnings plays"),
        ("Live overview", "Price, change, key ratios at a glance for all entries"),
        ("Price alerts", "Get notified when a stock hits your target price"),
        ("Quick access", "Jump to Company Overview or Valuation in one click"),
        ("Notes", "Add personal notes and thesis reminders per company"),
    ],
)
