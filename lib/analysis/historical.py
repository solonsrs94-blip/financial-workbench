"""Historical analysis — process raw financials into tables.

Takes merged historical data from lib/data/historical.py and produces
structured output for DCF Step 1 UI.

Handles both old key names (label_maps) and new XBRL-based keys (standardizer)
for backwards compatibility during migration.

No Streamlit imports allowed here (lib/ rule).
"""

from typing import Optional

# Re-export ratios from split file
from lib.analysis.historical_ratios import build_ratios_table  # noqa: F401


def _safe_div(a: Optional[float], b: Optional[float]) -> Optional[float]:
    if a is None or b is None or b == 0:
        return None
    return a / b


def _abs_cost(val: Optional[float]) -> Optional[float]:
    """Normalize cost fields — always positive (costs are positive numbers)."""
    if val is None:
        return None
    return abs(val)


def _get(d: dict, *keys) -> Optional[float]:
    """Get first non-None value from multiple possible keys."""
    for k in keys:
        v = d.get(k)
        if v is not None:
            return v
    return None


def build_income_table(hist: dict, years: list[str]) -> list[dict]:
    """Build per-year income statement table.

    Supports both old (label_maps) and new (XBRL standardizer) key names.
    """
    income = hist.get("income", {})
    cashflow = hist.get("cashflow", {})
    rows = []
    for yr in years:
        d = income.get(yr, {})
        cf = cashflow.get(yr, {})

        rev = _get(d, "revenue", "total_revenue")
        cogs = _abs_cost(_get(d, "cogs", "cost_of_revenue"))
        gp = _get(d, "gross_profit")
        sga = _abs_cost(_get(d, "sga", "selling_general_admin"))
        marketing = _abs_cost(_get(d, "marketing"))
        rd = _abs_cost(_get(d, "rd", "research_development"))
        ebit = _get(d, "ebit")
        ebitda = _get(d, "ebitda")
        tax = _abs_cost(_get(d, "tax_provision"))
        restructuring = _abs_cost(_get(d, "restructuring"))

        # D&A: try IS first, then CF
        da = _get(d, "da", "depreciation_amortization")
        if da is None:
            da = _get(cf, "depreciation_amortization", "da")
        da = _abs_cost(da)

        # Derived: gross profit
        if gp is None and rev is not None and cogs is not None:
            gp = rev - cogs

        # Derived: EBITDA
        if ebitda is None and ebit is not None and da is not None:
            ebitda = ebit + da

        rows.append({
            "year": yr,
            "source": d.get("_source", ""),
            "revenue": rev,
            "cogs": cogs,
            "gross_profit": gp,
            "sga": sga,
            "marketing": marketing,
            "rd": rd,
            "da": da,
            "restructuring": restructuring,
            "other_operating_expense": _get(d, "other_operating_expense"),
            "other_operating_income": _get(d, "other_operating_income"),
            "total_opex": _abs_cost(_get(d, "total_opex", "operating_expenses")),
            "total_costs": _abs_cost(_get(d, "total_costs")),
            "ebit": ebit,
            "ebitda": ebitda,
            "interest_expense": _abs_cost(_get(d, "interest_expense")),
            "interest_income": _get(d, "interest_income"),
            "other_non_operating": _get(d, "other_non_operating", "other_income_expense"),
            "equity_method_income": _get(d, "equity_method_income"),
            "pretax_income": _get(d, "pretax_income"),
            "tax_provision": tax,
            "net_income_including_minority": _get(d, "net_income_including_minority"),
            "minority_interest_income": _get(d, "minority_interest_income"),
            "discontinued_ops": _get(d, "discontinued_ops"),
            "net_income": _get(d, "net_income"),
            "diluted_shares": _get(d, "diluted_shares"),
            "basic_shares": _get(d, "basic_shares"),
            "unusual_items": _get(d, "unusual_items"),
        })
    return rows


def build_balance_table(hist: dict, years: list[str]) -> list[dict]:
    """Build per-year balance sheet table."""
    balance = hist.get("balance", {})
    rows = []
    for yr in years:
        d = balance.get(yr, {})

        # Total debt: explicit or sum of parts
        total_debt = _get(d, "total_debt")
        if total_debt is None:
            lt = _get(d, "long_term_debt") or 0
            st_debt = _get(d, "short_term_debt") or 0
            cp = _get(d, "current_portion_ltd", "current_debt") or 0
            total_debt = lt + st_debt + cp if (lt or st_debt or cp) else None

        cash = _get(d, "cash", "cash_and_equivalents")
        net_debt = None
        if total_debt is not None and cash is not None:
            net_debt = total_debt - cash

        rows.append({
            "year": yr,
            "source": d.get("_source", ""),
            # Assets
            "cash": cash,
            "short_term_investments": _get(d, "short_term_investments"),
            "accounts_receivable": _get(d, "accounts_receivable"),
            "inventories": _get(d, "inventories"),
            "other_current_assets": _get(d, "other_current_assets"),
            "total_current_assets": _get(d, "total_current_assets"),
            "pp_and_e": _get(d, "pp_and_e"),
            "gross_ppe": _get(d, "gross_ppe"),
            "accumulated_depreciation": _get(d, "accumulated_depreciation"),
            "goodwill": _get(d, "goodwill"),
            "intangible_assets": _get(d, "intangible_assets"),
            "goodwill_and_intangibles": _get(d, "goodwill_and_intangibles"),
            "operating_lease_assets": _get(d, "operating_lease_assets"),
            "long_term_investments": _get(d, "long_term_investments", "investments_and_advances"),
            "equity_method_investments": _get(d, "equity_method_investments"),
            "other_non_current_assets": _get(d, "other_non_current_assets"),
            "total_non_current_assets": _get(d, "total_non_current_assets"),
            "total_assets": _get(d, "total_assets"),
            # Liabilities
            "accounts_payable": _get(d, "accounts_payable"),
            "accrued_expenses": _get(d, "accrued_expenses"),
            "short_term_debt": _get(d, "short_term_debt"),
            "current_portion_ltd": _get(d, "current_portion_ltd", "current_debt"),
            "operating_lease_current": _get(d, "operating_lease_current"),
            "accrued_income_taxes": _get(d, "accrued_income_taxes"),
            "other_current_liabilities": _get(d, "other_current_liabilities"),
            "total_current_liabilities": _get(d, "total_current_liabilities"),
            "long_term_debt": _get(d, "long_term_debt"),
            "operating_lease_nc": _get(d, "operating_lease_nc"),
            "deferred_tax_liabilities": _get(d, "deferred_tax_liabilities"),
            "deferred_tax_nc": _get(d, "deferred_tax_nc"),
            "pension_obligations": _get(d, "pension_obligations"),
            "deferred_revenue_nc": _get(d, "deferred_revenue_nc"),
            "other_nc_liabilities": _get(d, "other_nc_liabilities"),
            "total_non_current_liabilities": _get(d, "total_non_current_liabilities"),
            "total_debt": total_debt,
            "total_liabilities": _get(d, "total_liabilities"),
            # Equity
            "common_stock": _get(d, "common_stock"),
            "additional_paid_in_capital": _get(d, "additional_paid_in_capital"),
            "retained_earnings": _get(d, "retained_earnings"),
            "accumulated_oci": _get(d, "accumulated_oci"),
            "treasury_stock": _get(d, "treasury_stock"),
            "preferred_stock": _get(d, "preferred_stock"),
            "total_equity": _get(d, "total_equity"),
            "total_equity_incl_minority": _get(d, "total_equity_incl_minority"),
            "minority_interest": _get(d, "minority_interest"),
            "total_liabilities_and_equity": _get(d, "total_liabilities_and_equity"),
            # Derived
            "net_debt": net_debt,
            "shares_outstanding": _get(d, "shares_outstanding", "shares_issued"),
            "working_capital": _get(d, "working_capital"),
            "invested_capital": _get(d, "invested_capital"),
        })
    return rows


def build_cashflow_table(hist: dict, years: list[str]) -> list[dict]:
    """Build per-year cash flow statement table."""
    cashflow = hist.get("cashflow", {})
    rows = []
    for yr in years:
        d = cashflow.get(yr, {})
        ocf = _get(d, "operating_cash_flow")
        capex = _get(d, "capital_expenditure")
        fcf = _get(d, "free_cash_flow")
        if fcf is None and ocf is not None and capex is not None:
            fcf = ocf + capex  # capex is negative

        rows.append({
            "year": yr,
            "source": d.get("_source", ""),
            # Operating
            "operating_cash_flow": ocf,
            "net_income_cf": _get(d, "net_income_cf"),
            "depreciation_amortization": _get(d, "depreciation_amortization", "da"),
            "stock_based_compensation": _get(d, "stock_based_compensation", "sbc"),
            "deferred_income_tax": _get(d, "deferred_income_tax", "deferred_tax"),
            "asset_impairment": _get(d, "asset_impairment"),
            "other_non_cash": _get(d, "other_non_cash"),
            "change_in_receivables": _get(d, "change_in_receivables", "change_in_ar"),
            "change_in_payables": _get(d, "change_in_payables", "change_in_ap"),
            "change_in_other_wc": _get(d, "change_in_other_wc"),
            "change_in_deferred_revenue": _get(d, "change_in_deferred_revenue"),
            # Investing
            "capital_expenditure": capex,
            "acquisitions": _get(d, "acquisitions"),
            "investment_purchases": _get(d, "investment_purchases"),
            "investment_proceeds": _get(d, "investment_proceeds"),
            "divestiture_proceeds": _get(d, "divestiture_proceeds"),
            "investing_cash_flow": _get(d, "investing_cash_flow"),
            # Financing
            "debt_issuance": _get(d, "debt_issuance"),
            "debt_repayment": _get(d, "debt_repayment"),
            "buybacks_and_issuance": _get(d, "buybacks_and_issuance", "buybacks"),
            "stock_issuance_proceeds": _get(d, "stock_issuance_proceeds"),
            "dividends_paid": _get(d, "dividends_paid"),
            "minority_distributions": _get(d, "minority_distributions"),
            "financing_cash_flow": _get(d, "financing_cash_flow"),
            # Summary
            "free_cash_flow": fcf,
            "fx_effect": _get(d, "fx_effect"),
            "net_change_in_cash": _get(d, "net_change_in_cash"),
            "ending_cash": _get(d, "ending_cash"),
        })
    return rows
