"""SimFin column name -> standardized key mappings.

Split from simfin_provider.py for file size compliance.
"""

# --- General IS ---
GENERAL_IS_MAP = {
    "Revenue": "revenue",
    "Cost of Revenue": "cogs",
    "Gross Profit": "gross_profit",
    "Selling, General & Administrative": "sga",
    "Research & Development": "rd",
    "Depreciation & Amortization": "da_is",
    "Operating Expenses": "total_opex",
    "Operating Income (Loss)": "ebit",
    "Non-Operating Income (Loss)": "other_non_operating",
    "Interest Expense, Net": "interest_expense",
    "Pretax Income (Loss), Adj.": "pretax_income_adj",
    "Abnormal Gains (Losses)": "abnormal_gains",
    "Pretax Income (Loss)": "pretax_income",
    "Income Tax (Expense) Benefit, Net": "tax_provision",
    "Income (Loss) from Continuing Operations": "income_continuing_ops",
    "Net Extraordinary Gains (Losses)": "extraordinary_items",
    "Net Income": "net_income",
    "Net Income (Common)": "net_income_common",
    "Shares (Basic)": "basic_shares",
    "Shares (Diluted)": "diluted_shares",
}

# --- General BS ---
GENERAL_BS_MAP = {
    "Cash, Cash Equivalents & Short Term Investments": "cash",
    "Accounts & Notes Receivable": "accounts_receivable",
    "Inventories": "inventories",
    "Total Current Assets": "total_current_assets",
    "Property, Plant & Equipment, Net": "pp_and_e",
    "Long Term Investments & Receivables": "long_term_investments",
    "Other Long Term Assets": "other_non_current_assets",
    "Total Noncurrent Assets": "total_non_current_assets",
    "Total Assets": "total_assets",
    "Payables & Accruals": "accounts_payable",
    "Short Term Debt": "short_term_debt",
    "Total Current Liabilities": "total_current_liabilities",
    "Long Term Debt": "long_term_debt",
    "Total Noncurrent Liabilities": "total_non_current_liabilities",
    "Total Liabilities": "total_liabilities",
    "Share Capital & Additional Paid-In Capital": "common_stock",
    "Treasury Stock": "treasury_stock",
    "Retained Earnings": "retained_earnings",
    "Total Equity": "total_equity",
    "Total Liabilities & Equity": "total_liabilities_and_equity",
    "Shares (Basic)": "basic_shares_bs",
    "Shares (Diluted)": "diluted_shares_bs",
}

# --- General CF ---
GENERAL_CF_MAP = {
    "Net Income/Starting Line": "net_income_cf",
    "Depreciation & Amortization": "depreciation_amortization",
    "Non-Cash Items": "non_cash_items",
    "Change in Working Capital": "change_in_working_capital",
    "Change in Accounts Receivable": "change_in_receivables",
    "Change in Inventories": "change_in_inventory",
    "Change in Accounts Payable": "change_in_payables",
    "Change in Other": "change_in_other_wc",
    "Net Cash from Operating Activities": "operating_cash_flow",
    "Change in Fixed Assets & Intangibles": "capital_expenditure",
    "Net Change in Long Term Investment": "net_investment",
    "Net Cash from Acquisitions & Divestitures": "acquisitions",
    "Net Cash from Investing Activities": "investing_cash_flow",
    "Dividends Paid": "dividends_paid",
    "Cash from (Repayment of) Debt": "net_debt_change",
    "Cash from (Repurchase of) Equity": "stock_repurchases",
    "Net Cash from Financing Activities": "financing_cash_flow",
    "Net Change in Cash": "net_change_in_cash",
}

# --- Bank IS ---
BANK_IS_MAP = {
    "Revenue": "revenue",
    "Provision for Loan Losses": "provision_for_loan_losses",
    "Net Revenue after Provisions": "net_revenue_after_provisions",
    "Total Non-Interest Expense": "total_non_interest_expense",
    "Operating Income (Loss)": "ebit",
    "Non-Operating Income (Loss)": "other_non_operating",
    "Pretax Income (Loss)": "pretax_income",
    "Income Tax (Expense) Benefit, Net": "tax_provision",
    "Income (Loss) from Continuing Operations": "income_continuing_ops",
    "Net Extraordinary Gains (Losses)": "extraordinary_items",
    "Net Income": "net_income",
    "Net Income (Common)": "net_income_common",
    "Shares (Basic)": "basic_shares",
    "Shares (Diluted)": "diluted_shares",
}

# --- Bank BS ---
BANK_BS_MAP = {
    "Cash, Cash Equivalents & Short Term Investments": "cash",
    "Interbank Assets": "interbank_assets",
    "Short & Long Term Investments": "investments",
    "Accounts & Notes Receivable": "accounts_receivable",
    "Net Loans": "net_loans",
    "Net Fixed Assets": "pp_and_e",
    "Total Assets": "total_assets",
    "Total Deposits": "total_deposits",
    "Short Term Debt": "short_term_debt",
    "Long Term Debt": "long_term_debt",
    "Total Liabilities": "total_liabilities",
    "Preferred Equity": "preferred_equity",
    "Share Capital & Additional Paid-In Capital": "common_stock",
    "Treasury Stock": "treasury_stock",
    "Retained Earnings": "retained_earnings",
    "Total Equity": "total_equity",
    "Total Liabilities & Equity": "total_liabilities_and_equity",
    "Shares (Basic)": "basic_shares_bs",
    "Shares (Diluted)": "diluted_shares_bs",
}

# --- Bank CF ---
BANK_CF_MAP = {
    "Net Income/Starting Line": "net_income_cf",
    "Depreciation & Amortization": "depreciation_amortization",
    "Provision for Loan Losses": "provision_for_loan_losses_cf",
    "Non-Cash Items": "non_cash_items",
    "Change in Working Capital": "change_in_working_capital",
    "Net Cash from Operating Activities": "operating_cash_flow",
    "Change in Fixed Assets & Intangibles": "capital_expenditure",
    "Net Change in Loans & Interbank": "net_change_in_loans",
    "Net Cash from Acquisitions & Divestitures": "acquisitions",
    "Net Cash from Investing Activities": "investing_cash_flow",
    "Dividends Paid": "dividends_paid",
    "Cash from (Repayment of) Debt": "net_debt_change",
    "Cash from (Repurchase of) Equity": "stock_repurchases",
    "Net Cash from Financing Activities": "financing_cash_flow",
    "Effect of Foreign Exchange Rates": "fx_effect",
    "Net Change in Cash": "net_change_in_cash",
}

# --- Insurance IS ---
INSURANCE_IS_MAP = {
    "Revenue": "revenue",
    "Total Claims & Losses": "total_claims_and_losses",
    "Operating Income (Loss)": "ebit",
    "Pretax Income (Loss)": "pretax_income",
    "Income Tax (Expense) Benefit, Net": "tax_provision",
    "Income (Loss) from Affiliates, Net of Taxes": "affiliate_income",
    "Income (Loss) from Continuing Operations": "income_continuing_ops",
    "Net Extraordinary Gains (Losses)": "extraordinary_items",
    "Net Income": "net_income",
    "Net Income (Common)": "net_income_common",
    "Shares (Basic)": "basic_shares",
    "Shares (Diluted)": "diluted_shares",
}
