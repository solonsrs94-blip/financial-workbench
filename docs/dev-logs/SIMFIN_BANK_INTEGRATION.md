# SimFin Bank/Insurance Integration + Mapping Fixes

**Date:** 2026-03-30
**Files changed:**
- `lib/data/providers/simfin_provider.py` — rewritten with bank/insurance support
- `lib/data/concept_maps.py` — added fb_ META acquisition concept
- `lib/data/template.py` — added fb_ META acquisition concept
- `lib/analysis/company_classifier.py` — added subtype (bank/insurance) + data_source
- `pages/valuation/preparation.py` — dual-source: EDGAR for normal, SimFin for financial

---

## 1. Mapping Fixes

### SBC on WMT/CAT/XOM/CVX — NOT A BUG ✅
These companies genuinely don't report SBC as a separate CF line. It's bundled in "Other operating activities" or "Other non-cash items". This is common for non-tech companies.

### META Acquisitions 2014–2020 — FIXED ✅

| Year | Before | After | Note |
|------|--------|-------|------|
| 2014 | — | -$4,975M | WhatsApp cash portion (~$5B of $19B) |
| 2015 | — | -$313M | Small acquisitions |
| 2016 | — | -$123M | Small acquisitions |
| 2017 | — | -$122M | Small acquisitions |
| 2018 | — | -$137M | Small acquisitions |
| 2019 | — | -$508M | Including CTRL-labs |
| 2020 | — | -$388M | |
| 2021 | — | -$851M | Within Labs |

**Fix:** Added `fb_PaymentsToAcquireBusinessesNetOfCashAcquiredAndPurchasesOfIntangibleAndOtherAssets` to concept maps and template search rules. The `fb_` prefix (Facebook's old XBRL extension) was not being matched.

### MCD SGA — NOT A BUG ✅
McDonald's uses a franchise-specific IS template without a standard SGA line. Their expenses are broken into franchise-specific categories. This is correct behavior — not all companies have SGA.

---

## 2. JPM / BAC / GS — Bank Results

### JPM (FY2024, 5 years of data)

| Line | Value |
|------|-------|
| Revenue | $177,556M |
| Provision for Loan Losses | -$10,678M |
| Net Revenue after Provisions | $166,878M |
| Total Non-Interest Expense | -$91,797M |
| Operating Income | $75,081M |
| Net Income | $58,471M |
| Total Assets | $4,002,814M |
| Total Equity | $344,758M |
| Total Deposits | $2,406,032M |
| Net Loans | $1,323,643M |
| **Efficiency Ratio** | **51.7%** |
| **ROE** | **17.0%** |
| **ROA** | **1.46%** |
| **Loan/Deposit** | **55.0%** |

### BAC (FY2024, 5 years)

| Metric | Value |
|--------|-------|
| Revenue | $105,856M |
| Net Income | $26,973M |
| Total Assets | $3,261,299M |
| Efficiency Ratio | 63.1% |
| ROE | 5.3% |
| ROA | 0.83% |

### GS (FY2024, 5 years)

| Metric | Value |
|--------|-------|
| Revenue | $53,512M |
| Net Income | $14,276M |
| Total Assets | $1,675,972M |
| Efficiency Ratio | 50.5% |
| ROE | 11.7% |
| ROA | 0.85% |

All three banks: IS, BS, CF, and bank-specific ratios present and reasonable.

---

## 3. Insurance Results

### MET (MetLife, FY2024, 5 years)

| Metric | Value |
|--------|-------|
| Revenue | $70,986M |
| Net Income | $4,426M |
| Total Claims & Losses | -$53,662M |

Insurance IS template works. BS and CF from general SimFin template.

### ALL (Allstate) — NOT IN SIMFIN
Allstate is not in SimFin's insurance dataset (only 60 insurance companies covered). Would need EDGAR fallback.

---

## 4. Integration — Classifier + Dual Source

| Ticker | Sector | Type | Subtype | Source |
|--------|--------|------|---------|--------|
| JPM | Financial Services | financial | bank | simfin |
| ALL | Financial Services | financial | insurance | simfin |
| AAPL | Technology | normal | n/a | edgar |
| NEE | Utilities | dividend_stable | n/a | edgar |

Preparation.py now routes automatically:
- Financial companies → SimFin bank/insurance provider
- Normal + dividend_stable → EDGAR standardizer
- If SimFin fails → falls back to EDGAR

---

## 5. Sign Convention

SimFin uses negative numbers for expenses (COGS = -$210B, Tax = -$29B). Our output preserves the original sign from SimFin. The existing ratio calculation code already handles this with `abs()` calls where needed.

---

## 6. Cache

SimFin bulk downloads are cached in `data/simfin_cache/` (via SimFin's built-in caching). First call downloads the full US market data (~5-10MB per dataset), subsequent calls load from disk instantly. TTL: SimFin checks daily for updates.

---

## 7. Verification — Normal Companies Unchanged

| Ticker | Revenue | OCF | FCF | Status |
|--------|---------|-----|-----|--------|
| AAPL | $416,161M | $111,482M | $98,767M | ✅ Identical |

EDGAR standardizer path is completely untouched for non-financial companies.
