"""Override rebuild logic — recompute tables/ratios/flags after overrides.

Split from preparation.py for file size compliance.
No Streamlit imports — pure data transformation.
"""

from lib.data.override_utils import apply_overrides
from lib.analysis.historical import (
    build_income_table, build_balance_table,
    build_cashflow_table, build_ratios_table,
)
from lib.analysis.historical_flags import detect_flags, compute_averages


def rebuild_with_overrides(
    data: dict, overrides: dict, sector: str, ticker: str,
) -> None:
    """Rebuild tables, ratios, flags, averages from overridden data.

    Mutates data dict in-place with new computed values.
    """
    original = data.get("original_standardized")
    if original is None:
        return

    applied = apply_overrides(original, overrides)
    years = applied["years"]

    is_t = build_income_table(applied, years)
    bs_t = build_balance_table(applied, years)
    cf_t = build_cashflow_table(applied, years)
    ratios = build_ratios_table(is_t, bs_t, cf_t)
    flags = detect_flags(
        ratios, is_table=is_t, bs_table=bs_t, cf_table=cf_t,
        sector=sector, ticker=ticker,
    )
    avgs = compute_averages(ratios)

    data["standardized"] = applied
    data["tables"] = {"income": is_t, "balance": bs_t, "cashflow": cf_t}
    data["ratios"] = ratios
    data["flags"] = flags
    data["averages"] = avgs
