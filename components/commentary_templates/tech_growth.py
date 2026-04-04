"""Step 2 templates — Technology / Growth sector."""

STEP2_BASE = """\
REVENUE:
Growth rates: (what anchors these as the most likely outcome — historical \
growth trend, management guidance, consensus estimates, or your own model? \
Are you assuming current growth rates persist, decelerate naturally, or \
stabilize at a mature level?)

TAM & penetration: (what is the addressable market and current penetration? \
Does the base case assume the company maintains its current share, or are \
you baking in modest gains/losses?)

Revenue mix: (are there multiple segments or products? Which segments drive \
growth, and are you assuming any mix shift?)

PROFITABILITY:
Gross margin: (is the business at scale or still scaling? Are you assuming \
stable unit economics, or is there a margin trajectory?)

Operating leverage: (how do R&D and SGA scale in the base case — ratio \
stable, improving, or investing ahead of growth? Is the company profitable \
or on a path to profitability?)

Stock-based compensation: (is SBC material? Are you treating it as a real \
expense in your projections?)

Tax rate: (effective or statutory? Any NOLs or tax attributes to consider?)

CAPEX & NWC:
Capital intensity: (is this asset-light? What is capex primarily — servers, \
infrastructure, capitalized development? Are you assuming capex/revenue \
ratio is stable?)

Working capital: (is the business working-capital-light? Any deferred \
revenue dynamics or significant receivables?)

OVERALL:
Base case narrative: (in 2-3 sentences, what is the story — steady \
execution on current trajectory? Why is this the most likely outcome?)\
"""

STEP2_BULL = """\
REVENUE:
Upside drivers: (what accelerates growth beyond base — faster TAM \
expansion, market share gains from competitors, successful new product \
launches, geographic expansion, upsell/cross-sell? Be specific about which \
assumptions differ from base and by how much.)

TAM expansion: (is the bull case driven by a larger market than base \
assumes, or better execution within the same market? Are there adjacent \
markets the company could enter?)

Plausibility: (has the company or its peers achieved these growth rates \
before? What evidence supports this acceleration — recent quarterly trends, \
product launches, customer wins?)

PROFITABILITY:
Margin expansion path: (what enables higher margins than base — operating \
leverage on faster growth, improving unit economics, mix shift toward \
higher-margin products, reduced customer acquisition costs?)

Scale effects: (at what revenue level do you expect meaningful operating \
leverage? Is the bull case above that threshold?)

CAPEX & NWC:
Investment needs: (does faster growth require proportionally more capex, \
or does the business scale efficiently? If you kept capex at base levels \
with higher revenue, is that realistic?)

OVERALL:
Bull catalyst: (what specific event or trend triggers this scenario — \
product launch, market expansion, competitor stumble, macro tailwind? How \
observable is this catalyst?)

Probability: (how likely is this scenario? What would you need to see in \
the next 1-2 quarters to increase confidence?)\
"""

STEP2_BEAR = """\
REVENUE:
Downside drivers: (what slows growth — competitive pressure, market \
saturation, customer churn, pricing erosion, loss of key customers, \
regulatory headwinds? Is this a deceleration or an actual decline?)

Competitive risk: (who is the competitive threat — incumbents, new \
entrants, or substitute products? What is the mechanism of share loss?)

Severity: (is this a mild disappointment vs. base, or a significant \
deterioration? Why this level of severity — what scenario would be even \
worse, and why is that less likely?)

PROFITABILITY:
Margin pressure: (what compresses margins — loss of pricing power, higher \
customer acquisition costs, inability to cut R&D without damaging the \
product, deleverage on lower revenue?)

Cost flexibility: (which costs can management cut quickly, and which are \
sticky? Would cost cuts damage long-term competitiveness?)

CAPEX & NWC:
Stranded investment: (if growth disappoints, is there risk of overcapacity \
or sunk investment that doesn't generate returns?)

OVERALL:
Bear trigger: (what observable signal tells you this scenario is playing \
out — slowing bookings, rising churn, competitive wins by rivals, macro \
deterioration?)

Downside floor: (is there a floor on value — recurring revenue base, \
switching costs, strategic acquirer interest, IP value? Or could things \
deteriorate further than this bear case?)

Probability: (how likely is this scenario? What would you need to see to \
increase its probability?)\
"""
