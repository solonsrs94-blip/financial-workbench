# EDGAR Multi-Filing Merge Fix

**Date:** 2026-03-30
**Files changed:** `lib/data/providers/edgar_provider.py`, `lib/data/standardizer.py`

---

## 1. How the New Merge Works

### Old Logic (broken)
1. Process filings newest→oldest
2. Mark years as "seen" when first encountered
3. **Skip entire filing** if all its years are already "seen"
4. Result: old concepts for already-seen years are lost

### New Logic (fixed)
1. **Phase 1**: Parse ALL filings (newest→oldest), extract every row with its year, concept, label, value, and filing index
2. **Phase 2**: For each year, collect all unique rows across all filings. When the same row (by sc+label) appears in multiple filings, prefer the **newest filing** (lowest filing_idx)
3. Rows that only exist in older filings (old concepts) are **added** — they fill gaps that newer filings don't have

Key difference: **no year is ever "seen" and skipped**. Every filing contributes all its rows. Deduplication happens at the row level, not the filing level.

### Also Fixed: sc_subtotal allowlist
Changed from blocklist ("skip if label contains dividend/debt/etc") to **allowlist** ("accept if label contains 'net cash'/'total'/'cash provided'/etc"). This fixed AMZN where "Other assets" was incorrectly matching as OCF subtotal.

---

## 2. META CapEx / FCF / Acquisitions

### CapEx — FIXED ✅

| Year | Before | After | Source |
|------|--------|-------|--------|
| 2014 | MISSING | -$1,831M | Primary filing (2015-01-29) |
| 2015 | MISSING | -$2,523M | Primary filing (2016-02-01) |
| 2016 | MISSING | -$4,491M | Primary filing (2017-02-02) |
| 2017 | MISSING | -$6,733M | Primary filing (2018-02-01) |
| 2018 | -$13,915M | -$13,915M | Unchanged |
| 2019–2025 | Present | Present | Unchanged |

### FCF — FIXED ✅

| Year | Before | After |
|------|--------|-------|
| 2014 | MISSING | $22,397M |
| 2015 | MISSING | $5,495M |
| 2016 | MISSING | $11,617M |
| 2017 | MISSING | $17,483M |

### Acquisitions
WhatsApp acquisition ($19B, 2014) — not verified separately. The merge captures rows from 2014 filing but WhatsApp may be under a custom META concept.

---

## 3. AMZN OCF Bug — FIXED ✅

AMZN had `operating_cash_flow` = -$15.6B (wrong — label "Other assets") because `sc_subtotal` logic used a blocklist that didn't include "other". Fixed by switching to allowlist.

| | Before | After |
|---|--------|-------|
| OCF | -$15,632M ❌ | $139,514M ✅ |
| FCF | -$147,451M ❌ | $7,695M ✅ |

---

## 4. Broad Test Results (10 Companies)

| Ticker | Years | Coverage | Gaps | OCF | FCF | CapEx |
|--------|-------|----------|------|-----|-----|-------|
| META | 12 | 175/180 (97%) | 5 | $115,800M | $46,109M | -$69,691M |
| GOOG | 11 | 160/165 (97%) | 5 | $164,713M | $73,266M | -$91,447M |
| AAPL | 12 | 175/180 (97%) | 5 | $111,482M | $98,767M | -$12,715M |
| MSFT | 12 | 175/180 (97%) | 5 | $136,162M | $71,611M | -$64,551M |
| AMZN | 12 | 171/180 (95%) | 9 | $139,514M | $7,695M | -$131,819M |
| XOM | 12 | 155/180 (86%) | 25 | $51,970M | $23,612M | -$28,358M |
| WMT | 12 | 175/180 (97%) | 5 | $41,565M | $14,923M | -$26,642M |
| INTC | 12 | 171/180 (95%) | 9 | $9,697M | -$4,949M | -$14,646M |
| NKE | 12 | 175/180 (97%) | 5 | $3,698M | $3,268M | -$430M |
| LLY | 12 | 174/180 (97%) | 6 | $16,813M | $8,972M | -$7,841M |

**Average coverage: 95.3%**

### Remaining gaps (5 per company = structural)
- revenue_growth on first year (no prior year)
- debt_ebitda on first year (no prior BS)
- dso on first 1-2 years (no prior AR)
- dpo on first year (no prior AP)
- roic on first 1-2 years (no prior invested capital)

---

## 5. Values That Changed

| Ticker | What Changed | Before | After | Why |
|--------|-------------|--------|-------|-----|
| AMZN | OCF 2025 | -$15,632M | $139,514M | sc_subtotal allowlist fix |
| AMZN | FCF 2025 | -$147,451M | $7,695M | Derived from fixed OCF |
| META | CapEx 2014-2017 | MISSING | -$1.8B to -$6.7B | Old filings now contribute |
| META | FCF 2014-2017 | MISSING | $5.5B to $22.4B | Derived from new CapEx |

No other latest-year values changed for any company. AAPL, MSFT, GOOG, XOM, WMT, INTC, NKE, LLY are all identical to before.

---

## 6. Summary

Two changes made:
1. **edgar_provider.py**: Complete rewrite of `fetch_xbrl_statements` merge logic. Now processes ALL filings and merges at row level instead of year level.
2. **standardizer.py**: Changed `sc_subtotal` from blocklist to allowlist to prevent individual items from being treated as subtotals.
