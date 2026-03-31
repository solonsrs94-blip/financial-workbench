"""Flag helpers and known events — shared by flags.py and flags_rules.py."""

from typing import Optional


KNOWN_EVENTS = {
    "AAPL": [
        {"year": "2020", "event": "4:1 stock split", "impact": "Share count 4x"},
        {"year": "2014", "event": "7:1 stock split", "impact": "Share count 7x"},
    ],
    "GOOG": [
        {"year": "2015", "event": "Alphabet restructuring",
         "impact": "Segment reporting changed"},
        {"year": "2022", "event": "20:1 stock split", "impact": "Share count 20x"},
        {"year": "2017", "event": "EU antitrust fine \u20ac2.4B",
         "impact": "One-off charge on EBIT"},
        {"year": "2018", "event": "EU antitrust fine \u20ac4.3B",
         "impact": "One-off charge on EBIT"},
        {"year": "2019", "event": "EU antitrust fine \u20ac1.5B",
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
        {"year": "2016", "event": "Visa Europe acquisition \u20ac21.2B",
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
