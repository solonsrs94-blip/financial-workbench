"""Step 1d: Standardized Financials — cleaned, normalized, ready for DCF.

Displays standardized IS/BS/CF tables with audit trail (click any value
to see where it came from) and cross-check results.
"""

import streamlit as st
from typing import Optional

from components.financial_table import render_financial_table


# Standardized IS fields: (key, label, scale, red_negative)
_IS_FIELDS = [
    ("revenue", "Revenue", "auto"),
    ("cogs", "Cost of Revenue", "auto", False),
    ("gross_profit", "= Gross Profit", "auto"),
    ("sga", "SG&A", "auto", False),
    ("marketing", "Marketing", "auto", False),
    ("rd", "R&D", "auto", False),
    ("da", "D&A", "auto", False),
    ("restructuring", "Restructuring", "auto", False),
    ("other_operating_expense", "Other Operating Expense", "auto", False),
    ("other_operating_income", "Other Operating Income", "auto"),
    ("total_opex", "Total OpEx", "auto", False),
    ("total_costs", "Total Costs", "auto", False),
    ("ebit", "= EBIT (Operating Income)", "auto"),
    ("ebitda", "EBITDA", "auto"),
    ("interest_expense", "Interest Expense", "auto", False),
    ("interest_income", "Interest Income", "auto"),
    ("other_non_operating", "Other Non-Operating", "auto"),
    ("equity_method_income", "Equity Method Income", "auto"),
    ("pretax_income", "= Pretax Income", "auto"),
    ("tax_provision", "Tax Provision", "auto", False),
    ("net_income_including_minority", "Net Income (incl. minority)", "auto"),
    ("minority_interest_income", "Minority Interest", "auto"),
    ("discontinued_ops", "Discontinued Operations", "auto"),
    ("net_income", "= Net Income", "auto"),
    ("diluted_shares", "Diluted Shares", "auto"),
    ("basic_shares", "Basic Shares", "auto"),
]

_BS_FIELDS = [
    ("cash", "Cash & Equivalents", "auto"),
    ("short_term_investments", "Short-term Investments", "auto"),
    ("accounts_receivable", "Accounts Receivable", "auto"),
    ("inventories", "Inventories", "auto"),
    ("other_current_assets", "Other Current Assets", "auto"),
    ("total_current_assets", "= Current Assets", "auto"),
    ("pp_and_e", "PP&E (net)", "auto"),
    ("goodwill", "Goodwill", "auto"),
    ("intangible_assets", "Intangible Assets", "auto"),
    ("operating_lease_assets", "Operating Lease Assets", "auto"),
    ("long_term_investments", "Long-term Investments", "auto"),
    ("equity_method_investments", "Equity Method Investments", "auto"),
    ("other_non_current_assets", "Other Non-current Assets", "auto"),
    ("total_non_current_assets", "Total Non-current Assets", "auto"),
    ("total_assets", ">> Total Assets", "auto"),
    ("accounts_payable", "Accounts Payable", "auto"),
    ("accrued_expenses", "Accrued Expenses", "auto"),
    ("short_term_debt", "Short-term Debt", "auto"),
    ("current_portion_ltd", "Current Portion of LTD", "auto"),
    ("other_current_liabilities", "Other Current Liabilities", "auto"),
    ("total_current_liabilities", "= Current Liabilities", "auto"),
    ("long_term_debt", "Long-term Debt", "auto"),
    ("operating_lease_nc", "Operating Lease Liabilities", "auto"),
    ("deferred_tax_liabilities", "Deferred Tax Liabilities", "auto"),
    ("pension_obligations", "Pension Obligations", "auto"),
    ("other_nc_liabilities", "Other Non-current Liabilities", "auto"),
    ("total_non_current_liabilities", "Total Non-current Liabilities", "auto"),
    ("total_liabilities", "= Total Liabilities", "auto"),
    ("common_stock", "Common Stock", "auto"),
    ("additional_paid_in_capital", "Additional Paid-in Capital", "auto"),
    ("retained_earnings", "Retained Earnings", "auto"),
    ("accumulated_oci", "Accumulated OCI", "auto"),
    ("treasury_stock", "Treasury Stock", "auto", False),
    ("total_equity", "= Total Equity", "auto"),
    ("minority_interest", "Minority Interest", "auto"),
    ("total_equity_incl_minority", "Total Equity (incl. minority)", "auto"),
    ("total_liabilities_and_equity", ">> Total L + E", "auto"),
    ("net_debt", ">> Net Debt", "auto"),
    ("shares_outstanding", "Shares Outstanding", "auto"),
]

_CF_FIELDS = [
    ("net_income_cf", "Net Income", "auto"),
    ("depreciation_amortization", "D&A", "auto"),
    ("stock_based_compensation", "Stock-Based Compensation", "auto"),
    ("deferred_income_tax", "Deferred Income Tax", "auto"),
    ("asset_impairment", "Asset Impairment", "auto"),
    ("other_non_cash", "Other Non-Cash Items", "auto"),
    ("change_in_receivables", "Change in Receivables", "auto"),
    ("change_in_payables", "Change in Payables", "auto"),
    ("change_in_other_wc", "Change in Other WC", "auto"),
    ("change_in_deferred_revenue", "Change in Deferred Revenue", "auto"),
    ("operating_cash_flow", "= Operating Cash Flow", "auto"),
    ("capital_expenditure", "Capital Expenditure", "auto", False),
    ("acquisitions", "Acquisitions", "auto", False),
    ("investment_purchases", "Investment Purchases", "auto", False),
    ("investment_proceeds", "Investment Proceeds", "auto"),
    ("divestiture_proceeds", "Divestiture Proceeds", "auto"),
    ("investing_cash_flow", "= Investing Cash Flow", "auto", False),
    ("debt_issuance", "Debt Issuance", "auto"),
    ("debt_repayment", "Debt Repayment", "auto", False),
    ("buybacks_and_issuance", "Buybacks / Stock Issuance", "auto", False),
    ("minority_distributions", "Minority Distributions", "auto", False),
    ("financing_cash_flow", "= Financing Cash Flow", "auto", False),
    ("fx_effect", "FX Effect", "auto"),
    ("net_change_in_cash", ">> Net Change in Cash", "auto"),
    ("free_cash_flow", ">> Free Cash Flow", "auto"),
]


def render_standardized(step1_data: Optional[dict], ticker: str) -> None:
    """Display standardized IS/BS/CF tables with audit trail and checks."""
    is_t = step1_data.get("is_table") if step1_data else None
    bs_t = step1_data.get("bs_table") if step1_data else None
    cf_t = step1_data.get("cf_table") if step1_data else None

    if not is_t:
        st.info("No standardized data available.")
        return

    # Cross-checks
    checks = step1_data.get("cross_checks", []) if step1_data else []
    if checks:
        _render_cross_checks(checks)

    # Statement tables
    stmt = st.segmented_control(
        "Statement", ["Income", "Balance Sheet", "Cash Flow"],
        default="Income", key=f"dcf_std_type_{ticker}",
        label_visibility="collapsed",
    )

    if stmt == "Income":
        render_financial_table(is_t, _IS_FIELDS)
    elif stmt == "Balance Sheet":
        render_financial_table(bs_t, _BS_FIELDS)
    else:
        render_financial_table(cf_t, _CF_FIELDS)

    # Audit trail
    _render_audit_trail(step1_data, stmt, ticker)


def _render_cross_checks(checks: list[dict]) -> None:
    """Show cross-check results."""
    if not checks:
        return

    failed = [c for c in checks if not c.get("ok")]
    passed = [c for c in checks if c.get("ok")]

    if failed:
        with st.expander(f"⚠ {len(failed)} cross-check(s) failed", expanded=False):
            for c in failed:
                st.warning(
                    f"**{c['year']}**: {c['check']} — "
                    f"off by ${c.get('diff', 0)/1e6:,.0f}M"
                )
    if passed:
        st.caption(f"✅ {len(passed)} cross-check(s) passed")


def _render_audit_trail(
    step1_data: Optional[dict], stmt: str, ticker: str,
) -> None:
    """Show mapping audit trail for the selected statement."""
    if not step1_data:
        return

    audit_key = {
        "Income": "income_audit",
        "Balance Sheet": "balance_audit",
        "Cash Flow": "cashflow_audit",
    }.get(stmt)

    audit = step1_data.get(audit_key, {}) if audit_key else {}
    if not audit:
        return

    with st.expander("🔍 Audit Trail — see where each number came from"):
        # Get latest year
        latest_yr = max(audit.keys()) if audit else None
        if not latest_yr:
            return

        fields = audit[latest_yr]
        layer_names = {0: "Derived", 1: "XBRL Concept", 2: "Keyword Match",
                       3: "Hierarchy", 4: "Other Bucket"}
        layer_colors = {0: "🔵", 1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴"}

        # Count by layer
        layer_counts = {}
        for k, v in fields.items():
            if isinstance(v, dict):
                l = v.get("layer", "?")
                layer_counts[l] = layer_counts.get(l, 0) + 1

        total = sum(layer_counts.values())
        summary = " | ".join(
            f"{layer_colors.get(l, '⚪')} L{l} ({layer_names.get(l, '?')}): {c}"
            for l, c in sorted(layer_counts.items())
        )
        st.caption(f"**{latest_yr}**: {total} fields mapped — {summary}")

        # Show mapping details
        for key, info in sorted(fields.items()):
            if not isinstance(info, dict):
                continue
            raw = info.get("raw_label", "?")
            layer = info.get("layer", "?")
            emoji = layer_colors.get(layer, "⚪")
            ln = layer_names.get(layer, f"Layer {layer}")
            st.caption(f"{emoji} `{key}` ← \"{raw}\" ({ln})")
