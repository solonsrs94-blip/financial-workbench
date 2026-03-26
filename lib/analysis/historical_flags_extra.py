"""Extra detection rules — leverage, shares, equity, OCF quality, revenue mix.

Supplements basic + advanced rules.
No Streamlit imports (lib/ rule).
"""

from typing import Optional


# === 1. DEBT/LEVERAGE SPIKE ===

def detect_debt_spike(
    bs_table: list[dict], flags: list[dict],
) -> None:
    """Flag when total debt jumps >50% (outside IFRS 16 year)."""
    for i in range(1, len(bs_table)):
        yr = bs_table[i]["year"]
        if yr == "2019":  # IFRS 16 handled separately
            continue
        curr = bs_table[i].get("total_debt")
        prev = bs_table[i - 1].get("total_debt")
        if curr is None or prev is None or prev <= 0:
            continue
        change = (curr - prev) / prev
        if change > 0.50:
            flags.append({
                "category": "one_off",
                "severity": "high",
                "year": yr,
                "what": (
                    f"Total debt jumped {change*100:.0f}% "
                    f"(${prev/1e9:.1f}B -> ${curr/1e9:.1f}B)"
                ),
                "why": (
                    "Major debt increase -- likely debt-funded acquisition, "
                    "recapitalization, or leveraged buyback"
                ),
                "action": (
                    "Check if debt increase is permanent (new capital structure) "
                    "or temporary. Affects WACC and cost of debt."
                ),
                "impact_mn": (curr - prev) / 1e6,
                "line_item": "total_debt",
            })
        elif change < -0.30 and abs(prev) > 1e9:
            flags.append({
                "category": "one_off",
                "severity": "medium",
                "year": yr,
                "what": f"Total debt dropped {abs(change)*100:.0f}%",
                "why": "Major deleveraging -- debt paydown or refinancing",
                "action": "Check if new lower leverage is the target capital structure.",
                "impact_mn": None,
                "line_item": "total_debt",
            })


# === 2. SHARE COUNT CHANGES ===

def detect_share_changes(
    is_table: list[dict], flags: list[dict],
) -> None:
    """Flag significant dilution or buybacks in share count.

    Filters out stock splits (>80% change is almost certainly a split).
    """
    for i in range(1, len(is_table)):
        yr = is_table[i]["year"]
        curr = is_table[i].get("diluted_shares")
        prev = is_table[i - 1].get("diluted_shares")
        if curr is None or prev is None or prev <= 0:
            continue
        change = (curr - prev) / prev

        # Skip stock splits (typically 2:1, 3:1, 4:1, 10:1, 20:1)
        # These show as >80% increase or >50% decrease
        if change > 0.80 or change < -0.50:
            continue

        if change > 0.05:
            flags.append({
                "category": "dilution",
                "severity": "medium" if change < 0.15 else "high",
                "year": yr,
                "what": f"Diluted shares increased {change*100:.1f}%",
                "why": (
                    "Share dilution -- likely equity offering, "
                    "convertible conversion, or heavy SBC vesting"
                ),
                "action": (
                    "Model dilution explicitly in equity bridge. "
                    "Check if one-time (offering) or ongoing (SBC)."
                ),
                "impact_mn": None,
                "line_item": "diluted_shares",
            })
        elif change < -0.05:
            flags.append({
                "category": "one_off",
                "severity": "low",
                "year": yr,
                "what": f"Diluted shares decreased {abs(change)*100:.1f}%",
                "why": "Aggressive share buyback program",
                "action": "Consider whether buyback pace is sustainable.",
                "impact_mn": None,
                "line_item": "diluted_shares",
            })


# === 3. NEGATIVE EQUITY ===

def detect_negative_equity(
    bs_table: list[dict], flags: list[dict],
) -> None:
    """Flag negative stockholders' equity.

    Common in AAPL, SBUX, MCD due to massive buybacks.
    Not necessarily bad but affects ratio interpretation.
    """
    for row in bs_table:
        yr = row["year"]
        equity = row.get("total_equity")
        if equity is not None and equity < 0:
            flags.append({
                "category": "quality",
                "severity": "medium",
                "year": yr,
                "what": f"Negative equity (${equity/1e9:.1f}B)",
                "why": (
                    "Accumulated buybacks exceed retained earnings. "
                    "Common in mature companies with heavy buyback programs."
                ),
                "action": (
                    "ROE and D/E ratios are meaningless with negative equity. "
                    "Use ROIC and Debt/EBITDA instead."
                ),
                "impact_mn": None,
                "line_item": "total_equity",
            })
            break  # Only flag once (likely persists across years)


# === 4. OCF/EBITDA QUALITY ===

def detect_ocf_quality(
    ratios: list[dict], is_table: list[dict],
    cf_table: list[dict], flags: list[dict],
) -> None:
    """Flag when OCF/EBITDA ratio deviates significantly.

    Healthy: OCF/EBITDA ~0.7-1.0
    Low (<0.5): WC drain, aggressive revenue recognition
    High (>1.2): Large non-cash charges or WC release
    """
    for i, r in enumerate(ratios):
        yr = r["year"]
        ebitda = is_table[i].get("ebitda") if i < len(is_table) else None
        ocf = cf_table[i].get("operating_cash_flow") if i < len(cf_table) else None

        if ebitda is None or ocf is None or ebitda <= 0:
            continue

        ratio = ocf / ebitda

        if ratio < 0.4:
            flags.append({
                "category": "quality",
                "severity": "high",
                "year": yr,
                "what": f"OCF/EBITDA ratio is {ratio:.2f} (very low)",
                "why": (
                    "Cash generation much lower than reported earnings -- "
                    "possible WC drain, aggressive accounting, or large "
                    "cash tax payments"
                ),
                "action": "Investigate cash flow quality before using EBITDA-based projections.",
                "impact_mn": None,
                "line_item": "operating_cash_flow",
            })
        elif ratio > 1.5 and i > 0:
            prev_ebitda = is_table[i-1].get("ebitda") if i-1 < len(is_table) else None
            prev_ocf = cf_table[i-1].get("operating_cash_flow") if i-1 < len(cf_table) else None
            if prev_ebitda and prev_ocf and prev_ebitda > 0:
                prev_ratio = prev_ocf / prev_ebitda
                if prev_ratio < 1.3:  # Only flag if it changed
                    flags.append({
                        "category": "quality",
                        "severity": "medium",
                        "year": yr,
                        "what": f"OCF/EBITDA jumped to {ratio:.2f} (from {prev_ratio:.2f})",
                        "why": "Large WC release or deferred revenue recognition boosting cash",
                        "action": "Check if WC release is one-time or sustainable.",
                        "impact_mn": None,
                        "line_item": "operating_cash_flow",
                    })


# === 5. REVENUE MIX SHIFT ===

def detect_revenue_mix_shift(
    ratios: list[dict], flags: list[dict],
) -> None:
    """Flag when gross margin changes >3pp with stable revenue growth.

    Suggests product/service mix shift (e.g., hardware -> services).
    """
    for i in range(1, len(ratios)):
        yr = ratios[i]["year"]
        gm_curr = ratios[i].get("gross_margin")
        gm_prev = ratios[i - 1].get("gross_margin")
        rev_g = ratios[i].get("revenue_growth")

        if gm_curr is None or gm_prev is None or rev_g is None:
            continue

        gm_change = gm_curr - gm_prev

        # Gross margin changed >3pp but revenue growth is moderate (<15%)
        # (High growth margin changes are caught by margin rules)
        if abs(gm_change) > 0.03 and abs(rev_g) < 0.15:
            # Check this isn't already flagged as margin anomaly
            already = any(
                f["year"] == yr and "Gross Margin" in f.get("what", "")
                for f in flags
            )
            if already:
                continue

            direction = "improved" if gm_change > 0 else "declined"
            flags.append({
                "category": "quality",
                "severity": "medium",
                "year": yr,
                "what": (
                    f"Gross Margin {direction} {abs(gm_change)*100:.1f}pp "
                    f"with moderate revenue growth ({rev_g*100:+.1f}%)"
                ),
                "why": (
                    "Revenue mix may be shifting (e.g., hardware to services, "
                    "premium to discount, or geographic mix change)"
                ),
                "action": (
                    "Check segment/product mix. Gross margin trend affects "
                    "long-term EBIT margin assumptions."
                ),
                "impact_mn": None,
                "line_item": "gross_profit",
            })
