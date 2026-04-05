"""Flag helpers and known events — shared by all flag rule files.

Provides:
- _get_company_category(): maps sector/industry/company_type to threshold
  category so every rule can branch on company type consistently.
- _g(), _pct_change(), _flag(): low-level helpers.
- KNOWN_EVENTS: hardcoded ticker→year→event dict.

No Streamlit imports (lib/ rule).
"""

from typing import Optional


# ── Company category detection ──────────────────────────────────────

def _get_company_category(sector: str, industry: str,
                          company_type: str) -> str:
    """Map sector/industry/company_type to a flag threshold category.

    Returns one of: "financial", "reit", "utility", "energy",
    "dividend_stable", "default".
    """
    if company_type == "financial":
        return "financial"
    if sector == "Real Estate" or "REIT" in (industry or "").upper():
        return "reit"
    if sector == "Utilities":
        return "utility"
    if sector == "Energy":
        return "energy"
    if company_type == "dividend_stable":
        return "dividend_stable"
    return "default"


# ── Known events (hardcoded) ────────────────────────────────────────

KNOWN_EVENTS = {
    "AAPL": [
        {"year": "2020", "event": "4:1 stock split", "impact": "Share count 4x"},
        {"year": "2014", "event": "7:1 stock split", "impact": "Share count 7x"},
    ],
    "GOOG": [
        {"year": "2015", "event": "Alphabet restructuring",
         "impact": "Segment reporting changed"},
        {"year": "2022", "event": "20:1 stock split", "impact": "Share count 20x"},
        {"year": "2017", "event": "EU antitrust fine €2.4B",
         "impact": "One-off charge on EBIT"},
        {"year": "2018", "event": "EU antitrust fine €4.3B",
         "impact": "One-off charge on EBIT"},
        {"year": "2019", "event": "EU antitrust fine €1.5B",
         "impact": "One-off charge on EBIT"},
    ],
    "META": [
        {"year": "2021", "event": "Rebranded to Meta, Reality Labs ramp",
         "impact": "Major OpEx increase"},
    ],
    "AMZN": [
        {"year": "2022", "event": "Rivian write-down ~$12B",
         "impact": "Non-cash loss"},
    ],
    "MSFT": [
        {"year": "2015", "event": "Nokia phone write-down $7.5B",
         "impact": "Goodwill impairment"},
        {"year": "2022", "event": "Activision Blizzard acquisition announced",
         "impact": "M&A activity"},
    ],
    "XOM": [
        {"year": "2024", "event": "Pioneer Natural Resources acquisition $60B",
         "impact": "Major M&A"},
    ],
    "V": [
        {"year": "2016", "event": "Visa Europe acquisition €21.2B",
         "impact": "Revenue and goodwill jump"},
    ],
    "PFE": [
        {"year": "2023", "event": "Seagen acquisition $43B",
         "impact": "Major M&A"},
    ],
    "JNJ": [
        {"year": "2023", "event": "Kenvue consumer health spinoff",
         "impact": "Revenue one-offs from separation"},
    ],
}


# ── Low-level helpers ───────────────────────────────────────────────

def _g(row: dict, key: str) -> Optional[float]:
    """Safe get — returns None for missing or zero-like values."""
    v = row.get(key)
    return v if v is not None else None


def _pct_change(curr, prev):
    if prev and prev != 0 and curr is not None:
        return (curr - prev) / abs(prev)
    return None


def _flag(category, severity, year, what, possible_causes=None,
          impact_mn=None, line_item=None):
    return {
        "category": category,
        "severity": severity,
        "year": str(year),
        "what": what,
        "possible_causes": possible_causes,
        "impact_mn": round(impact_mn, 1) if impact_mn else None,
        "line_item": line_item,
    }


# ── Industry context for flag messages ─────────────────────────────

def _industry_margin_ctx(ind_avg):
    """Build context strings for margin flag messages."""
    if not ind_avg:
        return {}
    ctx = {}
    name = ind_avg.get("industry_name", "")
    for key in ("operating_margin", "net_margin"):
        v = ind_avg.get(key)
        if v is not None and v > 0:
            ctx[key] = f" (industry avg: {v*100:.1f}%, {name})"
    return ctx


# ── Suppression ─────────────────────────────────────────────────────

def suppress(flags):
    """Remove redundant flags based on known interactions.

    Margin flags are suppressed in years where another flag already
    explains the margin movement:
    - Tax anomaly year + following year (ETR distorts NI margin)
    - M&A year (acquisition effects on revenue/costs)
    - Material unusual items year (one-offs distort EBIT/NI margin)
    """
    tax_years = set()
    ma_years = set()
    unusual_years = set()
    for f in flags:
        if f["category"] == "tax":
            tax_years.add(f["year"])
        if f["category"] == "m_and_a":
            ma_years.add(f["year"])
        if "unusual items" in f.get("what", "").lower():
            unusual_years.add(f["year"])

    tax_suppress = set()
    for y in tax_years:
        tax_suppress.add(y)
        tax_suppress.add(str(int(y) + 1))

    suppress_years = tax_suppress | ma_years | unusual_years
    return [
        f for f in flags
        if not (f["category"] == "margin" and f["year"] in suppress_years)
    ]
