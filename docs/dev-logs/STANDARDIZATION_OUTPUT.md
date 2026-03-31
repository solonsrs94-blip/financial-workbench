# Standardization Output — AAPL

**Date:** 2026-03-26
**Source:** EDGAR (SEC XBRL filings)
**Years:** 2014–2025 (12 years)

---

## 1. Raw Output Structure

`get_standardized_history("AAPL")` returns a `dict` with 9 keys:

| Key | Type | Size | Description |
|-----|------|------|-------------|
| `income` | dict | 12 years | Flattened IS: `{year: {key: value}}` |
| `balance` | dict | 11 years | Flattened BS: `{year: {key: value}}` (no 2014 BS from EDGAR) |
| `cashflow` | dict | 12 years | Flattened CF: `{year: {key: value}}` |
| `income_audit` | dict | 12 years | IS with audit: `{year: {key: {value, raw_label, layer}}}` |
| `balance_audit` | dict | 11 years | BS with audit |
| `cashflow_audit` | dict | 12 years | CF with audit |
| `cross_checks` | list | 23 items | Validation results |
| `years` | list | 12 items | `["2014", "2015", ..., "2025"]` |
| `source` | str | — | `"edgar"` |

**Note:** Balance sheet has 11 years (2015-2025) vs. 12 for IS/CF. 2014 BS data is missing from EDGAR filings.

---

## 2. Income Statement — All Years

All values in $millions. 14 standardized fields per year.

| Line Item (raw label) | 2025 | 2024 | 2023 | 2022 | 2021 | 2020 | 2019 | 2018 | 2017 | 2016 | 2015 | 2014 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **revenue** (Net sales) | 416,161 | 391,035 | 383,285 | 394,328 | 365,817 | 274,515 | 260,174 | 265,595 | 229,234 | 215,639 | 233,715 | 182,795 |
| **cogs** (Cost of sales) | 220,960 | 210,352 | 214,137 | 223,546 | 212,981 | 169,559 | 161,782 | 163,756 | 141,048 | 131,376 | 140,089 | 112,258 |
| **gross_profit** (Gross margin) | 195,201 | 180,683 | 169,148 | 170,782 | 152,836 | 104,956 | 98,392 | 101,839 | 88,186 | 84,263 | 93,626 | 70,537 |
| **rd** (Research and development) | 34,550 | 31,370 | 29,915 | 26,251 | 21,914 | 18,752 | 16,217 | 14,236 | 11,581 | 10,045 | 8,067 | 6,041 |
| **sga** (Selling, general and admin) | 27,601 | 26,097 | 24,932 | 25,094 | 21,973 | 19,916 | 18,245 | 16,705 | 15,261 | 14,194 | 14,329 | 11,993 |
| **total_opex** (Total operating expenses) | 62,151 | 57,467 | 54,847 | 51,345 | 43,887 | 38,668 | 34,462 | 30,941 | 26,842 | 24,239 | 22,396 | 18,034 |
| **ebit** (Operating income) | 133,050 | 123,216 | 114,301 | 119,437 | 108,949 | 66,288 | 63,930 | 70,898 | 61,344 | 60,024 | 71,230 | 52,503 |
| **other_non_operating** (Other income/(expense), net) | -321 | 269 | -565 | -334 | 258 | 803 | 1,807 | 2,005 | 2,745 | 1,348 | 1,285 | 980 |
| **pretax_income** (Income before provision for income taxes) | 132,729 | 123,485 | 113,736 | 119,103 | 109,207 | 67,091 | 65,737 | 72,903 | 64,089 | 61,372 | 72,515 | 53,483 |
| **tax_provision** (Provision for income taxes) | 20,719 | 29,749 | 16,741 | 19,300 | 14,527 | 9,680 | 10,481 | 13,372 | 15,738 | 15,685 | 19,121 | 13,973 |
| **net_income** (Net income) | 112,010 | 93,736 | 96,995 | 99,803 | 94,680 | 57,411 | 55,256 | 59,531 | 48,351 | 45,687 | 53,394 | 39,510 |
| **basic_shares** (Basic, in shares) | 14,949M | 15,344M | 15,744M | 16,216M | 16,701M | 17,352M | 18,471M | 19,822M | 5,217M | 5,471M | 5,753M | 6,086M |
| **diluted_shares** (Diluted, in shares) | 15,005M | 15,408M | 15,813M | 16,326M | 16,865M | 17,528M | 18,596M | 20,000M | 5,252M | 5,500M | 5,793M | 6,123M |
| **other_is_item** ⚠ (Diluted EPS) | 7.46 | 6.08 | 6.13 | 6.11 | 5.61 | 3.28 | 2.97 | 2.98 | 9.21 | 8.31 | 9.22 | 6.45 |

**Layer breakdown (2025):** 13 fields Layer 1 (XBRL), 1 field Layer 4 (other_is_item = Diluted EPS).

---

## 3. Balance Sheet — All Years

All values in $millions. 28 standardized fields. Years 2015-2025 (11 years).

| Line Item (raw label) | 2025 | 2024 | 2023 | 2022 | 2021 | 2020 | 2019 | 2018 | 2017 | 2016 | 2015 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **cash** (Cash and cash equivalents) | 35,934 | 29,943 | 29,965 | 23,646 | 34,940 | 38,016 | 48,844 | 25,913 | 20,289 | 20,484 | 21,120 |
| **short_term_investments** (Marketable securities) | 18,763 | 35,228 | 31,590 | 24,658 | 27,699 | 52,927 | 51,713 | 40,388 | 53,892 | — | — |
| **accounts_receivable** (Accounts receivable, net) | 39,777 | 33,410 | 29,508 | 28,184 | 26,278 | 16,120 | 22,926 | 23,186 | 17,874 | — | — |
| **inventories** (Inventories) | 5,718 | 7,286 | 6,331 | 4,946 | 6,580 | 4,061 | 4,106 | 3,956 | 4,855 | 2,132 | 2,349 |
| **other_current_assets** (Other current assets) | 14,585 | 14,287 | 14,695 | 21,223 | 14,111 | 11,264 | 12,352 | 12,087 | 13,936 | 8,283 | 15,085 |
| **total_current_assets** (Total current assets) | 147,957 | 152,987 | 143,566 | 135,405 | 134,836 | 143,713 | 162,819 | 131,339 | 128,645 | 106,869 | 89,378 |
| **pp_and_e** (Property, plant and equipment, net) | 49,834 | 45,680 | 43,715 | 42,117 | 39,440 | 36,766 | 37,378 | 41,304 | 33,783 | 27,010 | 22,471 |
| **other_non_current_assets** (Other non-current assets) | 83,727 | 74,834 | 64,758 | 54,428 | 48,849 | 42,522 | 32,978 | 22,283 | 18,177 | 8,757 | 5,422 |
| **total_non_current_assets** (Total non-current assets) | 211,284 | 211,993 | 209,017 | 217,350 | 216,166 | 180,175 | 175,697 | 234,386 | 246,674 | — | — |
| **total_assets** (Total assets) | 359,241 | 364,980 | 352,583 | 352,755 | 351,002 | 323,888 | 338,516 | 365,725 | 375,319 | 321,686 | 290,345 |
| **accounts_payable** (Accounts payable) | 69,860 | 68,960 | 62,611 | 64,115 | 54,763 | 42,296 | 46,236 | 55,888 | 44,242 | 37,294 | 35,490 |
| **accrued_expenses** (Deferred revenue) | 9,055 | 8,249 | 8,061 | 7,912 | 7,612 | 6,643 | 5,522 | 5,966 | 7,548 | 8,080 | 8,940 |
| **short_term_debt** (Commercial paper) | 7,979 | 9,967 | 5,985 | 9,982 | 6,000 | 4,996 | 5,980 | 11,964 | 11,977 | 8,105 | 8,499 |
| **current_portion_ltd** (Term debt) | 12,350 | 10,912 | 9,822 | 11,128 | 9,613 | 8,773 | 10,260 | 8,784 | 6,496 | — | — |
| **other_current_liabilities** (Other current liabilities) | 66,387 | 78,304 | 58,829 | 60,845 | 47,493 | 42,684 | 37,720 | 33,327 | 30,551 | — | — |
| **total_current_liabilities** (Total current liabilities) | 165,631 | 176,392 | 145,308 | 153,982 | 125,481 | 105,392 | 105,718 | 115,929 | 100,814 | 79,006 | 80,610 |
| **long_term_debt** (Term debt) | 78,328 | 85,750 | 95,281 | 98,959 | 109,106 | 98,667 | 91,807 | 93,735 | 97,207 | — | — |
| **other_nc_liabilities** (Other non-current liabilities) | 41,549 | 45,888 | 49,848 | 49,142 | 53,325 | 54,490 | 50,503 | 48,914 | 40,415 | 36,074 | 33,427 |
| **total_non_current_liabilities** (Total non-current liab.) | 119,877 | 131,638 | 145,129 | 148,101 | 162,431 | 153,157 | 142,310 | 142,649 | 140,458 | — | — |
| **total_liabilities** (Total liabilities) | 285,508 | 308,030 | 290,437 | 302,083 | 287,912 | 258,549 | 248,028 | 258,578 | 241,272 | 193,437 | 170,990 |
| **common_stock** (Common stock + APIC) | 93,568 | 83,276 | — | — | — | — | — | — | — | — | — |
| **retained_earnings** (Accumulated deficit) | -14,264 | -19,154 | -214 | -3,068 | — | — | — | — | — | — | — |
| **accumulated_oci** (Accumulated other comprehensive loss) | -5,571 | -7,172 | -11,452 | -11,109 | — | — | — | — | — | — | — |
| **total_equity** (Total shareholders' equity) | 73,733 | 56,950 | 62,146 | 50,672 | 63,090 | 65,339 | 90,488 | 107,147 | 134,047 | 128,249 | 119,355 |
| **total_liabilities_and_equity** (Total L + SE) | 359,241 | 364,980 | 352,583 | 352,755 | 351,002 | 323,888 | 338,516 | 365,725 | 375,319 | 321,686 | 290,345 |
| **shares_outstanding** (Common stock, shares outstanding) | 14,773M | 15,117M | 15,550M | 15,943M | — | — | — | — | — | — | — |
| **shares_issued** (Common stock, shares issued) | 14,773M | 15,117M | 15,550M | 15,943M | — | — | — | — | — | — | — |
| **net_debt** 🔵 (Derived: Total Debt - Cash) | 50,373 | 65,774 | 71,301 | 85,295 | 80,166 | 65,647 | 48,943 | 79,786 | 88,895 | -12,379 | -12,621 |

**Layer breakdown (2025):** All 26 mapped fields are Layer 1 (XBRL). 1 field Layer 0 (net_debt = derived). Zero Layer 4 items.

---

## 4. Cash Flow Statement — All Years

All values in $millions. 21 standardized fields per year.

| Line Item (raw label) | 2025 | 2024 | 2023 | 2022 | 2021 | 2020 | 2019 | 2018 | 2017 | 2016 | 2015 | 2014 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **net_income_cf** (Net income) | 112,010 | 93,736 | 96,995 | 99,803 | 94,680 | 57,411 | 55,256 | 59,531 | 48,351 | 45,687 | 53,394 | 39,510 |
| **depreciation_amortization** (D&A) | 11,698 | 11,445 | 11,519 | 11,104 | 11,284 | 11,056 | 12,547 | 10,903 | 10,157 | 10,505 | 11,257 | 7,946 |
| **stock_based_compensation** (SBC) | 12,863 | 11,688 | 10,833 | 9,038 | 7,906 | 6,829 | 6,068 | 5,340 | 4,840 | 4,210 | 3,586 | 2,863 |
| **deferred_income_tax** (Cash paid for income taxes) | 43,369 | 26,102 | 18,679 | 19,573 | 25,385 | 9,501 | 15,263 | 10,417 | 11,591 | 10,444 | 13,252 | 10,026 |
| **other_non_cash** (Other) | -89 | -2,266 | -2,227 | 1,006 | -4,921 | -97 | -652 | -444 | -166 | 486 | 385 | 26 |
| **other_operating_cf** ⚠ (Accounts payable) | 902 | 6,020 | -1,889 | 9,448 | 12,326 | -4,062 | -1,923 | 9,175 | 8,966 | 2,117 | 5,001 | 5,938 |
| **change_in_other_wc** (Other current and non-current liab.) | -11,076 | 15,552 | 3,031 | 6,110 | 7,475 | 8,916 | -4,700 | 38,449 | 1,092 | -1,906 | 9,058 | 6,010 |
| **operating_cash_flow** (Cash from operating activities) | 111,482 | 118,254 | 110,543 | 122,151 | 104,038 | 80,674 | 69,391 | 77,434 | 64,225 | 66,231 | 81,266 | 59,713 |
| **capital_expenditure** (Payments for PP&E) | -12,715 | -9,447 | -10,959 | -10,708 | -11,085 | -7,309 | -10,495 | -13,313 | -12,451 | -12,734 | -11,247 | -9,571 |
| **investment_proceeds** (Proceeds from sales of securities) | 12,890 | 11,135 | 5,828 | 37,446 | 47,460 | 50,473 | 56,988 | 47,838 | 94,564 | 90,536 | 107,447 | 189,301 |
| **other_investing_cf** ⚠ (Commercial paper / Purchases) | -2,032 | 3,960 | -3,978 | 3,955 | 1,022 | -963 | -5,977 | -71,356 | 3,852 | -142,428 | -166,402 | -217,128 |
| **investing_cash_flow** (Cash from investing activities) | 15,195 | 2,935 | 3,705 | -2,086 | -385 | -909 | -1,078 | -745 | -124 | -924 | -26 | 26 |
| **debt_issuance** (Proceeds from issuance of term debt) | 4,481 | 0 | 5,228 | 5,465 | 20,393 | 16,091 | 6,963 | 6,969 | 28,662 | 24,954 | 27,114 | 11,960 |
| **debt_repayment** (Repayments of term debt) | -10,932 | -9,958 | -11,151 | -9,543 | -8,750 | -12,629 | -8,805 | -6,500 | -3,500 | -2,500 | 0 | 0 |
| **buybacks_and_issuance** (Repurchases of common stock) | -90,711 | -94,949 | -77,550 | -89,402 | -85,971 | -72,358 | -66,897 | -72,738 | -32,900 | -29,722 | -35,253 | -45,000 |
| **minority_distributions** (Payments for dividends) | -15,421 | -15,234 | -15,025 | -14,841 | -14,467 | -14,081 | -14,119 | -13,712 | 12,769 | 12,150 | 11,561 | -11,126 |
| **other_cf_item** ⚠ (Tax on net share settlement) | -5,960 | -5,441 | -5,431 | -6,223 | -6,556 | -3,634 | -2,817 | -2,527 | -1,874 | -1,570 | -1,499 | -1,158 |
| **financing_cash_flow** (Cash used in financing) | -120,686 | -121,983 | -108,488 | -110,749 | -93,353 | -86,820 | -90,976 | -87,876 | -17,974 | -20,890 | -17,716 | -37,549 |
| **net_change_in_cash** (Increase/(Decrease) in cash) | 5,991 | -794 | 5,760 | -10,952 | — | — | — | — | — | — | — | — |
| **ending_cash** (Cash, ending balances) | 35,934 | 29,943 | 30,737 | 24,977 | — | — | — | — | — | — | — | — |
| **free_cash_flow** 🔵 (Derived: OCF - CapEx) | 98,767 | 108,807 | 99,584 | 111,443 | 92,953 | 73,365 | 58,896 | 64,121 | 51,774 | 53,497 | 70,019 | 50,142 |

**Layer breakdown (2025):** 17 fields Layer 1. 3 fields Layer 4 (other_operating_cf, other_cf_item, other_investing_cf). 1 field Layer 0 (free_cash_flow = derived).

---

## 5. Audit Trail — 5 Sample Line Items

### 5a. Revenue

| Field | Value |
|-------|-------|
| **Line item** | `revenue` |
| **Value (2025)** | 416,161,000,000 |
| **Raw label** | "Net sales" |
| **Source** | EDGAR |
| **Layer** | 1 (XBRL Concept) |
| **XBRL concept** | `Revenue` → `"revenue"` |

### 5b. Net Income

| Field | Value |
|-------|-------|
| **Line item** | `net_income` |
| **Value (2025)** | 112,010,000,000 |
| **Raw label** | "Net income" |
| **Source** | EDGAR |
| **Layer** | 1 (XBRL Concept) |
| **XBRL concept** | `NetIncome` → `"net_income"` |

### 5c. Free Cash Flow

| Field | Value |
|-------|-------|
| **Line item** | `free_cash_flow` |
| **Value (2025)** | 98,767,000,000 |
| **Raw label** | "Derived: OCF - CapEx" |
| **Source** | Computed |
| **Layer** | 0 (Derived) |
| **Formula** | `operating_cash_flow` (111,482M) - `capital_expenditure` (12,715M) = 98,767M |

### 5d. Net Debt

| Field | Value |
|-------|-------|
| **Line item** | `net_debt` |
| **Value (2025)** | 50,373,000,000 |
| **Raw label** | "Derived: Total Debt - Cash" |
| **Source** | Computed |
| **Layer** | 0 (Derived) |
| **Formula** | (`short_term_debt` 7,979 + `current_portion_ltd` 12,350 + `long_term_debt` 78,328) - `cash` 35,934 = 62,723M ⚠ **MISMATCH** (reported 50,373 vs expected 62,723) |

> **NOTE:** The net_debt derivation may use a different formula or the total_debt intermediate may differ. Needs investigation.

### 5e. Accrued Expenses

| Field | Value |
|-------|-------|
| **Line item** | `accrued_expenses` |
| **Value (2025)** | 9,055,000,000 |
| **Raw label** | "Deferred revenue" |
| **Source** | EDGAR |
| **Layer** | 1 (XBRL Concept) |
| **XBRL concept** | `OtherOperatingCurrentLiabilities` → `"accrued_expenses"` |

> **NOTE:** This is mapped **incorrectly**. The raw label is "Deferred revenue" but it's mapped to `accrued_expenses`. The XBRL concept `OtherOperatingCurrentLiabilities` is a catch-all that Apple uses for deferred revenue, but our concept map assigns it to `accrued_expenses`.

---

## 6. What's Missing / What's Wrong

### 6a. Missing Line Items a Professional Would Want

**Income Statement:**
| Missing Field | Why It Matters |
|---------------|----------------|
| `interest_expense` | Needed for WACC (cost of debt), interest coverage ratio. Apple has ~$3B/yr. Not mapped from IS. |
| `interest_income` | Apple earns ~$4B/yr on cash pile. Lost in `other_non_operating`. |
| `ebitda` | Not computed as derived field (should be EBIT + D&A). |
| `dividends_per_share` | Mapped in concept map but not appearing in output. |
| `earnings_per_share` | Diluted EPS falls into `other_is_item` (Layer 4) instead of having a proper key. |
| `da` (IS-level D&A) | Only appears on cash flow statement. IS doesn't break out D&A separately from COGS/OpEx. |
| `income_continuing_ops` | Defined in concept map but not present in AAPL output. |

**Balance Sheet:**
| Missing Field | Why It Matters |
|---------------|----------------|
| `goodwill` | Apple has no goodwill, so correctly absent. |
| `intangible_assets` | Apple has no material intangibles, correctly absent. |
| `operating_lease_assets` | IFRS 16/ASC 842 ROU assets. Apple has ~$11B. Buried in `other_non_current_assets`. |
| `operating_lease_current` | Current lease liabilities. Buried in `other_current_liabilities`. |
| `operating_lease_nc` | Non-current lease liabilities. Buried in `other_nc_liabilities`. |
| `deferred_tax_assets` | Not broken out. |
| `deferred_tax_liabilities` | Not broken out. Buried in `other_nc_liabilities`. |
| `additional_paid_in_capital` | Only combined with `common_stock` in recent years. |
| `treasury_stock` | Apple doesn't report treasury stock as separate line (it reduces equity directly). |
| `total_debt` | Not a standardized field — must be reconstructed from short_term_debt + current_portion_ltd + long_term_debt. |
| `long_term_investments` | Apple's $100B+ in long-term marketable securities. Missing for some years, likely in `other_non_current_assets`. |

**Cash Flow:**
| Missing Field | Why It Matters |
|---------------|----------------|
| `change_in_receivables` | Lumped into `other_operating_cf` or `change_in_other_wc`. |
| `change_in_payables` | Actually mapped to `other_operating_cf` (Layer 4) instead of its proper key. |
| `change_in_deferred_revenue` | Not broken out. |
| `acquisitions` | Apple has acquisitions but they may be immaterial or lumped. |
| `dividends_paid` | Falls into `minority_distributions` key (wrong name for Apple — they're dividends, not minority distributions). |
| `investment_purchases` | Purchases of marketable securities — falls into `other_investing_cf` (Layer 4). Huge amounts ($217B in 2014). |

### 6b. Incorrectly Mapped Items

| Standardized Key | Raw Label | Problem |
|------------------|-----------|---------|
| `accrued_expenses` | "Deferred revenue" | **Wrong mapping.** Deferred revenue is NOT accrued expenses. Should be `deferred_revenue_current`. |
| `other_operating_cf` | "Accounts payable" | **Wrong bucket.** Change in AP should map to `change_in_payables`, not `other_operating_cf`. |
| `other_investing_cf` | "Purchases of marketable securities" / "Commercial paper, net" | **Wrong bucket.** Investment purchases should map to `investment_purchases`, not `other_investing_cf`. |
| `other_cf_item` | "Payments for taxes related to net share settlement" | **Wrong bucket.** This is a financing activity (equity-related), but it's a generic catch-all. Should be `tax_on_share_settlement` or similar. |
| `minority_distributions` | "Payments for dividends and dividend equivalents" | **Wrong name.** Apple doesn't have minority interests. This is `dividends_paid`. |
| `deferred_income_tax` | "Cash paid for income taxes, net" | **Wrong mapping.** Cash paid for taxes is NOT deferred income tax. It's a supplemental disclosure. Should be `cash_taxes_paid` or similar. |
| `other_is_item` | "Diluted (in dollars per share)" | **Should be `diluted_eps`.** Has dedicated concept but falls to Layer 4. |

### 6c. Layer 4 Items — Full List

All items that fell through to the "other" catch-all:

| Statement | Key | Raw Label | Years | Severity |
|-----------|-----|-----------|-------|----------|
| Income | `other_is_item` | "Diluted (in dollars per share)" | All 12 | **High** — This is Diluted EPS, not "other." Needs `EarningsPerShareDiluted` concept in IS_CONCEPT_MAP. |
| Cash Flow | `other_operating_cf` | "Accounts payable" | All 12 | **High** — Change in AP should be `change_in_payables`. Missing XBRL concept mapping. |
| Cash Flow | `other_cf_item` | "Payments for taxes related to net share settlement" | All 12 | **Medium** — Needs dedicated key. |
| Cash Flow | `other_investing_cf` | "Purchases of marketable securities" / "Commercial paper, net" | All 12 | **High** — Investment purchases are a major CF item for Apple ($217B in 2014). |

---

## 7. Derived Fields — Verification

### gross_profit = revenue - cogs

| Year | Revenue | COGS | Expected GP | Actual GP | Status |
|------|---------|------|-------------|-----------|--------|
| 2025 | 416,161 | 220,960 | 195,201 | 195,201 | ✅ Match |
| 2024 | 391,035 | 210,352 | 180,683 | 180,683 | ✅ Match |
| 2023 | 383,285 | 214,137 | 169,148 | 169,148 | ✅ Match |

**Note:** Gross profit is NOT derived (Layer 0) for AAPL — it comes directly from EDGAR as "Gross margin" (Layer 1). The cross-check still validates it.

### ebitda = ebit + da

EBITDA is **NOT computed** by the standardizer. The `ebitda` key does not appear in AAPL output.

Manual check:
| Year | EBIT | D&A (from CF) | Expected EBITDA |
|------|------|---------------|-----------------|
| 2025 | 133,050 | 11,698 | 144,748 |
| 2024 | 123,216 | 11,445 | 134,661 |
| 2023 | 114,301 | 11,519 | 125,820 |

**Status: ⚠ EBITDA should be added as a derived field.**

### free_cash_flow = ocf - capex

| Year | OCF | CapEx | Expected FCF | Actual FCF | Status |
|------|-----|-------|--------------|------------|--------|
| 2025 | 111,482 | -12,715 | 98,767 | 98,767 | ✅ Match |
| 2024 | 118,254 | -9,447 | 108,807 | 108,807 | ✅ Match |
| 2023 | 110,543 | -10,959 | 99,584 | 99,584 | ✅ Match |
| 2022 | 122,151 | -10,708 | 111,443 | 111,443 | ✅ Match |

### net_debt = total_debt - cash

| Year | ST Debt | Current LTD | LT Debt | = Total Debt | Cash | Expected Net Debt | Actual Net Debt | Status |
|------|---------|-------------|---------|--------------|------|-------------------|-----------------|--------|
| 2025 | 7,979 | 12,350 | 78,328 | 98,657 | 35,934 | 62,723 | 50,373 | ⚠ **Off by $12.4B** |
| 2024 | 9,967 | 10,912 | 85,750 | 106,629 | 29,943 | 76,686 | 65,774 | ⚠ **Off by $10.9B** |
| 2023 | 5,985 | 9,822 | 95,281 | 111,088 | 29,965 | 81,123 | 71,301 | ⚠ **Off by $9.8B** |

**Status: ⚠ MISMATCH.** The derived `net_debt` is consistently lower than expected. The most likely explanation: the derivation subtracts **cash + short_term_investments** (i.e., uses total cash & equivalents including marketable securities). Checking: 2025: 98,657 - (35,934 + 18,763) = 43,960... still doesn't match. The formula needs investigation — it may use a different definition of "total debt" (excluding commercial paper or current portion).

---

## 8. Cross-Check Results

**23 cross-checks run, 23 passed:**

| Check | Years Tested | Result |
|-------|-------------|--------|
| Revenue - COGS = Gross Profit | 2014-2025 (12 years) | ✅ All pass (diff = 0) |
| Assets = Liabilities + Equity | 2015-2025 (11 years) | ✅ All pass (diff = 0) |

**Missing cross-checks that should be added:**
- OCF components sum to OCF total
- Investing components sum to Investing CF total
- Financing components sum to Financing CF total
- Net change in cash = OCF + ICF + FCF + FX
- Beginning cash + net change = ending cash

---

## 9. Summary Statistics

| Metric | Income | Balance | Cash Flow |
|--------|--------|---------|-----------|
| Total unique keys | 14 | 28 | 21 |
| Layer 1 (XBRL) | 13 | 26-27 | 17 |
| Layer 2 (Keyword) | 0 | 0 | 0 |
| Layer 3 (Hierarchy) | 0 | 0 | 0 |
| Layer 4 (Other) | 1 | 0 | 3 |
| Layer 0 (Derived) | 0 | 1 | 1 |
| **Mapping accuracy** | **93%** | **100%** | **81%** |

**Overall: 63 fields mapped, 59 via XBRL (Layer 1), 2 derived (Layer 0), 4 in Layer 4 catch-all.**

The 4 Layer 4 items are all fixable — they're well-known line items that just need concept mappings added.
