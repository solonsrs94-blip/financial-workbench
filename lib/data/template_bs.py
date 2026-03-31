"""Search rules for balance sheet template lines."""

BS_SEARCH_RULES = {
    "cash": {
        "statement": "balance",
        "searches": [
            {"type": "concept", "values": ["CashAndCashEquivalentsAtCarryingValue", "Cash", "CashEquivalentsAtCarryingValue"]},
            {"type": "sc", "values": ["CashAndMarketableSecurities"]},
            {"type": "keyword", "values": ["cash and cash equivalents"]},
        ],
    },
    "short_term_investments": {
        "statement": "balance",
        "searches": [
            {"type": "concept", "values": ["ShortTermInvestments", "MarketableSecuritiesCurrent", "AvailableForSaleSecuritiesDebtSecuritiesCurrent"]},
            {"type": "sc", "values": ["ShortTermInvestments"]},
            {"type": "keyword", "values": ["short-term investments", "short term investments", "marketable securities"]},
        ],
    },
    "accounts_receivable": {
        "statement": "balance",
        "searches": [
            {"type": "concept", "values": ["AccountsReceivableNetCurrent", "AccountsReceivableNet", "ReceivablesNetCurrent"]},
            {"type": "sc", "values": ["TradeReceivables"]},
            {"type": "keyword", "values": ["accounts receivable", "trade receivables", "notes and accounts receivable"]},
        ],
    },
    "inventories": {
        "statement": "balance",
        "searches": [
            {"type": "concept", "values": ["InventoryNet", "InventoryFinishedGoodsAndWorkInProcess"]},
            {"type": "sc", "values": ["Inventories"]},
            {"type": "keyword", "values": ["inventories", "inventory"]},
        ],
    },
    "total_current_assets": {
        "statement": "balance",
        "searches": [
            {"type": "concept", "values": ["AssetsCurrent"]},
            {"type": "sc", "values": ["CurrentAssetsTotal"]},
            {"type": "keyword", "values": ["total current assets"]},
        ],
    },
    "pp_and_e": {
        "statement": "balance",
        "searches": [
            {"type": "concept", "values": [
                "PropertyPlantAndEquipmentNet",
                "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization",
            ]},
            {"type": "sc", "values": ["PlantPropertyEquipmentNet"]},
            {"type": "keyword", "values": ["property, plant and equipment", "property and equipment", "property, plant, and equipment"]},
        ],
    },
    "goodwill": {
        "statement": "balance",
        "searches": [
            {"type": "concept", "values": ["Goodwill"]},
            {"type": "sc", "values": ["Goodwill"]},
            {"type": "keyword", "values": ["goodwill"]},
        ],
    },
    "intangible_assets": {
        "statement": "balance",
        "searches": [
            {"type": "concept", "values": ["IntangibleAssetsNetExcludingGoodwill", "FiniteLivedIntangibleAssetsNet"]},
            {"type": "sc", "values": ["IntangibleAssets"]},
            {"type": "keyword", "values": ["intangible assets"]},
        ],
    },
    "total_assets": {
        "statement": "balance",
        "searches": [
            {"type": "concept", "values": ["Assets"]},
            {"type": "sc", "values": ["Assets"]},
            {"type": "keyword", "values": ["total assets"]},
        ],
    },
    "accounts_payable": {
        "statement": "balance",
        "searches": [
            {"type": "concept", "values": ["AccountsPayableCurrent", "AccountsPayableAndAccruedLiabilitiesCurrent"]},
            {"type": "sc", "values": ["TradePayables"]},
            {"type": "keyword", "values": ["accounts payable", "payables and accruals"]},
        ],
    },
    "deferred_revenue_current": {
        "statement": "balance",
        "searches": [
            {"type": "concept", "values": ["ContractWithCustomerLiabilityCurrent", "DeferredRevenueCurrent", "DeferredRevenueCurrentAndNoncurrent"]},
            {"type": "sc", "values": ["DeferredRevenueCurrent", "ContractWithCustomerLiabilityCurrent"]},
            {"type": "keyword", "values": ["deferred revenue", "unearned revenue", "contract liabilities"]},
        ],
    },
    "short_term_debt": {
        "statement": "balance",
        "searches": [
            {"type": "concept", "values": ["ShortTermBorrowings", "CommercialPaper", "ShortTermDebt"]},
            {"type": "sc", "values": ["ShortTermDebt"]},
            {"type": "keyword", "values": ["short-term debt", "commercial paper", "notes and loans payable", "short-term borrowings"]},
        ],
    },
    "current_portion_ltd": {
        "statement": "balance",
        "searches": [
            {"type": "concept", "values": ["LongTermDebtCurrent", "LongTermDebtAndCapitalLeaseObligationsCurrent"]},
            {"type": "sc", "values": ["CurrentPortionOfLongTermDebt"]},
            {"type": "keyword", "values": ["current portion of long-term debt", "current maturities"]},
        ],
    },
    "total_current_liabilities": {
        "statement": "balance",
        "searches": [
            {"type": "concept", "values": ["LiabilitiesCurrent"]},
            {"type": "sc", "values": ["CurrentLiabilitiesTotal"]},
            {"type": "keyword", "values": ["total current liabilities"]},
        ],
    },
    "long_term_debt": {
        "statement": "balance",
        "searches": [
            {"type": "concept", "values": ["LongTermDebtNoncurrent", "LongTermDebt", "LongTermDebtAndCapitalLeaseObligations"]},
            {"type": "sc", "values": ["LongTermDebt"]},
            {"type": "keyword", "values": ["long-term debt", "long term debt"]},
        ],
    },
    "total_liabilities": {
        "statement": "balance",
        "searches": [
            {"type": "concept", "values": ["Liabilities", "LiabilitiesTotal"]},
            {"type": "sc", "values": ["Liabilities"]},
            {"type": "keyword", "values": ["total liabilities"]},
            {"type": "derived", "formula": "total_assets - total_equity"},
        ],
    },
    "common_stock": {
        "statement": "balance",
        "searches": [
            {"type": "concept", "values": ["CommonStocksIncludingAdditionalPaidInCapital", "CommonStockValue"]},
            {"type": "sc", "values": ["CommonEquity"]},
            {"type": "keyword", "values": ["common stock and additional paid-in", "common stock and paid-in"]},
        ],
    },
    "retained_earnings": {
        "statement": "balance",
        "searches": [
            {"type": "concept", "values": ["RetainedEarningsAccumulatedDeficit"]},
            {"type": "sc", "values": ["RetainedEarnings"]},
            {"type": "keyword", "values": ["retained earnings", "accumulated deficit", "earnings reinvested"]},
        ],
    },
    "total_equity": {
        "statement": "balance",
        "searches": [
            {"type": "concept", "values": [
                "StockholdersEquity",
                "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
            ]},
            {"type": "sc", "values": ["AllEquityBalance", "AllEquityBalanceIncludingMinorityInterest"]},
            {"type": "keyword", "values": ["total stockholders' equity", "total shareholders' equity", "total equity"]},
        ],
    },
    "total_liabilities_and_equity": {
        "statement": "balance",
        "searches": [
            {"type": "concept", "values": ["LiabilitiesAndStockholdersEquity"]},
            {"type": "sc", "values": ["LiabilitiesAndEquity"]},
            {"type": "keyword", "values": [
                "total liabilities and stockholders", "total liabilities and shareholders",
                "total liabilities and equity",
            ]},
        ],
    },
    "shares_outstanding": {
        "statement": "balance",
        "searches": [
            {"type": "concept", "values": ["CommonStockSharesOutstanding", "CommonStockSharesIssued", "EntityCommonStockSharesOutstanding"]},
            {"type": "sc", "values": ["SharesYearEnd", "SharesIssued"]},
            {"type": "keyword", "values": ["common stock, shares outstanding", "common stock, shares issued", "ordinary shares number"]},
            {"type": "keyword_exclude", "values": ["preferred"]},
        ],
    },
    "total_debt": {
        "statement": "balance",
        "searches": [
            {"type": "derived", "formula": "(short_term_debt or 0) + (current_portion_ltd or 0) + (long_term_debt or 0)"},
        ],
    },
    "net_debt": {
        "statement": "balance",
        "searches": [
            {"type": "derived", "formula": "total_debt - (cash or 0) - (short_term_investments or 0)"},
        ],
    },
}
