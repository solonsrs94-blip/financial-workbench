"""Step 4 Terminal Value templates — per scenario, all sectors."""

STEP4_BASE = """\
TERMINAL GROWTH:
Growth rate basis: (what anchors the terminal growth rate — long-term GDP \
growth, inflation expectations, industry long-term growth rate? Why is \
this rate sustainable in perpetuity?)

Comparison to economy: (how does your terminal growth rate compare to \
long-term nominal GDP? If above GDP, why can this company permanently \
outgrow the economy? If below, why?)

METHOD:
Approach: (perpetuity growth, exit multiple, or both as cross-check? \
Why this choice?)

Exit multiple: (if applicable — what comparable is the exit multiple \
based on? Is it consistent with the terminal growth rate implied by the \
perpetuity method?)

SANITY CHECK:
TV as % of EV: (what percentage of enterprise value comes from terminal \
value? If above 70-80%, are you comfortable with that given the base \
case assumptions?)

Implied terminal margin: (what profitability does the terminal year \
imply? Is this a realistic steady-state margin for this business?)\
"""

STEP4_BULL = """\
TERMINAL GROWTH:
Growth rate vs. base: (why is terminal growth higher than base — does \
the bull case assume permanently higher market position, industry \
leadership, or structural growth advantages? Is this defensible as a \
perpetuity assumption?)

Sustainability: (could a competitor or disruption erode this terminal \
growth rate? Are you assuming the bull case advantages persist forever, \
and is that realistic?)

METHOD:
Consistency: (are you using the same terminal value method as base? If \
using an exit multiple, is it higher than base, and what justifies the \
premium?)

SANITY CHECK:
TV dominance: (does terminal value represent an even larger share of EV \
in the bull case? If so, how confident are you in assumptions 10+ years \
out?)\
"""

STEP4_BEAR = """\
TERMINAL GROWTH:
Growth rate vs. base: (why is terminal growth lower — does the bear case \
assume permanent competitive damage, industry decline, or structural \
headwinds? Or is this simply a more conservative view of the same \
business?)

Secular vs. cyclical: (is the lower terminal growth a "the company \
matures" story or a "the industry faces secular decline" story? This \
distinction matters significantly for terminal value.)

METHOD:
Consistency: (same method as base? If using an exit multiple, is it \
lower, and does that reflect a permanently less attractive business or \
just current market pessimism?)

SANITY CHECK:
Floor value: (does the bear case terminal value imply the business is \
worth less than its current tangible assets? If so, is that realistic, \
or does it suggest your bear case is too aggressive?)\
"""
