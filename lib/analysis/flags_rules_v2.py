"""Financial statement flagging — rules 16-20 (sector-aware).

Sector-aware rules for payout ratio, unusual items, dividend coverage,
leverage, and margin-vs-history.  Uses _get_company_category() for
threshold selection to avoid false positives across company types.

No Streamlit imports (lib/ rule).
"""
import statistics
from lib.analysis.flags_helpers import _g, _flag, _get_company_category
from lib.analysis.flags_config import should_skip

# ── Threshold tables ────────────────────────────────────────────────

_PAYOUT_THRESHOLDS = {
    #                    medium  high
    "default":          (0.85,  0.95),
    "dividend_stable":  (0.85,  0.95),
    "reit":             (0.98,  1.10),
    "financial":        (0.70,  0.85),
    "utility":          (0.85,  0.95),
    "energy":           (0.85,  0.95),
}

_COVERAGE_THRESHOLDS = {
    #                    medium  high   (coverage < threshold triggers)
    "default":          (1.15,  1.00),
    "dividend_stable":  (1.15,  1.00),
    "utility":          (1.05,  0.90),
    "energy":           (1.15,  1.00),
    # reit, financial → skip entirely
}

_LEVERAGE_LEVEL = {
    #                    medium  high
    "default":          (3.5,   5.0),
    "dividend_stable":  (3.5,   5.0),
    "utility":          (5.5,   7.0),
    "reit":             (7.0,   9.0),
    "energy":           (4.0,   5.5),
    # financial → skip entirely
}

_LEVERAGE_CHANGE = {
    #                    medium YoY increase
    "default":          1.0,
    "dividend_stable":  1.0,
    "utility":          1.0,
    "reit":             1.5,
    "energy":           1.0,
}


# ── Rule 16: payout_ratio_high ──────────────────────────────────────

def rule_payout_ratio_high(ratios, cf_table, flags,
                           sector="", industry="", company_type="",
                           industry_avg=None):
    """Flag elevated dividend payout ratio (most recent year only)."""
    if not ratios:
        return
    cat = _get_company_category(sector, industry, company_type)
    if should_skip("payout_ratio_high", cat):
        return
    if industry_avg and industry_avg.get("payout_ratio"):
        ind_pr = industry_avg["payout_ratio"]
        med_t = max(ind_pr * 1.3, 0.70)
        high_t = max(ind_pr * 1.5, 0.85)
    else:
        med_t, high_t = _PAYOUT_THRESHOLDS.get(cat, (0.85, 0.95))

    r = ratios[-1]
    pr = _g(r, "payout_ratio")
    if pr is None or pr <= 0:
        return

    # Get dividends_paid for message context
    cf = cf_table[-1] if cf_table else {}
    divs = abs(_g(cf, "dividends_paid") or 0)
    impact = divs / 1e6 if divs else None

    if pr >= high_t:
        msg = (f"Payout ratio {pr*100:.0f}% — dividends exceed earnings"
               if pr > 1.0 else
               f"Payout ratio {pr*100:.0f}% — near ceiling, "
               f"limited room for dividend growth")
        flags.append(_flag(
            "quality", "high", r["year"], msg,
            ["Earnings dip with maintained dividend", "Mature business",
             "Management commitment to dividend"],
            impact, "dividends_paid",
        ))
    elif pr >= med_t:
        flags.append(_flag(
            "quality", "medium", r["year"],
            f"Payout ratio {pr*100:.0f}% — approaching ceiling",
            ["Mature business", "Dividend commitment",
             "Limited reinvestment needs"],
            impact, "dividends_paid",
        ))


# ── Rule 17: unusual_items_material ─────────────────────────────────

def rule_unusual_items_material(is_table, flags):
    """Flag material unusual/non-recurring items vs EBIT.  Universal."""
    for row in is_table:
        unusual = _g(row, "unusual_items")
        ebit = _g(row, "ebit")
        if unusual is None or unusual == 0:
            continue
        if ebit is None or abs(ebit) < 10e6:
            continue

        ratio = abs(unusual) / abs(ebit)
        if ratio <= 0.15:
            continue

        sev = "high" if ratio > 0.30 else "medium"
        sign = "-" if unusual < 0 else "+"
        flags.append(_flag(
            "quality", sev, row.get("year"),
            f"Unusual items (${sign}{abs(unusual)/1e9:.1f}B) represent "
            f"{ratio*100:.0f}% of EBIT",
            ["Restructuring charge", "Asset write-down",
             "Litigation settlement", "One-off gain/loss"],
            abs(unusual) / 1e6, "unusual_items",
        ))


# ── Rule 18: dividend_coverage_thin ─────────────────────────────────

def rule_dividend_coverage_thin(cf_table, flags,
                                sector="", industry="",
                                company_type=""):
    """Flag thin FCF coverage of dividends (most recent year only).
    Skip via config (REITs use AFFO, financials FCF meaningless)."""
    cat = _get_company_category(sector, industry, company_type)
    if should_skip("dividend_coverage", cat):
        return
    if not cf_table:
        return

    med_t, high_t = _COVERAGE_THRESHOLDS.get(cat, (1.15, 1.00))

    cf = cf_table[-1]
    fcf = _g(cf, "free_cash_flow")
    divs = _g(cf, "dividends_paid")
    if fcf is None or divs is None or divs == 0:
        return

    abs_divs = abs(divs)
    if abs_divs < 1e6:
        return

    coverage = fcf / abs_divs
    buffer = fcf - abs_divs

    if coverage < high_t:
        shortfall = abs_divs - fcf
        amt = (f"${shortfall/1e9:.1f}B" if shortfall >= 1e9
               else f"${shortfall/1e6:.0f}M")
        flags.append(_flag(
            "quality", "high", cf.get("year"),
            f"FCF does not fully cover dividends — shortfall of {amt}",
            ["Funded from reserves", "Debt-funded dividend",
             "Temporary capex spike", "Unsustainable payout"],
            shortfall / 1e6, "dividends_paid",
        ))
    elif coverage < med_t:
        amt = (f"${buffer/1e9:.1f}B" if buffer >= 1e9
               else f"${buffer/1e6:.0f}M")
        flags.append(_flag(
            "quality", "medium", cf.get("year"),
            f"FCF covers dividends by only {coverage:.2f}x — "
            f"buffer of {amt}",
            ["Thin safety margin", "Capex pressure",
             "Working capital needs"],
            buffer / 1e6, "dividends_paid",
        ))


# ── Rule 19: leverage_elevated ──────────────────────────────────────

def rule_leverage_elevated(ratios, flags,
                           sector="", industry="", company_type="",
                           industry_avg=None):
    """Flag elevated Debt/EBITDA level and/or rapid YoY increase.
    Skip via config."""
    cat = _get_company_category(sector, industry, company_type)
    if should_skip("leverage_elevated", cat):
        return
    if not ratios:
        return

    ind_de = (industry_avg or {}).get("debt_ebitda")
    if ind_de and ind_de > 0.5:
        med_lvl = ind_de * 1.5
        high_lvl = ind_de * 2.0
        ctx = f" (industry avg: {ind_de:.1f}x)"
    else:
        med_lvl, high_lvl = _LEVERAGE_LEVEL.get(cat, (3.5, 5.0))
        ctx = ""
    change_t = _LEVERAGE_CHANGE.get(cat, 1.0)

    # Level check — most recent year
    r = ratios[-1]
    de = _g(r, "debt_ebitda")
    if de is not None and de > 0:
        if de >= high_lvl:
            flags.append(_flag(
                "debt", "high", r["year"],
                f"Debt/EBITDA at {de:.1f}x — high leverage{ctx}",
                ["Debt-funded acquisition", "Earnings decline",
                 "Recapitalization", "Aggressive buyback"],
                None, "total_debt",
            ))
        elif de >= med_lvl:
            flags.append(_flag(
                "debt", "medium", r["year"],
                f"Debt/EBITDA at {de:.1f}x — elevated leverage{ctx}",
                ["Acquisition financing", "Capex cycle",
                 "Share repurchase program"],
                None, "total_debt",
            ))

    # YoY change check — most recent year vs prior
    if len(ratios) >= 2:
        prev_de = _g(ratios[-2], "debt_ebitda")
        if de is not None and prev_de is not None and de > 0 and prev_de > 0:
            increase = de - prev_de
            if increase >= change_t:
                flags.append(_flag(
                    "debt", "medium", r["year"],
                    f"Debt/EBITDA increased {increase:.1f}x YoY "
                    f"({prev_de:.1f}x to {de:.1f}x)",
                    ["Debt-funded acquisition", "EBITDA decline",
                     "New borrowing"],
                    None, "total_debt",
                ))


# ── Rule 20: margin_below_history ───────────────────────────────────

def rule_margin_below_history(ratios, flags, industry_avg=None,
                              category="default"):
    """Flag current margin significantly below own historical average.
    Self-calibrating via z-score. Skip via config."""
    if should_skip("margin_below_history", category):
        return
    if len(ratios) < 4:
        return

    causes = ["Competitive pressure", "Input cost inflation",
              "Business mix shift", "Temporary disruption"]
    ia = industry_avg or {}

    for metric, label, line, ind_key in [
        ("ebit_margin", "EBIT margin", "ebit", "operating_margin"),
        ("net_margin", "Net margin", "net_income", "net_margin"),
    ]:
        values = [_g(r, metric) for r in ratios if _g(r, metric) is not None]
        if len(values) < 4:
            continue

        curr = values[-1]
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)

        if stdev < 0.005:
            continue

        z = (curr - mean) / stdev
        if z >= -1.5:
            continue

        sev = "high" if z < -2.0 else "medium"
        ind_v = ia.get(ind_key)
        ctx = (f" — industry avg {ind_v*100:.1f}%"
               if ind_v and ind_v > 0 else "")
        flags.append(_flag(
            "margin", sev, ratios[-1]["year"],
            f"{label} {curr*100:.1f}% is {abs(z):.1f}σ below "
            f"{len(values)}-year average of {mean*100:.1f}%{ctx}",
            causes, None, line,
        ))
