"""News Feed — coming soon."""

from components.placeholder import render_placeholder

render_placeholder(
    title="News Feed",
    icon="📰",
    description="Aggregated financial news, filtered to your holdings and interests",
    phase="Fasi 3d — Macro & context",
    target_quarter="Q4 2026",
    progress_pct=0,
    tier="personal",
    features=[
        ("Per-ticker feeds", "All news for companies in your watchlist and portfolio"),
        ("Market news", "Major headlines from reputable financial sources"),
        ("Macro news", "Fed, inflation, geopolitics, major economic releases"),
        ("Thematic feeds", "AI, energy transition, healthcare, biotech — subscribe to topics"),
        ("AI-powered summarization", "One-click summary of long articles via Claude API"),
        ("Sentiment tagging", "Headlines tagged as bullish/bearish/neutral per ticker"),
        ("Source diversification", "RSS aggregation from Reuters, Bloomberg, Seeking Alpha, Yahoo Finance"),
    ],
)
