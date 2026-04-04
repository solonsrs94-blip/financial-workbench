"""DDM Step 2 templates — Financial sector (per scenario)."""

STEP2_BASE = """\
--- BASE CASE RATIONALE ---

DIVIDEND POLICY:
Current dividend: (what is the current DPS and payout ratio? Is the \
dividend well-covered by earnings? What is management's stated dividend \
policy — target payout ratio, progressive dividend, or opportunistic?)

Dividend track record: (how stable has the dividend been historically \
— any cuts, suspensions, or special dividends? How did the dividend \
perform during the last downturn or financial stress?)

GROWTH ASSUMPTIONS:
DPS growth rates: (what anchors these growth rates — historical DPS \
growth, earnings growth potential, management guidance? Are you assuming \
payout ratio stays constant, expands, or contracts?)

Earnings driver: (what drives the underlying earnings growth that \
supports dividend growth — loan growth, NIM expansion, fee income, \
cost efficiency, share buybacks? Is this sustainable?)

Near-term vs. terminal: (if near-term growth differs from terminal, \
what causes the transition — maturing business, competitive dynamics, \
regulatory changes, capital requirements?)

CAPITAL & REGULATORY:
Capital position: (is the company well-capitalized relative to \
regulatory requirements? How much excess capital exists? Could capital \
requirements change — Basel IV, stress test results, regulatory \
discretion?)

Capital return capacity: (what percentage of earnings can realistically \
be returned as dividends vs. retained for growth and regulatory buffers? \
Are share buybacks competing with dividends for capital allocation?)

Regulatory constraints: (are there any regulatory restrictions on \
dividends — stress test hurdles, MDA thresholds, supervisory \
expectations? How binding are these?)

FINANCIAL HEALTH:
Credit quality: (what is the credit environment — is the loan book \
performing well? What are your assumptions for provision expenses and \
net charge-offs? Any sector or geographic concentrations that create \
risk?)

Balance sheet strength: (is the balance sheet well-positioned — funding \
mix, liquidity, interest rate sensitivity? Are there any asset quality \
concerns?)

OVERALL:
Base case narrative: (steady earnings growth from established franchise, \
stable dividend policy, manageable credit environment, no significant \
regulatory disruption?)\
"""

STEP2_BULL = """\
--- BULL CASE RATIONALE ---

DIVIDEND UPSIDE:
Higher DPS growth drivers: (what enables faster dividend growth than \
base — accelerating earnings, payout ratio expansion, excess capital \
deployment, accretive M&A? Be specific about which assumptions differ \
from base.)

Payout ratio expansion: (if you're assuming higher payout ratio, what \
enables it — lower growth investment needs, excess capital above \
regulatory requirements, management commitment to higher returns? Is \
there precedent?)

EARNINGS DRIVERS:
Revenue upside: (what drives higher earnings — NIM expansion from rate \
environment, stronger loan growth, fee income growth, market share gains? \
For insurance — premium growth, favorable loss ratios, investment income?)

Efficiency gains: (can the company improve its efficiency ratio \
meaningfully? What drives it — technology investment, branch \
rationalization, scale benefits from M&A?)

CAPITAL & REGULATORY:
Capital release: (could regulatory capital requirements ease, releasing \
capital for dividends? Are there non-core assets that could be sold to \
fund additional returns?)

CREDIT QUALITY:
Benign credit: (does the bull case assume better-than-expected credit \
quality — lower provisions, reserve releases, improving economic \
conditions? How much earnings upside comes from lower credit costs vs. \
revenue growth?)

OVERALL:
Bull catalyst: (what triggers the upside — rate environment, regulatory \
easing, M&A, market share gains, capital return program announcement?)

Probability: (how likely? What would you need to see to increase \
confidence — specific financial metrics, regulatory decisions, macro \
conditions?)\
"""

STEP2_BEAR = """\
--- BEAR CASE RATIONALE ---

DIVIDEND RISK:
Dividend cut risk: (is there a realistic scenario where the dividend is \
cut or suspended? What would trigger it — earnings decline, regulatory \
intervention, capital shortfall, credit losses? Has this company or its \
peers cut dividends before?)

Payout sustainability: (at what earnings level does the payout ratio \
become unsustainably high? How far below base case earnings would trigger \
a reassessment of the dividend?)

EARNINGS PRESSURE:
Revenue downside: (what pressures earnings — NIM compression from rate \
changes, slower loan growth, fee income pressure, competitive dynamics? \
For insurance — adverse loss experience, catastrophe losses, reserve \
strengthening?)

Credit deterioration: (what credit scenario are you assuming — mild \
uptick in provisions, moderate credit cycle, or severe stress? What \
sectors or geographies are most vulnerable? What are historical peak \
loss rates for comparable downturns?)

Efficiency pressure: (could costs rise or become sticky while revenue \
declines — regulatory compliance costs, technology investment \
requirements, inability to reduce headcount quickly?)

CAPITAL & REGULATORY:
Capital adequacy: (does the bear case stress capital ratios close to \
regulatory minimums? Would the company need to raise capital, cut \
dividends, or reduce risk-weighted assets? What are the stress test \
implications?)

Regulatory intervention: (could regulators restrict dividends \
preemptively — as happened during COVID? What triggers regulatory \
concern?)

OVERALL:
Bear trigger: (what signals this scenario — credit metrics deteriorating, \
NIM compressing, regulatory tone shifting, macro indicators weakening?)

Dividend floor: (if the dividend is cut, what is the likely new level \
— zero, or a reduced but maintained payout? What determines the floor?)

Probability: (how likely? What macro or credit scenario does this \
assume? Is this a 2008-level stress or a mild credit cycle?)\
"""
