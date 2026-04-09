"""Stock Screener — coming soon."""

from components.placeholder import render_placeholder

render_placeholder(
    title="Stock Screener",
    icon="🔍",
    description="Filter the market by any financial metric to find opportunities",
    features=[
        ("Custom filters", "P/E, EV/EBITDA, margins, growth, dividend yield, and more"),
        ("Preset screens", "Value, growth, dividend, quality — one-click starting points"),
        ("Sort and rank", "Sort results by any column, see top/bottom performers"),
        ("Region and sector filters", "Narrow by country, exchange, GICS sector"),
        ("Save screens", "Store your favorite filter combinations for reuse"),
    ],
)
