"""Advanced detection rules — known events, revenue-earnings disconnect,
working capital anomalies.

Split from historical_flags_advanced.py for file size compliance.
No Streamlit imports (lib/ rule).
"""

from typing import Optional


# === 4. KNOWN EVENTS DATABASE ===

def detect_known_events(
    ratios: list[dict], is_table: list[dict],
    bs_table: list[dict], flags: list[dict],
) -> None:
    """Check for patterns associated with known macro/regulatory events."""
    years = {r["year"] for r in ratios}

    # COVID-19 (2020) — revenue decline or margin compression
    if "2020" in years:
        r_2020 = next((r for r in ratios if r["year"] == "2020"), None)
        if r_2020:
            rev_g = r_2020.get("revenue_growth")
            if rev_g is not None and rev_g < -0.10:
                already = any(f["year"] == "2020" for f in flags)
                if not already:
                    flags.append({
                        "category": "one_off",
                        "severity": "medium",
                        "year": "2020",
                        "what": f"Revenue declined {rev_g*100:.1f}% in 2020",
                        "why": "COVID-19 pandemic impact on operations",
                        "action": "Consider 2020 as anomalous. Use 2019 or 2021 as cleaner base year.",
                        "impact_mn": None,
                        "line_item": "revenue",
                    })

    # ASC 606 Revenue Recognition (2018)
    if "2018" in years and "2017" in years:
        r_2018 = next((r for r in ratios if r["year"] == "2018"), None)
        r_2017 = next((r for r in ratios if r["year"] == "2017"), None)
        if r_2018 and r_2017:
            gm_18 = r_2018.get("gross_margin")
            gm_17 = r_2017.get("gross_margin")
            rev_g = r_2018.get("revenue_growth")
            if (gm_18 and gm_17 and abs(gm_18 - gm_17) > 0.03
                    and rev_g and abs(rev_g) < 0.05):
                already = any(
                    f["year"] == "2018" and "ASC 606" in f.get("why", "")
                    for f in flags
                )
                if not already:
                    flags.append({
                        "category": "accounting_change",
                        "severity": "low",
                        "year": "2018",
                        "what": f"Gross Margin shifted {(gm_18-gm_17)*100:+.1f}pp with flat revenue",
                        "why": "Possible ASC 606 revenue recognition change (effective 2018)",
                        "action": "Check if gross/net revenue reporting changed. May affect comparability.",
                        "impact_mn": None,
                        "line_item": "gross_profit",
                    })


# === 5. REVENUE-EARNINGS DISCONNECT ===

def detect_revenue_earnings_disconnect(
    ratios: list[dict], is_table: list[dict], flags: list[dict],
) -> None:
    """Flag when revenue and earnings move in opposite directions."""
    for i in range(1, len(ratios)):
        yr = ratios[i]["year"]
        rev_g = ratios[i].get("revenue_growth")
        curr_ebit = is_table[i].get("ebit") if i < len(is_table) else None
        prev_ebit = is_table[i - 1].get("ebit") if i - 1 < len(is_table) else None

        if rev_g is None or curr_ebit is None or prev_ebit is None or prev_ebit == 0:
            continue

        ebit_g = (curr_ebit - prev_ebit) / abs(prev_ebit)

        # Revenue up >10% but EBIT down >10%
        if rev_g > 0.10 and ebit_g < -0.10:
            already = any(f["year"] == yr and "disconnect" in f.get("why", "").lower() for f in flags)
            if not already:
                flags.append({
                    "category": "one_off",
                    "severity": "high",
                    "year": yr,
                    "what": f"Revenue +{rev_g*100:.0f}% but EBIT {ebit_g*100:+.0f}%",
                    "why": "Revenue grew but profitability declined -- likely one-off charges or cost spike",
                    "action": "Check for restructuring, impairment, or acquisition integration costs.",
                    "impact_mn": abs(curr_ebit - prev_ebit * (1 + rev_g)) / 1e6,
                    "line_item": "ebit",
                })

        # Revenue down but EBIT up significantly
        if rev_g < -0.05 and ebit_g > 0.20:
            already = any(f["year"] == yr and "disconnect" in f.get("why", "").lower() for f in flags)
            if not already:
                flags.append({
                    "category": "one_off",
                    "severity": "medium",
                    "year": yr,
                    "what": f"Revenue {rev_g*100:+.0f}% but EBIT +{ebit_g*100:.0f}%",
                    "why": "Revenue declined but earnings improved -- likely divestiture of low-margin segment or cost cuts",
                    "action": "Check if revenue decline was strategic (divestiture) or demand-driven.",
                    "impact_mn": None,
                    "line_item": "ebit",
                })


# === 6. WORKING CAPITAL ANOMALIES ===

def detect_wc_anomalies(
    ratios: list[dict], flags: list[dict],
) -> None:
    """Flag unusual working capital changes."""
    for i in range(1, len(ratios)):
        yr = ratios[i]["year"]

        # DSO spike (>15 days increase)
        curr_dso = ratios[i].get("dso")
        prev_dso = ratios[i - 1].get("dso")
        if curr_dso and prev_dso and curr_dso - prev_dso > 15:
            flags.append({
                "category": "quality",
                "severity": "medium",
                "year": yr,
                "what": f"DSO jumped {curr_dso - prev_dso:.0f} days ({prev_dso:.0f} -> {curr_dso:.0f})",
                "why": "Collection slowing -- possible channel stuffing or customer credit issues",
                "action": "Check AR aging. Higher DSO ties up more cash in working capital.",
                "impact_mn": None,
                "line_item": "accounts_receivable",
            })

        # DIO spike (>20 days increase)
        curr_dio = ratios[i].get("dio")
        prev_dio = ratios[i - 1].get("dio")
        if curr_dio and prev_dio and curr_dio - prev_dio > 20:
            flags.append({
                "category": "quality",
                "severity": "medium",
                "year": yr,
                "what": f"DIO jumped {curr_dio - prev_dio:.0f} days ({prev_dio:.0f} -> {curr_dio:.0f})",
                "why": "Inventory building up -- possible demand slowdown or supply chain issue",
                "action": "Check if inventory build is strategic (new product) or problematic (obsolescence).",
                "impact_mn": None,
                "line_item": "inventories",
            })
