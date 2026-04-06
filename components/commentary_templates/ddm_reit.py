"""DDM Step 2 templates — REIT (per scenario)."""

STEP2_BASE = """\
--- BASE CASE RATIONALE ---

FFO/AFFO vs DIVIDENDS:
Coverage ratio: (what is the AFFO payout ratio — how much cushion \
exists between AFFO per share and dividends per share? Is the REIT \
retaining enough cash for maintenance capex and tenant improvements?)

FFO growth as dividend driver: (what drives FFO/AFFO growth — same-store \
NOI growth, acquisitions, development completions, rent escalators? \
What CAGR are you assuming for AFFO per share?)

TAX-MANDATED PAYOUT:
REIT distribution requirements: (REITs must distribute 90%+ of taxable \
income. Is the company distributing exactly the minimum or well above? \
How does taxable income relate to AFFO — are there depreciation \
differences?)

Special dividends: (does the company pay special dividends from asset \
sales or one-time gains? How should these be treated in the DDM — \
exclude from base DPS growth?)

NAV RELEVANCE:
NAV vs market price: (is the REIT trading at a premium or discount to \
NAV? How does this affect your view of dividend sustainability — a deep \
discount may signal market concerns about asset quality or leverage?)

Asset quality: (what is the quality of the property portfolio — \
occupancy rates, lease terms, tenant creditworthiness, location quality? \
Are there assets that may need significant reinvestment?)

PROPERTY FUNDAMENTALS:
Rent growth: (what is the same-store rent growth assumption — in-place \
rent vs. market rent, lease expiration schedule, renewal spreads? How \
does this drive NOI and FFO growth?)

Occupancy: (is occupancy stable, improving, or at risk? What is the \
vacancy rate vs. submarket average? Are there large tenant expirations \
approaching?)

DEVELOPMENT PIPELINE:
Pipeline contribution: (does the REIT have a development pipeline that \
will contribute to future FFO growth? What yields-on-cost are expected? \
When do projects deliver?)

OVERALL:
Base case narrative: (stable property fundamentals, predictable FFO \
growth from rent escalators and development, sustainable payout ratio \
with adequate retained cash for reinvestment?)\
"""

STEP2_BULL = """\
--- BULL CASE RATIONALE ---

DIVIDEND ACCELERATION:
Higher DPS growth drivers: (what enables faster dividend growth — \
stronger rent growth, accretive acquisitions, development completions, \
occupancy improvement, payout ratio expansion?)

AFFO per share growth: (could AFFO grow faster than base — share \
buybacks at discount to NAV, accretive capital recycling, operating \
leverage from occupancy gains?)

PROPERTY UPSIDE:
Rent growth acceleration: (what drives above-trend rent growth — supply \
constraints, demand drivers, below-market lease roll-ups, favorable \
demographics?)

Occupancy upside: (could occupancy improve beyond base — limited new \
supply, tenant expansion, market recovery?)

CAPITAL MARKETS:
Acquisition opportunities: (could favorable capital markets enable \
accretive acquisitions — spreads between cap rates and cost of capital? \
Are there motivated sellers?)

NAV re-rating: (could the market re-price the REIT closer to or above \
NAV — catalyst could be asset sales at premiums, privatization interest, \
sector rotation?)

OVERALL:
Bull catalyst: (what triggers the upside — supply tightening, demand \
acceleration, capital markets improvement, portfolio optimization?)

Probability: (how likely? What property market or macro conditions \
would confirm this?)\
"""

STEP2_BEAR = """\
--- BEAR CASE RATIONALE ---

DIVIDEND RISK:
Payout pressure: (could AFFO decline to where the payout ratio becomes \
unsustainable? What tenant losses, occupancy declines, or rent \
reductions would trigger a dividend reassessment?)

Dividend cut history: (has this REIT or comparable REITs cut dividends \
before — during GFC, COVID, or sector downturns? What were the triggers \
and magnitude of cuts?)

PROPERTY STRESS:
Occupancy decline: (what drives lower occupancy — tenant bankruptcy, \
lease non-renewals, new supply, secular demand shifts? What is the \
impact on NOI per dollar of occupancy loss?)

Rent pressure: (could market rents decline or renewal spreads turn \
negative? What is the exposure to lease expirations in weak submarkets?)

BALANCE SHEET:
Leverage risk: (is the REIT's leverage manageable in a downturn — \
debt/EBITDA, interest coverage, debt maturity schedule? Could \
refinancing costs increase materially?)

Access to capital: (could capital markets close for REITs — rising \
rates, widening spreads, equity issuance at deep discount to NAV? \
How does this constrain growth and dividend capacity?)

OVERALL:
Bear trigger: (what signals this scenario — tenant credit deterioration, \
new supply deliveries, interest rate spike, cap rate expansion?)

Dividend floor: (would the REIT cut to the minimum distribution \
requirement, or could it suspend entirely via special election? What \
determines the floor?)

Probability: (how likely? What property market or macro scenario does \
this assume?)\
"""
