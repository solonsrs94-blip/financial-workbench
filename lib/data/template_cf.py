"""Search rules for cash flow statement template lines."""

CF_SEARCH_RULES = {
    "net_income_cf": {
        "statement": "cashflow",
        "searches": [
            {"type": "concept", "values": ["ProfitLoss", "NetIncomeLoss", "NetIncomeLossAvailableToCommonStockholdersBasic"]},
            {"type": "sc", "values": ["NetIncome", "ProfitLoss"]},
            {"type": "keyword", "values": ["net income"]},
        ],
    },
    "depreciation_amortization": {
        "statement": "cashflow",
        "searches": [
            {"type": "concept", "values": [
                "DepreciationDepletionAndAmortization", "DepreciationAndAmortization",
                "DepreciationAmortizationAndAccretionNet", "Depreciation",
            ]},
            {"type": "sc", "values": ["DepreciationDepletionAndAmortization", "DepreciationExpense"]},
            {"type": "keyword", "values": [
                "depreciation, depletion and amortization", "depreciation and amortization",
                "depreciation, amortization", "depreciation of property",
            ]},
            {"type": "concept", "values": ["msft_DepreciationAmortizationAndOther"]},
            {"type": "combination", "parts": ["depreciation_only", "amortization_only"]},
        ],
    },
    "depreciation_only": {
        "statement": "cashflow",
        "helper": True,
        "searches": [
            {"type": "concept", "values": ["Depreciation", "goog_DepreciationAndImpairmentOnDispositionOfPropertyAndEquipment"]},
            {"type": "keyword", "values": ["depreciation and impairment of property", "depreciation of property"]},
        ],
    },
    "amortization_only": {
        "statement": "cashflow",
        "helper": True,
        "searches": [
            {"type": "concept", "values": ["AmortizationOfIntangibleAssets", "AdjustmentForAmortization", "goog_AmortizationAndImpairmentOfIntangibleAssets"]},
            {"type": "keyword", "values": ["amortization and impairment of intangible", "amortization of intangible"]},
        ],
    },
    "stock_based_compensation": {
        "statement": "cashflow",
        "searches": [
            {"type": "concept", "values": ["ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"]},
            {"type": "sc", "values": ["StockBasedCompensationExpense"]},
            {"type": "keyword", "values": ["stock-based compensation", "share-based compensation", "stock based compensation"]},
        ],
    },
    "deferred_income_tax": {
        "statement": "cashflow",
        "searches": [
            {"type": "concept", "values": ["DeferredIncomeTaxExpenseBenefit", "DeferredIncomeTaxesAndTaxCredits", "IncreaseDecreaseInDeferredIncomeTaxes"]},
            {"type": "sc", "values": ["DeferredIncomeTaxCF"]},
            {"type": "keyword", "values": ["deferred income tax", "deferred tax"]},
            {"type": "keyword_exclude", "values": ["cash paid", "taxes paid"]},
        ],
    },
    "change_in_receivables": {
        "statement": "cashflow",
        "searches": [
            {"type": "concept", "values": ["IncreaseDecreaseInAccountsReceivable", "IncreaseDecreaseInReceivables", "IncreaseDecreaseInAccountsAndNotesReceivable"]},
            {"type": "sc", "values": ["ChangeInReceivables"]},
            {"type": "keyword", "values": ["accounts receivable", "notes and accounts receivable", "receivables, net"]},
            {"type": "bs_delta", "bs_key": "accounts_receivable", "negate": True},
        ],
    },
    "change_in_inventory": {
        "statement": "cashflow",
        "searches": [
            {"type": "concept", "values": ["IncreaseDecreaseInInventories"]},
            {"type": "sc", "values": ["ChangeInInventories"]},
            {"type": "keyword", "values": ["inventories", "inventory"]},
            {"type": "bs_delta", "bs_key": "inventories", "negate": True},
        ],
    },
    "change_in_payables": {
        "statement": "cashflow",
        "searches": [
            {"type": "concept", "values": [
                "IncreaseDecreaseInAccountsPayable",
                "IncreaseDecreaseInAccountsPayableAndAccruedLiabilities",
                "IncreaseDecreaseInAccountsPayableTradeCurrent",
            ]},
            {"type": "sc", "values": ["ChangeInPayables"]},
            {"type": "keyword", "values": ["accounts payable", "accounts and other payables"]},
            {"type": "bs_delta", "bs_key": "accounts_payable", "negate": False},
        ],
    },
    "change_in_working_capital": {
        "statement": "cashflow",
        "searches": [
            {"type": "concept", "values": ["IncreaseDecreaseInOperatingCapital", "IncreaseDecreaseInOtherOperatingCapitalNet"]},
            {"type": "sc", "values": ["ChangeInOtherWorkingCapital"]},
            {"type": "keyword", "values": ["change in working capital", "changes in operating assets"]},
        ],
    },
    "operating_cash_flow": {
        "statement": "cashflow",
        "is_subtotal": True,
        "searches": [
            {"type": "concept", "values": ["NetCashProvidedByOperatingActivities", "NetCashProvidedByUsedInOperatingActivities"]},
            {"type": "sc_subtotal", "values": ["NetCashFromOperatingActivities"]},
            {"type": "keyword", "values": [
                "net cash provided by operating", "cash generated by operating",
                "net cash from operating", "cash from operating activities",
            ]},
        ],
    },
    "capital_expenditure": {
        "statement": "cashflow",
        "searches": [
            {"type": "concept", "values": [
                "PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets",
                "PaymentsForCapitalImprovements",
            ]},
            {"type": "sc", "values": ["CapitalExpenses"]},
            {"type": "keyword", "values": [
                "purchases of property, plant and equipment", "purchases of property and equipment",
                "additions to property, plant", "additions to property and equipment",
                "capital expenditure", "payments for acquisition of property",
            ]},
        ],
    },
    "acquisitions": {
        "statement": "cashflow",
        "searches": [
            {"type": "concept", "values": [
                "PaymentsToAcquireBusinessesNetOfCashAcquired", "PaymentsToAcquireBusinessesGross",
                "PaymentsToAcquireBusinessTwoNetOfCashAcquired",
            ]},
            {"type": "sc", "values": ["AcquisitionsNet"]},
            {"type": "keyword", "values": ["acquisitions, net of cash", "acquisition of companies", "purchase of business"]},
            {"type": "concept", "values": [
                "msft_AcquisitionsNetOfCashAcquiredAndPurchasesOfIntangibleAndOtherAssets",
                "goog_AcquisitionsNetOfCashAcquiredAndPurchasesOfIntangibleAssets",
                "amzn_PaymentsToAcquireBusinessesNetOfCashAcquiredAndPaymentsForIntangibleAndOtherAssets",
                "meta_PaymentsToAcquireBusinessesNetOfCashAcquiredAndPurchasesOfIntangibleAssets",
                "meta_AcquisitionOfBusinessAndIntangibleAssets",
                "fb_PaymentsToAcquireBusinessesNetOfCashAcquiredAndPurchasesOfIntangibleAndOtherAssets",
                "fb_PaymentsToAcquireBusinessesNetOfCashAcquiredAndPurchasesOfIntangibleAssets",
            ]},
        ],
    },
    "investment_purchases": {
        "statement": "cashflow",
        "searches": [
            {"type": "concept", "values": [
                "PaymentsToAcquireInvestments", "PaymentsToAcquireAvailableForSaleSecuritiesDebt",
                "PaymentsToAcquireMarketableSecurities", "PaymentsToAcquireShortTermInvestments",
            ]},
            {"type": "sc", "values": ["InvestmentPurchases"]},
            {"type": "keyword", "values": ["purchases of investments", "purchases of marketable securities"]},
        ],
    },
    "investment_proceeds": {
        "statement": "cashflow",
        "searches": [
            {"type": "concept", "values": [
                "ProceedsFromSaleAndMaturityOfMarketableSecurities",
                "ProceedsFromSaleMaturityAndCollectionsOfInvestments",
                "ProceedsFromMaturitiesPrepaymentsAndCallsOfAvailableForSaleSecurities",
                "ProceedsFromSaleOfAvailableForSaleSecuritiesDebt",
            ]},
            {"type": "sc", "values": ["InvestmentProceeds"]},
            {"type": "keyword", "values": ["maturities of investments", "sales of investments", "proceeds from maturities", "proceeds from sales of marketable"]},
            {"type": "concept", "values": ["msft_ProceedsFromInvestments"]},
        ],
    },
    "investing_cash_flow": {
        "statement": "cashflow",
        "is_subtotal": True,
        "searches": [
            {"type": "concept", "values": ["NetCashProvidedByUsedInInvestingActivities"]},
            {"type": "sc_subtotal", "values": ["NetCashFromInvestingActivities"]},
            {"type": "keyword", "values": ["net cash used in investing", "cash used in investing", "net cash from investing", "cash generated by investing"]},
        ],
    },
    "dividends_paid": {
        "statement": "cashflow",
        "searches": [
            {"type": "concept", "values": ["PaymentsOfDividendsCommonStock", "PaymentsOfDividends", "PaymentsOfOrdinaryDividends"]},
            {"type": "keyword", "values": [
                "dividends paid", "dividend payments", "cash dividends paid",
                "dividends to shareholders", "dividends and dividend equivalents",
            ]},
            {"type": "keyword_exclude", "values": ["noncontrolling", "minority"]},
        ],
    },
    "stock_repurchases": {
        "statement": "cashflow",
        "searches": [
            {"type": "concept", "values": ["PaymentsForRepurchaseOfCommonStock", "PaymentsForRepurchaseOfEquity"]},
            {"type": "sc", "values": ["EquityExpenseIncome(BuybackIssued)"]},
            {"type": "keyword", "values": [
                "repurchases of common stock", "repurchases of stock",
                "repurchase of capital stock", "common stock acquired", "common stock repurchased",
            ]},
        ],
    },
    "debt_issuance": {
        "statement": "cashflow",
        "searches": [
            {"type": "concept", "values": ["ProceedsFromIssuanceOfLongTermDebt", "ProceedsFromIssuanceOfDebt"]},
            {"type": "sc", "values": ["DebtProceeds"]},
            {"type": "keyword", "values": ["proceeds from issuance of", "issuance of debt", "additions to long-term debt"]},
        ],
    },
    "debt_repayment": {
        "statement": "cashflow",
        "searches": [
            {"type": "concept", "values": ["RepaymentsOfLongTermDebt", "RepaymentsOfDebt"]},
            {"type": "sc", "values": ["DebtRepayments"]},
            {"type": "keyword", "values": ["repayments of", "repayment of debt", "reductions in long-term debt"]},
        ],
    },
    "financing_cash_flow": {
        "statement": "cashflow",
        "is_subtotal": True,
        "searches": [
            {"type": "concept", "values": ["NetCashProvidedByUsedInFinancingActivities"]},
            {"type": "sc_subtotal", "values": ["NetCashFromFinancingActivities"]},
            {"type": "keyword", "values": ["net cash used in financing", "cash used in financing", "net cash from financing"]},
        ],
    },
    "net_change_in_cash": {
        "statement": "cashflow",
        "searches": [
            {"type": "concept", "values": [
                "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect",
                "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseExcludingExchangeRateEffect",
            ]},
            {"type": "sc", "values": ["NetChangeInCash"]},
            {"type": "keyword", "values": ["increase/(decrease) in cash", "net change in cash", "increase (decrease) in cash"]},
        ],
    },
    "free_cash_flow": {
        "statement": "cashflow",
        "searches": [
            {"type": "derived", "formula": "operating_cash_flow - abs(capital_expenditure)"},
        ],
    },
}
