"""Trend-based detection rules — multi-year patterns, CCC, interest/debt,
capex/D&A trends.

Supplements basic + advanced + extra rules.
No Streamlit imports (lib/ rule).
"""

from typing import Optional
import statistics


# === 1. MULTI-YEAR TREND BREAK ===

def detect_trend_breaks(
    ratios: list[dict], flags: list[dict],
) -> None:
    """Detect when a multi-year improving/declining trend reverses.

    More significant than random YoY noise because it signals a
    structural change in the business.
    """
    if len(ratios) < 5:
        return

    metrics = [
        ("gross_margin", "Gross Margin", "margin"),
        ("ebit_margin", "EBIT Margin", "margin"),
        ("net_margin", "Net Margin", "margin"),
        ("revenue_growth", "Revenue Growth", "growth"),
    ]

    for key, label, fmt in metrics:
        vals = [(i, r.get(key)) for i, r in enumerate(ratios) if r.get(key) is not None]
        if len(vals) < 5:
            continue

        # Look for 3+ years of consistent direction then reversal
        for j in range(3, len(vals)):
            idx, curr = vals[j]
            yr = ratios[idx]["year"]

            # Get prior 3 values
            prior = [vals[j - k][1] for k in range(1, 4)]
            prior.reverse()  # chronological

            # Check if prior 3 were all improving
            all_improving = all(prior[k] < prior[k + 1] for k in range(len(prior) - 1))
            # Check if prior 3 were all declining
            all_declining = all(prior[k] > prior[k + 1] for k in range(len(prior) - 1))

            if all_improving and curr < prior[-1]:
                change = curr - prior[-1]
                if abs(change) < 0.02:  # Ignore tiny reversals
                    continue
                already = any(
                    f["year"] == yr and "trend" in f.get("why", "").lower()
                    for f in flags
                )
                if already:
                    continue
                if fmt == "margin":
                    desc = f"{label} reversed after 3yr improvement ({change*100:+.1f}pp)"
                else:
                    desc = f"{label} reversed after 3yr acceleration"
                flags.append({
                    "category": "quality",
                    "severity": "medium",
                    "year": yr,
                    "what": desc,
                    "why": "Multi-year improving trend broke — investigate if structural or temporary",
                    "action": f"Determine if {label} decline is one-off or start of new trend.",
                    "impact_mn": None,
                    "line_item": key.replace("_margin", "").replace("_growth", ""),
                })

            elif all_declining and curr > prior[-1]:
                change = curr - prior[-1]
                if abs(change) < 0.02:
                    continue
                already = any(
                    f["year"] == yr and "trend" in f.get("why", "").lower()
                    for f in flags
                )
                if already:
                    continue
                if fmt == "margin":
                    desc = f"{label} reversed after 3yr decline ({change*100:+.1f}pp)"
                else:
                    desc = f"{label} reversed after 3yr deceleration"
                flags.append({
                    "category": "quality",
                    "severity": "low",
                    "year": yr,
                    "what": desc,
                    "why": "Multi-year declining trend broke — possible turnaround",
                    "action": f"Positive signal if sustainable. Check if driven by one-off or restructuring.",
                    "impact_mn": None,
                    "line_item": key.replace("_margin", "").replace("_growth", ""),
                })


# === 2. CASH CONVERSION CYCLE (CCC) TREND ===

def detect_ccc_trend(
    ratios: list[dict], flags: list[dict],
) -> None:
    """Flag when Cash Conversion Cycle lengthens consistently.

    CCC = DSO + DIO - DPO. Lengthening CCC means company needs more
    working capital per dollar of revenue.
    """
    if len(ratios) < 4:
        return

    cccs = []
    for r in ratios:
        dso = r.get("dso")
        dio = r.get("dio")
        dpo = r.get("dpo")
        if dso is not None and dpo is not None:
            dio_val = dio if dio is not None else 0
            cccs.append((r["year"], dso + dio_val - dpo))
        else:
            cccs.append((r["year"], None))

    # Check for 3+ years of lengthening
    valid = [(yr, c) for yr, c in cccs if c is not None]
    if len(valid) < 4:
        return

    for j in range(3, len(valid)):
        yr, curr = valid[j]
        prior3 = [valid[j - k][1] for k in range(1, 4)]
        prior3.reverse()

        all_lengthening = all(prior3[k] < prior3[k + 1] for k in range(len(prior3) - 1))
        if all_lengthening and curr > prior3[-1]:
            total_change = curr - valid[j - 3][1]
            if total_change > 10:  # >10 days over 3+ years
                flags.append({
                    "category": "quality",
                    "severity": "medium",
                    "year": yr,
                    "what": f"Cash Conversion Cycle lengthened {total_change:.0f} days over 4 years",
                    "why": "Company needs increasingly more working capital per $ of revenue",
                    "action": "Model higher NWC in projections. Check if DSO, DIO, or DPO is the driver.",
                    "impact_mn": None,
                    "line_item": "accounts_receivable",
                })
                break  # Only flag once


# === 3. INTEREST EXPENSE vs DEBT CONSISTENCY ===

def detect_interest_debt_mismatch(
    is_table: list[dict], bs_table: list[dict], flags: list[dict],
) -> None:
    """Flag when implied interest rate changes significantly.

    If interest/debt jumps, company is refinancing at higher rates.
    If it drops, they locked in low rates.
    """
    if len(is_table) < 3 or len(bs_table) < 3:
        return

    implied_rates = []
    for i in range(len(is_table)):
        interest = is_table[i].get("interest_expense")
        debt = bs_table[i].get("total_debt") if i < len(bs_table) else None
        yr = is_table[i]["year"]

        if interest is not None and debt is not None and debt > 0:
            rate = abs(interest) / debt
            if 0.001 < rate < 0.20:  # Sanity: 0.1% to 20%
                implied_rates.append((yr, rate))

    if len(implied_rates) < 3:
        return

    for j in range(1, len(implied_rates)):
        yr, curr = implied_rates[j]
        _, prev = implied_rates[j - 1]
        change = curr - prev

        if abs(change) > 0.015:  # >1.5pp change
            direction = "rose" if change > 0 else "fell"
            flags.append({
                "category": "quality",
                "severity": "medium",
                "year": yr,
                "what": (
                    f"Implied interest rate {direction} "
                    f"{abs(change)*100:.1f}pp ({prev*100:.1f}% -> {curr*100:.1f}%)"
                ),
                "why": (
                    f"{'Refinancing at higher rates or new expensive debt' if change > 0 else 'Locked in lower rates or paid off expensive debt'}. "
                    "Affects cost of debt in WACC."
                ),
                "action": "Update Kd assumption in WACC. Check debt maturity schedule.",
                "impact_mn": None,
                "line_item": "interest_expense",
            })


# === 4. CAPEX vs D&A TREND ===

def detect_capex_da_trend(
    ratios: list[dict], flags: list[dict],
) -> None:
    """Flag sustained over/under-investment relative to depreciation.

    CapEx/D&A > 1.5 for 3+ years = heavy investment cycle.
    CapEx/D&A < 0.8 for 3+ years = under-investing (harvesting).
    """
    if len(ratios) < 3:
        return

    cd_ratios = []
    for r in ratios:
        cd = r.get("capex_da")
        if cd is not None:
            cd_ratios.append((r["year"], cd))

    if len(cd_ratios) < 3:
        return

    # Check for 3+ years of over-investment
    over_investing = [(yr, cd) for yr, cd in cd_ratios if cd > 1.5]
    if len(over_investing) >= 3:
        latest = over_investing[-1]
        avg = statistics.mean([cd for _, cd in over_investing])
        flags.append({
            "category": "investment_cycle",
            "severity": "medium",
            "year": latest[0],
            "what": f"CapEx/D&A has been >{1.5:.1f}x for {len(over_investing)} years (avg {avg:.1f}x)",
            "why": "Sustained heavy investment — building capacity or replacing aging assets",
            "action": (
                "Determine if this normalizes (CapEx → D&A) or if it's a new "
                "higher baseline. Affects FCF projection significantly."
            ),
            "impact_mn": None,
            "line_item": "capital_expenditure",
        })

    # Check for 3+ years of under-investment
    under_investing = [(yr, cd) for yr, cd in cd_ratios if cd < 0.8]
    if len(under_investing) >= 3:
        latest = under_investing[-1]
        avg = statistics.mean([cd for _, cd in under_investing])
        flags.append({
            "category": "quality",
            "severity": "medium",
            "year": latest[0],
            "what": f"CapEx/D&A has been <{0.8:.1f}x for {len(under_investing)} years (avg {avg:.1f}x)",
            "why": "Sustained under-investment — assets aging, future capex spike likely",
            "action": "Factor in a catch-up capex period in projections.",
            "impact_mn": None,
            "line_item": "capital_expenditure",
        })
