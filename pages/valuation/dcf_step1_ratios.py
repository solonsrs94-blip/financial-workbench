"""Step 1 sub-component: Key Ratios display."""

import streamlit as st
from components.financial_table import render_financial_table


_RATIO_FIELDS = [
    # Growth
    ("revenue_growth", "Revenue Growth", "pct"),
    ("ebitda_growth", "EBITDA Growth", "pct"),
    ("eps_growth", "EPS Growth", "pct"),
    # Margins
    ("gross_margin", "Gross Margin", "pct"),
    ("ebit_margin", "EBIT Margin", "pct"),
    ("ebitda_margin", "EBITDA Margin", "pct"),
    ("net_margin", "Net Margin", "pct"),
    ("fcf_margin", "FCF Margin", "pct"),
    ("effective_tax_rate", "Effective Tax Rate", "pct"),
    # Efficiency
    ("dso", "DSO (days)", "days"),
    ("dio", "DIO (days)", "days"),
    ("dpo", "DPO (days)", "days"),
    ("nwc_pct_revenue", "NWC / Revenue", "pct"),
    ("asset_turnover", "Asset Turnover", "ratio"),
    # Investment
    ("capex_pct", "CapEx / Revenue", "pct"),
    ("da_pct", "D&A / Revenue", "pct"),
    ("capex_da_ratio", "CapEx / D&A", "ratio"),
    ("sbc_pct", "SBC / Revenue", "pct"),
    # Leverage & Coverage
    ("interest_coverage", "Interest Coverage", "ratio"),
    ("debt_ebitda", "Debt / EBITDA", "ratio"),
    ("debt_equity", "Debt / Equity", "ratio"),
    ("current_ratio", "Current Ratio", "ratio"),
    # Returns
    ("roic", "ROIC", "pct"),
    ("roe", "ROE", "pct"),
    ("roa", "ROA", "pct"),
    # Quality
    ("fcf_conversion", "FCF Conversion", "pct"),
    ("payout_ratio", "Payout Ratio", "pct"),
]


def render_ratios_section(ratios: list[dict]) -> None:
    """Render key ratios table in an expander."""
    with st.expander("Key Ratios & Drivers"):
        render_financial_table(ratios, _RATIO_FIELDS, show_source=False)
