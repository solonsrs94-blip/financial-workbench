"""Step 5 Scenario Comparison template — shared across scenarios."""

STEP5_COMPARISON = """\
PROBABILITY WEIGHTING:
Assigned weights: (what probability do you assign each scenario — e.g., \
Bull 20% / Base 60% / Bear 20%? What drives this allocation? Is there \
more uncertainty on the upside or downside?)

Weighted fair value: (what is the probability-weighted implied share \
price? Do you consider this your point estimate of fair value?)

RANGE ANALYSIS:
Spread assessment: (is the gap between bull and bear implied prices wide \
or narrow relative to the current stock price? What does this say about \
the risk/reward and the predictability of this business?)

Asymmetry: (is there more upside to bull than downside to bear, or vice \
versa? What does this imply for the investment decision — is this a \
skewed bet?)

MARKET POSITIONING:
Current pricing: (which scenario does the current stock price most \
closely reflect — bull, base, or bear? Is the market pricing in your \
base case, or leaning toward one extreme?)

Mispricing thesis: (if you believe the stock is mispriced, which \
scenario is the market missing, and why might the market be wrong? \
What would cause the market to reprice?)

MODEL CONSISTENCY:
Cross-model check: (do your DCF scenario results align with the ranges \
from Comps and Historical Multiples? If DCF bull is higher than the top \
of your Comps range, what explains the gap?)

Key assumption sensitivity: (across all three scenarios, which single \
input has the largest impact on implied price? Is there a way to gain \
more confidence on that input?)\
"""
