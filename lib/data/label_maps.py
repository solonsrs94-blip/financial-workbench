"""Label maps — standardize financial statement labels across providers.

Maps lowercase label strings to standardized keys.
Covers EDGAR (as-reported), Yahoo Finance, and SimFin label variations.
Updated iteratively by testing across diverse companies.
"""

# Income Statement labels -> standardized keys
IS_LABEL_MAP = {
    # Revenue (many variations across companies)
    "total revenue": "total_revenue",
    "net sales": "total_revenue",
    "revenues": "total_revenue",
    "net revenues": "total_revenue",
    "revenue": "total_revenue",
    "sales and other operating revenue": "total_revenue",
    "sales to customers": "total_revenue",  # JNJ
    "net revenue": "total_revenue",
    "total net revenue": "total_revenue",
    "total revenues and other income": "total_revenue",
    "total net sales": "total_revenue",  # AMZN
    "total sales and revenues": "total_revenue",  # CAT
    "total revenues": "total_revenue",  # XOM
    # COGS
    "cost of revenue": "cost_of_revenue",
    "cost of revenues": "cost_of_revenue",
    "cost of sales": "cost_of_revenue",
    "cost of goods sold": "cost_of_revenue",
    "cost of products sold": "cost_of_revenue",  # JNJ
    "cost of goods sold": "cost_of_revenue",  # CAT
    # Gross profit
    "gross profit": "gross_profit",
    "gross margin": "gross_profit",
    # OpEx
    "selling general and administration": "selling_general_admin",
    "selling, general and administrative": "selling_general_admin",
    "selling, marketing and administrative expenses": "selling_general_admin",  # JNJ
    "general and administrative": "general_admin",
    "sales and marketing": "selling_marketing",
    "selling and marketing expense": "selling_marketing",
    "research and development": "research_development",
    "research & development": "research_development",
    "research and development expense": "research_development",  # JNJ
    "total operating expenses": "operating_expenses",
    "total costs and expenses": "operating_expenses",
    "operating expense": "operating_expenses",
    # D&A
    "depreciation and amortization": "depreciation_amortization",
    "depreciation & amortization": "depreciation_amortization",
    "depreciation and depletion (includes impairments)": "depreciation_amortization",
    "reconciled depreciation": "depreciation_amortization",
    # Operating income
    "operating income": "ebit",
    "income from operations": "ebit",
    "operating income (loss)": "ebit",
    "ebit": "ebit",
    "ebitda": "ebitda",
    "operating profit": "ebit",  # CAT
    "total operating costs": "operating_expenses",  # CAT
    # Below EBIT
    "interest expense": "interest_expense",
    "interest expense, net of portion capitalized": "interest_expense",  # JNJ
    "interest income": "interest_income",
    "other income (expense), net": "other_income_expense",
    "other income expense": "other_income_expense",
    "other (income) expense, net": "other_income_expense",  # JNJ
    "non-operating income (loss)": "other_income_expense",
    "restructuring": "restructuring_charges",
    # Pretax
    "pretax income": "pretax_income",
    "income before provision for income taxes": "pretax_income",
    "income before income taxes": "pretax_income",
    "income (loss) before income taxes": "pretax_income",
    "earnings before provision for taxes on income": "pretax_income",  # JNJ
    "income before income taxes": "pretax_income",  # AMZN
    "consolidated profit before taxes": "pretax_income",  # CAT
    "income (loss) before income taxes": "pretax_income",  # XOM
    # Tax
    "tax provision": "tax_provision",
    "provision for income taxes": "tax_provision",
    "provision for taxes on income": "tax_provision",  # JNJ
    "income tax expense (benefit)": "tax_provision",
    "income taxes expense (benefit)": "tax_provision",
    "income tax (expense) benefit, net": "tax_provision",
    "income tax expense (benefit)": "tax_provision",  # XOM
    "provision (benefit) for income taxes": "tax_provision",  # CAT
    # Net income
    "net income": "net_income",
    "net earnings": "net_income",  # JNJ
    "net income (loss) attributable to exxonmobil": "net_income",
    "net earnings from continuing operations": "net_income",
    "profit (loss)": "net_income",  # CAT
    "net income (loss) attributable to exxonmobil": "net_income",  # XOM
    "net income (loss) including noncontrolling interests": "net_income",
    "net income (loss)": "net_income",  # AMZN older filings
    "income from continuing operations": "net_income",  # PFE
    "net income before allocation to noncontrolling interests": "net_income",  # PFE
    "profit of consolidated and affiliated companies": "net_income",  # CAT alt
    # Pretax extra
    "income from continuing operations before provision/(benefit) for taxes on income": "pretax_income",  # PFE
    "income from continuing operations before provision for taxes on income": "pretax_income",  # PFE
    # Tax extra
    "provision/(benefit) for taxes on income": "tax_provision",  # PFE
    "benefit (provision) for income taxes": "tax_provision",  # AMZN alt
    # EPS / Shares
    "diluted eps": "diluted_eps",
    "diluted (in dollars per share)": "diluted_eps",
    "diluted average shares": "diluted_shares",
    "diluted (in shares)": "diluted_shares",
    "shares (diluted)": "diluted_shares",
    # Special items
    "european commission fines": "special_charges",
    "in-process research and development impairments": "special_charges",
    "total unusual items": "unusual_items",
}

# Balance Sheet labels -> standardized keys
BS_LABEL_MAP = {
    "cash and cash equivalents": "cash_and_equivalents",
    "cash & cash equivalents": "cash_and_equivalents",
    "marketable securities": "short_term_investments",
    "accounts receivable, net": "accounts_receivable",
    "accounts receivable": "accounts_receivable",
    "trade receivables": "accounts_receivable",
    "inventories": "inventories",
    "inventory": "inventories",
    "other current assets": "other_current_assets",
    "total current assets": "total_current_assets",
    "property, plant and equipment, net": "pp_and_e",
    "property and equipment, net": "pp_and_e",
    "net ppe": "pp_and_e",
    "goodwill": "goodwill",
    "intangible assets, net": "other_intangibles",
    "total assets": "total_assets",
    "accounts payable": "accounts_payable",
    "total current liabilities": "total_current_liabilities",
    "long-term debt": "long_term_debt",
    "term debt": "long_term_debt",
    "long term debt": "long_term_debt",
    "total debt": "total_debt",
    "total liabilities": "total_liabilities",
    "total liabilities net minority interest": "total_liabilities",
    "stockholders equity": "total_equity",
    "stockholders' equity": "total_equity",
    "total shareholders' equity": "total_equity",
    "total stockholders' equity": "total_equity",
    "total shareholders\u2019 equity": "total_equity",
    "stockholders' equity/(deficit) attributable to parent": "total_equity",  # SBUX
    "stockholders' equity/(deficit), including portion attributable to noncontrolling interest": "total_equity",
    "total shareholders' deficit": "total_equity",
    "retained earnings": "retained_earnings",
    "accumulated deficit": "retained_earnings",
    "minority interest": "minority_interest",
    "ordinary shares number": "shares_outstanding",
    "working capital": "working_capital",
    "invested capital": "invested_capital",
    "net debt": "net_debt",
}

# Cash Flow Statement labels -> standardized keys
CF_LABEL_MAP = {
    # Operating
    "operating cash flow": "operating_cash_flow",
    "cash generated by operating activities": "operating_cash_flow",
    "net cash from operating activities": "operating_cash_flow",
    "net cash provided by operating activities": "operating_cash_flow",  # META
    "cash flow from continuing operating activities": "operating_cash_flow",
    # CapEx (many variations!)
    "capital expenditure": "capital_expenditure",
    "payments for acquisition of property, plant and equipment": "capital_expenditure",
    "purchases of property and equipment": "capital_expenditure",  # META
    "purchases of property and equipment, net": "capital_expenditure",
    "purchases of property, plant and equipment": "capital_expenditure",
    "additions to property and equipment": "capital_expenditure",
    "purchase of ppe": "capital_expenditure",
    # FCF
    "free cash flow": "free_cash_flow",
    # Investing
    "investing cash flow": "investing_cash_flow",
    "cash generated by investing activities": "investing_cash_flow",
    "cash used in investing activities": "investing_cash_flow",
    "net cash from investing activities": "investing_cash_flow",
    "net cash used in investing activities": "investing_cash_flow",  # META
    "cash flow from continuing investing activities": "investing_cash_flow",
    # Financing
    "financing cash flow": "financing_cash_flow",
    "cash used in financing activities": "financing_cash_flow",
    "net cash from financing activities": "financing_cash_flow",
    "net cash used in financing activities": "financing_cash_flow",  # META
    "cash flow from continuing financing activities": "financing_cash_flow",
    # D&A
    "depreciation and amortization": "depreciation_amortization",
    "depreciation & amortization": "depreciation_amortization",
    "depreciation amortization depletion": "depreciation_amortization",
    # SBC (many variations!)
    "stock based compensation": "stock_based_compensation",
    "share-based compensation expense": "stock_based_compensation",
    "share-based compensation": "stock_based_compensation",  # META
    "stock-based compensation": "stock_based_compensation",
    "stock-based compensation expense": "stock_based_compensation",
    # Dividends
    "common stock dividend paid": "dividends_paid",
    "cash dividends paid": "dividends_paid",
    "payments for dividends and dividend equivalents": "dividends_paid",  # META
    # Buybacks
    "repurchase of capital stock": "buybacks",
    "repurchases of common stock": "buybacks",
    "repurchases of class a common stock": "buybacks",  # META
    # WC
    "change in working capital": "change_in_wc",
    # Acquisitions
    "purchase of business": "acquisitions",
    "acquisitions of businesses and intangible assets": "acquisitions",
    "acquisitions of businesses, net of cash acquired, and purchases of intangible assets": "acquisitions",
    # Debt
    "issuance of debt": "debt_issuance",
    "repayment of debt": "debt_repayment",
    "net issuance payments of debt": "net_debt_issuance",
    "proceeds from issuance of long-term debt, net": "debt_issuance",
}
