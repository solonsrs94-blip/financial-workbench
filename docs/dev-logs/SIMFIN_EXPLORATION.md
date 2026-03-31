# SimFin Exploration — What Do We Actually Get for Free?

**Date:** 2026-03-26
**API Key:** Registered free account (71937d...)

---

## 1. Overview — What's Free?

| Dataset | Works Free? | Years | Tickers | Columns | Delay? |
|---------|-------------|-------|---------|---------|--------|
| Income Statement (annual) | ✅ | 5 (2020-2024) | ~3,400 | 26 | ~12 months (FY2025 missing) |
| Balance Sheet (annual) | ✅ | 5 (2020-2024) | ~3,400 | 28 | ~12 months |
| Cash Flow (annual) | ✅ | 5 (2020-2024) | ~3,400 | 26 | ~12 months |
| IS Banks (annual) | ✅ | 5 | ~175 | 20 | ~12 months |
| IS Insurance (annual) | ✅ | 5 | ~60 | 18 | ~12 months |
| Income Quarterly | ✅ | 5 (20 quarters) | ~3,400 | 26 | ~12 months |
| Income TTM | ✅ | 5 | ~3,400 | 26 | ~12 months |
| Share Prices (daily) | ✅ | ~5 yr (2020-2025) | ~3,400 | 9 | A few days |
| Derived Ratios (annual) | ❌ 500 error | — | — | — | — |
| Derived Share Prices | ❌ 500 error | — | — | — | — |
| Full variants (annual-full) | ❌ 500 error | — | — | — | — |
| Companies List | ✅ | — | 6,536 | 10 | — |
| Germany | ✅ | 5 | 27 | 26 | ~12 months |
| UK | ❌ 500 error | — | — | — | — |

**Key finding:** `sf.set_api_key('free')` no longer works — you MUST register and get a real API key.

---

## 2. Column Lists

### Income Statement (26 columns)
SimFinId, Currency, Fiscal Year, Fiscal Period, Publish Date, Restated Date, Shares (Basic), Shares (Diluted), **Revenue**, **Cost of Revenue**, **Gross Profit**, **Operating Expenses**, **Selling, General & Administrative**, **Research & Development**, **Depreciation & Amortization**, **Operating Income (Loss)**, **Non-Operating Income (Loss)**, **Interest Expense, Net**, **Pretax Income (Loss), Adj.**, Abnormal Gains (Losses), **Pretax Income (Loss)**, **Income Tax (Expense) Benefit, Net**, Income (Loss) from Continuing Operations, Net Extraordinary Gains (Losses), **Net Income**, **Net Income (Common)**

### Balance Sheet (28 columns)
SimFinId, Currency, Fiscal Year, Fiscal Period, Publish Date, Restated Date, Shares (Basic), Shares (Diluted), **Cash, Cash Equivalents & Short Term Investments**, **Accounts & Notes Receivable**, **Inventories**, **Total Current Assets**, **Property, Plant & Equipment, Net**, **Long Term Investments & Receivables**, Other Long Term Assets, **Total Noncurrent Assets**, **Total Assets**, **Payables & Accruals**, **Short Term Debt**, **Total Current Liabilities**, **Long Term Debt**, **Total Noncurrent Liabilities**, **Total Liabilities**, **Share Capital & Additional Paid-In Capital**, Treasury Stock, **Retained Earnings**, **Total Equity**, **Total Liabilities & Equity**

### Cash Flow (26 columns)
SimFinId, Currency, Fiscal Year, Fiscal Period, Publish Date, Restated Date, Shares (Basic), Shares (Diluted), **Net Income/Starting Line**, **Depreciation & Amortization**, Non-Cash Items, **Change in Working Capital**, **Change in Accounts Receivable**, **Change in Inventories**, **Change in Accounts Payable**, Change in Other, **Net Cash from Operating Activities**, **Change in Fixed Assets & Intangibles** (CapEx), Net Change in Long Term Investment, Net Cash from Acquisitions & Divestitures, **Net Cash from Investing Activities**, **Dividends Paid**, Cash from (Repayment of) Debt, Cash from (Repurchase of) Equity, **Net Cash from Financing Activities**, **Net Change in Cash**

### IS Banks (extra columns vs standard)
Revenue, **Provision for Loan Losses**, **Net Revenue after Provisions**, **Total Non-Interest Expense**, Operating Income — no COGS/GP/SGA/R&D

### IS Insurance (extra columns vs standard)
Revenue, **Total Claims & Losses**, Operating Income — minimal detail

### Share Prices (9 columns)
SimFinId, **Open**, **High**, **Low**, **Close**, **Adj. Close**, **Volume**, **Dividend**, Shares Outstanding

### Companies List (10 columns)
SimFinId, **Company Name**, **IndustryId**, ISIN, End of financial year (month), Number Employees, Business Summary, Market, CIK, Main Currency

---

## 3. AAPL Comparison — SimFin vs EDGAR (FY2024)

### Income Statement

| Line | SimFin | EDGAR (Std) | Match? |
|------|--------|-------------|--------|
| Revenue | $391,035M | $391,035M | ✅ |
| Cost of Revenue | -$210,352M | $210,352M | ✅ (sign diff) |
| Gross Profit | $180,683M | $180,683M | ✅ |
| SGA | -$26,097M | $26,097M | ✅ |
| R&D | -$31,370M | $31,370M | ✅ |
| D&A | NOT in IS | NOT in IS | — |
| Operating Income | $123,216M | $123,216M | ✅ |
| Interest Expense, Net | — | — | Both missing |
| Pretax Income | $123,485M | $123,485M | ✅ |
| Tax | -$29,749M | $29,749M | ✅ |
| Net Income | $93,736M | $93,736M | ✅ |
| Diluted Shares | 15,408M | 15,408M | ✅ |
| Diluted EPS | NOT in dataset | `other_is_item` (wrong key) | Both bad |

**IS: 10/10 matching values. SimFin uses negative for costs; EDGAR uses positive.**

### Cash Flow Statement

| Line | SimFin | EDGAR (Std) | Match? |
|------|--------|-------------|--------|
| Net Income | $93,736M | $93,736M | ✅ |
| D&A | $11,445M | $11,445M | ✅ |
| Change in Working Capital | $3,651M | MISSING | ❌ SimFin has it |
| Change in Receivables | MISSING | MISSING | Both missing! |
| Change in Inventories | MISSING | MISSING | Both missing! |
| Change in Payables | MISSING | MISSING | Both missing! |
| Operating Cash Flow | $118,254M | $118,254M | ✅ |
| CapEx | -$9,447M | -$9,447M | ✅ |
| Investing CF | $2,935M | $2,935M | ✅ |
| **Dividends Paid** | **-$15,234M** | **MISSING (wrong key)** | ❌ SimFin correct |
| Debt (repayment) | -$5,998M | -$9,958M | ❌ Different grouping |
| Buybacks | -$94,949M | -$94,949M | ✅ |
| Financing CF | -$121,983M | -$121,983M | ✅ |
| Net Change in Cash | -$794M | -$794M | ✅ |

**Key CF finding:** SimFin ALSO does NOT have receivables/inventory/payables detail for AAPL on the free tier! These columns exist but are NaN for AAPL. SimFin has "Change in Working Capital" as a single aggregated line, but individual components are often missing. However, SimFin correctly labels **Dividends Paid** (EDGAR puts it in `minority_distributions`).

---

## 4. CF Detail Lines — The Key Question

| CF Detail Line | EDGAR (our std) | SimFin Free |
|---|---|---|
| Change in Receivables | ❌ Lost (no XBRL concept) | ⚠️ Column exists, but NaN for AAPL |
| Change in Inventory | ❌ Lost (no XBRL concept) | ⚠️ Column exists, but NaN for AAPL |
| Change in Payables | ❌ Wrong key (other_operating_cf) | ⚠️ Column exists, but NaN for AAPL |
| Change in Working Capital (total) | ❌ Missing | ✅ $3,651M |
| Dividends Paid | ❌ Wrong key (minority_distributions) | ✅ Correct key |
| D&A | ✅ | ✅ |
| SBC | ✅ (separate line) | ⚠️ Bundled in "Non-Cash Items" |
| CapEx | ✅ | ✅ |
| Acquisitions | ❌ Not always | ✅ Separate column |
| Debt issuance/repayment | ✅ (separate) | ⚠️ Combined into one line |

**Conclusion:** SimFin does NOT solve the WC detail problem for AAPL. The columns exist in the schema but Apple's specific data doesn't have them broken out. SimFin DO fix the dividends labeling issue, and provides acquisitions and total working capital change.

---

## 5. Banking & Insurance Templates

### JPM (Bank) — FY2024

| Line | Value |
|------|-------|
| Revenue | $177,556M |
| Provision for Loan Losses | -$10,678M |
| Net Revenue after Provisions | $166,878M |
| Total Non-Interest Expense | -$91,797M |
| Operating Income | $75,081M |
| Tax | -$16,610M |
| Net Income | $58,471M |

Different template: No COGS/GP/SGA/R&D. Uses banking-specific lines (provision for loan losses, non-interest expense). This is exactly what we need for financial companies.

### Insurance
Small dataset (304 rows, ~60 companies). Has Revenue, Total Claims & Losses, Operating Income. Minimal but functional.

---

## 6. What's NOT Free

| Feature | Required Tier | Cost |
|---------|--------------|------|
| >5 years of history | START | $15/mo |
| Current data (no 12-month delay) | START+ | $15/mo+ |
| Premium bulk datasets (derived ratios) | BASIC | $35/mo |
| Full variants (more columns) | BASIC | $35/mo |
| Excel plugin | START | $15/mo |
| UK market | Unknown (500 error) | ? |
| >500 API credits/month | START+ | $15/mo+ |

---

## 7. Sign Convention Difference

**Critical for integration:**
- **SimFin:** Costs are NEGATIVE (COGS = -$210B, Tax = -$29B, CapEx = -$9B)
- **EDGAR/Our std:** Costs are POSITIVE (COGS = $210B, Tax = $29B) but CapEx is NEGATIVE

If we integrate SimFin, we need to handle sign normalization.

---

## 8. Multi-Company Comparison

### CF Detail Lines — 10 Companies

| Ticker | ChgRecv | ChgInv | ChgPay | ChgWC (total) | DivPaid | Acquisitions | D&A |
|--------|---------|--------|--------|---------------|---------|-------------|-----|
| AAPL | -- | -- | -- | $3,651M | -$15,234M | -- | $11,445M |
| MSFT | -- | -- | -- | $1,824M | -$21,771M | -$69,132M | $22,287M |
| GOOG | -- | -- | -- | -$8,406M | -$7,363M | -$2,931M | $15,311M |
| XOM | -- | -- | -- | $484M | -$16,704M | $754M | $23,442M |
| WMT | -- | -- | -- | $2,553M | -$6,114M | -$740M | $10,945M |
| JPM | N/A (bank) | N/A | N/A | N/A | N/A | N/A | N/A |
| AMZN | -- | -- | -- | -$15,541M | -- | -$7,082M | $52,795M |
| JNJ | -- | -- | -- | $1,848M | -$11,823M | -$15,146M | $7,339M |
| **PG** | **-$766M** | **-$70M** | **$878M** | $533M | -$9,312M | -$21M | $2,896M |
| META | -- | -- | -- | $1,048M | -$5,072M | -$270M | $15,498M |

**PG er eitt af aðeins 33 fyrirtækjum (0.7%) sem hafa sundurliðaðar WC línur.** Flest stór fyrirtæki (AAPL, MSFT, GOOG, AMZN, XOM) hafa bara aggregated "Change in Working Capital".

### Availability across ALL US companies (latest year)

| CF Detail Line | Companies with data | % of 4,413 |
|---|---|---|
| Change in Accounts Receivable | 33 | 0.7% |
| Change in Inventories | 26 | 0.6% |
| Change in Accounts Payable | 28 | 0.6% |
| Dividends Paid | 1,464 | 33.2% |
| Acquisitions | 1,599 | 36.2% |
| D&A | 4,064 | 92.1% |

### IS Comparison — Values Match?

| Ticker | Revenue | Net Income | EBIT | Notes |
|--------|---------|------------|------|-------|
| AAPL | ✅ | ✅ | ✅ | Perfect match |
| MSFT | ✅ | ✅ | ✅ | Perfect match |
| GOOG | ✅ | ✅ | ✅ | Perfect match |
| XOM | ❌ SF=$343B, E=$350B | ✅ | ❌ SF=$70B, E=$50B | SimFin reclassifies XOM's revenue and expenses differently |
| PG | ✅ | ✅ | ❌ SF=$19.9B, E=$18.5B | Minor EBIT difference (operating expense classification) |

**XOM discrepancy:** SimFin breaks XOM's IS into standard COGS/GP/OpEx template ($343B revenue, $70B EBIT). EDGAR reports $350B revenue and $50B EBIT because XOM includes items like "Equity earnings" in revenue and classifies costs differently. Both result in the same Net Income ($33.7B). This shows SimFin reclassifies items to fit their standard template — may or may not be what you want.

### WMT Year Mismatch
SimFin free only has WMT through FY2022 (calendar 2023). EDGAR has WMT through FY2026. SimFin's 12-month delay means it lags significantly — for a January fiscal year-end company, the gap is even wider.

### Dividend Label Fix Confirmed

| Ticker | SimFin "Dividends Paid" | EDGAR label | Match? |
|--------|------------------------|-------------|--------|
| AAPL | -$15,234M | `minority_distributions` (-$15,234M) | ✅ Same $, wrong EDGAR key |
| GOOG | -$7,363M | `minority_distributions` (-$7,363M) | ✅ Same $, wrong EDGAR key |
| PG | -$9,312M | `minority_distributions` (-$9,312M) | ✅ Same $, wrong EDGAR key |
| XOM | -$16,704M | `minority_distributions` (-$658M) | ❌ DIFFERENT! |

**XOM exception:** EDGAR's `minority_distributions` for XOM is genuinely minority interest distributions (-$658M), not dividends. SimFin's -$16,704M is ExxonMobil shareholder dividends. This confirms that EDGAR's XBRL concept `DistributionsToMinorityInterests` is sometimes correct (XOM) and sometimes wrong (AAPL, GOOG, PG). SimFin always has the right answer here.

### Banking Templates — Full Coverage

**Bank IS** (20 columns): Revenue, Provision for Loan Losses, Net Revenue after Provisions, Total Non-Interest Expense, Operating Income, Pretax, Tax, Net Income — completely different from standard IS.

**Bank BS** (25 columns): Cash, Interbank Assets, Short/Long Term Investments, Net Loans, Total Deposits, ST/LT Debt, Preferred Equity — proper banking balance sheet with deposits, loans, interbank.

**Bank CF** (24 columns): Net Income, D&A, Provision for Loan Losses, Net Change in Loans & Interbank, Dividends Paid — includes banking-specific CF items.

**JPM example:** Total Assets $4.0T, Deposits $2.4T, Net Loans $1.3T, Net Income $58.5B. All reasonable.

---

## 9. Summary & Recommendation

### What SimFin Free IS Good For
1. **Banking/Insurance IS templates** — we don't have these at all
2. **Dividends Paid** — correctly labeled (EDGAR puts it in `minority_distributions`)
3. **Acquisitions** — separate column (EDGAR often loses this)
4. **Total Working Capital change** — aggregated line available
5. **Quarterly data** — 20 quarters of IS/BS/CF
6. **Share prices** — daily with adj. close and dividends
7. **Company metadata** — 6,536 companies with sector, ISIN, CIK

### What SimFin Free Is NOT Good For
1. **WC Detail Lines** — receivables/inventory/payables are NaN for many companies (including AAPL)
2. **History** — only 5 years (vs 10-12 from EDGAR)
3. **Freshness** — 12-month delay (our EDGAR has FY2025, SimFin stops at FY2024)
4. **EPS** — not in the dataset at all (EDGAR at least has it, just wrong key)
5. **SBC** — bundled into "Non-Cash Items" (EDGAR has it separate)
6. **Derived ratios** — 500 error on free tier

### My Updated Recommendation

**Dual-source approach:**
1. **Primary: EDGAR** — 10-12 years, current data, all companies, free
2. **Secondary: SimFin** — banking/insurance templates, dividends fix, quarterly data
3. **Fix EDGAR mapper** — still the highest-ROI improvement for CF detail lines

SimFin is useful as a complement (especially for banking IS) but does NOT replace EDGAR or solve the WC detail problem. The 12-month delay is a dealbreaker for primary use.
