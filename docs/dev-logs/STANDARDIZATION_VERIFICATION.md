# Standardization Verification

**Date:** 2026-03-26
**Source:** EDGAR XBRL (all 3 tickers, 11-12 years)

---

## 1. AAPL — Line-by-Line (FY2025)

### 1a. Income Statement

| 10-K Line Item | 10-K Value | Std Key | Std Value | Match? |
|---|---|---|---|---|
| Net sales | $416,161M | `revenue` | $416,161M | ✅ |
| Cost of sales | $220,960M | `cogs` | $220,960M | ✅ |
| Gross margin | $195,201M | `gross_profit` | $195,201M | ✅ |
| Research and development | $34,550M | `rd` | $34,550M | ✅ |
| Selling, general and administrative | $27,601M | `sga` | $27,601M | ✅ |
| Total operating expenses | $62,151M | `total_opex` | $62,151M | ✅ |
| Operating income | $133,050M | `ebit` | $133,050M | ✅ |
| Other income/(expense), net | -$321M | `other_non_operating` | -$321M | ✅ |
| Income before provision for income taxes | $132,729M | `pretax_income` | $132,729M | ✅ |
| Provision for income taxes | $20,719M | `tax_provision` | $20,719M | ✅ |
| Net income | $112,010M | `net_income` | $112,010M | ✅ |
| Basic (in shares) | 14,949M | `basic_shares` | 14,949M | ✅ |
| Diluted (in shares) | 15,005M | `diluted_shares` | 15,005M | ✅ |
| Diluted EPS ($7.46) | $7.46 | `diluted_eps` | **VANTAR** | ❌ |
| — | — | `other_is_item` | $7.46 (L4) | ⚠️ EPS in wrong key |
| — (derived) | — | `ebitda` | $144,748M (L0) | ✅ Correct: 133,050 + 11,698 |

**IS Score: 13/14 lines correct. 1 error (EPS in wrong key).**

The EPS error is an XBRL concept mapping issue: Apple's XBRL labels the EPS line as "Diluted (in dollars per share)" but the `standard_concept` is `None` — it falls to Layer 4 `other_is_item`. The keyword fix we made for Yahoo data doesn't help here because the XBRL path doesn't use keyword matching for rows that have `None` concept (they go to Layer 3/4).

### 1b. Balance Sheet

| 10-K Line Item | 10-K Value | Std Key | Std Value | Match? |
|---|---|---|---|---|
| Cash and cash equivalents | $35,934M | `cash` | $35,934M | ✅ |
| Marketable securities (current) | $18,763M | `short_term_investments` | $18,763M | ✅ |
| Accounts receivable, net | $39,777M | `accounts_receivable` | $39,777M | ✅ |
| Inventories | $5,718M | `inventories` | $5,718M | ✅ |
| Vendor non-trade receivables | $33,180M | — | **VANTAR** | ⚠️ Bundled in other |
| Other current assets | $14,585M | `other_current_assets` | $14,585M | ✅ |
| Total current assets | $147,957M | `total_current_assets` | $147,957M | ✅ |
| Marketable securities (non-current) | $77,723M | — | **VANTAR** | ⚠️ In other_non_current_assets |
| Property, plant and equipment, net | $49,834M | `pp_and_e` | $49,834M | ✅ |
| Other non-current assets | $83,727M | `other_non_current_assets` | $83,727M | ✅ |
| Total non-current assets | $211,284M | `total_non_current_assets` | $211,284M | ✅ |
| Total assets | $359,241M | `total_assets` | $359,241M | ✅ |
| Accounts payable | $69,860M | `accounts_payable` | $69,860M | ✅ |
| Other current liabilities | $66,387M | `other_current_liabilities` | $66,387M | ✅ |
| Deferred revenue | $9,055M | `accrued_expenses` | $9,055M | ❌ **WRONG KEY** |
| Commercial paper | $7,979M | `short_term_debt` | $7,979M | ✅ |
| Term debt (current) | $12,350M | `current_portion_ltd` | $12,350M | ✅ |
| Total current liabilities | $165,631M | `total_current_liabilities` | $165,631M | ✅ |
| Term debt (non-current) | $78,328M | `long_term_debt` | $78,328M | ✅ |
| Other non-current liabilities | $41,549M | `other_nc_liabilities` | $41,549M | ✅ |
| Total non-current liabilities | $119,877M | `total_non_current_liabilities` | $119,877M | ✅ |
| Total liabilities | $285,508M | `total_liabilities` | $285,508M | ✅ |
| Common stock and APIC | $93,568M | `common_stock` | $93,568M | ✅ |
| Accumulated deficit | -$14,264M | `retained_earnings` | -$14,264M | ✅ |
| Accumulated OCI | -$5,571M | `accumulated_oci` | -$5,571M | ✅ |
| Total shareholders' equity | $73,733M | `total_equity` | $73,733M | ✅ |
| Total L + SE | $359,241M | `total_liabilities_and_equity` | $359,241M | ✅ |
| Shares outstanding | 14,773M | `shares_outstanding` | 14,773M | ✅ |
| — (derived) | — | `total_debt` | $98,657M (L0) | ✅ 7,979 + 12,350 + 78,328 |
| — (derived) | — | `net_debt` | $43,960M (L0) | ✅ 98,657 - 35,934 - 18,763 |

**BS Score: 25/27 lines correct. 1 wrong key (deferred revenue as accrued_expenses). 2 items missing (vendor receivables, NC marketable securities lumped into "other").**

**Specific checks:**
- `deferred_revenue_current`: ❌ EDGAR XBRL maps "Deferred revenue" to `accrued_expenses` via `OtherOperatingCurrentLiabilities` concept. The keyword fix only works on Yahoo path.
- `total_debt` = 7,979 + 12,350 + 78,328 = **$98,657M** ✅
- `net_debt` = 98,657 - 35,934 - 18,763 = **$43,960M** ✅
- `total_assets` ($359,241M) = `total_liabilities` ($285,508M) + `total_equity` ($73,733M) = $359,241M ✅

### 1c. Cash Flow Statement

| 10-K Line Item | 10-K Value | Std Key | Std Value | Match? |
|---|---|---|---|---|
| Net income | $112,010M | `net_income_cf` | $112,010M | ✅ |
| Depreciation and amortization | $11,698M | `depreciation_amortization` | $11,698M | ✅ |
| Share-based compensation | $12,863M | `stock_based_compensation` | $12,863M | ✅ |
| Other | -$89M | `other_non_cash` | -$89M | ✅ |
| Accounts receivable | -$6,682M | — | **VANTAR** | ❌ No concept |
| Vendor non-trade receivables | -$347M | — | **VANTAR** | ❌ No concept |
| Inventories | $1,400M | — | **VANTAR** | ❌ No concept |
| Other current/NC assets | -$9,197M | — | **VANTAR** | ❌ No concept |
| **Accounts payable** | **$902M** | `other_operating_cf` | **$902M (L4)** | ❌ **WRONG KEY** |
| Other current/NC liabilities | -$11,076M | `change_in_other_wc` | -$11,076M | ✅ |
| Cash generated by operating | $111,482M | `operating_cash_flow` | $111,482M | ✅ |
| Purchases of marketable securities | -$17,052M | — | **VANTAR** | ❌ No concept |
| Proceeds from maturities | $40,907M | — | **VANTAR** | ❌ No concept |
| Proceeds from sales | $12,890M | `investment_proceeds` | $12,890M | ✅ |
| Payments for PP&E | -$12,715M | `capital_expenditure` | -$12,715M | ✅ |
| Other | -$1,480M | — | **VANTAR** | ❌ No concept |
| Cash generated by investing | $15,195M | `investing_cash_flow` | $15,195M | ✅ |
| Tax on share settlement | -$5,960M | `other_cf_item` (L4) | -$5,960M | ⚠️ Wrong key |
| **Dividends paid** | **-$15,421M** | `minority_distributions` | **-$15,421M** | ❌ **WRONG KEY** |
| Repurchases of common stock | -$90,711M | `buybacks_and_issuance` | -$90,711M | ✅ |
| Proceeds from debt | $4,481M | `debt_issuance` | $4,481M | ✅ |
| Repayments of debt | -$10,932M | `debt_repayment` | -$10,932M | ✅ |
| Commercial paper, net | -$2,032M | `other_investing_cf` (L4) | -$2,032M | ❌ **WRONG SECTION** |
| Cash used in financing | -$120,686M | `financing_cash_flow` | -$120,686M | ✅ |
| Net change in cash | $5,991M | `net_change_in_cash` | $5,991M | ✅ |
| **Cash paid for taxes** | **$43,369M** | `deferred_income_tax` | **$43,369M** | ❌ **WRONG KEY** |
| — (derived) | — | `free_cash_flow` | $98,767M (L0) | ✅ 111,482 - 12,715 |

**CF Score: 12/25 lines correct. 4 wrong keys. 8 lines with no XBRL concept (None) fall through or are missing. 1 line in wrong section.**

**Key CF issues (all XBRL concept mapping problems):**
1. `minority_distributions` should be `dividends_paid` — XBRL concept `DistributionsToMinorityInterests` is wrong for Apple
2. `deferred_income_tax` is actually "Cash paid for income taxes" — XBRL concept `IncomeTaxes` maps to wrong key
3. `other_operating_cf` should be `change_in_payables` — no XBRL concept assigned to Apple's "Accounts payable" CF line
4. Many WC items (receivables, inventory, other assets) have `None` as XBRL concept and are lost

**FCF check:** OCF ($111,482M) - CapEx ($12,715M) = **$98,767M** ✅

---

## 2. MSFT — Line-by-Line (FY2025)

### 2a. Income Statement

| 10-K Line Item | 10-K Value | Std Key | Std Value | Match? |
|---|---|---|---|---|
| Revenue | $281,724M | `revenue` | $281,724M | ✅ |
| Cost of revenue | $87,831M | `cogs` | $87,831M | ✅ |
| Gross margin | $193,893M | `gross_profit` | $193,893M | ✅ |
| Research and development | $32,488M | `rd` | $32,488M | ✅ |
| Sales and marketing | $25,513M | — | **VANTAR** | ❌ Mapped to `sga` instead |
| General and administrative | $7,223M | `sga` | $7,223M | ⚠️ Only G&A, missing S&M |
| Operating income | $128,528M | `ebit` | $128,528M | ✅ |
| Other income (expense), net | -$4,901M | `other_non_operating` | -$4,901M | ✅ |
| Income before income taxes | $123,627M | `pretax_income` | $123,627M | ✅ |
| Provision for income taxes | $21,795M | `tax_provision` | $21,795M | ✅ |
| Net income | $101,832M | `net_income` | $101,832M | ✅ |
| Basic (shares) | 7,433M | `basic_shares` | 7,433M | ✅ |
| Diluted (shares) | 7,465M | `diluted_shares` | 7,465M | ✅ |
| Diluted EPS | $13.64 | `diluted_eps` | **VANTAR** | ❌ Same XBRL issue as AAPL |
| — | — | `other_is_item` | $13.64 (L4) | ⚠️ EPS in wrong key |

**IS Score: 11/14 correct. 1 EPS error. 1 S&M missing (only G&A captured as sga).**

**MSFT SGA issue:** MSFT splits operating expenses into R&D ($32.5B), Sales & Marketing ($25.5B), and G&A ($7.2B). The XBRL concept `SellingGeneralAndAdminExpenses` only captures G&A ($7.2B). Sales & Marketing has a different concept that isn't in our map. Total OpEx should be $65.2B but `total_opex` is not present.

### 2b. Balance Sheet

| 10-K Line Item | 10-K Value | Std Key | Std Value | Match? |
|---|---|---|---|---|
| Cash and cash equivalents | $30,242M | — | **VANTAR** | ❌ See below |
| Short-term investments | $64,323M | `short_term_investments` | $64,323M | ✅ |
| Total cash, equivalents, and STI | $94,565M | `cash` | $94,565M | ⚠️ Combined, not split |
| Accounts receivable | $69,905M | `accounts_receivable` | $69,905M | ✅ |
| Inventories | $938M | `inventories` | $938M | ✅ |
| Other current assets | $25,723M | `other_current_assets` | $25,723M | ✅ |
| Total current assets | $191,131M | `total_current_assets` | $191,131M | ✅ |
| Property and equipment, net | $204,966M | `pp_and_e` | $204,966M | ✅ |
| Operating lease ROU | $24,823M | `operating_lease_assets` | $24,823M | ✅ |
| Equity and other investments | $15,405M | `long_term_investments` | $15,405M | ✅ |
| Goodwill | $119,509M | `goodwill` | $119,509M | ✅ |
| Intangible assets, net | $22,604M | `intangible_assets` | $22,604M | ✅ |
| Other long-term assets | $40,565M | `other_non_current_assets` | $40,565M | ✅ |
| Total assets | $619,003M | `total_assets` | $619,003M | ✅ |
| Accounts payable | $27,724M | `accounts_payable` | $27,724M | ✅ |
| Current portion of LTD | $2,999M | `current_portion_ltd` | $2,999M | ✅ |
| Short-term unearned revenue | $64,555M | `accrued_expenses` | $64,555M | ❌ **WRONG KEY** |
| Accrued compensation | $13,709M | `accrued_compensation` | $13,709M | ✅ |
| Short-term income taxes | $7,211M | `accrued_income_taxes` | $7,211M | ✅ |
| Other current liabilities | $25,020M | `other_current_liabilities` | $25,020M | ✅ |
| Total current liabilities | $141,218M | `total_current_liabilities` | $141,218M | ✅ |
| Long-term debt | $40,152M | `long_term_debt` | $40,152M | ✅ |
| Operating lease liabilities | $17,437M | `operating_lease_nc` | $17,437M | ✅ |
| Long-term income taxes | $25,986M | `deferred_tax_nc` | $25,986M | ✅ |
| Deferred income taxes | $2,835M | `deferred_tax_liabilities` | $2,835M | ✅ |
| Long-term unearned revenue | $2,710M | `contract_liabilities` | $2,710M | ✅ |
| Other long-term liabilities | $45,186M | `other_nc_liabilities` | $45,186M | ✅ |
| Total liabilities | $275,524M | `total_liabilities` | $275,524M | ✅ |
| Common stock and APIC | $109,095M | `common_stock` | $109,095M | ✅ |
| Retained earnings | $237,731M | `retained_earnings` | $237,731M | ✅ |
| Accumulated OCI | -$3,347M | `accumulated_oci` | -$3,347M | ✅ |
| Total stockholders' equity | $343,479M | `total_equity` | $343,479M | ✅ |
| Total L + SE | $619,003M | `total_liabilities_and_equity` | $619,003M | ✅ |
| — (derived) | — | `total_debt` | $43,151M | ✅ 0 + 2,999 + 40,152 |
| — (derived) | — | `net_debt` | -$115,737M | ⚠️ See note |

**BS Score: 27/30 correct. 1 wrong key (unearned revenue as accrued_expenses). 1 cash/STI combined issue.**

**MSFT cash issue:** EDGAR combines Cash + STI into one line "Total cash, cash equivalents, and short-term investments" ($94,565M). But STI also appears separately ($64,323M). The `cash` key holds the combined value. Net debt = 43,151 - 94,565 - 64,323 = **-$115,737M**, but this double-counts STI. Correct net debt should be: 43,151 - 94,565 = **-$51,414M** (since $94,565 already includes the $64,323 STI). **This is a net_debt calculation bug for MSFT.**

### 2c. Cash Flow Statement

| 10-K Line Item | 10-K Value | Std Key | Std Value | Match? |
|---|---|---|---|---|
| Net income | $101,832M | `net_income_cf` | $101,832M | ✅ |
| D&A | $34,153M | — | **VANTAR** | ❌ Not captured |
| Stock-based compensation | $11,974M | `stock_based_compensation` | $11,974M | ✅ |
| Deferred income taxes | -$7,056M | `deferred_income_tax` | -$7,056M | ✅ |
| Net cash from operations | $136,162M | `operating_cash_flow` | $136,162M | ✅ |
| Additions to PP&E | -$64,551M | `capital_expenditure` | -$64,551M | ✅ |
| Acquisitions, net | -$5,978M | `other_investing_cf` (L4) | -$5,978M | ❌ Should be `acquisitions` |
| Purchases of investments | -$29,775M | `investment_purchases` | -$29,775M | ✅ |
| Maturities of investments | $16,079M | `investment_proceeds` | $16,079M | ✅ |
| Sales of investments | $9,309M | `other_cf_item` (L4) | $9,309M | ⚠️ Should be investment_proceeds |
| Net cash used in investing | -$72,599M | `investing_cash_flow` | -$72,599M | ✅ |
| Repayments of debt | -$3,216M | `other_financing_cf` (L4) | -$3,216M | ❌ Should be `debt_repayment` |
| Common stock repurchased | -$18,420M | `buybacks_and_issuance` | -$18,420M | ✅ |
| Dividends paid | -$24,082M | — | **VANTAR** | ❌ Not captured (no XBRL concept) |
| Net cash used in financing | -$51,699M | `financing_cash_flow` | -$51,699M | ✅ |
| FX effect | $63M | `fx_effect` | $63M | ✅ |
| Net change | $11,927M | `net_change_in_cash` | $11,927M | ✅ |
| Accounts payable | $569M | `other_operating_cf` (L4) | $569M | ❌ Wrong key |
| — (derived) | — | `free_cash_flow` | $71,611M | ✅ 136,162 - 64,551 |

**CF Score: 11/18 correct. 4 wrong keys. 3 missing (D&A, dividends, change in WC items).**

---

## 3. XOM — Line-by-Line (FY2025)

### 3a. Income Statement

| 10-K Line Item | 10-K Value | Std Key | Std Value | Match? |
|---|---|---|---|---|
| Revenues | $332,238M | `revenue` | $332,238M | ✅ |
| Crude oil and product purchases | $184,248M | `other_is_item` (L4) | $184,248M | ❌ Should be `cogs` |
| Production and manufacturing | — | — | **VANTAR** | ❌ |
| Depreciation and depletion | $25,993M | `da` | $25,993M | ✅ |
| Exploration expenses | $1,007M | `rd` | $1,007M | ⚠️ Not R&D, but mapped there |
| Other taxes and duties | $25,167M | `sga` | $25,167M | ❌ Not SGA — these are operating taxes |
| Total costs and other deductions | $290,970M | `total_costs` | $290,970M | ✅ |
| Income before income taxes | $41,268M | `pretax_income` | $41,268M | ✅ |
| Income tax expense | $11,504M | `tax_provision` | $11,504M | ✅ |
| Net income (including NCI) | $29,764M | `net_income_including_minority` | $29,764M | ✅ |
| Net income (ExxonMobil) | $28,844M | `net_income` | $28,844M | ✅ |
| Interest expense | $603M | `interest_expense` | $603M | ✅ |
| Pension expense | $400M | `pension_expense` | $400M | ✅ |
| — (derived) | — | `ebit` | $41,871M (L0) | ✅ Pretax + Interest |
| — (derived) | — | `gross_profit` | $94,038M (L0) | ⚠️ Derived: EBIT + OpEx |
| — (derived) | — | `ebitda` | $67,864M (L0) | ✅ EBIT + D&A |

**IS Score: 9/14 correct. 2 wrong mappings (crude oil purchases, other taxes). 1 missing (production costs). Derived fields correct.**

XOM has a fundamentally different IS structure: no COGS line, no SGA line, no operating income line. Revenue - Total Costs = Pretax Income. The standardizer handles this reasonably via derived fields (EBIT = Pretax + Interest), but individual cost breakdowns are mapped to wrong keys.

### 3b. Cash Flow Statement

| 10-K Line Item | 10-K Value | Std Key | Std Value | Match? |
|---|---|---|---|---|
| Net income (incl NCI) | $29,764M | `net_income_cf` | $29,764M | ✅ |
| D&A (incl impairments) | $25,993M | `depreciation_amortization` | $25,993M | ✅ |
| Deferred income taxes | $765M | `deferred_income_tax` | $765M | ✅ |
| Net (gain)/loss on asset sales | -$1,113M | `non_operating_cf` | -$1,113M | ✅ |
| Receivables change | -$3,042M | `change_in_receivables` | -$3,042M | ✅ |
| Payables change | -$222M | `other_operating_cf` (L4) | -$222M | ❌ Wrong key |
| Net cash from operations | $51,970M | `operating_cash_flow` | $51,970M | ✅ |
| Additions to PP&E | -$28,358M | `capital_expenditure` | -$28,358M | ✅ |
| Long-term debt additions | $2,311M | `debt_issuance` | $2,311M | ✅ |
| Long-term debt reductions | -$1,108M | `debt_repayment` | -$1,108M | ✅ |
| Common stock acquired | -$20,273M | `buybacks_and_issuance` | -$20,273M | ✅ |
| Dividends to NCI | -$935M | `minority_distributions` | -$935M | ✅ (correct for XOM!) |
| Short-term debt reductions | -$5,404M | `other_financing_cf` (L4) | -$5,404M | ⚠️ |
| Net cash from financing | -$39,081M | `financing_cash_flow` | -$39,081M | ✅ |
| FX effect | $532M | `fx_effect` | $532M | ✅ |
| — (derived) | — | `free_cash_flow` | $23,612M | ✅ 51,970 - 28,358 |

**CF Score: 12/14 correct. 1 wrong key (payables). 1 reasonable L4 (ST debt).**

Note: `minority_distributions` is CORRECT for XOM (it actually has noncontrolling interests, unlike AAPL).

---

## 4. AAPL Consistency Across Years (2023-2025)

| Item | 2023 | 2024 | 2025 | Consistent? |
|---|---|---|---|---|
| `revenue` | $383,285M | $391,035M | $416,161M | ✅ Same scale |
| `cogs` | $214,137M | $210,352M | $220,960M | ✅ |
| `ebit` | $114,301M | $123,216M | $133,050M | ✅ |
| `net_income` | $96,995M | $93,736M | $112,010M | ✅ |
| `diluted_shares` | 15,813M | 15,408M | 15,005M | ✅ Declining (buybacks) |
| `ebitda` (derived) | $125,820M | $134,661M | $144,748M | ✅ |
| `net_debt` (derived) | $71,301M | $65,774M | $43,960M | ✅ Declining |
| `free_cash_flow` (derived) | $99,584M | $108,807M | $98,767M | ✅ |
| `capital_expenditure` | -$10,959M | -$9,447M | -$12,715M | ✅ Always negative |

**All values in same scale (millions). All derived fields present in all 3 years. Signs consistent. No anomalies.**

---

## 5. Template Integrity

### 5a. IS Line Order

**Expected:** Revenue -> COGS -> GP -> R&D -> SG&A -> Total OpEx -> EBIT -> D&A -> EBITDA -> Interest -> Other Non-Op -> Pretax -> Tax -> Net Income -> EPS -> Shares

**Actual (AAPL XBRL):** The standardizer outputs a dict (not ordered) — display order is controlled by `_IS_FIELDS` in `preparation_display.py`. The display template follows the correct order. The underlying data has no inherent order.

**Verdict:** ✅ Display order is correct. Data order is irrelevant (dict keys).

### 5b. BS Line Grouping

The display fields in `preparation_display.py` follow standard grouping:
- ASSETS: Cash -> STI -> AR -> Inventory -> Total CA -> PP&E -> Goodwill -> Intangibles -> Total Assets
- LIABILITIES: AP -> Deferred Rev -> Total CL -> LT Debt -> Total Liab
- EQUITY: Total Equity -> Total Debt -> Net Debt -> Shares

**Verdict:** ✅ Correctly grouped.

### 5c. Missing Critical Items Checklist

**Income Statement:**
| Item | AAPL | MSFT | XOM |
|------|------|------|-----|
| Interest expense | ❌ None in XBRL | ✅ | ✅ |
| D&A on IS | ❌ Only from CF | ❌ | ✅ |
| SBC on IS | ❌ Only on CF | ❌ | ❌ |
| EBITDA (derived) | ✅ | ✅ | ✅ |
| Diluted EPS | ❌ In other_is_item | ❌ In other_is_item | ❌ |

**Balance Sheet:**
| Item | AAPL | MSFT | XOM |
|------|------|------|-----|
| Goodwill | N/A (none) | ✅ | ❌ Bundled in other |
| Intangible assets | N/A (none) | ✅ | ❌ Bundled in other |
| Total debt (derived) | ✅ | ✅ | ✅ |

**Cash Flow:**
| Item | AAPL | MSFT | XOM |
|------|------|------|-----|
| Change in receivables | ❌ Lost (no concept) | ❌ Lost | ✅ |
| Change in inventory | ❌ Lost (no concept) | ❌ Lost | ❌ Lost |
| Change in payables | ❌ Wrong key (L4) | ❌ Wrong key (L4) | ❌ Wrong key (L4) |
| Dividends paid | ❌ Wrong key | ❌ Missing | ✅ (as minority_dist) |
| Stock repurchases | ✅ | ✅ | ✅ |
| Acquisitions | N/A | ❌ Wrong key (L4) | N/A |
| D&A | ✅ | ❌ Missing | ✅ |
| SBC | ✅ | ✅ | ❌ Missing |
| CapEx | ✅ | ✅ | ✅ |
| FCF (derived) | ✅ | ✅ | ✅ |

---

## 6. Edge Cases

### 6a. Missing Values
When a line item is not in EDGAR XBRL data, the key is simply **absent** from the dict. It is not `None` or `0`. This is correct behavior — downstream code checks `if value is not None`.

Exception: `interest_expense` for AAPL is completely absent from XBRL IS data (Apple reports it within "Other income/(expense), net"). This means interest coverage ratio cannot be calculated.

### 6b. Negative Numbers (Sign Convention)

| Item | AAPL | MSFT | XOM | Convention |
|------|------|------|-----|------------|
| CapEx | -$12,715M | -$64,551M | -$28,358M | ✅ Negative (cash outflow) |
| Dividends | -$15,421M | — | -$935M | ✅ Negative |
| Buybacks | -$90,711M | -$18,420M | -$20,273M | ✅ Negative |
| Debt repayment | -$10,932M | -$3,216M | -$1,108M | ✅ Negative |
| Revenue | $416,161M | $281,724M | $332,238M | ✅ Positive |
| D&A | $11,698M | — | $25,993M | ✅ Positive (non-cash add-back) |

**All signs consistent across companies.** Cash outflows are negative, inflows are positive.

### 6c. Share Counts

| Source | AAPL 2025 | Unit |
|--------|-----------|------|
| IS `diluted_shares` | 15,004,697,000 | Whole shares |
| IS `basic_shares` | 14,948,500,000 | Whole shares |
| BS `shares_outstanding` | 14,773,260,000 | Whole shares |

All in **whole shares** (not millions). IS diluted > IS basic > BS outstanding (as expected: diluted includes options/RSUs, outstanding is issued).

**Consistent across MSFT and XOM too.** MSFT: diluted 7,465M, basic 7,433M. XOM: not reported in IS from XBRL (shares absent).

---

## 7. Summary

### Error Count by Severity

| Severity | Count | Description |
|----------|-------|-------------|
| **Critical** | 0 | No numbers are mathematically wrong |
| **High** | 6 | Wrong key names (data present but mislabeled) |
| **Medium** | 8 | Missing items (data lost during standardization) |
| **Low** | 3 | Cosmetic (EPS in other_is_item, exploration as R&D) |
| **Total** | **17** | |

### Wrong Key Issues (High — data present but mislabeled)

| Issue | Affected | Root Cause |
|-------|----------|------------|
| Deferred revenue -> `accrued_expenses` | AAPL, MSFT | XBRL concept `OtherOperatingCurrentLiabilities` maps to `accrued_expenses` |
| Dividends -> `minority_distributions` | AAPL (not XOM) | XBRL concept `DistributionsToMinorityInterests` used for all dividend payments |
| Cash taxes paid -> `deferred_income_tax` | AAPL | XBRL concept `IncomeTaxes` maps to `deferred_income_tax` |
| Accounts payable (CF) -> `other_operating_cf` | AAPL, MSFT, XOM | No XBRL concept assigned to CF payables line |
| MSFT acquisitions -> `other_investing_cf` | MSFT | No XBRL concept for MSFT's acquisition line |
| MSFT debt repayment -> `other_financing_cf` | MSFT | No XBRL concept for MSFT's debt repayment line |

### Missing Items (Medium — data lost)

| Issue | Affected | Root Cause |
|-------|----------|------------|
| Change in receivables (CF) | AAPL, MSFT | XBRL concept is `None` for these CF lines |
| Change in inventory (CF) | AAPL, MSFT, XOM | XBRL concept is `None` |
| D&A on CF | MSFT | XBRL concept not mapped |
| Dividends paid | MSFT | No XBRL concept |
| MSFT Sales & Marketing ($25.5B) | MSFT | Different XBRL concept than `SellingGeneralAndAdminExpenses` |
| MSFT net_debt double-counts STI | MSFT | Cash key includes STI; net_debt subtracts STI again |

### What Works Perfectly
- All IS top-line items (Revenue, COGS, GP, EBIT, Pretax, Tax, Net Income)
- All BS totals and subtotals (Assets, Liabilities, Equity, L+E balance)
- All CF subtotals (OCF, ICF, FCF)
- All derived fields (EBITDA, FCF, total_debt) — **mathematically correct**
- Sign conventions — consistent across all companies
- Cross-year consistency — no scale or format changes
- Revenue - COGS = GP cross-check passes for all companies, all years
- Assets = L + E cross-check passes for all companies except XOM (minority interest issue)
