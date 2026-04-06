"""DDM Step 2 templates — Consumer / Dividend Aristocrat (per scenario)."""

STEP2_BASE = """\
--- BASE CASE RATIONALE ---

PAYOUT TRAJECTORY:
Current payout: (what is the current payout ratio vs. historical average? \
Is management targeting a specific payout ratio or prioritizing absolute \
DPS growth? How much room exists between current and target payout?)

DPS vs EPS growth: (is DPS growing faster or slower than EPS? If faster, \
payout ratio is expanding — is this deliberate or unsustainable? What is \
the long-term relationship between dividend growth and earnings growth?)

DIVIDEND STREAK:
Streak commitment: (how long is the dividend increase streak? Is this \
a Dividend Aristocrat / King? How important is the streak to management \
and investor base? What would it take for management to break the streak?)

Minimum raise dynamics: (in lean years, has the company done token raises \
to preserve the streak? What does the minimum raise tell you about \
management's confidence in the business?)

FRANCHISE DURABILITY:
Brand and pricing power: (does the company have pricing power sufficient \
to grow earnings and dividends through inflation? How defensible are \
market shares? What competitive threats exist?)

Revenue stability: (how cyclical is demand? What percentage of revenue is \
recurring or subscription-based? Geographic and product diversification?)

CAPITAL ALLOCATION:
Buyback interaction: (how do buybacks interact with dividends — does the \
company use buybacks as the flexible component while dividends are \
sacrosanct? What is the total shareholder yield?)

Investment needs: (what organic investment is required to maintain the \
franchise — capex, R&D, marketing? Could investment needs crowd out \
dividend growth?)

OVERALL:
Base case narrative: (steady franchise generating predictable earnings \
growth, committed to dividend growth, payout ratio stable or gradually \
expanding within sustainable bounds?)\
"""

STEP2_BULL = """\
--- BULL CASE RATIONALE ---

DIVIDEND ACCELERATION:
Higher DPS growth drivers: (what enables faster dividend growth — \
accelerating earnings, deliberate payout expansion, share count reduction \
via buybacks, margin expansion from pricing power? Which assumptions \
differ from base?)

Payout ratio expansion: (if assuming higher payout, what enables it — \
lower reinvestment needs, mature growth phase, management guidance toward \
higher shareholder returns?)

EARNINGS UPSIDE:
Revenue drivers: (what drives higher revenue — market share gains, \
pricing power, new product categories, international expansion, \
channel growth? How realistic are these catalysts?)

Margin expansion: (can margins improve — input cost deflation, \
operating leverage, mix shift to higher-margin products, supply chain \
optimization?)

CAPITAL RETURN:
Accelerated buybacks: (could share repurchase accelerate, boosting \
per-share metrics? What triggers increased buyback activity — low \
valuation, excess cash, activist pressure?)

OVERALL:
Bull catalyst: (what triggers the upside — category growth, competitive \
exit, pricing cycle, M&A synergies, portfolio optimization?)

Probability: (how likely? What would you need to see — specific sales \
trends, margin improvements, capital allocation announcements?)\
"""

STEP2_BEAR = """\
--- BEAR CASE RATIONALE ---

DIVIDEND RISK:
Streak break scenario: (under what conditions would the company cut or \
freeze dividends — severe earnings decline, balance sheet stress, \
transformational M&A? Has the company ever cut dividends before?)

Payout sustainability: (at what EPS level does the payout ratio become \
unsustainable? How close is the bear-case EPS to that threshold?)

EARNINGS PRESSURE:
Revenue threats: (what pressures revenue — market share loss to private \
label or disruptors, channel shift, category decline, consumer trade-down? \
How severe and how persistent?)

Margin compression: (what compresses margins — input cost inflation, \
promotional intensity, mix deterioration, volume deleverage? Can the \
company pass through costs?)

BALANCE SHEET:
Debt burden: (does debt servicing constrain dividend capacity in a \
downturn? What are covenant risks? Could a credit downgrade force \
capital allocation changes?)

OVERALL:
Bear trigger: (what signals this scenario — market share data, pricing \
surveys, input cost trends, consumer confidence, retailer inventory?)

Dividend floor: (if growth slows, what is the likely minimum DPS — \
flat dividend, token raise, or outright cut? What determines the floor?)

Probability: (how likely? What macro or competitive scenario does this \
assume?)\
"""
