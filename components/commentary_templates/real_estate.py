"""Step 2 templates — Real Estate sector."""

STEP2_BASE = """\
REVENUE:
NOI growth: (what drives net operating income growth — rent escalations, \
occupancy improvements, lease renewals at higher rates, same-property NOI \
growth? What are the lease expiration schedules and renewal assumptions?)

Occupancy: (what occupancy rate are you assuming, and how does it compare \
to historical and market averages? Is there any lease-up risk on vacant \
space or development deliveries?)

Rental rate trajectory: (are market rents rising, stable, or declining? \
What is the mark-to-market opportunity on expiring leases vs. in-place \
rents?)

Portfolio activity: (are you assuming acquisitions, dispositions, or \
development deliveries? At what cap rates and yields?)

PROFITABILITY:
Operating margins: (what drives property-level margins — management \
efficiency, property taxes, insurance, maintenance costs? Are operating \
expenses growing faster or slower than revenue?)

G&A: (is corporate overhead appropriate for portfolio size? Any expected \
changes?)

Interest expense: (what is the debt maturity profile and refinancing \
assumptions? Are you assuming current rates, lower rates, or higher rates \
on refinancing?)

FFO/AFFO:
FFO adjustments: (what non-cash items are you adjusting for? Are you \
using FFO or AFFO as the primary metric, and why?)

Maintenance capex: (what is the recurring capex for tenant improvements, \
leasing commissions, and building maintenance? Is this stable or \
increasing as the portfolio ages?)

CAPEX & NWC:
Development pipeline: (are there development projects underway or \
planned? What are the expected yields on cost vs. market cap rates? \
What is the timeline to stabilization?)

OVERALL:
Base case narrative: (stable portfolio performance, modest rent growth \
in line with market, predictable lease expiration and renewal cycle?)\
"""

STEP2_BULL = """\
REVENUE:
NOI upside: (what drives above-base NOI growth — stronger rent growth, \
faster lease-up, below-market leases rolling to market, portfolio \
repositioning?)

Occupancy gains: (can occupancy exceed base case — tenant demand \
improving, limited new supply, successful leasing of vacant space?)

External growth: (does the bull case include accretive acquisitions or \
development deliveries? At what cap rates, and are there identified \
opportunities?)

PROFITABILITY:
Margin improvement: (what enables better margins — operating \
efficiencies, reduced vacancy costs, scale benefits, technology \
investments in property management?)

Interest expense: (could refinancing at lower rates boost earnings? \
Is there an opportunity to optimize the capital structure?)

FFO/AFFO:
Growth drivers: (which combination drives FFO growth — same-store NOI, \
external growth, lower interest expense, reduced G&A as % of revenue?)

OVERALL:
Bull catalyst: (what triggers the upside — supply shortage, market rent \
spike, portfolio acquisition, interest rate decline, rezoning or \
development approval?)

Probability: (how likely? What market conditions are required?)\
"""

STEP2_BEAR = """\
REVENUE:
NOI risk: (what could weaken NOI — tenant bankruptcies, non-renewals, \
rising vacancy, rent concessions to retain tenants, sublease competition, \
market rent declines?)

Occupancy risk: (what could push occupancy lower — new supply deliveries, \
tenant downsizing, work-from-home impact (if office), e-commerce impact \
(if retail), demand slowdown?)

Tenant credit: (are there concentrated tenant exposures? What happens if \
a major tenant defaults or downsizes? Are there co-tenancy clauses that \
could trigger cascading vacancy?)

PROFITABILITY:
Margin pressure: (what compresses margins — fixed operating costs on \
lower occupancy, rising property taxes or insurance, increased tenant \
inducements and capital?)

Interest rate risk: (what is the impact of higher interest rates on \
refinancing? Are there near-term maturities at risk? What is the \
variable rate exposure?)

FFO/AFFO:
Dividend coverage: (is the dividend safe under the bear case? What is \
the AFFO payout ratio? Would a dividend cut be necessary?)

CAPEX & NWC:
Capital obligations: (are there committed development projects that \
must be completed regardless of market conditions? What is the remaining \
spend and funding source?)

OVERALL:
Bear trigger: (what signals this — rising vacancy in the market, tenant \
watchlist, new supply pipeline, interest rate spike, cap rate expansion?)

Asset value floor: (what are the properties worth in a downturn — \
replacement cost, distressed cap rates, land value? Is there NAV \
downside protection or could assets be impaired?)

Probability: (how likely? What macro or real estate market conditions \
does this assume?)\
"""
