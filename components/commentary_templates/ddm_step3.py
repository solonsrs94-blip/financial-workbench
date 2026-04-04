"""DDM Step 3 Scenario Comparison template — shared across scenarios."""

STEP3_COMPARISON = """\
PROBABILITY WEIGHTING:
Assigned weights: (what probability do you assign each scenario — e.g., \
Bull 20% / Base 60% / Bear 20%? Is there more uncertainty on credit \
quality, rates, or dividends?)

Weighted fair value: (what is the probability-weighted implied share \
price? Do you consider this your DDM point estimate?)

RANGE ANALYSIS:
Spread assessment: (how wide is the bull-bear range? For a financial \
company, is this spread driven more by dividend growth uncertainty or \
credit risk? What does the spread say about the predictability of this \
company's earnings and dividends?)

Asymmetry: (is dividend upside or downside more likely? Financial \
companies often have asymmetric downside from credit events — is that \
reflected in your scenarios?)

MODEL FIT:
DDM appropriateness: (is DDM the right primary model for this company? \
Does it have a stable, predictable dividend policy, or is the dividend \
volatile? If volatile, how much should you weight the DDM result vs. \
other approaches like P/Book?)

Gordon vs. 2-Stage: (which DDM variant do you trust more for this \
company, and why? Does the 2-Stage model give a materially different \
answer, and if so, what drives the difference?)

CROSS-MODEL CHECK:
Consistency with other models: (does the DDM range align with your \
Comps and Historical Multiples ranges? If DDM gives a very different \
answer, what explains the gap — growth assumptions, Ke vs. market \
implied cost of equity, or payout assumptions?)

Relative to book value: (what P/Book does your DDM implied price \
represent? Is that consistent with the company's ROE and growth — does \
it pass the P/Book = (ROE - g) / (Ke - g) sanity check?)\
"""
