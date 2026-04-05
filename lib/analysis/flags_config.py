"""Centralized flagging knowledge base — per-category rule behavior.

Encodes financial domain knowledge about what is normal vs anomalous
for each company category. Rules consult this config instead of
maintaining scattered if/else logic.

Categories: financial, reit, utility, energy, dividend_stable, default.
No Streamlit imports.
"""

# ── Rules to skip entirely per category ────────────────────────────
# Key = category from _get_company_category()
# Value = set of rule function names that should NOT fire
#
# WHY each rule is skipped is documented inline — this IS the
# knowledge base. A rule is skipped only when the underlying metric
# is structurally meaningless for that company type.

SKIP_RULES = {
    "financial": {
        # Banks/insurance: balance sheet IS the business
        "margin_drop",          # NIM is the metric, not operating margin
        "margin_jump",          # Same — EBIT margin is meaningless
        "debt_spike",           # Deposits = "debt" in accounting
        "capex_spike",          # Minimal capex, not relevant
        "fcf_ni_divergence",    # FCF concept doesn't apply
        "working_capital",      # No inventory/receivables cycle
        "interest_rate_spike",  # Interest expense IS the business
        "margin_mean_reversion",  # NIM is the relevant metric
        "long_trend_reversal",  # Same
        "major_dilution",       # Regulatory capital raises normal
        "earnings_quality",     # SBC/FCF metrics don't apply
        "dividend_coverage",    # No FCF to measure against
        "leverage_elevated",    # Debt/EBITDA meaningless
        "margin_below_history", # EBIT margin not relevant
        "leverage_above_industry",  # Debt/EBITDA meaningless
    },
    "reit": {
        # REITs: pass-through entities, D&A >> maintenance capex
        "tax_anomaly",          # Pass-through entity — ETR 2-8% is normal
        "fcf_ni_divergence",    # D&A >> maintenance capex; FCF >> NI structural
        "earnings_quality",     # FCF/NI ratio is structurally high
        "payout_ratio_high",    # Must distribute 90%+ of taxable income
        "dividend_coverage",    # FCF is wrong metric, need AFFO
    },
    "utility": {
        # Utilities: heavy capex for rate base growth
        "fcf_ni_divergence",    # Negative FCF normal (growth capex)
        "earnings_quality",     # FCF/NI ratio doesn't apply
        "dividend_coverage",    # FCF-based coverage wrong (capex != growth)
    },
    "energy": set(),            # Cyclical but all metrics apply
    "dividend_stable": set(),   # All metrics apply
    "default": set(),           # All metrics apply
}


def should_skip(rule_name: str, category: str) -> bool:
    """Check if a rule should be skipped for the given category."""
    return rule_name in SKIP_RULES.get(category, set())


# ── Margin-below-industry: industries where low margin IS the model ─
# Damodaran industry names where below-average margins should NOT flag
# because the business model is structurally low-margin (volume/scale).

LOW_MARGIN_INDUSTRIES = {
    "retail (general)",         # Walmart, Costco — volume/scale model
    "retail (grocery and food)",  # Kroger, Albertsons
    "retail (online)",          # Low-margin e-commerce
    "auto & truck",             # Thin-margin manufacturing
    "electronics (consumer & office)",  # Commodity electronics
    "farming/agriculture",      # Commodity production
    "food processing",          # Low-margin processing
    "food wholesalers",         # Distribution margins
}


def is_low_margin_industry(industry_name: str) -> bool:
    """Check if the industry has structurally low margins."""
    if not industry_name:
        return False
    return industry_name.strip().lower() in LOW_MARGIN_INDUSTRIES


# ── ROE: skip when equity is negative ──────────────────────────────
# When total equity < 0 (from buybacks or M&A goodwill), ROE is
# mathematically meaningless — negative equity / negative NI = positive
# ROE, positive NI / negative equity = negative ROE. Neither is useful.
# This is checked by the rule itself, not via category config.

# ── Resource companies: high ETR is structural ─────────────────────
# Mining and energy companies pay resource taxes, royalties, and
# production-sharing — 35-50% ETR is normal. High-ETR threshold
# raised from 35% to 50% for these industries.

RESOURCE_INDUSTRIES = {
    "metals & mining", "steel", "gold", "silver", "copper",
    "coal & consumable fuels", "other industrial metals & mining",
    "other precious metals & mining", "aluminum",
}


def is_resource_industry(industry_name: str) -> bool:
    """Check if the Damodaran industry is a resource extractor."""
    if not industry_name:
        return False
    return industry_name.strip().lower() in RESOURCE_INDUSTRIES


def is_resource_company(category: str, sub_industry: str = "") -> bool:
    """Energy or mining — pays resource taxes (higher ETR normal)."""
    if category == "energy":
        return True
    kw = (sub_industry or "").lower()
    return any(w in kw for w in ("mining", "metals", "steel", "gold"))


# ── Duplicate suppression ──────────────────────────────────────────
# When industry averages are available, Rule 23 (leverage_above_industry)
# is redundant with Rule 19 (leverage_elevated) since Rule 19 already
# derives thresholds from industry data. Don't run Rule 23 when Rule 19
# had industry data.
