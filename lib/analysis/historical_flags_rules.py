"""Detection rules for historical anomaly flagging.

Each rule function appends flags to the flags list.
No Streamlit imports (lib/ rule).
"""

from typing import Optional


def detect_margin_anomalies(
    ratios: list[dict], is_table: Optional[list[dict]], flags: list[dict],
) -> None:
    """Detect margin jumps >5pp and diagnose likely cause."""
    margin_keys = [
        ("gross_margin", "Gross Margin", "gross_profit"),
        ("ebit_margin", "EBIT Margin", "ebit"),
        ("net_margin", "Net Margin", "net_income"),
    ]
    for i in range(1, len(ratios)):
        curr, prev = ratios[i], ratios[i - 1]
        yr = curr["year"]

        for key, label, line_item in margin_keys:
            c_val, p_val = curr.get(key), prev.get(key)
            if c_val is None or p_val is None:
                continue
            change = c_val - p_val
            if abs(change) <= 0.05:
                continue

            direction = "jumped" if change > 0 else "dropped"
            severity = "high" if abs(change) > 0.10 else "medium"
            rev_g = curr.get("revenue_growth")

            why = _diagnose_margin(direction, rev_g, label)
            rev = is_table[i].get("revenue") if is_table and i < len(is_table) else None
            impact = abs(change) * rev if rev else None

            flags.append({
                "category": "one_off",
                "severity": severity,
                "year": yr,
                "what": f"{label} {direction} {abs(change)*100:.1f}pp ({p_val*100:.1f}% -> {c_val*100:.1f}%)",
                "why": why,
                "action": _margin_action(line_item, direction, yr, impact),
                "impact_mn": impact / 1e6 if impact else None,
                "line_item": line_item,
            })


def _diagnose_margin(direction: str, rev_g: Optional[float], label: str) -> str:
    if rev_g is not None and abs(rev_g) < 0.05:
        cause = "one-off charge or cost spike" if direction == "dropped" else "cost reduction or one-off gain"
        return f"Revenue was stable ({rev_g*100:+.1f}%) but {label} {direction} -- likely {cause}"
    if rev_g is not None and rev_g > 0.15 and direction == "dropped":
        return f"Revenue grew {rev_g*100:.0f}% but margin dropped -- possible M&A integration costs"
    if rev_g is not None and rev_g < -0.05 and direction == "dropped":
        return f"Revenue declined {rev_g*100:.1f}% causing operating deleverage"
    if rev_g is not None and rev_g > 0.10 and direction == "jumped":
        return f"Revenue grew {rev_g*100:.0f}% with operating leverage"
    return f"{label} changed significantly -- review 10-K for details"


def _margin_action(line_item: str, direction: str, yr: str, impact: Optional[float]) -> str:
    imp = f"${impact/1e9:.1f}B" if impact and impact > 1e9 else (f"${impact/1e6:.0f}M" if impact else "unknown amount")
    if direction == "dropped":
        return f"Consider adding back {imp} to {yr} {line_item.upper()} if one-off. Check 10-K."
    return f"Consider removing {imp} one-off gain from {yr} {line_item.upper()}. Check 10-K."


def detect_revenue_anomalies(ratios: list[dict], flags: list[dict]) -> None:
    for i in range(1, len(ratios)):
        yr = ratios[i]["year"]
        rev_g = ratios[i].get("revenue_growth")
        if rev_g is None:
            continue
        if rev_g > 0.50:
            flags.append({
                "category": "m_and_a", "severity": "medium", "year": yr,
                "what": f"Revenue grew {rev_g*100:.1f}%",
                "why": "Growth this high is unusual organically -- likely includes acquisition revenue",
                "action": "Separate organic vs inorganic growth. Use organic rate for projections.",
                "impact_mn": None, "line_item": "revenue",
            })
        elif rev_g < -0.30:
            flags.append({
                "category": "m_and_a", "severity": "high", "year": yr,
                "what": f"Revenue declined {rev_g*100:.1f}%",
                "why": "Decline this sharp likely means divestiture, spinoff, or discontinuation",
                "action": "Rebase revenue to continuing operations for projections.",
                "impact_mn": None, "line_item": "revenue",
            })


def detect_tax_anomalies(ratios: list[dict], flags: list[dict]) -> None:
    for i in range(1, len(ratios)):
        yr = ratios[i]["year"]
        etr = ratios[i].get("effective_tax_rate")
        if etr is None:
            continue
        if yr == "2017" and etr > 0.40:
            flags.append({
                "category": "tax", "severity": "medium", "year": "2017",
                "what": f"Effective tax rate {etr*100:.1f}%",
                "why": "TCJA Tax Reform (Dec 2017) -- one-time deemed repatriation tax",
                "action": "Use normalized post-TCJA rate (~21-25%) for projections.",
                "impact_mn": None, "line_item": "tax_provision",
            })
        elif etr < 0.05:
            flags.append({
                "category": "tax", "severity": "medium", "year": yr,
                "what": f"Very low tax rate ({etr*100:.1f}%)",
                "why": "Possible NOL utilization, tax credits, or jurisdictional mix",
                "action": "Check if sustainable. Model NOL depletion if applicable.",
                "impact_mn": None, "line_item": "tax_provision",
            })
        elif etr > 0.35 and yr != "2017":
            flags.append({
                "category": "tax", "severity": "medium", "year": yr,
                "what": f"High tax rate ({etr*100:.1f}%)",
                "why": "Possible write-down, repatriation, or geographic mix shift",
                "action": "Use normalized rate for projections.",
                "impact_mn": None, "line_item": "tax_provision",
            })


def detect_capex_cycle(ratios: list[dict], flags: list[dict]) -> None:
    for i in range(1, len(ratios)):
        yr = ratios[i]["year"]
        cp = ratios[i].get("capex_pct")
        pp = ratios[i - 1].get("capex_pct")
        if cp and pp and pp > 0 and cp / pp > 1.5:
            flags.append({
                "category": "investment_cycle", "severity": "medium", "year": yr,
                "what": f"CapEx jumped to {cp*100:.1f}% of revenue (from {pp*100:.1f}%)",
                "why": "Investment cycle -- new capacity, data centers, or expansion",
                "action": "Determine if temporary (normalize) or structural (new baseline).",
                "impact_mn": None, "line_item": "capital_expenditure",
            })


def detect_sbc_dilution(ratios: list[dict], flags: list[dict]) -> None:
    for curr in ratios:
        sbc = curr.get("sbc_pct")
        if sbc is not None and sbc > 0.10:
            flags.append({
                "category": "dilution", "severity": "medium", "year": curr["year"],
                "what": f"SBC is {sbc*100:.1f}% of revenue",
                "why": "Significant shareholder dilution from stock-based compensation",
                "action": "Model dilution via diluted shares OR deduct SBC from FCF (not both).",
                "impact_mn": None, "line_item": "sbc",
            })


def detect_ifrs16(bs_table: list[dict], flags: list[dict]) -> None:
    for i in range(1, len(bs_table)):
        if bs_table[i]["year"] != "2019":
            continue
        curr_d = bs_table[i].get("total_debt")
        prev_d = bs_table[i - 1].get("total_debt")
        lease = bs_table[i].get("total_lease_obligations")
        if curr_d and prev_d and prev_d > 0:
            jump = (curr_d - prev_d) / prev_d
            if jump > 0.15 and lease:
                flags.append({
                    "category": "accounting_change", "severity": "medium", "year": "2019",
                    "what": f"Total debt jumped {jump*100:.0f}% in 2019",
                    "why": "IFRS 16/ASC 842 -- operating leases moved onto balance sheet",
                    "action": "Not a real leverage increase. Adjust for comparability.",
                    "impact_mn": (curr_d - prev_d) / 1e6, "line_item": "total_debt",
                })


def detect_ma(
    is_table: list[dict], bs_table: list[dict],
    ratios: list[dict], flags: list[dict],
) -> None:
    for i in range(1, min(len(is_table), len(bs_table))):
        yr = is_table[i]["year"]
        cr, pr = is_table[i].get("revenue"), is_table[i - 1].get("revenue")
        cg, pg = bs_table[i].get("goodwill"), bs_table[i - 1].get("goodwill")
        if not all(v and v > 0 for v in [cr, pr, cg, pg]):
            continue
        rev_j = (cr - pr) / pr
        gw_j = (cg - pg) / pg
        if rev_j > 0.15 and gw_j > 0.20:
            acq = cr - pr * 1.05
            flags.append({
                "category": "m_and_a", "severity": "high", "year": yr,
                "what": f"Revenue +{rev_j*100:.0f}% and goodwill +{gw_j*100:.0f}%",
                "why": "Strong acquisition signal -- both revenue and goodwill jumped",
                "action": f"Est. acquisition revenue: ~${acq/1e9:.1f}B. Use organic growth for baseline.",
                "impact_mn": acq / 1e6 if acq > 0 else None, "line_item": "revenue",
            })


def detect_unusual_items(is_table: list[dict], flags: list[dict]) -> None:
    for row in is_table:
        unusual = row.get("unusual_items")
        if unusual is None or abs(unusual) < 1:
            continue
        rev = row.get("revenue") or 1
        pct = abs(unusual) / rev
        if pct > 0.01:
            flags.append({
                "category": "one_off",
                "severity": "medium" if pct < 0.05 else "high",
                "year": row["year"],
                "what": f"Unusual items: ${unusual/1e9:.1f}B ({pct*100:.1f}% of revenue)",
                "why": "Company reported unusual/special items",
                "action": f"Add back ${abs(unusual)/1e9:.1f}B to normalize EBIT.",
                "impact_mn": abs(unusual) / 1e6, "line_item": "ebit",
            })
