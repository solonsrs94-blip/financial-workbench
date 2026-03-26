"""Historical averages — compute 3yr/5yr averages for key ratios.

Split from historical_flags.py to keep files under 200 lines.
No Streamlit imports (lib/ rule).
"""

from typing import Optional


def compute_averages(ratios_table: list[dict]) -> dict:
    """Compute 3yr and 5yr averages for key ratios."""
    def _avg(key: str, n: int) -> Optional[float]:
        vals = [r.get(key) for r in ratios_table[-n:] if r.get(key) is not None]
        return sum(vals) / len(vals) if vals else None

    return {
        "gross_margin_3yr": _avg("gross_margin", 3),
        "ebit_margin_3yr": _avg("ebit_margin", 3),
        "net_margin_3yr": _avg("net_margin", 3),
        "revenue_growth_3yr": _avg("revenue_growth", 3),
        "revenue_growth_5yr": _avg("revenue_growth", 5),
        "capex_pct_3yr": _avg("capex_pct", 3),
        "da_pct_3yr": _avg("da_pct", 3),
        "sbc_pct_3yr": _avg("sbc_pct", 3),
        "dso_3yr": _avg("dso", 3),
        "dio_3yr": _avg("dio", 3),
        "dpo_3yr": _avg("dpo", 3),
        "roic_3yr": _avg("roic", 3),
        "roe_3yr": _avg("roe", 3),
        "eff_tax_3yr": _avg("effective_tax_rate", 3),
        "interest_coverage_3yr": _avg("interest_coverage", 3),
        "debt_ebitda_3yr": _avg("debt_ebitda", 3),
        "fcf_conversion_3yr": _avg("fcf_conversion", 3),
    }
