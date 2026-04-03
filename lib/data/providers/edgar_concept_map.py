"""
EDGAR XBRL concept name mappings — researched across 55 companies,
all major US sectors.
Last updated: 2026-04-03.
Coverage: 51/55 companies at 8/8 fields, 4 with 7/8 (GM/F debt, GE cash, CMCSA shares).

Each field has a list of (taxonomy, concept_name) tuples to try.
The provider tries ALL concepts and MERGES results (companies change
concepts over time). Higher-priority concepts listed first and take
precedence for overlapping dates.

type="flow": Revenue, Net Income, etc. — summed for TTM.
  Dedup by period length (75-110 days for single quarter).
  Q4 derived from: annual (10-K) minus Q1+Q2+Q3.

type="stock": Debt, Cash, Equity, Shares — point-in-time.
  All 10-Q/10-K entries used, dedup by end date.
"""

FIELD_CONCEPTS: dict = {
    # ── Revenue ──────────────────────────────────────────────
    "revenue": {
        "type": "flow",
        "concepts": [
            # ASC 606, most common post-2018 (covers 35+ companies)
            ("us-gaap", "RevenueFromContractWithCustomerExcludingAssessedTax"),
            # Broad catch-all — pre-2018 for most, still active for BAC, T, XOM
            ("us-gaap", "Revenues"),
            # Pre-2014 standard (AAPL, MSFT, AMZN, WMT, PFE, GM)
            ("us-gaap", "SalesRevenueNet"),
            # Goods-specific (JNJ, AMZN, PFE pre-2018)
            ("us-gaap", "SalesRevenueGoodsNet"),
            # Tax-inclusive variant (NEE, BRK-B)
            ("us-gaap", "RevenueFromContractWithCustomerIncludingAssessedTax"),
            # Utilities (NEE, DUK, SO — 148Q+)
            ("us-gaap", "RegulatedAndUnregulatedOperatingRevenue"),
            # Banks — net interest income as revenue proxy (JPM, BAC, GS, WFC, C, MS)
            ("us-gaap", "InterestIncomeExpenseNet"),
            # Banks alt (BAC, GS)
            ("us-gaap", "InterestAndDividendIncomeOperating"),
        ],
    },
    # ── Net Income ───────────────────────────────────────────
    "net_income": {
        "type": "flow",
        "concepts": [
            # Universal — all 55 test companies
            ("us-gaap", "NetIncomeLoss"),
            # Good fallback, more entries for BRK-B, WMT, GM, XOM
            ("us-gaap", "ProfitLoss"),
            # Common shareholders only (GOOGL, JPM, BAC, GS, PFE, T, GM)
            ("us-gaap", "NetIncomeLossAvailableToCommonStockholdersBasic"),
        ],
    },
    # ── Operating Income ─────────────────────────────────────
    "operating_income": {
        "type": "flow",
        "concepts": [
            # Standard (most industrials, tech, consumer)
            ("us-gaap", "OperatingIncomeLoss"),
            # Pre-tax income — banks (JPM, BAC, GS, WFC, C, MS), BRK-B
            ("us-gaap", "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest"),
            # CVX, energy companies — includes equity method investments
            ("us-gaap", "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"),
        ],
    },
    # ── Depreciation & Amortization ──────────────────────────
    # D&A is typically on the CF statement, reported as YTD cumulative
    # in 10-Q filings: Q1(90d), H1(180d), 9M(270d), FY(365d).
    # "cumulative" flag tells provider to derive quarterly values
    # from cumulative periods (H1-Q1=Q2, 9M-H1=Q3, FY-9M=Q4).
    "da": {
        "type": "flow",
        "cumulative": True,
        "concepts": [
            # Most common CF concept (21/31: AMZN, XOM, T, GM, CAT, etc.)
            ("us-gaap", "DepreciationDepletionAndAmortization"),
            # Alt CF concept (10/31: UNH, GS, NVDA, WMT, NEE)
            ("us-gaap", "DepreciationAndAmortization"),
            # Apple, JPM, C, WFC specific (accretion included)
            ("us-gaap", "DepreciationAmortizationAndAccretionNet"),
            # PP&E depreciation only (ABBV, TSLA, META, F, GOOGL)
            ("us-gaap", "Depreciation"),
            # Intangible amortization only (BAC 100Q, PG 94Q, GS 93Q)
            ("us-gaap", "AmortizationOfIntangibleAssets"),
            # Utilities (DUK — 46Q)
            ("us-gaap", "CostDepreciationAmortizationAndDepletion"),
        ],
    },
    # ── Total Debt ───────────────────────────────────────────
    # Most complex field — no single concept fits all. Companies
    # with financial subsidiaries (GM, F, BRK-B) often lack standard
    # debt BS concepts entirely.
    "total_debt": {
        "type": "stock",
        "concepts": [
            # Includes current portion (MSFT, AMZN, BAC, etc.)
            ("us-gaap", "LongTermDebt"),
            # LT only — good EV proxy (MSFT, AMZN, JNJ, WMT, PFE, NEE)
            ("us-gaap", "LongTermDebtNoncurrent"),
            # Includes capital leases (GOOGL, XOM, T — 56-100Q)
            ("us-gaap", "LongTermDebtAndCapitalLeaseObligations"),
            # All debt + leases incl current (GM 15Q, F)
            ("us-gaap", "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities"),
            # Debt + capital leases combined (F — 72Q)
            ("us-gaap", "DebtAndCapitalLeaseObligations"),
            # Short-term component (JPM, BAC, GS, WMT)
            ("us-gaap", "ShortTermBorrowings"),
            # Current debt (XOM, PFE, T)
            ("us-gaap", "DebtCurrent"),
            # Commercial paper (AAPL, MSFT, GS, NEE)
            ("us-gaap", "CommercialPaper"),
        ],
    },
    # ── Cash & Equivalents ───────────────────────────────────
    "cash": {
        "type": "stock",
        "concepts": [
            # Universal — all 55 companies
            ("us-gaap", "CashAndCashEquivalentsAtCarryingValue"),
            # Includes restricted cash (good fallback)
            ("us-gaap", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"),
            # Broader: includes ST investments (MSFT, GOOGL)
            ("us-gaap", "CashCashEquivalentsAndShortTermInvestments"),
            # GE-specific: includes discontinued ops (68Q)
            ("us-gaap", "CashAndCashEquivalentsAtCarryingValueIncludingDiscontinuedOperations"),
        ],
    },
    # ── Stockholders' Equity ─────────────────────────────────
    "equity": {
        "type": "stock",
        "concepts": [
            # Most common (48/55 companies)
            ("us-gaap", "StockholdersEquity"),
            # Includes NCI (BRK-B, JNJ, XOM, WMT, PFE, T, GM, NEE)
            ("us-gaap", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"),
        ],
    },
    # ── Intangible Assets (for Tangible Book Value) ─────────
    # TBV = Equity − Intangibles. Used for P/TBV (financial cos).
    "intangibles": {
        "type": "stock",
        "concepts": [
            # Goodwill alone — all 6 test banks (118-324Q), ~95% of total
            ("us-gaap", "Goodwill"),
            # Full intangibles incl goodwill (GS 46Q)
            ("us-gaap", "IntangibleAssetsNetIncludingGoodwill"),
            # Intangibles excl goodwill (BAC, C, MS — supplement)
            ("us-gaap", "IntangibleAssetsNetExcludingGoodwill"),
        ],
    },
    # ── Shares Outstanding ───────────────────────────────────
    # Treated as stock type (use latest value for per-share calcs).
    "shares": {
        "type": "stock",
        "concepts": [
            # Diluted weighted avg — best for EPS (48/55)
            ("us-gaap", "WeightedAverageNumberOfDilutedSharesOutstanding"),
            # Basic weighted avg (fallback)
            ("us-gaap", "WeightedAverageNumberOfShareOutstandingBasicAndDiluted"),
            # BS shares outstanding (GOOGL, XOM)
            ("us-gaap", "CommonStockSharesOutstanding"),
            # Shares issued (XOM 192Q, covers some gaps)
            ("us-gaap", "CommonStockSharesIssued"),
            # dei taxonomy — different URL path (broad coverage)
            ("dei", "EntityCommonStockSharesOutstanding"),
        ],
    },
}
