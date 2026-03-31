"""Search rules for income statement template lines."""

IS_SEARCH_RULES = {
    "revenue": {
        "statement": "income",
        "searches": [
            {"type": "concept", "values": [
                "RevenueFromContractWithCustomerExcludingAssessedTax",
                "RevenueFromContractWithCustomerIncludingAssessedTax",
                "Revenues", "SalesRevenueNet", "SalesRevenueGoodsNet",
                "SalesRevenueServicesNet", "RegulatedAndUnregulatedOperatingRevenue",
                "ElectricUtilityRevenue", "RealEstateRevenueNet",
                "InterestAndDividendIncomeOperating", "RevenueFromContractWithCustomerBeforeAssessedTax",
                "HealthCareOrganizationRevenue",
            ]},
            {"type": "sc", "values": ["Revenue"]},
            {"type": "keyword", "values": [
                "total revenue", "net sales", "net revenue", "revenue",
                "sales to customers",
            ]},
        ],
    },
    "cogs": {
        "statement": "income",
        "searches": [
            {"type": "concept", "values": [
                "CostOfGoodsAndServicesSold", "CostOfRevenue", "CostOfGoodsSold",
                "CostOfServices", "CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization",
            ]},
            {"type": "sc", "values": ["CostOfGoodsAndServicesSold"]},
            {"type": "keyword", "values": [
                "cost of revenue", "cost of goods sold", "cost of goods and services",
                "cost of sales", "cost of products sold",
            ]},
        ],
    },
    "gross_profit": {
        "statement": "income",
        "searches": [
            {"type": "concept", "values": ["GrossProfit"]},
            {"type": "sc", "values": ["GrossProfit"]},
            {"type": "keyword", "values": ["gross profit", "gross margin"]},
            {"type": "derived", "formula": "revenue - abs(cogs)"},
        ],
    },
    "sga": {
        "statement": "income",
        "searches": [
            {"type": "concept", "values": [
                "SellingGeneralAndAdministrativeExpense",
                "SellingGeneralAndAdministrative",
            ]},
            {"type": "keyword", "values": [
                "selling, general and admin", "selling general and admin",
                "operating, selling, general", "selling, general &",
                "selling, marketing and admin",
            ]},
            {"type": "combination", "parts": [
                "selling_and_marketing", "general_and_administrative",
            ]},
        ],
    },
    "selling_and_marketing": {
        "statement": "income",
        "helper": True,
        "searches": [
            {"type": "concept", "values": [
                "SellingAndMarketingExpense", "SellingExpense",
                "MarketingAndAdvertisingExpense",
            ]},
            {"type": "keyword", "values": [
                "sales and marketing", "selling and marketing",
                "marketing expense",
            ]},
        ],
    },
    "general_and_administrative": {
        "statement": "income",
        "helper": True,
        "searches": [
            {"type": "concept", "values": ["GeneralAndAdministrativeExpense"]},
            {"type": "keyword", "values": ["general and admin"]},
        ],
    },
    "rd": {
        "statement": "income",
        "searches": [
            {"type": "concept", "values": [
                "ResearchAndDevelopmentExpense",
                "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost",
                "ResearchAndDevelopmentExpenseSoftwareExcludingAcquiredInProcessCost",
            ]},
            {"type": "sc", "values": ["ResearchAndDevelopementExpenses"]},
            {"type": "keyword", "values": ["research and development", "research & development"]},
        ],
    },
    "da_is": {
        "statement": "income",
        "searches": [
            {"type": "concept", "values": [
                "DepreciationDepletionAndAmortization", "DepreciationAndAmortization",
                "Depreciation", "DepreciationAmortizationAndAccretionNet",
            ]},
            {"type": "sc", "values": ["DepreciationExpense"]},
            {"type": "keyword", "values": [
                "depreciation and amortization", "depreciation, depletion",
                "depreciation and depletion",
            ]},
        ],
    },
    "total_opex": {
        "statement": "income",
        "searches": [
            {"type": "concept", "values": ["OperatingExpenses", "CostsAndExpenses"]},
            {"type": "sc", "values": ["TotalOperatingExpenses"]},
            {"type": "keyword", "values": ["total operating expenses", "operating expenses"]},
        ],
    },
    "ebit": {
        "statement": "income",
        "searches": [
            {"type": "concept", "values": ["OperatingIncomeLoss"]},
            {"type": "sc", "values": ["OperatingIncomeLoss"]},
            {"type": "keyword", "values": ["operating income", "income from operations", "operating profit"]},
            {"type": "derived", "formula": "pretax_income + abs(interest_expense)"},
            {"type": "derived", "formula": "gross_profit - abs(sga) - abs(rd)"},
        ],
    },
    "ebitda": {
        "statement": "income",
        "searches": [
            {"type": "derived", "formula": "ebit + abs(depreciation_amortization)"},
        ],
    },
    "interest_expense": {
        "statement": "income",
        "searches": [
            {"type": "concept", "values": [
                "InterestExpense", "InterestExpenseDebt",
                "InterestIncomeExpenseNonoperatingNet", "InterestIncomeExpenseNet",
            ]},
            {"type": "sc", "values": ["InterestExpense"]},
            {"type": "keyword", "values": ["interest expense"]},
        ],
    },
    "other_non_operating": {
        "statement": "income",
        "searches": [
            {"type": "concept", "values": ["NonoperatingIncomeExpense", "OtherNonoperatingIncomeExpense"]},
            {"type": "sc", "values": ["NonoperatingIncomeExpense"]},
            {"type": "keyword", "values": [
                "other income/(expense)", "other income (expense)",
                "other non-operating", "other income expense",
            ]},
        ],
    },
    "pretax_income": {
        "statement": "income",
        "searches": [
            {"type": "concept", "values": [
                "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
                "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
                "IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic",
            ]},
            {"type": "sc", "values": ["PretaxIncomeLoss"]},
            {"type": "keyword", "values": [
                "income before income tax", "income before provision",
                "income (loss) before income tax", "pretax income", "earnings before income tax",
            ]},
        ],
    },
    "tax_provision": {
        "statement": "income",
        "searches": [
            {"type": "concept", "values": ["IncomeTaxExpenseBenefit", "IncomeTaxExpenseBenefitContinuingOperations"]},
            {"type": "sc", "values": ["IncomeTaxes"]},
            {"type": "keyword", "values": [
                "provision for income tax", "income tax expense",
                "income tax (expense)", "provision for income",
            ]},
        ],
    },
    "net_income": {
        "statement": "income",
        "searches": [
            {"type": "concept", "values": ["NetIncomeLoss", "NetIncomeLossAvailableToCommonStockholdersBasic"]},
            {"type": "sc", "values": ["NetIncome", "NetIncomeToCommonShareholders"]},
            {"type": "keyword", "values": ["net income attributable to", "net income", "net earnings"]},
            {"type": "derived", "formula": "pretax_income - abs(tax_provision)"},
        ],
    },
    "diluted_eps": {
        "statement": "income",
        "searches": [
            {"type": "concept", "values": ["EarningsPerShareDiluted"]},
            {"type": "sc", "values": ["EarningsPerShareDiluted"]},
            {"type": "keyword", "values": [
                "diluted earnings per share", "diluted net income per share",
                "earnings per share, diluted", "diluted eps",
            ]},
            {"type": "value_filter", "max_abs": 1000, "label_contains": ["diluted", "per share"], "label_excludes": ["share"]},
        ],
    },
    "basic_eps": {
        "statement": "income",
        "searches": [
            {"type": "concept", "values": ["EarningsPerShareBasic"]},
            {"type": "sc", "values": ["EarningsPerShareBasic"]},
            {"type": "keyword", "values": [
                "basic earnings per share", "basic net income per share",
                "earnings per share, basic", "basic eps",
            ]},
        ],
    },
    "diluted_shares": {
        "statement": "income",
        "searches": [
            {"type": "concept", "values": [
                "WeightedAverageNumberOfDilutedSharesOutstanding",
                "WeightedAverageNumberDilutedSharesOutstandingAdjustment",
            ]},
            {"type": "sc", "values": ["SharesFullyDilutedAverage"]},
            {"type": "keyword", "values": ["diluted (in shares)", "diluted shares"]},
            {"type": "derived", "formula": "net_income / diluted_eps if diluted_eps and abs(diluted_eps) > 0.01 else None"},
        ],
    },
    "basic_shares": {
        "statement": "income",
        "searches": [
            {"type": "concept", "values": ["WeightedAverageNumberOfSharesOutstandingBasic"]},
            {"type": "sc", "values": ["SharesAverage"]},
            {"type": "keyword", "values": ["basic (in shares)", "basic shares"]},
        ],
    },
}
