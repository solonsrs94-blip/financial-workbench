"""Recommendation building blocks — attention items and risk rules.

Split from recommendations_rules.py for file size compliance.
No Streamlit imports (lib/ rule).
"""
from typing import Optional


def _fmt_pct(v): return f"{v * 100:.1f}%"
def _fmt_m(v): return f"${v / 1000:.1f}B" if abs(v) >= 1000 else f"${v:.0f}M"
def _attn(sev, title, detail, src="ratio"):
    return {"severity": sev, "title": title, "detail": detail, "source": src}
def _risk(cat, title, detail):
    return {"category": cat, "title": title, "detail": detail}


# ═══════════════════════════════════════════════════════════════════
# ATTENTION ITEM RULES — return dict or None
# ═══════════════════════════════════════════════════════════════════

def attention_from_flags(ctx: dict) -> list[dict]:
    """Group triggered flags into analyst-actionable attention items."""
    flags = ctx.get("flags", [])
    if not flags:
        return []

    items = []
    themes = {}
    for f in flags:
        themes.setdefault(f.get("category", ""), []).append(f)

    if "m_and_a" in themes:
        fs = themes["m_and_a"]
        yrs = ", ".join(sorted(set(f["year"] for f in fs)))
        impacts = [f for f in fs if f.get("impact_mn")]
        imp_s = f" ({_fmt_m(max(f['impact_mn'] for f in impacts))})" if impacts else ""
        items.append(_attn("high",
            "M&A activity distorts base financials",
            f"Acquisition activity in {yrs}{imp_s}. Strip acquisition effects "
            "from projections or use pro-forma adjustments.", "flag"))

    if "margin" in themes:
        high = [f for f in themes["margin"] if f["severity"] == "high"]
        if high:
            items.append(_attn("high",
                "Significant margin movement detected",
                f"{high[0]['what']}. Investigate whether temporary or structural "
                "before projecting margins forward.", "flag"))

    if "debt" in themes:
        fs = themes["debt"]
        items.append(_attn(
            "high" if any(f["severity"] == "high" for f in fs) else "medium",
            "Leverage change affects WACC assumptions",
            "Debt structure changed materially — stress-test capital structure "
            "in WACC and consider debt paydown trajectory.", "flag"))

    if "tax" in themes:
        items.append(_attn("medium",
            "Tax rate anomaly — normalize before projecting",
            f"{themes['tax'][0]['what']}. Use normalized ETR in projections, "
            "not the anomalous rate.", "flag"))

    if "quality" in themes:
        items.append(_attn("medium",
            "Earnings quality gap — FCF diverges from net income",
            "Cash earnings differ materially from accounting earnings. "
            "Examine working capital and non-cash items.", "flag"))

    if "dilution" in themes:
        items.append(_attn("medium",
            "Share count changed materially",
            f"{themes['dilution'][0]['what']}. Adjust per-share projections and "
            "consider ongoing dilution/buyback in terminal value.", "flag"))

    if "capex" in themes:
        items.append(_attn("medium",
            "Capital expenditure spike",
            "CapEx jumped significantly — determine if growth capex "
            "(one-time) or new maintenance run-rate.", "flag"))

    return items


def attention_dividend_health(ctx: dict) -> Optional[dict]:
    """Flag dividend sustainability concerns."""
    div = ctx.get("dividend_data") or {}
    if not div.get("has_dividend"):
        return None
    issues = []
    payout = div.get("payout_ratio")
    if payout and payout > 0.85:
        issues.append(f"payout ratio {_fmt_pct(payout)} approaching ceiling")
    cuts = div.get("dividend_cuts_clean", div.get("dividend_cuts", []))
    if cuts:
        issues.append(f"dividend cuts in {', '.join(str(y) for y in cuts[-3:])}")
    if not issues:
        return None
    return _attn("high" if (payout and payout > 0.95) or cuts else "medium",
        "Dividend sustainability concerns",
        f"Watch: {'; '.join(issues)}. DPS growth may be constrained "
        "by earnings growth capacity.", "dividend")


def attention_negative_equity(ctx: dict) -> Optional[dict]:
    """Flag negative equity and its valuation impact."""
    if not ctx.get("negative_equity"):
        return None
    return _attn("medium",
        "Negative book equity — impacts multiple metrics",
        "Total equity is negative (typically from buybacks or accumulated losses). "
        "ROIC, P/B, and DDM terminal value calculations are affected. "
        "Focus on enterprise value metrics.", "ratio")


def attention_sbc_dilution(ctx: dict) -> Optional[dict]:
    """Flag high stock-based compensation."""
    sbc = ctx["averages"].get("sbc_pct_3yr")
    if not sbc or sbc <= 0.03:
        return None
    return _attn("medium",
        f"High stock-based compensation ({_fmt_pct(sbc)} of revenue)",
        "SBC is a real economic cost that dilutes shareholders. "
        "Either subtract SBC from FCF or account for dilution "
        "in share count projections.", "ratio")


def attention_cyclicality(ctx: dict) -> Optional[dict]:
    """Flag cyclical companies needing scenario discipline."""
    if not ctx.get("revenue_volatile") and ctx.get("category") not in ("energy",):
        return None
    detail = "Revenue is highly cyclical"
    if ctx.get("category") == "energy":
        detail = "Energy company — revenue driven by commodity prices"
    return _attn("medium",
        "Cyclicality requires wider scenario ranges",
        f"{detail}. Use wide bull/bear spreads on revenue assumptions "
        "and be explicit about cycle positioning.", "industry")


# ═══════════════════════════════════════════════════════════════════
# RISK RULES — return dict or None
# ═══════════════════════════════════════════════════════════════════

_SECTOR_RISKS = {
    "Technology": (
        "Technology obsolescence and competitive disruption",
        "Rapid innovation cycles can shift TAM and invalidate long-term "
        "projections. Stress-test terminal value assumptions and consider "
        "shorter explicit forecast periods."),
    "Healthcare": (
        "Patent cliff and pipeline concentration risk",
        "Revenue concentration in key drugs/devices with finite patent life. "
        "Check patent expiration timeline and pipeline success rates. "
        "Model revenue cliff scenarios in bear case."),
    "Energy": (
        "Commodity price sensitivity",
        "Revenue heavily correlated with oil/gas/commodity prices. "
        "Use commodity price scenarios rather than single-point estimates. "
        "Consider hedging program in near-term projections."),
    "Financial Services": (
        "Credit cycle and regulatory capital exposure",
        "Provision for loan losses can swing earnings 50%+ in downturns. "
        "Model credit loss scenarios. ROE vs cost of equity is the key "
        "value driver — focus WACC analysis on equity cost."),
    "Financials": (
        "Credit cycle and regulatory capital exposure",
        "Provision for loan losses can swing earnings 50%+ in downturns. "
        "Model credit loss scenarios. ROE vs cost of equity is the key "
        "value driver — focus WACC analysis on equity cost."),
    "Real Estate": (
        "Interest rate sensitivity and lease risk",
        "Rising rates compress cap rates and increase financing costs. "
        "For REITs, focus on occupancy rates, lease expirations, and "
        "same-property NOI growth. NAV/share is an important cross-check."),
    "Consumer Cyclical": (
        "Consumer spending cyclicality",
        "Revenue tied to discretionary spending — vulnerable to macro downturns. "
        "Model recession scenario in bear case. Watch consumer confidence "
        "and employment trends."),
    "Industrials": (
        "Capital cycle and order backlog visibility",
        "Long lead times between capex decisions and revenue realization. "
        "Backlog and book-to-bill ratios are leading indicators. "
        "Working capital swings can be large and cyclical."),
    "Utilities": (
        "Regulatory and rate case risk",
        "Earnings growth depends on rate base expansion and regulatory approval. "
        "Rate case outcomes are binary events. Allowed ROE and capex recovery "
        "mechanisms are the key value drivers."),
    "Communication Services": (
        "Subscriber dynamics and content/capex intensity",
        "Recurring revenue dependent on subscriber retention and ARPU. "
        "High fixed-cost structure means operating leverage works both ways. "
        "Content/network capex is ongoing, not one-time."),
    "Consumer Defensive": (
        "Pricing power sustainability and private label risk",
        "Valuation assumes stable margins from pricing power. "
        "Watch for private label share gains, retailer pushback, "
        "and input cost pass-through timing."),
    "Basic Materials": (
        "Commodity cycle and cost curve positioning",
        "Revenue and margins tied to commodity prices and volumes. "
        "Cost curve position determines profitability through the cycle. "
        "Use mid-cycle normalized margins for terminal value."),
}


def risk_industry_specific(ctx: dict) -> Optional[dict]:
    """Industry-specific risk based on sector."""
    sector = ctx.get("sector", "")
    if not sector:
        return None
    entry = _SECTOR_RISKS.get(sector)
    if not entry:
        return None
    return _risk("industry", entry[0], entry[1])


def risk_leverage(ctx: dict) -> Optional[dict]:
    """Elevated leverage risk."""
    avg = ctx["averages"]
    de = None
    ratios = ctx.get("ratios", [])
    if ratios:
        de = ratios[0].get("debt_ebitda")
    cov = avg.get("interest_coverage_3yr")

    issues = []
    if de is not None and de > 3.0:
        issues.append(f"Debt/EBITDA {de:.1f}x")
    if cov is not None and cov < 3.0 and cov > 0:
        issues.append(f"interest coverage only {cov:.1f}x")
    if not issues:
        return None

    ind = ctx.get("industry_averages") or {}
    ind_de = ind.get("debt_ebitda")
    ctx_s = f" Industry average: {ind_de:.1f}x." if ind_de else ""

    return _risk("leverage",
        "Elevated leverage — stress-test capital structure",
        f"{'; '.join(issues)}.{ctx_s} Model debt paydown in projections "
        "and sensitivity-test WACC to different leverage assumptions.")


def risk_margin_vs_industry(ctx: dict) -> Optional[dict]:
    """Risk from margin significantly above or below industry."""
    ind = ctx.get("industry_averages")
    if not ind:
        return None
    ebit_m = ctx["averages"].get("ebit_margin_3yr")
    ind_m = ind.get("operating_margin")
    if not ebit_m or not ind_m or ind_m <= 0:
        return None

    ratio = ebit_m / ind_m
    name = ind.get("industry_name", "industry")

    if ratio > 1.5:
        return _risk("margin",
            "Premium margins may attract competition",
            f"EBIT margin {_fmt_pct(ebit_m)} is {ratio:.1f}x the {name} average "
            f"({_fmt_pct(ind_m)}). Assess sustainability — premium margins "
            "attract new entrants and customer pressure.")
    if ratio < 0.7:
        return _risk("margin",
            "Below-industry margins — turnaround or structural?",
            f"EBIT margin {_fmt_pct(ebit_m)} vs {name} average {_fmt_pct(ind_m)}. "
            "Determine if below-average margins reflect a turnaround story "
            "(upside potential) or structural disadvantage (lower target multiple).")
    return None


def risk_growth_deceleration(ctx: dict) -> Optional[dict]:
    """Risk from decelerating revenue growth."""
    ratios = ctx.get("ratios", [])
    if len(ratios) < 3:
        return None
    growths = [r.get("revenue_growth") for r in ratios[:3]
               if r.get("revenue_growth") is not None]
    if len(growths) < 3:
        return None
    if growths[0] < growths[1] < growths[2]:
        return _risk("growth",
            "Revenue growth decelerating — extrapolation risk",
            f"Revenue growth has decelerated for 3 consecutive years "
            f"({_fmt_pct(growths[2])} → {_fmt_pct(growths[1])} → {_fmt_pct(growths[0])}). "
            "Do not extrapolate past peak growth rates. Model a gradual "
            "slowdown path in base case.")
    return None
