"""Smart detection — industry profiles, cyclicality, earnings quality.

Uses AI-designed rules that run without real-time AI.
No Streamlit imports (lib/ rule).
"""

from typing import Optional
import statistics


# ============================================================
# INDUSTRY PROFILES
# ============================================================

# Expected ranges per sector: gm_range, em_range, margin_vol, typical_capex_rev,
# sbc_threshold, cyclical. Designed from market data.
def _p(gm, em, vol, capex, sbc, cyc):
    return {"gm_range": gm, "em_range": em, "margin_vol": vol,
            "typical_capex_rev": capex, "sbc_threshold": sbc, "cyclical": cyc}

SECTOR_PROFILES = {
    "Technology":            _p((0.50, 0.85), (0.15, 0.45), 0.05, (0.03, 0.15), 0.08, False),
    "Communication Services": _p((0.45, 0.80), (0.10, 0.40), 0.06, (0.05, 0.20), 0.08, False),
    "Healthcare":            _p((0.55, 0.80), (0.15, 0.35), 0.04, (0.03, 0.08), 0.05, False),
    "Consumer Defensive":    _p((0.20, 0.65), (0.05, 0.25), 0.02, (0.02, 0.06), 0.03, False),
    "Consumer Cyclical":     _p((0.20, 0.55), (0.02, 0.15), 0.04, (0.03, 0.10), 0.05, True),
    "Industrials":           _p((0.25, 0.45), (0.08, 0.20), 0.04, (0.03, 0.08), 0.03, True),
    "Energy":                _p((0.15, 0.50), (0.05, 0.20), 0.10, (0.05, 0.15), 0.02, True),
    "Financial Services":    _p((0.40, 0.90), (0.20, 0.50), 0.05, (0.01, 0.05), 0.05, False),
    "Utilities":             _p((0.30, 0.70), (0.10, 0.25), 0.02, (0.10, 0.25), 0.02, False),
    "Real Estate":           _p((0.30, 0.70), (0.10, 0.35), 0.03, (0.05, 0.15), 0.02, True),
    "Basic Materials":       _p((0.20, 0.50), (0.05, 0.20), 0.06, (0.05, 0.15), 0.02, True),
}

_DEFAULT_PROFILE = _p((0.20, 0.70), (0.05, 0.30), 0.05, (0.03, 0.10), 0.05, False)


def get_sector_profile(sector: str) -> dict:
    """Get industry profile for a sector. Falls back to default."""
    return SECTOR_PROFILES.get(sector, _DEFAULT_PROFILE)


# ============================================================
# 1. INDUSTRY-SPECIFIC MARGIN FLAGS
# ============================================================

def detect_industry_margin_flags(
    ratios: list[dict], sector: str, flags: list[dict],
) -> None:
    """Flag margins outside expected sector range."""
    profile = get_sector_profile(sector)
    gm_lo, gm_hi = profile["gm_range"]
    em_lo, em_hi = profile["em_range"]

    for r in ratios:
        yr = r["year"]
        gm = r.get("gross_margin")
        em = r.get("ebit_margin")

        if gm is not None and (gm < gm_lo - 0.10 or gm > gm_hi + 0.10):
            flags.append({
                "category": "quality",
                "severity": "medium",
                "year": yr,
                "what": (
                    f"Gross Margin {gm*100:.1f}% is outside {sector} "
                    f"typical range ({gm_lo*100:.0f}-{gm_hi*100:.0f}%)"
                ),
                "why": "May indicate business model difference, accounting, or data issue",
                "action": "Verify GM is correct. If real, understand why it differs from peers.",
                "impact_mn": None,
                "line_item": "gross_profit",
            })

        if em is not None and em < em_lo - 0.10:
            flags.append({
                "category": "quality",
                "severity": "medium",
                "year": yr,
                "what": (
                    f"EBIT Margin {em*100:.1f}% is well below {sector} "
                    f"typical range ({em_lo*100:.0f}-{em_hi*100:.0f}%)"
                ),
                "why": "Structurally lower profitability or one-off charge year",
                "action": "Determine if this is temporary (normalize) or structural (adjust target margin).",
                "impact_mn": None,
                "line_item": "ebit",
            })


# ============================================================
# 2. CYCLICALITY CLASSIFICATION
# ============================================================

def classify_cyclicality(ratios: list[dict], sector: str) -> dict:
    """Classify company as cyclical/stable based on revenue volatility.

    Returns: {is_cyclical, volatility_score, classification, margin_threshold}
    """
    profile = get_sector_profile(sector)

    rev_growths = [r.get("revenue_growth") for r in ratios if r.get("revenue_growth") is not None]
    em_vals = [r.get("ebit_margin") for r in ratios if r.get("ebit_margin") is not None]

    if len(rev_growths) < 4:
        return {
            "is_cyclical": profile["cyclical"],
            "volatility_score": 5,
            "classification": "Unknown (insufficient data)",
            "margin_threshold_pp": 5.0,
        }

    rev_vol = statistics.stdev(rev_growths)
    em_vol = statistics.stdev(em_vals) if len(em_vals) >= 4 else 0.05

    # Score 1-10 (10 = most volatile)
    vol_score = min(10, max(1, int(rev_vol * 30)))

    if vol_score <= 3:
        classification = "Stable"
        threshold = 3.0  # Flag 3pp margin changes
    elif vol_score <= 6:
        classification = "Moderate"
        threshold = 5.0  # Flag 5pp
    else:
        classification = "Cyclical"
        threshold = 8.0  # Flag 8pp — higher tolerance

    # Override: if sector is known-cyclical but data shows stable (e.g. CAT
    # in a multi-year upcycle), trust the sector classification and bump score
    is_cyclical = vol_score > 5 or profile["cyclical"]
    if profile["cyclical"] and vol_score <= 3:
        classification = "Cyclical (sector)"
        threshold = 6.0  # Higher than pure-stable but lower than data-cyclical
        vol_score = max(vol_score, 4)  # Bump minimum to 4

    return {
        "is_cyclical": is_cyclical,
        "volatility_score": vol_score,
        "classification": classification,
        "margin_threshold_pp": threshold,
        "rev_volatility": rev_vol,
        "margin_volatility": em_vol,
    }


# ============================================================
# 3. EARNINGS QUALITY SCORE
# ============================================================

def compute_earnings_quality(
    ratios: list[dict],
    is_table: Optional[list[dict]] = None,
    cf_table: Optional[list[dict]] = None,
) -> dict:
    """Compute earnings quality score (1-10) from multiple signals.

    Signals:
      1. FCF/NI ratio (>0.8 = good, <0.5 = poor)
      2. OCF/EBITDA ratio (>0.7 = good, <0.4 = poor)
      3. DSO trend (stable = good, rising = poor)
      4. Accruals (NI - OCF, smaller = better)
      5. Revenue quality (stable growth = good, lumpy = poor)

    Returns: {score, signals, assessment}
    """
    signals = {}
    scores = []

    # Use last 3 years
    recent = ratios[-3:] if len(ratios) >= 3 else ratios

    # Signal 1: FCF/NI consistency
    if is_table and cf_table:
        fcf_ni_ratios = []
        for i in range(max(0, len(ratios) - 3), len(ratios)):
            if i >= len(is_table) or i >= len(cf_table):
                continue
            ni = is_table[i].get("net_income")
            fcf = cf_table[i].get("free_cash_flow")
            if ni and ni > 0 and fcf is not None:
                fcf_ni_ratios.append(fcf / ni)
        if fcf_ni_ratios:
            avg_fcf_ni = statistics.mean(fcf_ni_ratios)
            if avg_fcf_ni >= 0.9:
                s = 10
            elif avg_fcf_ni >= 0.7:
                s = 8
            elif avg_fcf_ni >= 0.5:
                s = 6
            elif avg_fcf_ni >= 0.3:
                s = 4
            else:
                s = 2
            signals["FCF/NI"] = {"value": f"{avg_fcf_ni:.2f}", "score": s}
            scores.append(s)

    # Signal 2: OCF/EBITDA
    if is_table and cf_table:
        ocf_ebitda = []
        for i in range(max(0, len(ratios) - 3), len(ratios)):
            if i >= len(is_table) or i >= len(cf_table):
                continue
            ebitda = is_table[i].get("ebitda")
            ocf = cf_table[i].get("operating_cash_flow")
            if ebitda and ebitda > 0 and ocf is not None:
                ocf_ebitda.append(ocf / ebitda)
        if ocf_ebitda:
            avg = statistics.mean(ocf_ebitda)
            if avg >= 0.85:
                s = 10
            elif avg >= 0.70:
                s = 8
            elif avg >= 0.55:
                s = 6
            elif avg >= 0.40:
                s = 4
            else:
                s = 2
            signals["OCF/EBITDA"] = {"value": f"{avg:.2f}", "score": s}
            scores.append(s)

    # Signal 3: DSO stability
    dso_vals = [r.get("dso") for r in recent if r.get("dso") is not None]
    if len(dso_vals) >= 2:
        dso_change = dso_vals[-1] - dso_vals[0]
        if abs(dso_change) < 5:
            s = 9
        elif abs(dso_change) < 10:
            s = 7
        elif dso_change > 0:
            s = 4  # Rising = worse
        else:
            s = 6  # Declining = ok
        signals["DSO Stability"] = {"value": f"{dso_change:+.0f} days", "score": s}
        scores.append(s)

    # Signal 4: Revenue growth consistency
    rev_gs = [r.get("revenue_growth") for r in ratios[-5:] if r.get("revenue_growth") is not None]
    if len(rev_gs) >= 3:
        rev_vol = statistics.stdev(rev_gs)
        if rev_vol < 0.05:
            s = 10
        elif rev_vol < 0.10:
            s = 8
        elif rev_vol < 0.20:
            s = 6
        elif rev_vol < 0.30:
            s = 4
        else:
            s = 2
        signals["Rev Consistency"] = {"value": f"σ={rev_vol*100:.1f}%", "score": s}
        scores.append(s)

    # Signal 5: Margin stability
    em_vals = [r.get("ebit_margin") for r in ratios[-5:] if r.get("ebit_margin") is not None]
    if len(em_vals) >= 3:
        em_vol = statistics.stdev(em_vals)
        if em_vol < 0.02:
            s = 10
        elif em_vol < 0.04:
            s = 8
        elif em_vol < 0.08:
            s = 6
        elif em_vol < 0.12:
            s = 4
        else:
            s = 2
        signals["Margin Stability"] = {"value": f"σ={em_vol*100:.1f}pp", "score": s}
        scores.append(s)

    # Overall score
    if scores:
        overall = round(statistics.mean(scores))
    else:
        overall = 5  # Default

    if overall >= 8:
        assessment = "High quality — earnings well-supported by cash flow"
    elif overall >= 6:
        assessment = "Good quality — some items to monitor"
    elif overall >= 4:
        assessment = "Mixed quality — investigate cash flow divergences"
    else:
        assessment = "Low quality — significant gap between earnings and cash"

    return {
        "score": overall,
        "signals": signals,
        "assessment": assessment,
    }
