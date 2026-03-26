"""Historical anomaly detection — smart flagging with what/why/action.

Combines basic rules (margin, revenue, tax, capex, SBC, IFRS16, M&A)
with advanced rules (FCF/NI divergence, goodwill, statistical, known events,
revenue-earnings disconnect, WC anomalies).

No Streamlit imports (lib/ rule).
"""

from typing import Optional
from lib.analysis.historical_flags_rules import (
    detect_margin_anomalies, detect_revenue_anomalies,
    detect_tax_anomalies, detect_capex_cycle, detect_sbc_dilution,
    detect_ifrs16, detect_ma, detect_unusual_items,
)
from lib.analysis.historical_flags_advanced import (
    detect_fcf_ni_divergence, detect_goodwill_impairment,
    detect_statistical_outliers,
)
from lib.analysis.historical_flags_advanced2 import (
    detect_known_events,
    detect_revenue_earnings_disconnect, detect_wc_anomalies,
)
from lib.analysis.historical_flags_extra import (
    detect_debt_spike, detect_share_changes, detect_negative_equity,
    detect_ocf_quality, detect_revenue_mix_shift,
)
from lib.analysis.historical_flags_trends import (
    detect_trend_breaks, detect_ccc_trend,
    detect_interest_debt_mismatch, detect_capex_da_trend,
)
from lib.analysis.historical_flags_trends2 import (
    detect_deferred_revenue_trend, detect_cumulative_decline,
)
from lib.analysis.historical_flags_smart import (
    detect_industry_margin_flags, compute_earnings_quality,
    classify_cyclicality,
)
from lib.analysis.historical_flags_smart2 import (
    detect_mean_reversion, detect_acquisition_fingerprint,
    detect_capital_allocation,
)
from lib.analysis.historical_flags_smart3 import (
    detect_known_company_events,
)

# Re-export
from lib.analysis.historical_averages import compute_averages  # noqa: F401


def detect_flags(
    ratios: list[dict],
    is_table: Optional[list[dict]] = None,
    bs_table: Optional[list[dict]] = None,
    cf_table: Optional[list[dict]] = None,
    sector: str = "",
    ticker: str = "",
) -> list[dict]:
    """Run all detection rules (basic + advanced). Returns flag list."""
    flags = []

    # Basic rules
    detect_margin_anomalies(ratios, is_table, flags)
    detect_revenue_anomalies(ratios, flags)
    detect_tax_anomalies(ratios, flags)
    detect_capex_cycle(ratios, flags)
    detect_sbc_dilution(ratios, flags)
    if bs_table:
        detect_ifrs16(bs_table, flags)
    if is_table and bs_table:
        detect_ma(is_table, bs_table, ratios, flags)
    if is_table:
        detect_unusual_items(is_table, flags)

    # Advanced rules
    if is_table and cf_table:
        detect_fcf_ni_divergence(ratios, is_table, cf_table, flags)
    if bs_table:
        detect_goodwill_impairment(bs_table, flags)
    detect_statistical_outliers(ratios, flags)
    if is_table and bs_table:
        detect_known_events(ratios, is_table, bs_table, flags)
    if is_table:
        detect_revenue_earnings_disconnect(ratios, is_table, flags)
    detect_wc_anomalies(ratios, flags)

    # Extra rules
    if bs_table:
        detect_debt_spike(bs_table, flags)
        detect_negative_equity(bs_table, flags)
    if is_table:
        detect_share_changes(is_table, flags)
    if is_table and cf_table:
        detect_ocf_quality(ratios, is_table, cf_table, flags)
    detect_revenue_mix_shift(ratios, flags)

    # Trend rules
    detect_trend_breaks(ratios, flags)
    detect_ccc_trend(ratios, flags)
    if is_table and bs_table:
        detect_interest_debt_mismatch(is_table, bs_table, flags)
    detect_capex_da_trend(ratios, flags)
    if bs_table:
        detect_deferred_revenue_trend(bs_table, ratios, flags)
    if is_table:
        detect_cumulative_decline(ratios, is_table, flags)

    # Smart rules (industry-aware, AI-designed)
    if sector:
        detect_industry_margin_flags(ratios, sector, flags)
    detect_mean_reversion(ratios, flags)
    if is_table and bs_table:
        detect_acquisition_fingerprint(is_table, bs_table, cf_table, flags)
    detect_capital_allocation(ratios, cf_table, is_table, flags)
    if ticker:
        detect_known_company_events(ticker, ratios, flags)

    # Sort: high severity first, then by year
    flags.sort(key=lambda f: (0 if f["severity"] == "high" else 1, f.get("year", "")))

    return flags
