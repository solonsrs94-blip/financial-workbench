"""How to Use — quick-start guide and detailed module walkthroughs."""

import streamlit as st

from components.layout import load_css
from components.auth_guard import require_auth, show_user_sidebar

load_css()
require_auth()
show_user_sidebar()

st.title("How to Use")
st.caption("A guide to getting the most out of Financial Workbench")

# ── Quick Start ─────────────────────────────────────────────
st.markdown("---")
st.markdown("## Quick Start")

st.markdown("""
The typical workflow is:

1. **Company Overview** — Search for a company, review its financials and key metrics
2. **Valuation** — Run one or more valuation models (DCF, Comps, Historical Multiples, DDM)
3. **Save** — Save your analysis to the cloud for later review

You can jump to any page directly from the sidebar. Each valuation model
is independent — use one, some, or all depending on the company.
""")

# ── Page Guide ──────────────────────────────────────────────
st.markdown("---")
st.markdown("## Pages")

with st.expander("**Company Overview** — Your starting point", expanded=False):
    st.markdown("""
- **Search** by ticker or company name, or **Browse** by category
- See price charts, key metrics, 52-week range, and analyst targets
- Tabs for: Detail, Financials, Ownership, Peers, Analysts, News, About
- Use the **Financials** tab to review income statement, balance sheet, and cash flow
- Click a company's ticker anywhere in the app to jump here
""")

with st.expander("**Saved Valuations** — Your analysis library", expanded=False):
    st.markdown("""
- Browse all your saved valuations, grouped by ticker
- **Load** a saved analysis to pick up where you left off
- **Delete** analyses you no longer need
- Each save is a full snapshot — all assumptions, scenarios, and commentary
""")

with st.expander("**Valuation** — The analysis workbench", expanded=False):
    st.markdown("""
Start by entering a ticker. The app runs **Financial Preparation** automatically:
- Standardizes financial statements (5 years)
- Detects anomalies and flags (22 rules)
- Classifies the company (normal, financial, dividend-stable)
- Generates model recommendations (which models fit best)

Then choose your valuation model(s) from the tabs.
""")

# ── Valuation Models ────────────────────────────────────────
st.markdown("---")
st.markdown("## Valuation Models")

with st.expander("**DCF** — Discounted Cash Flow", expanded=False):
    st.markdown("""
A 5-step IB-grade DCF:

**Step 1 — Preparation** (automatic)
Financial data is standardized and flagged.

**Step 2 — FCF Projections**
- Set revenue growth, EBIT margin, and other assumptions for 5 projection years
- Bull / Base / Bear scenarios with independent assumptions
- Historical data shown alongside for reference

**Step 3 — WACC**
- Cost of Equity (CAPM with 3 beta methods: raw, adjusted, peer group)
- Cost of Debt (actual from financials or synthetic from rating)
- Capital structure (market-based, book-based, target, or custom)
- All inputs are overridable

**Step 4 — Terminal Value**
- Gordon Growth Model or Exit Multiple method
- Bull / Base / Bear terminal assumptions
- Cross-checks and warnings (e.g., implied growth > GDP)

**Step 5 — Output**
- Enterprise Value breakdown
- Equity Bridge (EV to equity per share, with overridable items)
- Sensitivity tables (WACC x growth, WACC x multiple)
- Bull / Base / Bear comparison
""")

with st.expander("**Comps** — Comparable Companies", expanded=False):
    st.markdown("""
A 3-step comparable company analysis:

**Step 1 — Peer Selection**
- Auto-generates candidates from global indices (800+ companies)
- Matched by GICS industry classification
- Add or remove peers manually

**Step 2 — Comps Table**
- Multiples for all selected peers (EV/Revenue, EV/EBITDA, P/E, etc.)
- Financial companies use P/Book, P/TBV, Div Yield instead of EV-based
- Summary statistics (mean, median, percentiles)

**Step 3 — Implied Valuation**
- Apply a multiple to derive implied share price
- Bull / Base / Bear scenarios (25th / median / 75th percentile defaults)
- Football field chart showing the range
""")

with st.expander(
    "**Historical Multiples** — What the market has paid", expanded=False,
):
    st.markdown("""
Analyzes how the market has historically valued the company:

- Daily trailing-twelve-month (TTM) multiples going back 10+ years
- Sources: SEC EDGAR (quarterly) with yfinance fallback
- Time series charts with mean and +/-1 standard deviation bands
- Summary statistics (10th, 25th, median, 75th, 90th percentile)
- Implied value at each percentile
- EPS basis selector (trailing, forward, or manual override)
- Bull / Base / Bear scenarios (-1 sigma / mean / +1 sigma defaults)
""")

with st.expander("**DDM** — Dividend Discount Model", expanded=False):
    st.markdown("""
For dividend-paying companies:

**Step 1 — Cost of Equity**
- Independent CAPM calculation (not shared with DCF)
- Same 3 beta methods available

**Step 2 — Dividend Projections**
- Gordon Growth (perpetual) or 2-Stage model
- Reference data: DPS history, CAGR, dividend streaks, payout ratio
- Anomaly detection (filters out stock-split artifacts)
- Bull / Base / Bear scenarios

**Step 3 — Output**
- Implied share price per scenario
- Sensitivity table (Ke x growth rate)
- Football field chart
""")

with st.expander("**Summary** — All models combined", expanded=False):
    st.markdown("""
Aggregates results from all completed models:

- Overview table with implied prices from each model and scenario
- Combined football field chart (all models side by side)
- Model weighting (set custom weights, default equal)
- Weighted fair value alongside mean and median
- **Save to Cloud** button to store the full analysis
""")

# ── Tips ────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## Tips")

st.markdown("""
- **Analyst Commentary** boxes appear throughout the valuation. Use them to
  document your reasoning — they are saved with the analysis and included in
  JSON exports.
- **Flags** (colored badges) highlight anomalies in the financial data.
  Hover or click for details. They help you spot issues before they affect
  your valuation.
- **Recommendations** on the Preparation page tell you which models are the
  best fit for this company and what risks to watch for.
- **Override** any prepared data value in the Preparation step if you
  disagree with the source data. The entire cascade (ratios, flags,
  averages) rebuilds automatically.
- **Save often** — each save creates a new snapshot. You can always load an
  earlier version.
""")
