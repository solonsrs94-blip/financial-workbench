"""Smart detection — known company events, cross-source validation.

Split from historical_flags_smart.py for file size compliance.
No Streamlit imports (lib/ rule).
"""


# ============================================================
# 7. CROSS-VALIDATE SOURCES
# ============================================================

def detect_source_discrepancies(
    std_data: dict, flags: list[dict],
) -> None:
    """Flag years where different sources give different values.

    Compares overlapping years between Yahoo, SimFin, and EDGAR.
    """
    if not std_data:
        return

    income = std_data.get("income", {})
    years = std_data.get("years", [])

    # Find overlapping years (where we might have multiple sources)
    # This requires raw multi-source data — skip if not available
    # (Placeholder for when we store per-source values)
    pass


# ============================================================
# 8. KNOWN COMPANY EVENTS
# ============================================================

# Major corporate events that affect financials
KNOWN_EVENTS = {
    "AAPL": [
        {"year": "2020", "event": "4:1 stock split", "impact": "Share count 4x — check per-share metrics"},
        {"year": "2014", "event": "7:1 stock split", "impact": "Share count 7x — check per-share metrics"},
    ],
    "GOOG": [
        {"year": "2015", "event": "Alphabet restructuring", "impact": "Segment reporting changed"},
        {"year": "2022", "event": "20:1 stock split", "impact": "Share count 20x"},
        {"year": "2017", "event": "EU antitrust fine €2.4B", "impact": "One-off charge on EBIT"},
        {"year": "2018", "event": "EU antitrust fine €4.3B", "impact": "One-off charge on EBIT"},
        {"year": "2019", "event": "EU antitrust fine €1.5B", "impact": "One-off charge on EBIT"},
    ],
    "META": [
        {"year": "2021", "event": "Rebranded to Meta, Reality Labs ramp", "impact": "Major OpEx increase"},
    ],
    "JNJ": [
        {"year": "2023", "event": "Kenvue consumer health spinoff", "impact": "Revenue and earnings one-offs from separation"},
    ],
    "AMZN": [
        {"year": "2022", "event": "Rivian investment write-down", "impact": "~$12B non-cash loss"},
        {"year": "1998", "event": "20:1 stock split", "impact": "Share count adjustment"},
    ],
    "MSFT": [
        {"year": "2015", "event": "Nokia phone business write-down $7.5B", "impact": "Goodwill impairment"},
        {"year": "2022", "event": "Activision Blizzard acquisition announced", "impact": "M&A activity"},
    ],
    "XOM": [
        {"year": "2024", "event": "Pioneer Natural Resources acquisition $60B", "impact": "Major M&A"},
    ],
    "V": [
        {"year": "2016", "event": "Visa Europe acquisition €21.2B", "impact": "Revenue and goodwill jump"},
    ],
    "PFE": [
        {"year": "2020", "event": "COVID vaccine development (BNT162b2)", "impact": "R&D ramp"},
        {"year": "2023", "event": "Seagen acquisition $43B", "impact": "Major M&A"},
    ],
}


def detect_known_company_events(
    ticker: str, ratios: list[dict], flags: list[dict],
) -> None:
    """Flag known corporate events from the database."""
    events = KNOWN_EVENTS.get(ticker.upper(), [])
    if not events:
        return

    available_years = {r["year"] for r in ratios}

    for event in events:
        yr = event["year"]
        if yr not in available_years:
            continue

        # Check not already flagged
        already = any(
            f["year"] == yr and event["event"][:20].lower() in f.get("why", "").lower()
            for f in flags
        )
        if already:
            continue

        flags.append({
            "category": "one_off",
            "severity": "medium",
            "year": yr,
            "what": f"Known event: {event['event']}",
            "why": event["impact"],
            "action": f"Adjust for {event['event']} impact when normalizing.",
            "impact_mn": None,
            "line_item": "ebit",
        })
