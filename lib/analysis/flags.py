"""Financial statement flagging — 15 rules, fact-based output.

Each flag reports WHAT happened (fact) and POSSIBLE CAUSES (hypotheses).
No "why" (we don't know) and no "action" (not our job).
No "low" severity -- if it's not medium or high, don't flag it.

Rules 1-7 here; rules 8-15 + suppress in flags_rules.py.
Helpers in flags_helpers.py.
No Streamlit imports (lib/ rule).
"""

from typing import Optional

from lib.analysis.flags_helpers import _g, _pct_change, _flag, KNOWN_EVENTS
from lib.analysis.flags_rules import (
    rule_fcf_ni_divergence,
    rule_working_capital_trend,
    rule_interest_rate_spike,
    rule_goodwill_impairment,
    rule_margin_mean_reversion,
    rule_long_trend_reversal,
    rule_major_dilution,
    rule_earnings_quality,
    suppress,
)


# ── Rule 1: margin_drop ─────────────────────────────────────────────

def _rule_margin_drop(ratios, is_table, flags):
    causes = ["One-off charge", "Business deterioration",
              "M&A integration", "Input cost spike"]
    for metric, line in [("ebit_margin", "ebit"), ("net_margin", "net_income")]:
        for i in range(1, len(ratios)):
            curr_m = _g(ratios[i], metric)
            prev_m = _g(ratios[i - 1], metric)
            if curr_m is None or prev_m is None:
                continue
            delta = curr_m - prev_m
            if delta >= -0.05:
                continue
            sev = "high" if delta < -0.10 else "medium"
            rev = _g(is_table[i], "revenue") if i < len(is_table) else None
            impact = abs(delta) * rev / 1e6 if rev else None
            label = "EBIT Margin" if "ebit" in metric else "Net Margin"
            flags.append(_flag(
                "margin", sev, ratios[i]["year"],
                f"{label} dropped {abs(delta)*100:.1f}pp "
                f"({prev_m*100:.1f}% -> {curr_m*100:.1f}%)",
                causes, impact, line,
            ))


# ── Rule 2: margin_jump ─────────────────────────────────────────────

def _rule_margin_jump(ratios, is_table, flags):
    causes = ["One-off gain", "Operating leverage",
              "Cost restructuring", "Mix shift"]
    for metric, line in [("ebit_margin", "ebit"), ("net_margin", "net_income")]:
        for i in range(1, len(ratios)):
            curr_m = _g(ratios[i], metric)
            prev_m = _g(ratios[i - 1], metric)
            if curr_m is None or prev_m is None:
                continue
            delta = curr_m - prev_m
            if delta <= 0.05:
                continue
            sev = "high" if delta > 0.10 else "medium"
            rev = _g(is_table[i], "revenue") if i < len(is_table) else None
            impact = abs(delta) * rev / 1e6 if rev else None
            label = "EBIT Margin" if "ebit" in metric else "Net Margin"
            flags.append(_flag(
                "margin", sev, ratios[i]["year"],
                f"{label} jumped {delta*100:.1f}pp "
                f"({prev_m*100:.1f}% -> {curr_m*100:.1f}%)",
                causes, impact, line,
            ))


# ── Rule 3: debt_spike ──────────────────────────────────────────────

def _rule_debt_spike(bs_table, flags):
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


# ── Rule 4: tax_anomaly ─────────────────────────────────────────────

def _rule_tax_anomaly(ratios, is_table, flags):
    for i, r in enumerate(ratios):
        etr = _g(r, "effective_tax_rate")
        if etr is None:
            continue
        year = r["year"]
        pretax = _g(is_table[i], "pretax_income") if i < len(is_table) else None
        if etr > 0.35:
            impact = (etr - 0.21) * pretax / 1e6 if pretax and pretax > 0 else None
            causes = ["Repatriation tax", "Write-down tax effect",
                      "Geographic mix shift", "Deferred tax reversal"]
            if year in ("2017", "2018"):
                causes.insert(0, "TCJA transition")
            flags.append(_flag("tax", "medium", year,
                f"Effective tax rate {etr*100:.1f}%", causes, impact, "tax_provision"))
        elif etr < 0.10 and etr >= 0:
            impact = (0.21 - etr) * pretax / 1e6 if pretax and pretax > 0 else None
            flags.append(_flag("tax", "medium", year,
                f"Effective tax rate {etr*100:.1f}%",
                ["NOL utilization", "Tax credit", "IP structure", "Deferred tax benefit"],
                impact, "tax_provision"))


# ── Rule 5: known_event ─────────────────────────────────────────────

def _rule_known_event(ticker, ratios, flags):
    events = KNOWN_EVENTS.get(ticker.upper(), [])
    ratio_years = {r["year"] for r in ratios}
    for ev in events:
        if ev["year"] in ratio_years:
            flags.append(_flag("event", "medium", ev["year"],
                f"Known event: {ev['event']}", None, None, "ebit"))
    for i in range(1, len(ratios)):
        curr_yr = ratios[i]["year"]
        if any(f["year"] == curr_yr and "split" in f.get("what", "").lower()
               for f in flags):
            continue


# ── Rule 6: capex_spike ─────────────────────────────────────────────

def _rule_capex_spike(ratios, cf_table, flags):
    causes = ["Capacity expansion", "Technology investment",
              "Maintenance backlog", "New facility"]
    for i in range(1, len(ratios)):
        curr_pct = _g(ratios[i], "capex_pct")
        prev_pct = _g(ratios[i - 1], "capex_pct")
        if not curr_pct or not prev_pct or prev_pct <= 0:
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
            f"Acquisition spend ${acq/1e9:.1f}B ({acq/rev*100:.0f}% of revenue)",
            None, acq / 1e6, "revenue"))


# ── Orchestrator ─────────────────────────────────────────────────────

def detect_flags(
    ratios: list[dict],
    is_table: Optional[list[dict]] = None,
    bs_table: Optional[list[dict]] = None,
    cf_table: Optional[list[dict]] = None,
    sector: str = "",
    ticker: str = "",
) -> list[dict]:
    """Run all 15 detection rules. Returns flag list."""
    flags = []
    is_t = is_table or []
    bs_t = bs_table or []
    cf_t = cf_table or []

    _rule_margin_drop(ratios, is_t, flags)
    _rule_margin_jump(ratios, is_t, flags)
    if bs_t:
        _rule_debt_spike(bs_t, flags)
    _rule_tax_anomaly(ratios, is_t, flags)
    if ticker:
        _rule_known_event(ticker, ratios, flags)
    _rule_capex_spike(ratios, cf_t, flags)
    if is_t and bs_t:
        _rule_acquisition_fingerprint(is_t, bs_t, cf_t, flags)
    if is_t and cf_t:
        rule_fcf_ni_divergence(is_t, cf_t, flags)
    rule_working_capital_trend(ratios, flags)
    if is_t and bs_t:
        rule_interest_rate_spike(is_t, bs_t, flags)
    if bs_t:
        rule_goodwill_impairment(bs_t, flags)
    rule_margin_mean_reversion(ratios, flags)
    rule_long_trend_reversal(ratios, flags)
    if is_t:
        rule_major_dilution(is_t, flags)
    if is_t and cf_t:
        rule_earnings_quality(ratios, is_t, cf_t, flags)

    flags = suppress(flags)
    flags.sort(key=lambda f: (
        f.get("year", ""),
        0 if f["severity"] == "high" else 1,
    ))
    return flags
