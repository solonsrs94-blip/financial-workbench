"""Step 2 templates — Energy / Utilities sector."""

STEP2_BASE = """\
REVENUE:
Growth rates: (what drives revenue — commodity price assumptions, \
production volume, rate base growth, customer additions, regulatory rate \
decisions? What commodity price deck are you using and why?)

Volume vs. price: (is growth driven by production/output increases, \
commodity price assumptions, or regulated rate increases? For utilities \
— what is the allowed ROE and rate base growth?)

Commodity exposure: (how hedged is the company? What percentage of \
revenue is contracted vs. spot? What is the hedge book duration?)

Regulatory environment: (for regulated businesses — what is the \
regulatory calendar? Any pending rate cases, ROE reviews, or regulatory \
policy changes?)

PROFITABILITY:
Operating costs: (what are the key cost drivers — lifting costs, fuel \
costs, labor, maintenance? How do costs scale with production/output?)

Depletion and DD&A: (for E&P — what are depletion assumptions? For \
utilities — what is the depreciation trajectory as rate base grows?)

Tax rate: (are there tax incentives — production tax credits, renewable \
energy credits, depletion allowances, tax equity structures?)

CAPEX & NWC:
Capital program: (what is the capital program — maintenance, growth, \
regulatory compliance, energy transition? Is this a heavy investment \
period or steady state?)

Reserve replacement / rate base: (for E&P — what are the reserve \
replacement assumptions and finding costs? For utilities — what is the \
rate base growth rate from the capital plan?)

Working capital: (any commodity-related working capital swings — margin \
calls, inventory, receivables?)

OVERALL:
Base case narrative: (stable commodity/regulatory environment, steady \
operational execution, predictable capital program?)\
"""

STEP2_BULL = """\
REVENUE:
Commodity upside: (for E&P — what commodity price scenario drives the \
bull case? What fundamental supports higher prices — supply constraints, \
demand growth, geopolitical risk?)

Volume upside: (what drives higher production/output — successful \
exploration, capacity expansion, debottlenecking, better-than-expected \
reservoir performance or wind/solar output?)

Regulatory tailwind: (for utilities — could the regulator approve \
higher ROE, faster rate base additions, or favorable recovery \
mechanisms? Any constructive regulatory precedent?)

PROFITABILITY:
Margin expansion: (what enables higher margins — commodity price \
leverage, cost efficiencies, favorable hedges rolling off into higher \
spot prices, economies of scale?)

CAPEX & NWC:
Investment returns: (does the bull case require additional investment? \
What are the expected returns on incremental capital — IRRs on new \
projects, rate base additions, reserve additions at favorable F&D costs?)

OVERALL:
Bull catalyst: (what triggers the upside — commodity price increase, \
regulatory decision, new discovery, project completion, energy policy \
change?)

Probability: (how likely? What macro or regulatory conditions are \
required?)\
"""

STEP2_BEAR = """\
REVENUE:
Commodity downside: (for E&P — what price scenario drives the bear \
case? What could push prices lower — oversupply, demand destruction, \
recession, OPEC decisions, energy transition acceleration?)

Volume risk: (what could reduce output — operational problems, \
regulatory restrictions, resource depletion, permitting delays, \
weather/natural disasters?)

Regulatory risk: (for utilities — could the regulator deny rate \
increases, lower allowed ROE, impose unfavorable cost recovery \
mechanisms, or mandate expensive compliance investments with uncertain \
recovery?)

PROFITABILITY:
Margin compression: (what compresses margins — commodity price declines \
with sticky costs, rising operating costs, increased royalty or tax \
burden, unfavorable hedge positions?)

Impairment risk: (at what commodity price level do assets face \
impairment? Are there goodwill or PP&E write-down risks?)

CAPEX & NWC:
Capital flexibility: (can the capital program be deferred or cut in a \
downturn? What is the minimum maintenance capex? Are there contractual \
commitments — rigs, pipelines, construction contracts?)

Dividend sustainability: (is the dividend safe in the bear case? What \
is the breakeven commodity price for covering dividends and maintenance \
capex?)

OVERALL:
Bear trigger: (what signals this — commodity price decline, regulatory \
adverse decision, operational incident, policy change?)

Asset floor: (what is the base value — PDP reserves, regulated asset \
base, contracted cash flows? Does the balance sheet withstand this \
scenario without distress?)

Probability: (how likely? What macro scenario does this assume?)\
"""
