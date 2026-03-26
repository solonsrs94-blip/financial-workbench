"""Advanced detection rules — cross-statement, statistical.

Supplements basic rules in historical_flags_rules.py.
No Streamlit imports (lib/ rule).
"""

from typing import Optional
import statistics


# === 1. FCF vs NET INCOME DIVERGENCE ===

def detect_fcf_ni_divergence(
    ratios: list[dict], is_table: list[dict],
    cf_table: list[dict], flags: list[dict],
) -> None:
    """Flag when FCF and Net Income diverge significantly.

    Signs of earnings quality issues, aggressive accounting,
    or large non-cash charges.
    """
    for i, r in enumerate(ratios):
        yr = r["year"]
        ni = is_table[i].get("net_income") if i < len(is_table) else None
        fcf = cf_table[i].get("free_cash_flow") if i < len(cf_table) else None

        if ni is None or fcf is None or ni == 0:
            continue

        # NI positive but FCF negative
        if ni > 0 and fcf < 0:
            flags.append({
                "category": "quality",
                "severity": "high",
                "year": yr,
                "what": f"Net Income positive (${ni/1e9:.1f}B) but FCF negative (${fcf/1e9:.1f}B)",
                "why": (
                    "Earnings not converting to cash -- possible aggressive "
                    "revenue recognition, large capex, or working capital drain"
                ),
                "action": "Investigate cash flow quality. Use FCF, not NI, as DCF baseline.",
                "impact_mn": abs(ni - fcf) / 1e6,
                "line_item": "net_income",
            })
        # FCF much higher than NI (>2x)
        elif fcf > 0 and ni > 0 and fcf / ni > 2.0:
            flags.append({
                "category": "quality",
                "severity": "medium",
                "year": yr,
                "what": f"FCF (${fcf/1e9:.1f}B) is {fcf/ni:.1f}x Net Income (${ni/1e9:.1f}B)",
                "why": (
                    "Large non-cash charges (D&A, SBC) inflating FCF vs earnings. "
                    "Common in asset-heavy or high-SBC companies."
                ),
                "action": "Consider whether high FCF conversion is sustainable.",
                "impact_mn": None,
                "line_item": "free_cash_flow",
            })
        # NI negative but FCF positive (can be normal for growth)
        elif ni < 0 and fcf > 0:
            flags.append({
                "category": "quality",
                "severity": "medium",
                "year": yr,
                "what": f"Net loss (${ni/1e9:.1f}B) but positive FCF (${fcf/1e9:.1f}B)",
                "why": "Large non-cash charges below EBIT (likely impairment or SBC)",
                "action": "Check for write-downs. FCF may be better baseline than NI.",
                "impact_mn": None,
                "line_item": "net_income",
            })


# === 2. GOODWILL IMPAIRMENT ===

def detect_goodwill_impairment(
    bs_table: list[dict], flags: list[dict],
) -> None:
    """Flag significant goodwill declines (impairment write-downs)."""
    for i in range(1, len(bs_table)):
        yr = bs_table[i]["year"]
        curr_gw = bs_table[i].get("goodwill")
        prev_gw = bs_table[i - 1].get("goodwill")

        if curr_gw is None or prev_gw is None or prev_gw <= 0:
            continue

        decline = (curr_gw - prev_gw) / prev_gw
        if decline < -0.10:  # >10% decline
            amount = prev_gw - curr_gw
            flags.append({
                "category": "one_off",
                "severity": "high",
                "year": yr,
                "what": (
                    f"Goodwill declined {abs(decline)*100:.0f}% "
                    f"(${amount/1e9:.1f}B impairment)"
                ),
                "why": (
                    "Goodwill impairment write-down -- prior acquisition "
                    "worth less than originally paid"
                ),
                "action": (
                    f"Add back ${amount/1e9:.1f}B impairment to normalize EBIT. "
                    f"This is a non-cash, non-recurring charge."
                ),
                "impact_mn": amount / 1e6,
                "line_item": "ebit",
            })


# === 3. STATISTICAL DEVIATION ===

def detect_statistical_outliers(
    ratios: list[dict], flags: list[dict],
) -> None:
    """Flag metrics >2 std from company's own historical mean.

    Adapts to each company -- stable companies flag small changes,
    volatile companies only flag large swings.
    """
    if len(ratios) < 4:
        return

    metrics = [
        ("gross_margin", "Gross Margin"),
        ("ebit_margin", "EBIT Margin"),
        ("net_margin", "Net Margin"),
    ]
    for key, label in metrics:
        vals = [(i, r.get(key)) for i, r in enumerate(ratios) if r.get(key) is not None]
        if len(vals) < 4:
            continue

        numbers = [v for _, v in vals]
        mean = statistics.mean(numbers)
        stdev = statistics.stdev(numbers)
        if stdev < 0.01:  # Very stable, skip
            continue

        for idx, val in vals:
            yr = ratios[idx]["year"]
            z_score = (val - mean) / stdev
            if abs(z_score) > 2.0:
                # Check not already flagged by basic margin detection
                already = any(
                    f["year"] == yr and label in f.get("what", "")
                    for f in flags
                )
                if already:
                    continue
                direction = "above" if z_score > 0 else "below"
                flags.append({
                    "category": "one_off",
                    "severity": "medium",
                    "year": yr,
                    "what": (
                        f"{label} ({val*100:.1f}%) is {abs(z_score):.1f} std "
                        f"{direction} historical mean ({mean*100:.1f}%)"
                    ),
                    "why": f"Statistical outlier relative to company's own history",
                    "action": f"Investigate whether {label} is reverting or structurally changed.",
                    "impact_mn": None,
                    "line_item": key,
                })
