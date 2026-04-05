"""Financial statement flagging — rules 1-7 + orchestrator.
Rules 8-15 in flags_rules.py; 16-20 in flags_rules_v2.py;
21-22 in flags_industry.py.  No Streamlit imports.
"""
from typing import Optional

from lib.analysis.flags_helpers import (
    _g, _pct_change, _flag, _get_company_category, KNOWN_EVENTS, suppress,
    _industry_margin_ctx,
)
from lib.analysis.flags_config import should_skip, is_resource_company
from lib.analysis.flags_rules import (
    rule_fcf_ni_divergence,
    rule_working_capital_trend,
    rule_interest_rate_spike,
    rule_goodwill_impairment,
    rule_margin_mean_reversion,
    rule_long_trend_reversal,
    rule_major_dilution,
    rule_earnings_quality,
)
from lib.analysis.flags_rules_v2 import (
    rule_payout_ratio_high,
    rule_unusual_items_material,
    rule_dividend_coverage_thin,
    rule_leverage_elevated,
    rule_margin_below_history,
)
from lib.analysis.flags_industry import (
    rule_margin_below_industry,
    rule_roe_below_industry,
)


# ── Rule 1: margin_drop ─────────────────────────────────────────────

def _rule_margin_drop(ratios, is_table, flags, category="default",
                      industry_avg=None):
    """YoY margin drop.  Skip via config.  Wider band for energy/REITs."""
    if should_skip("margin_drop", category):
        return
    wide = category in ("energy", "reit")
    med_t = -0.05 if wide else -0.03
    high_t = -0.10 if wide else -0.07
    causes = ["One-off charge", "Business deterioration",
              "M&A integration", "Input cost spike"]
    ind_ctx = _industry_margin_ctx(industry_avg)
    for metric, line in [("ebit_margin", "ebit"), ("net_margin", "net_income")]:
        for i in range(1, len(ratios)):
            curr_m = _g(ratios[i], metric)
            prev_m = _g(ratios[i - 1], metric)
            if curr_m is None or prev_m is None:
                continue
            delta = curr_m - prev_m
            if delta >= med_t:
                continue
            sev = "high" if delta < high_t else "medium"
            rev = _g(is_table[i], "revenue") if i < len(is_table) else None
            impact = abs(delta) * rev / 1e6 if rev else None
            label = "EBIT Margin" if "ebit" in metric else "Net Margin"
            ctx_key = "operating_margin" if "ebit" in metric else "net_margin"
            ctx = ind_ctx.get(ctx_key, "")
            flags.append(_flag(
                "margin", sev, ratios[i]["year"],
                f"{label} dropped {abs(delta)*100:.1f}pp "
                f"({prev_m*100:.1f}% -> {curr_m*100:.1f}%){ctx}",
                causes, impact, line,
            ))


# ── Rule 2: margin_jump ─────────────────────────────────────────────

def _rule_margin_jump(ratios, is_table, flags, category="default",
                      industry_avg=None):
    """YoY margin jump.  Skip via config.  Wider band for energy/REITs."""
    if should_skip("margin_jump", category):
        return
    wide = category in ("energy", "reit")
    med_t = 0.07 if wide else 0.05
    high_t = 0.12 if wide else 0.10
    causes = ["One-off gain", "Operating leverage",
              "Cost restructuring", "Mix shift"]
    ind_ctx = _industry_margin_ctx(industry_avg)
    for metric, line in [("ebit_margin", "ebit"), ("net_margin", "net_income")]:
        for i in range(1, len(ratios)):
            curr_m = _g(ratios[i], metric)
            prev_m = _g(ratios[i - 1], metric)
            if curr_m is None or prev_m is None:
                continue
            delta = curr_m - prev_m
            if delta <= med_t:
                continue
            sev = "high" if delta > high_t else "medium"
            rev = _g(is_table[i], "revenue") if i < len(is_table) else None
            impact = abs(delta) * rev / 1e6 if rev else None
            label = "EBIT Margin" if "ebit" in metric else "Net Margin"
            ctx_key = "operating_margin" if "ebit" in metric else "net_margin"
            ctx = ind_ctx.get(ctx_key, "")
            flags.append(_flag(
                "margin", sev, ratios[i]["year"],
                f"{label} jumped {delta*100:.1f}pp "
                f"({prev_m*100:.1f}% -> {curr_m*100:.1f}%){ctx}",
                causes, impact, line,
            ))

# ── Rule 3: debt_spike ──────────────────────────────────────────────

def _rule_debt_spike(bs_table, flags, category="default"):
    """Total debt >100% YoY.  Skip via config."""
    if should_skip("debt_spike", category):
        return
    causes = ["Debt-funded acquisition", "Recapitalization",
              "Leveraged buyback", "Refinancing"]
    for i in range(1, len(bs_table)):
        curr = _g(bs_table[i], "total_debt")
        prev = _g(bs_table[i - 1], "total_debt")
        if not curr or not prev or prev <= 0:
            continue
        pct = (curr - prev) / prev
        abs_change = (curr - prev) / 1e6
        if pct > 1.0 and abs_change > 1000:
            flags.append(_flag(
                "debt", "high", bs_table[i].get("year"),
                f"Total debt jumped {pct*100:.0f}% "
                f"(${prev/1e9:.1f}B -> ${curr/1e9:.1f}B)",
                causes, abs_change, "total_debt",
            ))

def _rule_tax_anomaly(ratios, is_table, flags, category="default",
                      industry=""):
    """ETR >35% or <10%.  Skip via config (REITs are pass-through)."""
    if should_skip("tax_anomaly", category):
        return
    resource = is_resource_company(category, industry)
    for i, r in enumerate(ratios):
        etr = _g(r, "effective_tax_rate")
        if etr is None:
            continue
        year = r["year"]
        pretax = _g(is_table[i], "pretax_income") if i < len(is_table) else None
        # Energy and mining pay resource taxes, royalties, and production-
        # sharing — 35-50% ETR is structurally normal. Use 50% threshold.
        high_etr_t = 0.50 if resource else 0.35
        if etr > high_etr_t:
            impact = (etr - 0.21) * pretax / 1e6 if pretax and pretax > 0 else None
            causes = ["Repatriation tax", "Write-down tax effect",
                      "Geographic mix shift", "Deferred tax reversal"]
            if year in ("2017", "2018"):
                causes.insert(0, "TCJA transition")
            flags.append(_flag("tax", "medium", year,
                f"Effective tax rate {etr*100:.1f}%", causes, impact,
                "tax_provision"))
        # Utilities have structurally low ETR (accelerated depreciation)
        # — only flag at <3% instead of <10%
        elif etr < (0.03 if category == "utility" else 0.10) and etr >= 0:
            impact = (0.21 - etr) * pretax / 1e6 if pretax and pretax > 0 else None
            flags.append(_flag("tax", "medium", year,
                f"Effective tax rate {etr*100:.1f}%",
                ["NOL utilization", "Tax credit", "IP structure",
                 "Deferred tax benefit"],
                impact, "tax_provision"))


def _rule_known_event(ticker, ratios, flags):
    """Hardcoded events.  Universal."""
    events = KNOWN_EVENTS.get(ticker.upper(), [])
    ratio_years = {r["year"] for r in ratios}
    for ev in events:
        if ev["year"] in ratio_years:
            flags.append(_flag("event", "medium", ev["year"],
                f"Known event: {ev['event']}", None, None, "ebit"))


def _rule_capex_spike(ratios, cf_table, flags, category="default"):
    """CapEx/Revenue >50% jump.  Skip via config."""
    if should_skip("capex_spike", category):
        return
    causes = ["Capacity expansion", "Technology investment",
              "Maintenance backlog", "New facility"]
    for i in range(1, len(ratios)):
        curr_pct = _g(ratios[i], "capex_pct")
        prev_pct = _g(ratios[i - 1], "capex_pct")
        if not curr_pct or not prev_pct or prev_pct <= 0:
            continue
        # Skip if capex is negligible (< 1% of revenue) — tiny amounts
        # jumping from 0.05% to 0.12% is not meaningful
        if curr_pct < 0.01 and prev_pct < 0.01:
            continue
        if curr_pct / prev_pct > 1.5:
            capex = abs(_g(cf_table[i], "capital_expenditure") or 0) / 1e6 \
                if i < len(cf_table) else None
            flags.append(_flag(
                "capex", "medium", ratios[i]["year"],
                f"CapEx/Revenue jumped to {curr_pct*100:.1f}% "
                f"(from {prev_pct*100:.1f}%)",
                causes, capex, "capital_expenditure",
            ))


# ── Rule 7: acquisition_fingerprint ─────────────────────────────────

def _rule_acquisition_fingerprint(is_table, bs_table, cf_table, flags):
    """M&A detection.  Universal — acquisitions are noteworthy everywhere."""
    for i in range(1, min(len(is_table), len(bs_table))):
        year = is_table[i].get("year")
        rev = _g(is_table[i], "revenue")
        prev_rev = _g(is_table[i - 1], "revenue")
        acq = abs(_g(cf_table[i], "acquisitions") or 0) \
            if i < len(cf_table) else 0
        if not rev or rev <= 0 or acq < rev * 0.05:
            continue
        signals = 0
        rev_jump = _pct_change(rev, prev_rev)
        if rev_jump and rev_jump > 0.20:
            signals += 1
        gw_curr = _g(bs_table[i], "goodwill") or 0
        gw_prev = _g(bs_table[i - 1], "goodwill") or 0
        if gw_prev > 0 and (gw_curr - gw_prev) / gw_prev > 0.20:
            signals += 1
        if signals < 1:
            continue
        sev = "high" if acq >= rev * 0.10 else "medium"
        flags.append(_flag("m_and_a", sev, year,
            f"Acquisition spend ${acq/1e9:.1f}B "
            f"({acq/rev*100:.0f}% of revenue)",
            None, acq / 1e6, "revenue"))


# ── Orchestrator ─────────────────────────────────────────────────────

def detect_flags(
    ratios: list[dict],
    is_table: Optional[list[dict]] = None,
    bs_table: Optional[list[dict]] = None,
    cf_table: Optional[list[dict]] = None,
    sector: str = "",
    ticker: str = "",
    industry: str = "",
    company_type: str = "",
    industry_averages: Optional[dict] = None,
) -> list[dict]:
    """Run all detection rules.  Returns flag list."""
    flags: list[dict] = []
    is_t = is_table or []
    bs_t = bs_table or []
    cf_t = cf_table or []
    cat = _get_company_category(sector, industry, company_type)
    ia = industry_averages

    # Rules 1-7
    _rule_margin_drop(ratios, is_t, flags, cat, industry_avg=ia)
    _rule_margin_jump(ratios, is_t, flags, cat, industry_avg=ia)
    if bs_t:
        _rule_debt_spike(bs_t, flags, cat)
    _rule_tax_anomaly(ratios, is_t, flags, cat, industry=industry)
    if ticker:
        _rule_known_event(ticker, ratios, flags)
    _rule_capex_spike(ratios, cf_t, flags, cat)
    if is_t and bs_t:
        _rule_acquisition_fingerprint(is_t, bs_t, cf_t, flags)

    # Rules 8-15
    if is_t and cf_t:
        rule_fcf_ni_divergence(is_t, cf_t, flags, cat)
    rule_working_capital_trend(ratios, flags, cat)
    if is_t and bs_t:
        rule_interest_rate_spike(is_t, bs_t, flags, cat)
    if bs_t:
        rule_goodwill_impairment(bs_t, flags)
    rule_margin_mean_reversion(ratios, flags, cat)
    rule_long_trend_reversal(ratios, flags, cat)
    if is_t:
        rule_major_dilution(is_t, flags, cat)
    if is_t and cf_t:
        rule_earnings_quality(ratios, is_t, cf_t, flags, cat)

    # Rules 16-20 (sector-aware)
    sa = dict(sector=sector, industry=industry,
              company_type=company_type)
    rule_payout_ratio_high(ratios, cf_t, flags, **sa, industry_avg=ia)
    if is_t:
        rule_unusual_items_material(is_t, flags)
    if cf_t:
        rule_dividend_coverage_thin(cf_t, flags, **sa)
    rule_leverage_elevated(ratios, flags, **sa, industry_avg=ia)
    rule_margin_below_history(ratios, flags, industry_avg=ia, category=cat)

    # Rules 21-22 (industry-relative — only when data available)
    if ia:
        rule_margin_below_industry(ratios, flags, ia, cat)
        rule_roe_below_industry(ratios, flags, ia, bs_t)

    flags = suppress(flags)
    flags.sort(key=lambda f: (
        f.get("year", ""),
        0 if f["severity"] == "high" else 1,
    ))
    return flags
