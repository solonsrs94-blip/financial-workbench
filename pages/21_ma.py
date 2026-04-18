"""M&A Analysis — Professional tier, coming soon."""

from components.tier_guard import require_professional
from components.placeholder import render_placeholder

# Guard: if user is on personal tier, show upgrade placeholder and stop.
require_professional()

# Professional tier users see the roadmap placeholder for this feature.
render_placeholder(
    title="M&A Analysis",
    icon="🤝",
    description="Accretion/dilution, synergies, and pro-forma merger model",
    phase="Fasi 6+ — Professional tier",
    target_quarter="TBD 2027+",
    progress_pct=0,
    tier="professional",
    features=[
        ("Target & acquirer setup", "Pick two public tickers as acquirer + target; auto-pull financials"),
        ("Deal structure", "Cash/stock mix, premium paid, financing source"),
        ("Synergies model", "Revenue synergies, cost synergies, integration costs over time"),
        ("Pro-forma financials", "Combined IS/BS/CF with consolidation adjustments"),
        ("Accretion/dilution", "EPS impact Year 1-3, sensitivity to premium and synergies"),
        ("Credit impact", "Pro-forma leverage, coverage ratios, implied rating"),
        ("Exchange ratio analysis", "Fixed vs floating exchange ratio, collars, walk rights"),
    ],
)
