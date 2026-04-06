"""DDM Step 2 templates — Utility / Infrastructure (per scenario)."""

STEP2_BASE = """\
--- BASE CASE RATIONALE ---

RATE BASE GROWTH:
Capital investment plan: (what is the planned rate base growth — \
transmission upgrades, distribution hardening, renewable integration, \
grid modernization? What CAGR does this imply for rate base over the \
projection period?)

Regulatory allowed ROE: (what is the current allowed ROE across \
jurisdictions? Is the regulatory environment constructive, neutral, or \
hostile? How quickly are rate cases processed?)

DIVIDEND POLICY:
DPS growth link to earnings: (is DPS growth explicitly tied to rate \
base growth and earnings growth? What is the target payout ratio — \
typically 60-75% for utilities? Is the payout ratio at, above, or \
below target?)

Regulatory risk to dividends: (could regulatory decisions reduce \
earnings below dividend coverage thresholds? How much cushion exists \
between earned ROE and dividend requirements?)

CAPEX RECOVERY:
Rate case outcomes: (are capital investments being recovered through \
rate adjustments in a timely manner? Are there any disallowances or \
prudency reviews pending? What is the regulatory lag?)

Rider mechanisms: (does the company benefit from infrastructure riders \
or trackers that reduce regulatory lag? What percentage of capex is \
recovered through automatic mechanisms vs. rate cases?)

ENERGY TRANSITION:
Renewable integration: (how is the transition to renewables affecting \
capital needs and earnings? Are renewable investments earning comparable \
returns? What is the stranded asset risk for fossil generation?)

Load growth: (is electrification — EVs, heat pumps, data centers — \
driving load growth? How does this affect capital needs and rate base?)

OVERALL:
Base case narrative: (steady rate base growth driving predictable \
earnings and dividend growth, constructive regulatory environment, \
manageable transition risks?)\
"""

STEP2_BULL = """\
--- BULL CASE RATIONALE ---

DIVIDEND ACCELERATION:
Higher DPS growth drivers: (what enables faster dividend growth — \
accelerated rate base growth, higher allowed ROE, payout ratio \
expansion, favorable rate case outcomes?)

Constructive regulation: (could regulatory outcomes exceed expectations \
— higher allowed ROE, faster cost recovery, favorable treatment of \
new investments?)

EARNINGS UPSIDE:
Rate base acceleration: (what drives faster rate base growth — grid \
hardening mandates, renewable targets, electrification, transmission \
buildout? Federal incentives or subsidies?)

Load growth: (could electrification or data center demand drive \
higher-than-expected load growth? How does this flow through to \
earnings?)

CAPITAL RETURN:
Balance sheet optimization: (could the company increase leverage \
toward optimal capital structure, freeing cash for dividends? Is there \
room for holding company activities or unregulated earnings?)

OVERALL:
Bull catalyst: (what triggers the upside — policy mandates, technology \
cost declines, constructive rate cases, load growth surprises?)

Probability: (how likely? What regulatory or macro developments \
would confirm this scenario?)\
"""

STEP2_BEAR = """\
--- BEAR CASE RATIONALE ---

DIVIDEND RISK:
Regulatory risk: (could adverse rate case outcomes compress earned ROE \
below dividend coverage? What jurisdictions pose the greatest risk? \
Are there pending regulatory proceedings with uncertain outcomes?)

Equity issuance dilution: (could large capex programs require equity \
issuance that dilutes DPS growth even as total dividends grow? How \
much external equity is in the financing plan?)

EARNINGS PRESSURE:
Disallowances: (could regulators disallow recovery of certain \
investments — coal plant retirements, storm costs, nuclear projects? \
What is the magnitude of exposure?)

ROE compression: (are allowed ROEs trending down as interest rates \
change? How does authorized vs. earned ROE gap affect earnings?)

OPERATIONAL RISKS:
Storm and weather exposure: (what is the exposure to extreme weather \
events — hurricanes, wildfires, winter storms? Is insurance adequate? \
Could liabilities exceed expectations?)

Stranded assets: (are there stranded asset risks from premature fossil \
plant retirements? How are these being recovered or absorbed?)

OVERALL:
Bear trigger: (what signals this scenario — adverse regulatory \
decisions, rising interest rates, large storm events, political \
intervention in rate-setting?)

Dividend floor: (would the company cut or freeze dividends, or slow \
growth? What determines the floor — minimum payout ratio, credit \
rating targets, regulatory constraints?)

Probability: (how likely? What regulatory or macro scenario does \
this assume?)\
"""
