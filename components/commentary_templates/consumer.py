"""Step 2 templates — Consumer sector."""

STEP2_BASE = """\
REVENUE:
Growth rates: (what supports these rates — same-store sales trends, \
store count growth, e-commerce penetration, category growth rates? Are \
you assuming the consumer environment remains stable?)

Volume vs. pricing: (is growth driven by traffic/units, pricing/ticket \
size, or channel mix? What is the consumer's price sensitivity in this \
category?)

Brand and market position: (is the brand gaining or losing relevance? \
Are you assuming stable market share?)

Seasonality: (are there seasonal patterns that affect projections? Are \
you normalizing for any one-time events in the historical base?)

PROFITABILITY:
Gross margin: (what drives product margin — input costs, sourcing, \
promotional intensity, channel mix between wholesale/DTC/e-commerce? \
Are input costs at normalized levels?)

SGA and marketing: (what is the marketing spend trajectory? Is the \
company investing in brand building or harvesting? Any channel transition \
costs — e.g., building out DTC or e-commerce infrastructure?)

Tax rate: (effective or statutory? Any considerations?)

CAPEX & NWC:
Store investment: (if brick-and-mortar — new stores, remodels, or \
closures? What is the capex per store? If e-commerce — fulfillment, \
logistics, technology?)

Inventory management: (is inventory well-managed historically? Any \
markdown or obsolescence risk? Seasonal inventory build patterns?)

OVERALL:
Base case narrative: (steady brand performance, stable consumer \
environment, predictable growth from established channels?)\
"""

STEP2_BULL = """\
REVENUE:
Upside drivers: (what accelerates growth — new store openings, category \
expansion, successful product launches, DTC growth, international \
expansion, market share gains from weaker competitors?)

Brand momentum: (is there evidence of strengthening brand — social \
engagement, customer acquisition trends, market research? Is the brand \
in an upcycle?)

Pricing power: (can the company raise prices without volume loss? What \
supports this — brand strength, limited substitutes, premiumization \
trend?)

PROFITABILITY:
Margin expansion: (what enables higher margins — channel mix shift to \
DTC, scale in e-commerce, input cost deflation, reduced promotional \
activity, operating leverage?)

CAPEX & NWC:
Growth investment: (does the bull case require accelerated store \
openings or fulfillment buildout? What is the payback period on \
incremental investment?)

OVERALL:
Bull catalyst: (what drives the upside — viral product, consumer trend \
tailwind, competitor exit, successful rebranding or repositioning?)

Probability: (how likely? What consumer or company data would \
confirm this?)\
"""

STEP2_BEAR = """\
REVENUE:
Downside drivers: (what weakens growth — consumer spending slowdown, \
brand fatigue, competitive inroads, channel disruption, trade-down to \
private label or lower-priced alternatives?)

Consumer sensitivity: (how discretionary is this product? In a downturn, \
does the consumer cut back, trade down, or defer purchases?)

Market share risk: (who takes share — private label, emerging brands, \
direct competitors, Amazon or other platforms? What is the mechanism?)

PROFITABILITY:
Margin pressure: (what compresses margins — promotional intensity to \
defend share, input cost inflation that can't be passed through, \
deleverage on same-store sales declines, markdowns on unsold inventory?)

Cost response: (can the company cut marketing or SGA without accelerating \
the brand decline? Are there store closure costs or lease obligations \
that limit flexibility?)

CAPEX & NWC:
Inventory risk: (does weaker demand lead to inventory buildup and \
markdowns? How quickly can the supply chain adjust?)

Store portfolio: (are there underperforming stores that become \
liabilities? What are the lease terms and closure costs?)

OVERALL:
Bear trigger: (what signals this — falling traffic, same-store sales \
misses, rising promotional spend, consumer confidence data?)

Brand durability: (does the brand have staying power through a downturn, \
or is it vulnerable to permanent impairment?)

Probability: (how likely? What consumer macro scenario does this \
assume?)\
"""
