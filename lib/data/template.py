"""Top-down financial statement template — hub file.

Defines the 35 line items needed for valuation (DCF, Comps, DDM)
and combines search rules from template_is.py, template_bs.py, template_cf.py.
"""

from lib.data.template_is import IS_SEARCH_RULES
from lib.data.template_bs import BS_SEARCH_RULES
from lib.data.template_cf import CF_SEARCH_RULES

# ═══════════════════════════════════════════════════════════════════════
#  TEMPLATE DEFINITION
# ═══════════════════════════════════════════════════════════════════════

TEMPLATE = {
    "income": [
        "revenue", "cogs", "gross_profit", "sga", "rd", "da_is",
        "total_opex", "ebit", "ebitda", "interest_expense",
        "other_non_operating", "pretax_income", "tax_provision",
        "net_income", "diluted_eps", "basic_eps",
        "diluted_shares", "basic_shares",
    ],
    "balance": [
        "cash", "short_term_investments", "accounts_receivable",
        "inventories", "total_current_assets", "pp_and_e", "goodwill",
        "intangible_assets", "total_assets", "accounts_payable",
        "deferred_revenue_current", "short_term_debt", "current_portion_ltd",
        "total_current_liabilities", "long_term_debt", "total_liabilities",
        "common_stock", "retained_earnings", "total_equity",
        "total_liabilities_and_equity", "shares_outstanding",
        "total_debt", "net_debt",
    ],
    "cashflow": [
        "net_income_cf", "depreciation_amortization",
        "stock_based_compensation", "deferred_income_tax",
        "change_in_receivables", "change_in_inventory",
        "change_in_payables", "change_in_working_capital",
        "operating_cash_flow", "capital_expenditure", "acquisitions",
        "investment_purchases", "investment_proceeds",
        "investing_cash_flow", "dividends_paid", "stock_repurchases",
        "debt_issuance", "debt_repayment", "financing_cash_flow",
        "net_change_in_cash", "free_cash_flow",
    ],
}

# Lines that are critical for valuation — warn if missing
CRITICAL_LINES = [
    "revenue", "ebit", "net_income",
    "total_assets", "total_equity",
    "operating_cash_flow", "capital_expenditure", "free_cash_flow",
    "depreciation_amortization", "diluted_shares",
]

IMPORTANT_LINES = [
    "cogs", "gross_profit", "sga", "rd",
    "cash", "accounts_receivable", "pp_and_e",
    "long_term_debt", "total_debt", "net_debt",
    "dividends_paid", "stock_repurchases",
    "tax_provision", "pretax_income",
]

# Combined search rules from all 3 statements
SEARCH_RULES = {**IS_SEARCH_RULES, **BS_SEARCH_RULES, **CF_SEARCH_RULES}
