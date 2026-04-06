"""DDM Step 2 templates — Cyclical Dividend (per scenario)."""

STEP2_BASE = """\
--- BASE CASE RATIONALE ---

THROUGH-CYCLE SUSTAINABILITY:
Cycle position: (where is the company in the current industry cycle — \
early recovery, mid-cycle expansion, late cycle, or downturn? How does \
cycle position affect your dividend growth assumptions?)

Through-cycle earnings: (what is the normalized mid-cycle earnings \
level? Is the current dividend well-covered by mid-cycle earnings, not \
just current peak or trough earnings?)

DIVIDEND POLICY:
Progressive vs variable: (does the company follow a progressive policy \
— steady increases regardless of cycle — or a variable policy with a \
base dividend plus variable/special component? How should you model each?)

Base dividend floor: (what is the minimum "base" dividend the company \
would maintain through a downturn? Is this explicitly communicated by \
management or implied by historical behavior?)

DIVIDEND CUT HISTORY:
Past cuts: (has the company cut dividends before — when, by how much, \
and why? How quickly were dividends restored after the cut? What does \
the history tell you about management's commitment to the dividend?)

Peer behavior: (how have peers managed dividends through recent cycles? \
Is there an industry norm for dividend policy during downturns?)

COMMODITY / CYCLE EXPOSURE:
Earnings sensitivity: (how sensitive are earnings to commodity prices, \
end-market demand, or economic cycles? What is the revenue/earnings \
beta to the cycle driver?)

Hedging and contracts: (does the company hedge commodity exposure or \
have fixed-price contracts that reduce near-term earnings volatility? \
How far out does the hedge book extend?)

BALANCE SHEET BUFFER:
Financial flexibility: (does the balance sheet provide sufficient buffer \
to maintain dividends through a downturn — net debt/EBITDA, interest \
coverage, cash reserves, undrawn credit facilities?)

Capital allocation priority: (where do dividends rank in capital \
allocation — after debt service and maintenance capex but before growth \
capex and buybacks? Would management sacrifice growth to protect the \
dividend?)

OVERALL:
Base case narrative: (mid-cycle earnings support current dividend with \
moderate growth, balance sheet provides buffer for cyclical downturn, \
management has demonstrated commitment to dividend through past cycles?)\
"""

STEP2_BULL = """\
--- BULL CASE RATIONALE ---

DIVIDEND ACCELERATION:
Higher DPS growth drivers: (what enables faster dividend growth — \
cycle upswing lifting earnings above mid-cycle, special dividends from \
excess cash, payout ratio increase as cycle matures, share buybacks \
boosting per-share metrics?)

Supernormal returns: (if the company is in an upcycle, how much of \
the earnings uplift flows to dividends vs. debt reduction, capex, or \
reserves? What is the variable dividend component?)

CYCLE UPSIDE:
Demand strength: (what drives stronger-than-expected demand — economic \
recovery, restocking, infrastructure investment, supply constraints? \
How long could the upcycle last?)

Pricing power: (could product/commodity prices rise above base \
expectations? What is the operating leverage — how much incremental \
earnings per dollar of revenue upside?)

BALANCE SHEET:
Deleveraging benefit: (could strong cash flows accelerate deleveraging, \
enabling higher dividends sooner? Could the company reach a leverage \
target that triggers increased returns?)

OVERALL:
Bull catalyst: (what triggers the upside — commodity price surge, demand \
recovery, supply disruption, competitor exit, capacity tightening?)

Probability: (how likely? Where are we in the cycle? What leading \
indicators would confirm this?)\
"""

STEP2_BEAR = """\
--- BEAR CASE RATIONALE ---

DIVIDEND RISK:
Cut probability: (how likely is a dividend cut in a downturn — based \
on historical behavior, balance sheet capacity, and management signals? \
What is the expected magnitude of a cut — 25%, 50%, suspension?)

Trigger point: (at what earnings or cash flow level would the company \
cut — is there a specific payout ratio ceiling, leverage ratio, or \
liquidity threshold that would force action?)

CYCLE DOWNSIDE:
Demand collapse: (what drives a significant demand decline — recession, \
destocking, substitution, overcapacity? How severe and how long could \
the downturn last based on historical cycles?)

Pricing pressure: (could commodity/product prices fall significantly — \
what is the cost curve support level? How quickly does earnings \
deteriorate below that level?)

BALANCE SHEET STRESS:
Covenant risk: (could a downturn push leverage ratios toward covenant \
limits? Would the company need to preserve cash by cutting dividends \
to avoid covenant breach or credit downgrade?)

Refinancing risk: (are there significant debt maturities during the \
projection period? Could refinancing at higher rates or in stressed \
markets consume cash that would otherwise fund dividends?)

OVERALL:
Bear trigger: (what signals this scenario — leading indicators turning \
down, inventory building, pricing weakness, peer dividend cuts, credit \
spread widening?)

Dividend floor: (would the company cut to a sustainable base level, \
suspend entirely, or switch to a variable-only policy? What determines \
the floor — maintenance capex needs, debt service, minimum liquidity?)

Probability: (how likely? What stage of the cycle are we in? What \
historical analogue does this bear case resemble?)\
"""
