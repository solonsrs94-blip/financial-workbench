"""Non-DCF commentary templates — WACC, Comps, Historical, DDM, Summary.

These templates are used by modules that don't have per-scenario support.
"""

STEP3_WACC = """\
COST OF EQUITY:
Beta selection: (which beta method did you choose and why? If using \
peer/industry beta, why is it more appropriate than the company's own \
regression beta? Does the company's risk profile differ from peers?)

Size premium: (is the size premium tier appropriate — is the company \
near a boundary? Any reason to override?)

Country risk: (if applicable — is the CRP method appropriate for this \
company's actual geographic revenue exposure vs. domicile?)

COST OF DEBT:
Kd method: (did you use yield-to-maturity on existing debt or synthetic \
rating? Why? Does current capital market environment affect this choice?)

Credit quality: (is the company's credit profile stable, improving, or \
deteriorating? Any near-term refinancing risk?)

CAPITAL STRUCTURE:
Weights: (using current, target, or peer-based — why? Is the company \
actively deleveraging or levering up? Is current structure representative \
of steady state?)

OVERALL WACC:
Reasonableness check: (does the final WACC feel right for this company's \
risk profile? How does it compare to peers? Would you expect it to move \
over time?)\
"""

COMPS = """\
PEER SELECTION:
Peer universe rationale: (what criteria define comparability — business \
model, size, geography, growth profile, margins, end market? Why are \
these the right peers and not others?)

Excluded peers: (are there obvious candidates you deliberately excluded? \
Why — too large/small, different business mix, distressed, recent M&A?)

VALUATION:
Multiple selection: (which multiples are most meaningful for this sector \
and company? Why are certain multiples less reliable here — e.g., \
negative earnings making P/E unusable?)

Premium or discount: (should the target trade at a premium or discount \
to the peer median? What justifies that — superior growth, better \
margins, higher risk, weaker market position?)

Outlier treatment: (are any peers distorting the median/mean? Did you \
exclude them or keep them, and why?)\
"""

HISTORICAL = """\
TIME PERIOD:
Relevant period: (is the full historical window representative, or should \
certain periods be weighted more or less? Any structural breaks — M&A, \
spin-offs, business model shifts, COVID distortions — that affect \
comparability?)

POSITIONING:
Current vs. history: (where does the stock currently trade relative to \
its historical range? Is there a fundamental reason for the current \
positioning — changed growth outlook, margin profile, or risk?)

Mean reversion: (do you expect multiples to revert toward the mean, and \
over what timeframe? Or has something structurally changed that justifies \
a permanently different level?)

MULTIPLE SELECTION:
Metric choice: (which historical multiples are most informative for this \
company, and why? Are any distorted by accounting issues or cyclicality?)\
"""

DDM_LEGACY = """\
APPLICABILITY:
Model relevance: (is DDM appropriate for this company — does it have a \
stable, predictable dividend policy? If not, why are you running this \
model?)

DIVIDEND ASSUMPTIONS:
Dividend sustainability: (is the current payout ratio sustainable? Is \
management committed to the dividend — any history of cuts or suspension?)

Growth rates: (what supports the DPS growth assumptions — earnings growth, \
payout ratio expansion, or both? Are near-term and terminal growth rates \
consistent with the company's earnings trajectory?)

COST OF EQUITY:
Ke independence: (if your DDM cost of equity differs from the WACC Ke, \
why? Different beta, different assumptions, or a deliberate methodological \
choice?)\
"""

SUMMARY = """\
THESIS:
Overall conclusion: (in 2-3 sentences, what is your investment view — \
undervalued, overvalued, or fairly valued, and why?)

Valuation range: (what do you consider the fair value range, and which \
model(s) do you weight most heavily in reaching that conclusion? Why?)

MODEL RECONCILIATION:
Consistency: (where do your models agree and disagree? If DCF says one \
thing and Comps another, what explains the gap — and which do you trust \
more for this specific company?)

KEY DRIVERS:
Catalysts: (what events or developments could drive the stock toward your \
fair value — earnings, M&A, capital return, market re-rating?)

Risks: (what are the top 2-3 risks that could invalidate your thesis? \
How likely are they?)

CONFIDENCE:
Conviction level: (how confident are you in this analysis? What additional \
information would increase your confidence?)\
"""
