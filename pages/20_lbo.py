"""LBO Modeling — Professional tier, coming soon."""

from components.tier_guard import require_professional
from components.placeholder import render_placeholder

# Guard: if user is on personal tier, show upgrade placeholder and stop.
require_professional()

# Professional tier users see the roadmap placeholder for this feature.
render_placeholder(
    title="LBO Modeling",
    icon="🏦",
    description="Leveraged buyout analysis — entry price, debt schedule, exit IRR",
    phase="Fasi 6+ — Professional tier",
    target_quarter="TBD 2027+",
    progress_pct=0,
    tier="professional",
    features=[
        ("Entry assumptions", "Entry multiple, debt capacity (typically 5-7x EBITDA), equity check size"),
        ("Debt schedule", "Year-by-year debt paydown path with mandatory + cash sweep"),
        ("Projection engine", "Reuses DCF Step 2 FCF build or standalone assumptions"),
        ("Exit analysis", "Exit multiple × terminal EBITDA → equity proceeds"),
        ("IRR & MOIC", "Required entry price for target IRR (e.g. 25%), MOIC over hold period"),
        ("Debt/equity mix sensitivity", "2D grid: entry multiple × debt ratio → IRR"),
        ("Integration with Valuation", "LBO result shown on Summary football field alongside DCF/Comps/DDM"),
    ],
)
