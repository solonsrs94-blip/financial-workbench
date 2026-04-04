"""Comps Step 3 commentary templates — per-scenario + shared comparison."""

STEP3_BEAR = """\
--- BEAR CASE RATIONALE ---

MULTIPLE SELECTION:
Applied multiple: (why this multiple level for the bear case — 25th \
percentile, bottom of range, or custom? What peer characteristics justify \
valuing the target at the low end of the distribution?)

Discount rationale: (if applying a discount to the peer multiple, why \
— inferior growth, weaker margins, higher risk, smaller scale, governance \
concerns? How large is the discount and what benchmarks support it?)

COMPARABILITY:
Bear case peers: (are the peers at the low end of the distribution truly \
comparable, or are they lower-quality businesses? Could the low multiples \
reflect company-specific issues rather than a fair comp for your target?)

OVERALL:
Bear narrative: (what market or company conditions would cause the target \
to trade at these lower multiples — sentiment shift, earnings \
disappointment, sector rotation, loss of growth premium?)\
"""

STEP3_BASE = """\
--- BASE CASE RATIONALE ---

MULTIPLE SELECTION:
Applied multiple: (why median — is the target an average-quality company \
within its peer group? Or are you using median as a starting point and \
adjusting with a premium/discount?)

Premium or discount: (if applying a premium or discount to the median, \
what justifies it — superior/inferior growth, margins, market position, \
balance sheet strength, management quality? How did you size the \
adjustment?)

COMPARABILITY:
Peer relevance: (how comparable are the peers to the target on the \
dimensions that matter most for this multiple — growth, profitability, \
risk, size, geography? Are any peers distorting the median?)

Multiple choice: (why is this the right multiple for this sector and \
company — why EV/EBITDA over P/E, or vice versa? Are there sector \
conventions?)

OVERALL:
Base narrative: (does the implied price from comps align with your \
fundamental view? If not, what explains the gap — is the market \
mispricing the peers, or is your fundamental view too \
aggressive/conservative?)\
"""

STEP3_BULL = """\
--- BULL CASE RATIONALE ---

MULTIPLE SELECTION:
Applied multiple: (why this multiple level for the bull case — 75th \
percentile, top of range, or custom? What characteristics justify the \
target trading at a premium within the peer group?)

Premium rationale: (if applying a premium above the peer multiple, why \
— superior growth, best-in-class margins, market leadership, scarcity \
value, M&A premium? Is this premium sustainable or temporary?)

COMPARABILITY:
Bull case peers: (are the peers at the high end truly comparable, or are \
they higher-quality businesses? Could the high multiples reflect temporary \
factors — momentum, speculative premium, or recent re-rating?)

OVERALL:
Bull narrative: (what drives the market to award the target a premium \
multiple — earnings beat, re-rating catalyst, sector rotation into the \
space, M&A speculation? How realistic is this?)\
"""

COMPARISON = """\
--- SCENARIO COMPARISON ---

RANGE ASSESSMENT:
Spread: (how wide is the bear-to-bull range from comps? Is the peer \
distribution tight (suggesting consensus) or wide (suggesting \
heterogeneous peer group)? What does this imply about the reliability \
of the comps-based valuation?)

CROSS-MODEL CHECK:
Consistency with DCF: (does the comps range overlap with your DCF \
scenario range? If comps gives a higher/lower range, what explains \
the difference — growth expectations baked into multiples vs. your \
explicit projections, or different risk assessments?)

PEER GROUP CONFIDENCE:
Quality of comps: (overall, how confident are you in this peer group? \
Are there enough comparable companies to draw meaningful conclusions? \
If the peer group is small or imperfect, how much weight should comps \
carry in your final valuation?)

Multiple reliability: (is the chosen multiple stable and meaningful for \
this sector, or is it noisy? For example, are there many peers with \
negative earnings making P/E unreliable?)\
"""
