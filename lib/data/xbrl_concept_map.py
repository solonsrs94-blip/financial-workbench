"""XBRL US-GAAP concept → standardized key mapping.

Layer 1 of the standardization system. Maps SEC-required XBRL taxonomy
concepts to our internal keys. Covers ~90-95% of line items.

Built from analysis of 10 diverse companies' EDGAR filings:
AAPL, MSFT, XOM, JNJ, WMT, V, CAT, MCD, PFE, AMZN.
"""

# === INCOME STATEMENT ===

IS_CONCEPT_MAP = {
    # Revenue
    "Revenue": "revenue",
    # Costs
    "CostOfGoodsAndServicesSold": "cogs",
    "GrossProfit": "gross_profit",
    # Operating expenses
    "SellingGeneralAndAdminExpenses": "sga",
    "MarketingExpenses": "marketing",
    "ResearchAndDevelopementExpenses": "rd",
    "DepreciationExpense": "da",
    "CommunicationAndTechnologyExpense": "network_processing",
    "ProfessionalFees": "professional_fees",
    "PensionExpense": "pension_expense",
    "RestructuringExpenseBenefit": "restructuring",
    "TotalOperatingExpenses": "total_opex",
    "CostsSubtotal": "total_costs",
    "OtherExpenseIS": "other_operating_expense",
    "OtherIncomeIS": "other_operating_income",
    # Operating income
    "OperatingIncomeLoss": "ebit",
    # Non-operating
    "InterestExpense": "interest_expense",
    "InterestAndDividendIncome": "interest_income",
    "NonoperatingIncomeExpense": "other_non_operating",
    "EquityMethodInvestmentIncome": "equity_method_income",
    # Pre-tax & tax
    "PretaxIncomeLoss": "pretax_income",
    "IncomeTaxes": "tax_provision",
    # Net income
    "ProfitLoss": "net_income_including_minority",
    "MinorityInterestIncomeExpense": "minority_interest_income",
    "NetIncome": "net_income",
    "NetIncomeToCommonShareholders": "net_income_common",
    "IncomeLossContinuingOperations": "income_continuing_ops",
    "DiscontinuedOperationsIncome": "discontinued_ops",
    # Per share
    "SharesAverage": "basic_shares",
    "SharesFullyDilutedAverage": "diluted_shares",
    "CommonDividendsPerShare": "dividends_per_share",
}


# === BALANCE SHEET ===

BS_CONCEPT_MAP = {
    # Current assets
    "CashAndMarketableSecurities": "cash",
    "ShortTermInvestments": "short_term_investments",
    "RestrictedCashCurrent": "restricted_cash_current",
    "TradeReceivables": "accounts_receivable",
    "Inventories": "inventories",
    "OtherNonOperatingCurrentAssets": "other_current_assets",
    "CurrentAssetsTotal": "total_current_assets",
    # Non-current assets
    "PlantPropertyEquipmentNet": "pp_and_e",
    "GrossPropertyPlantEquipment": "gross_ppe",
    "AccumulatedDepreciation": "accumulated_depreciation",
    "Goodwill": "goodwill",
    "IntangibleAssets": "intangible_assets",
    "OperatingLeaseRightOfUseAsset": "operating_lease_assets",
    "LongtermInvestments": "long_term_investments",
    "InvestmentsEquityMethod": "equity_method_investments",
    "DeferredTaxNoncurrentAssets": "deferred_tax_assets",
    "OtherNonOperatingNonCurrentAssets": "other_non_current_assets",
    "OtherOperatingNonCurrentAssets": "other_operating_nc_assets",
    "NotesReceivableNonCurrent": "notes_receivable_nc",
    "NonCurrentAssetsTotal": "total_non_current_assets",
    "Assets": "total_assets",
    # Current liabilities
    "TradePayables": "accounts_payable",
    "ShortTermDebt": "short_term_debt",
    "CurrentPortionOfLongTermDebt": "current_portion_ltd",
    "OtherOperatingCurrentLiabilities": "accrued_expenses",
    "OtherNonOperatingCurrentLiabilities": "other_current_liabilities",
    "AccruedIncomeTaxes": "accrued_income_taxes",
    "AccruedCompensation": "accrued_compensation",
    "DividendsPayable": "dividends_payable",
    "OperatingLeaseCurrentDebtEquivalent": "operating_lease_current",
    "CurrentLiabilitiesTotal": "total_current_liabilities",
    # Non-current liabilities
    "LongTermDebt": "long_term_debt",
    "OperatingLeaseNonCurrentDebtEquivalent": "operating_lease_nc",
    "DeferredTaxCurrentLiabilities": "deferred_tax_liabilities",
    "DeferredTaxNonCurrentLiabilities": "deferred_tax_nc",
    "PensionObligations": "pension_obligations",
    "OtherNonOperatingNonCurrentLiabilities": "other_nc_liabilities",
    "DeferredRevenueNonCurrent": "deferred_revenue_nc",
    "ContractLiabilities": "contract_liabilities",
    "NonCurrentLiabilitiesTotal": "total_non_current_liabilities",
    "Liabilities": "total_liabilities",
    "TemporaryAndMezzanineFinancing": "redeemable_minority",
    # Equity
    "CommonEquity": "common_stock",
    "AdditionalPaidInCapital": "additional_paid_in_capital",
    "RetainedEarnings": "retained_earnings",
    "AccumulatedOtherComprehensiveIncome": "accumulated_oci",
    "TreasuryShares": "treasury_stock",
    "PreferredStock": "preferred_stock",
    "AllEquityBalance": "total_equity",
    "AllEquityBalanceIncludingMinorityInterest": "total_equity_incl_minority",
    "MinorityInterestBalance": "minority_interest",
    "SharesYearEnd": "shares_outstanding",
    "SharesIssued": "shares_issued",
    "LiabilitiesAndEquity": "total_liabilities_and_equity",
    "TaxesPayable": "taxes_payable",
}


# === CASH FLOW STATEMENT ===
# NOTE: NetCashFromOperating/Investing/FinancingActivities appear multiple
# times in EDGAR — as individual items AND as sub-totals. These are excluded
# from the concept map and handled specially in the standardizer using
# SUBTOTAL_CONCEPTS, which ensures the sub-total (last occurrence) is used.

CF_CONCEPT_MAP = {
    # Operating
    "ProfitLoss": "net_income_cf",
    "NetIncome": "net_income_cf",
    "DepreciationExpense": "depreciation_amortization",
    "StockBasedCompensationExpense": "stock_based_compensation",
    "IncomeTaxes": "deferred_income_tax",
    "OtherNonCashItemsCF": "other_non_cash",
    "ProvisionForDoubtfulAccountsCF": "provision_doubtful",
    "AssetImpairmentChargesIS": "asset_impairment",
    "RestructuringExpenseBenefit": "restructuring_cf",
    "GainLossOnInvestmentsIS": "investment_gains_losses",
    "GainLossOnDispositions": "disposition_gains_losses",
    "NonoperatingIncomeExpense": "non_operating_cf",
    "ChangeInReceivables": "change_in_receivables",
    "ChangeInPayables": "change_in_payables",
    "ChangeInAccruedLiabilities": "change_in_accrued",
    "ChangeInOtherWorkingCapital": "change_in_other_wc",
    "ChangeInDeferredRevenue": "change_in_deferred_revenue",
    "DiscontinuedOperationsIncome": "discontinued_ops_cf",
    # Investing
    "CapitalExpenses": "capital_expenditure",
    "AcquisitionsNet": "acquisitions",
    "InvestmentPurchases": "investment_purchases",
    "InvestmentProceeds": "investment_proceeds",
    "ProceedsFromSaleOfPPE": "proceeds_ppe_sale",
    "DivestitureProceeds": "divestiture_proceeds",
    # Financing
    "DebtProceeds": "debt_issuance",
    "DebtRepayments": "debt_repayment",
    "EquityExpenseIncome(BuybackIssued)": "buybacks_and_issuance",
    "StockIssuanceProceeds": "stock_issuance_proceeds",
    "DistributionsToMinorityInterests": "minority_distributions",
    "FinanceLeasePayments": "finance_lease_payments",
    # Other
    "ForeignExchangeEffectOnCash": "fx_effect",
    "NetChangeInCash": "net_change_in_cash",
    "CashAndCashEquivalents": "ending_cash",
    "InterestExpense": "interest_paid",
}

# Concepts that appear multiple times — always use the LAST occurrence
# (which is the sub-total). Map concept → standardized key.
CF_SUBTOTAL_CONCEPTS = {
    "NetCashFromOperatingActivities": "operating_cash_flow",
    "NetCashFromInvestingActivities": "investing_cash_flow",
    "NetCashFromFinancingActivities": "financing_cash_flow",
}


# === KEYWORD FALLBACK (Layer 2) ===
# (keyword_substring, standardized_key, statement_type)

KEYWORD_FALLBACKS = [
    # Income
    ("revenue", "revenue", "income"),
    ("net sales", "revenue", "income"),
    ("sales to customers", "revenue", "income"),
    ("cost of revenue", "cogs", "income"),
    ("cost of goods", "cogs", "income"),
    ("cost of products", "cogs", "income"),
    ("cost of sales", "cogs", "income"),
    ("gross profit", "gross_profit", "income"),
    ("gross margin", "gross_profit", "income"),
    ("selling, general", "sga", "income"),
    ("selling general", "sga", "income"),
    ("research and development", "rd", "income"),
    ("depreciation", "da", "income"),
    ("amortization", "da", "income"),
    ("operating income", "ebit", "income"),
    ("operating profit", "ebit", "income"),
    ("interest expense", "interest_expense", "income"),
    ("interest income", "interest_income", "income"),
    ("pretax income", "pretax_income", "income"),
    ("income before", "pretax_income", "income"),
    ("earnings before provision", "pretax_income", "income"),
    ("income tax", "tax_provision", "income"),
    ("provision for", "tax_provision", "income"),
    ("net income", "net_income", "income"),
    ("net earnings", "net_income", "income"),
    ("restructuring", "restructuring", "income"),
    ("impairment", "impairment", "income"),
    # Balance sheet
    ("cash and cash equivalents", "cash", "balance"),
    ("accounts receivable", "accounts_receivable", "balance"),
    ("inventories", "inventories", "balance"),
    ("total current assets", "total_current_assets", "balance"),
    ("property and equipment", "pp_and_e", "balance"),
    ("property, plant", "pp_and_e", "balance"),
    ("goodwill", "goodwill", "balance"),
    ("intangible", "intangible_assets", "balance"),
    ("total assets", "total_assets", "balance"),
    ("accounts payable", "accounts_payable", "balance"),
    ("total current liabilities", "total_current_liabilities", "balance"),
    ("long-term debt", "long_term_debt", "balance"),
    ("total liabilities", "total_liabilities", "balance"),
    ("retained earnings", "retained_earnings", "balance"),
    ("accumulated deficit", "retained_earnings", "balance"),
    ("stockholders' equity", "total_equity", "balance"),
    ("shareholders' equity", "total_equity", "balance"),
    ("total equity", "total_equity", "balance"),
    ("minority interest", "minority_interest", "balance"),
    ("noncontrolling interest", "minority_interest", "balance"),
    # Cash flow
    ("operating cash flow", "operating_cash_flow", "cashflow"),
    ("net cash from operating", "operating_cash_flow", "cashflow"),
    ("net cash provided by operating", "operating_cash_flow", "cashflow"),
    ("capital expenditure", "capital_expenditure", "cashflow"),
    ("purchases of property", "capital_expenditure", "cashflow"),
    ("additions to property", "capital_expenditure", "cashflow"),
    ("depreciation and amortization", "depreciation_amortization", "cashflow"),
    ("stock-based comp", "stock_based_compensation", "cashflow"),
    ("share-based comp", "stock_based_compensation", "cashflow"),
    ("acquisition", "acquisitions", "cashflow"),
    ("repurchase", "buybacks_and_issuance", "cashflow"),
    ("common stock acquired", "buybacks_and_issuance", "cashflow"),
    ("dividend", "dividends_paid", "cashflow"),
    ("investing cash flow", "investing_cash_flow", "cashflow"),
    ("net cash from investing", "investing_cash_flow", "cashflow"),
    ("net cash used in investing", "investing_cash_flow", "cashflow"),
    ("financing cash flow", "financing_cash_flow", "cashflow"),
    ("net cash from financing", "financing_cash_flow", "cashflow"),
    ("net cash used in financing", "financing_cash_flow", "cashflow"),
    ("free cash flow", "free_cash_flow", "cashflow"),
]
