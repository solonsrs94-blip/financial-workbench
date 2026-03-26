"""Trend-based detection rules — deferred revenue, cumulative decline.

Split from historical_flags_trends.py for file size compliance.
No Streamlit imports (lib/ rule).
"""

from typing import Optional


# === 5. DEFERRED REVENUE TREND ===

def detect_deferred_revenue_trend(
    bs_table: list[dict], ratios: list[dict], flags: list[dict],
) -> None:
    """Flag significant deferred revenue changes.

    For SaaS/subscription: growing deferred rev = positive (locked-in).
    Declining deferred rev = potential revenue quality issue.
    """
    if len(bs_table) < 3:
        return

    dr_vals = []
    for i, row in enumerate(bs_table):
        dr = row.get("deferred_revenue") or row.get("current_deferred_revenue")
        rev = ratios[i].get("revenue") if i < len(ratios) else None
        if rev is None and i < len(ratios):
            # Try to get from another source
            pass
        yr = row["year"]
        dr_vals.append((yr, dr))

    valid = [(yr, dr) for yr, dr in dr_vals if dr is not None and dr > 0]
    if len(valid) < 3:
        return

    # Check for consistent decline
    declining_years = 0
    for j in range(1, len(valid)):
        if valid[j][1] < valid[j - 1][1]:
            declining_years += 1

    if declining_years >= 3:
        latest_yr = valid[-1][0]
        first_val = valid[-declining_years - 1][1]
        last_val = valid[-1][1]
        pct_change = (last_val - first_val) / first_val
        flags.append({
            "category": "quality",
            "severity": "medium",
            "year": latest_yr,
            "what": f"Deferred revenue declined {abs(pct_change)*100:.0f}% over {declining_years} years",
            "why": "Declining backlog — fewer prepaid contracts or shorter contract terms",
            "action": "Check if business model is shifting. May signal slowing demand.",
            "impact_mn": None,
            "line_item": "deferred_revenue",
        })


# === 6. CUMULATIVE SLOW DECLINE ===

def detect_cumulative_decline(
    ratios: list[dict], is_table: list[dict], flags: list[dict],
) -> None:
    """Detect slow, steady revenue or margin decline over 3+ years.

    Individual years may be -1% to -3% (under normal thresholds) but
    cumulative effect is significant. Common in tobacco, legacy media, retail.
    """
    if len(ratios) < 4 or len(is_table) < 4:
        return

    # Revenue cumulative decline
    rev_vals = []
    for i, r in enumerate(ratios):
        rev = is_table[i].get("revenue") if i < len(is_table) else None
        if rev and rev > 0:
            rev_vals.append((r["year"], rev))

    if len(rev_vals) >= 4:
        # Check if revenue declined in 3+ of last 5 years
        recent = rev_vals[-5:] if len(rev_vals) >= 5 else rev_vals
        decline_years = 0
        for j in range(1, len(recent)):
            if recent[j][1] < recent[j-1][1]:
                decline_years += 1

        if decline_years >= 3:
            first_rev = recent[0][1]
            last_rev = recent[-1][1]
            total_decline = (last_rev - first_rev) / first_rev
            if total_decline < -0.05:  # >5% cumulative
                flags.append({
                    "category": "quality",
                    "severity": "medium",
                    "year": recent[-1][0],
                    "what": (
                        f"Revenue declined in {decline_years} of last "
                        f"{len(recent)} years ({total_decline*100:+.1f}% cumulative)"
                    ),
                    "why": (
                        "Slow but persistent revenue erosion — may indicate "
                        "secular decline, market share loss, or shrinking TAM"
                    ),
                    "action": (
                        "Model conservative or negative revenue growth. "
                        "Check if company is managing decline (cost cuts, buybacks) "
                        "or investing in turnaround."
                    ),
                    "impact_mn": None,
                    "line_item": "revenue",
                })

    # Margin cumulative decline
    em_vals = [(r["year"], r.get("ebit_margin")) for r in ratios
               if r.get("ebit_margin") is not None]

    if len(em_vals) >= 5:
        recent = em_vals[-5:]
        decline_years = sum(
            1 for j in range(1, len(recent))
            if recent[j][1] < recent[j-1][1]
        )
        if decline_years >= 4:  # 4 of 5 years declining
            total = recent[-1][1] - recent[0][1]
            if total < -0.03:  # >3pp cumulative
                flags.append({
                    "category": "quality",
                    "severity": "medium",
                    "year": recent[-1][0],
                    "what": (
                        f"EBIT Margin declined in {decline_years} of last 5 years "
                        f"({total*100:+.1f}pp cumulative)"
                    ),
                    "why": "Persistent margin erosion — competitive pressure or cost inflation",
                    "action": "Model conservative terminal margins. Check if trend is reversible.",
                    "impact_mn": None,
                    "line_item": "ebit",
                })
