"""Smart detection — mean-reversion, acquisition fingerprinting,
capital allocation pattern.

Split from historical_flags_smart.py for file size compliance.
No Streamlit imports (lib/ rule).
"""

from typing import Optional
import statistics


# ============================================================
# 4. MARGIN MEAN-REVERSION SIGNAL
# ============================================================

def detect_mean_reversion(
    ratios: list[dict], flags: list[dict],
) -> None:
    """Flag when current margins are at historical extremes.

    If at 90th+ percentile: flag that projections should consider reversion down.
    If at 10th- percentile: flag that projections should consider reversion up.
    """
    if len(ratios) < 5:
        return

    metrics = [
        ("gross_margin", "Gross Margin"),
        ("ebit_margin", "EBIT Margin"),
        ("net_margin", "Net Margin"),
    ]

    for key, label in metrics:
        vals = [r.get(key) for r in ratios if r.get(key) is not None]
        if len(vals) < 5:
            continue

        latest = vals[-1]
        sorted_vals = sorted(vals)
        n = len(sorted_vals)
        rank = sorted_vals.index(latest)
        percentile = rank / (n - 1) if n > 1 else 0.5

        mean = statistics.mean(vals)
        stdev = statistics.stdev(vals)

        if percentile >= 0.90:
            flags.append({
                "category": "quality",
                "severity": "low",
                "year": ratios[-1]["year"],
                "what": (
                    f"{label} at {percentile*100:.0f}th percentile of own history "
                    f"({latest*100:.1f}% vs avg {mean*100:.1f}%)"
                ),
                "why": "Margins at historical high — may not be sustainable long-term",
                "action": (
                    f"Consider mean-reversion in terminal year. "
                    f"Historical range: {sorted_vals[0]*100:.1f}%-{sorted_vals[-1]*100:.1f}%"
                ),
                "impact_mn": None,
                "line_item": key,
            })
        elif percentile <= 0.10:
            flags.append({
                "category": "quality",
                "severity": "low",
                "year": ratios[-1]["year"],
                "what": (
                    f"{label} at {percentile*100:.0f}th percentile of own history "
                    f"({latest*100:.1f}% vs avg {mean*100:.1f}%)"
                ),
                "why": "Margins at historical low — likely to recover if fundamentals intact",
                "action": (
                    f"Consider margin recovery in projections. "
                    f"Historical range: {sorted_vals[0]*100:.1f}%-{sorted_vals[-1]*100:.1f}%"
                ),
                "impact_mn": None,
                "line_item": key,
            })


# ============================================================
# 5. ACQUISITION FINGERPRINTING
# ============================================================

def detect_acquisition_fingerprint(
    is_table: list[dict], bs_table: list[dict],
    cf_table: Optional[list[dict]], flags: list[dict],
) -> None:
    """Multi-signal acquisition detection.

    Scores: goodwill jump + intangibles jump + debt jump + revenue jump
    + acquisition line in CF. More signals = higher confidence.
    """
    if len(is_table) < 2 or len(bs_table) < 2:
        return

    for i in range(1, min(len(is_table), len(bs_table))):
        yr = is_table[i]["year"]
        signals = 0
        details = []

        # Signal 1: Goodwill jump >20%
        gw_curr = bs_table[i].get("goodwill") if i < len(bs_table) else None
        gw_prev = bs_table[i-1].get("goodwill") if i-1 < len(bs_table) else None
        if gw_curr and gw_prev and gw_prev > 0:
            gw_change = (gw_curr - gw_prev) / gw_prev
            if gw_change > 0.20:
                signals += 2  # Strong signal
                details.append(f"Goodwill +{gw_change*100:.0f}%")

        # Signal 2: Intangibles jump >30%
        int_curr = bs_table[i].get("intangible_assets") if i < len(bs_table) else None
        int_prev = bs_table[i-1].get("intangible_assets") if i-1 < len(bs_table) else None
        if int_curr and int_prev and int_prev > 0:
            int_change = (int_curr - int_prev) / int_prev
            if int_change > 0.30:
                signals += 1
                details.append(f"Intangibles +{int_change*100:.0f}%")

        # Signal 3: Revenue jump >20%
        rev_curr = is_table[i].get("revenue")
        rev_prev = is_table[i-1].get("revenue")
        if rev_curr and rev_prev and rev_prev > 0:
            rev_change = (rev_curr - rev_prev) / rev_prev
            if rev_change > 0.20:
                signals += 1
                details.append(f"Revenue +{rev_change*100:.0f}%")

        # Signal 4: Debt jump >30%
        debt_curr = bs_table[i].get("total_debt") if i < len(bs_table) else None
        debt_prev = bs_table[i-1].get("total_debt") if i-1 < len(bs_table) else None
        if debt_curr and debt_prev and debt_prev > 0:
            debt_change = (debt_curr - debt_prev) / debt_prev
            if debt_change > 0.30:
                signals += 1
                details.append(f"Debt +{debt_change*100:.0f}%")

        # Signal 5: Acquisition cash outflow in CF
        if cf_table and i < len(cf_table):
            acq = cf_table[i].get("acquisitions")
            if acq is not None and acq < -1e8:  # >$100M outflow
                signals += 2  # Strong signal
                details.append(f"Acquisition spend ${abs(acq)/1e9:.1f}B")

        # Need 3+ signals for high confidence
        if signals >= 3:
            # Check not already flagged as M&A
            already = any(
                f["year"] == yr and f["category"] == "m_and_a"
                for f in flags
            )
            if not already:
                flags.append({
                    "category": "m_and_a",
                    "severity": "high",
                    "year": yr,
                    "what": f"Acquisition fingerprint detected ({signals} signals: {', '.join(details)})",
                    "why": "Multiple balance sheet and income signals point to material acquisition",
                    "action": "Calculate organic growth excluding acquisition. Check 10-K for deal details.",
                    "impact_mn": None,
                    "line_item": "revenue",
                })


# ============================================================
# 6. CAPITAL ALLOCATION PATTERN
# ============================================================

def detect_capital_allocation(
    ratios: list[dict],
    cf_table: Optional[list[dict]],
    is_table: Optional[list[dict]],
    flags: list[dict],
) -> None:
    """Classify capital allocation mode: invest / return / acquire.

    Helps user understand lifecycle phase for projections.
    """
    if not cf_table or len(cf_table) < 3:
        return

    recent = cf_table[-3:]
    recent_is = is_table[-3:] if is_table and len(is_table) >= 3 else None

    total_capex = 0
    total_buyback = 0
    total_dividend = 0
    total_acq = 0
    total_rev = 0

    for i, cf in enumerate(recent):
        capex = abs(cf.get("capital_expenditure") or 0)
        buyback = abs(cf.get("buybacks") or 0)
        dividend = abs(cf.get("dividends_paid") or 0)
        acq = abs(cf.get("acquisitions") or 0)
        total_capex += capex
        total_buyback += buyback
        total_dividend += dividend
        total_acq += acq
        if recent_is and i < len(recent_is):
            total_rev += recent_is[i].get("revenue") or 0

    total_deployed = total_capex + total_buyback + total_dividend + total_acq
    if total_deployed == 0:
        return

    capex_pct = total_capex / total_deployed
    return_pct = (total_buyback + total_dividend) / total_deployed
    acq_pct = total_acq / total_deployed

    yr = recent[-1].get("year", "?")

    if capex_pct > 0.50:
        mode = "Invest"
        desc = f"CapEx is {capex_pct*100:.0f}% of capital deployed (3yr)"
        why = "Company in investment/growth mode — building capacity"
        action = "Expect elevated CapEx to continue. Model gradual normalization."
    elif return_pct > 0.50:
        mode = "Return"
        desc = f"Buybacks + dividends are {return_pct*100:.0f}% of capital deployed (3yr)"
        why = "Company in shareholder return mode — mature/cash cow phase"
        action = "Model sustained buybacks (reduces share count) and dividend growth."
    elif acq_pct > 0.30:
        mode = "Acquire"
        desc = f"M&A is {acq_pct*100:.0f}% of capital deployed (3yr)"
        why = "Company in acquisition mode — inorganic growth strategy"
        action = "Separate organic from inorganic growth in projections."
    else:
        mode = "Balanced"
        desc = (
            f"CapEx {capex_pct*100:.0f}%, Returns {return_pct*100:.0f}%, "
            f"M&A {acq_pct*100:.0f}% of capital deployed"
        )
        why = "Balanced capital allocation across investment, returns, and M&A"
        action = "Current allocation mix likely continues."

    flags.append({
        "category": "quality",
        "severity": "low",
        "year": yr,
        "what": f"Capital allocation: {mode} — {desc}",
        "why": why,
        "action": action,
        "impact_mn": None,
        "line_item": "capital_expenditure",
    })
