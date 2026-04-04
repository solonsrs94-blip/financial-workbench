"""Step 2 templates — Industrials / Manufacturing sector."""

STEP2_BASE = """\
REVENUE:
Growth rates: (what anchors these rates — order backlog, capacity \
utilization, end-market demand forecasts, historical cycle patterns? Are \
you assuming mid-cycle conditions?)

Volume vs. pricing: (is growth driven by unit volume increases, \
pricing/inflation pass-through, or both? What is the pricing environment \
in the industry?)

Cyclicality: (where are we in the cycle? Are you assuming the cycle \
continues, peaks, or normalizes? What indicators are you watching?)

PROFITABILITY:
Gross margin: (what drives gross margin — input costs, manufacturing \
efficiency, product mix, capacity utilization? Are raw material costs at \
normal levels?)

Operating leverage: (what is the fixed vs. variable cost split? How \
sensitive are margins to revenue changes?)

Restructuring or initiatives: (are there any in-flight cost programs, \
plant rationalizations, or automation investments that affect margins?)

Tax rate: (effective or statutory? Any jurisdiction mix considerations?)

CAPEX & NWC:
Maintenance vs. growth capex: (what is the maintenance capex baseline? \
Is the company in an expansion or replacement cycle? Any large committed \
projects?)

Working capital intensity: (how significant is inventory and receivables? \
Are there seasonal patterns? Is the cash conversion cycle stable?)

OVERALL:
Base case narrative: (what does normal look like for this business — \
steady demand, stable margins, predictable capex cycle?)\
"""

STEP2_BULL = """\
REVENUE:
Upside drivers: (what drives above-base growth — cycle upturn, market \
share gains, new contracts, capacity expansion coming online, geographic \
expansion, M&A? Be specific.)

Order backlog: (is there evidence of strengthening demand — rising orders, \
longer backlogs, improving lead indicators?)

Pricing power: (can the company push through above-inflation price \
increases? What gives them leverage — proprietary technology, limited \
competition, switching costs?)

PROFITABILITY:
Margin expansion: (what enables higher margins — operating leverage on \
higher volumes, input cost tailwinds, mix shift toward higher-margin \
products, benefits from prior restructuring?)

Capacity utilization: (does the bull case push utilization above historical \
averages? At what point do capacity constraints limit upside?)

CAPEX & NWC:
Expansion investment: (does the bull case require incremental capex for \
capacity? Is this already committed or would it need new approval? What \
is the lag between investment and revenue?)

OVERALL:
Bull catalyst: (what triggers the upside — cycle recovery, contract win, \
end-market inflection? How visible is this currently?)

Probability: (how likely? What early indicators would confirm this \
scenario?)\
"""

STEP2_BEAR = """\
REVENUE:
Downside drivers: (what causes weakness — cyclical downturn, end-market \
demand decline, contract loss, competitive undercutting, destocking in \
the supply chain? How deep and how long?)

Cycle risk: (if this is a cyclical downturn, what does the historical \
trough look like? Are you assuming a mild correction or a full recession?)

Volume vulnerability: (which segments or customers are most at risk? Is \
revenue concentrated in a way that creates downside risk?)

PROFITABILITY:
Margin compression: (how much margin is at risk — deleverage on lower \
volumes, inability to cut fixed costs, input cost inflation without \
pricing offset, unfavorable mix?)

Cost rigidity: (which costs are fixed — labor, leases, depreciation? \
How quickly can management respond with cost cuts? Any contractual \
commitments that limit flexibility?)

Restructuring risk: (would a downturn trigger restructuring charges, \
plant closures, or impairments? Factor these in if material.)

CAPEX & NWC:
Working capital risk: (does a slowdown cause inventory buildup or \
receivables deterioration? How much cash could be trapped in working \
capital?)

Capex floor: (can maintenance capex be deferred, or is there a hard \
floor? Any committed expansion projects that can't be cancelled?)

OVERALL:
Bear trigger: (what signals this scenario — falling orders, rising \
inventories, end-market data, competitor behavior?)

Trough value: (what is the floor — asset value, replacement cost, \
strategic value to an acquirer? Does this business survive a prolonged \
downturn without financial stress?)

Probability: (how likely? What macro or industry conditions would \
trigger it?)\
"""
