"""M&A Precedents Database — Professional tier, coming soon."""

from components.tier_guard import require_professional
from components.placeholder import render_placeholder

# Guard: if user is on personal tier, show upgrade placeholder and stop.
require_professional()

# Professional tier users see the roadmap placeholder for this feature.
render_placeholder(
    title="M&A Precedents",
    icon="📋",
    description="Searchable database of historical M&A transactions with implied multiples",
    phase="Fasi 6+ — Professional tier",
    target_quarter="TBD 2027+",
    progress_pct=0,
    tier="professional",
    features=[
        ("EDGAR-scraped database", "US public-target deals parsed from DEFM14A and 8-K filings"),
        ("Transaction multiples", "EV/Revenue, EV/EBITDA, P/E paid at announcement; premium to unaffected price"),
        ("Industry filtering", "GICS Sub-Industry matching to find relevant comps"),
        ("Time filtering", "Last 1yr / 3yr / 5yr / 10yr windows; exclude pre-GFC etc."),
        ("Strategic vs financial", "Filter by acquirer type (strategic vs PE)"),
        ("Deal size bucketing", "Small-mid-large cap target buckets"),
        ("Integration with Comps", "Precedent multiples shown alongside trading multiples on Valuation Summary"),
        ("LLM-parsed deal summaries", "Claude-generated 3-sentence summary of each deal's thesis"),
    ],
)
