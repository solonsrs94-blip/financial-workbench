"""Industry-relative flag rules (21-22).

Compare company metrics against Damodaran industry averages.
Only fire when industry_averages is available.
No Streamlit imports.
"""

from typing import Optional

from lib.analysis.flags_helpers import _g, _flag
from lib.analysis.flags_config import is_low_margin_industry, should_skip


def _ind(avg: dict, key: str) -> Optional[float]:
    """Get industry average value, None if missing or non-positive."""
    v = avg.get(key)
    if v is not None and v > 0:
        return v
    return None


def _label(avg: dict) -> str:
    """Industry label for flag messages."""
    name = avg.get("industry_name", "industry")
    n = avg.get("n_firms")
    return f"{name} ({n} firms)" if n else name


# ── Rule 21: Margins below industry average ─────────────────────

def rule_margin_below_industry(
    ratios: list[dict], flags: list[dict], ind_avg: dict,
    category: str = "default",
) -> None:
    """Flag when EBIT or net margin is significantly below industry avg.

    Relative gap: >30% below = medium, >50% below = high.
    Skips low-margin industries (discount retail, auto) where being
    below average is the business model, not a problem.
    Skips financials (margin structure is fundamentally different).
    """
    if not ratios:
        return
    if should_skip("margin_below_industry", category):
        return
    if is_low_margin_industry(ind_avg.get("industry_name", "")):
        return

    row = ratios[-1]
    year = row.get("year", "")
    label = _label(ind_avg)

    ebit_m = _g(row, "ebit_margin")
    ind_op = _ind(ind_avg, "operating_margin")
    if ebit_m is not None and ind_op is not None and ind_op > 0.02:
        gap = (ind_op - ebit_m) / ind_op
        if gap > 0.30:
            sev = "high" if gap > 0.50 else "medium"
            flags.append(_flag(
                "margin", sev, year,
                f"EBIT margin {ebit_m*100:.1f}% — "
                f"{gap*100:.0f}% below {label} avg {ind_op*100:.1f}%",
                line_item="ebit",
            ))

    net_m = _g(row, "net_margin")
    ind_net = _ind(ind_avg, "net_margin")
    if net_m is not None and ind_net is not None and ind_net > 0.02:
        gap = (ind_net - net_m) / ind_net
        if gap > 0.30:
            sev = "high" if gap > 0.50 else "medium"
            flags.append(_flag(
                "margin", sev, year,
                f"Net margin {net_m*100:.1f}% — "
                f"{gap*100:.0f}% below {label} avg {ind_net*100:.1f}%",
                line_item="net_income",
            ))


# ── Rule 22: ROE below industry average ─────────────────────────

def rule_roe_below_industry(
    ratios: list[dict], flags: list[dict], ind_avg: dict,
    bs_table: list = None,
) -> None:
    """Flag when ROE is significantly below industry average.

    Relative gap: >30% below = medium, >50% below = high.
    Skips when company has negative equity (makes ROE meaningless).
    """
    if not ratios:
        return

    # Skip if equity is negative — ROE is mathematically meaningless
    if bs_table:
        last_bs = bs_table[-1] if bs_table else {}
        equity = _g(last_bs, "total_equity")
        if equity is not None and equity <= 0:
            return

    row = ratios[-1]
    year = row.get("year", "")
    label = _label(ind_avg)

    roe = _g(row, "roe")
    ind_roe = _ind(ind_avg, "roe")
    if roe is not None and ind_roe is not None and ind_roe > 0.01:
        # Also skip if company ROE is negative (separate issue)
        if roe < 0:
            return
        gap = (ind_roe - roe) / ind_roe
        if gap > 0.30:
            sev = "high" if gap > 0.50 else "medium"
            flags.append(_flag(
                "quality", sev, year,
                f"ROE {roe*100:.1f}% — "
                f"{gap*100:.0f}% below {label} avg {ind_roe*100:.1f}%",
                line_item="net_income",
            ))
