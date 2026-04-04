"""Historical Multiples commentary templates — per-scenario + comparison."""

STEP_BEAR = """\
--- BEAR CASE RATIONALE ---

MULTIPLE SELECTION:
Historical anchor: (why this level for the bear case — -1\u03c3, historical \
trough, 25th percentile, or custom? What historical period traded at \
these levels, and are current conditions comparable?)

Structural vs. cyclical: (does the bear case assume the company reverts \
to historical lows due to cyclical weakness, or has something structurally \
changed that justifies permanently lower multiples — growth slowdown, \
margin deterioration, competitive disruption?)

COMPARABILITY:
Historical relevance: (is the historical low period a fair comparison — \
was the company the same size, in the same business mix, with the same \
growth profile? Or has the company fundamentally changed, making \
historical troughs less relevant?)

OVERALL:
Bear narrative: (what market or company conditions would push multiples \
to these levels — earnings disappointment, sector derating, risk-off \
environment, company-specific negative catalyst?)\
"""

STEP_BASE = """\
--- BASE CASE RATIONALE ---

MULTIPLE SELECTION:
Historical anchor: (why this level — historical mean, median, or a \
specific period you consider most representative? If the mean and median \
differ significantly, which is more appropriate and why?)

Current vs. history: (where does the stock currently trade relative to \
your selected base case level? If it trades above or below, what explains \
the current deviation — temporary factors or a fundamental shift?)

REPRESENTATIVENESS:
Time period relevance: (is the full historical window representative of \
the company's current state? Should certain periods be excluded or \
weighted differently — COVID distortion, pre/post M&A, business model \
transition, different growth era?)

Structural breaks: (has anything fundamentally changed about the company \
or its industry that makes historical averages less reliable — new \
management, strategic pivot, regulatory change, competitive landscape \
shift?)

OVERALL:
Base narrative: (do you believe multiples will revert to this historical \
level? Over what timeframe? What drives the reversion — normalization of \
sentiment, earnings trajectory, or valuation discipline?)\
"""

STEP_BULL = """\
--- BULL CASE RATIONALE ---

MULTIPLE SELECTION:
Historical anchor: (why this level for the bull case — +1\u03c3, historical \
peak, 75th percentile, or custom? What historical period traded at these \
levels, and what drove the premium valuation?)

Sustainability: (were the historical peak multiples sustainable, or \
driven by temporary factors — bubble, speculative excess, unsustainable \
earnings trough inflating P/E? Could the company sustain these multiples \
today?)

RE-RATING POTENTIAL:
Structural improvement: (has something improved about the company that \
could justify permanently higher multiples than history — better growth \
profile, higher margins, improved competitive position, better management, \
ESG re-rating?)

OVERALL:
Bull narrative: (what drives the market to re-rate the stock to these \
historical highs — earnings acceleration, sector tailwind, multiple \
expansion across the market, company-specific positive catalyst?)\
"""

COMPARISON = """\
--- SCENARIO COMPARISON ---

RANGE ASSESSMENT:
Historical spread: (how wide is the -1\u03c3 to +1\u03c3 range historically? \
Is this company's valuation volatile or relatively stable? What does the \
width imply about confidence in a historical multiples-based valuation?)

Current positioning: (where in the historical range does the stock \
currently sit — closer to bear, base, or bull? Has it been trending \
in a direction?)

MEAN REVERSION:
Reversion thesis: (do you believe in mean reversion for this stock's \
multiples? If so, over what timeframe — quarters or years? What would \
prevent reversion — structural change, permanently different growth, \
or regime shift in the market?)

CROSS-MODEL CHECK:
Consistency with Comps: (does the historical range align with the Comps \
scenario range? If historical multiples are higher/lower than current \
peer multiples, what explains the gap — the company has changed, or \
the market has changed?)

Consistency with DCF/DDM: (does the historical multiples range overlap \
with your DCF/DDM scenario range? If not, which do you trust more and \
why?)

METRIC RELIABILITY:
Multiple choice: (which historical multiple is most informative for this \
company — P/E, EV/EBITDA, EV/Revenue? Are any distorted by accounting \
changes, cyclicality, or one-time items over the historical period?)\
"""
