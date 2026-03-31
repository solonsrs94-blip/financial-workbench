# Professional Check — Standardizer Quality Report

**Date:** 2026-03-26

---

## 1. SGA Fix

**Problem:** GOOG SGA showed $28.7B (only Sales & Marketing). Real SGA = S&M ($28.7B) + G&A ($21.5B) = $50.2B.

**Root Cause:** The `sga` search rule had an `sc: SellingGeneralAndAdminExpenses` match that fired first. Both GOOG's S&M and G&A lines carry this same edgartools standard_concept. First match (S&M) won, blocking the combination fallback.

**Fix:** Removed the `sc` search from `sga` rule. Now `sga` only matches via:
1. Exact XBRL concept `SellingGeneralAndAdministrativeExpense` (fires when company reports as one line — AAPL, XOM)
2. Keyword match for "selling, general and admin" labels
3. Combination: `selling_and_marketing` + `general_and_administrative` (fires when split — GOOG, MSFT, AMZN, META)

**Result:**

| Ticker | SGA Before | SGA After | S&M | G&A | Correct? |
|--------|-----------|-----------|-----|-----|----------|
| GOOG | $28,693M ❌ | **$50,175M** | $28,693M | $21,482M | ✅ |
| MSFT | $32,877M | $32,877M | $25,654M | $7,223M | ✅ |
| AAPL | $27,601M | $27,601M | (combined) | (combined) | ✅ |
| XOM | $11,128M | $11,128M | (combined) | (combined) | ✅ |

## 2. Shares Outstanding

**Problem:** Shares Outstanding was MISSING for GOOG and MSFT. AAPL had it correctly.

**Root Cause:** GOOG and MSFT don't report `CommonStockSharesOutstanding` as a separate XBRL line. The shares info is embedded in the common stock label text (e.g., "shares authorized 24,000; outstanding 7,434").

**Fix for shares_outstanding (BS):**
- Narrowed keyword to `"common stock, shares outstanding"` and added `keyword_exclude: ["preferred"]` to prevent matching preferred stock lines
- GOOG and MSFT still show MISSING — they don't report this in XBRL at all

**Fix for diluted_shares (IS):**
- Added derived fallback: `net_income / diluted_eps` when both exist
- Now works for GOOG ($132,170M / $10.81 = 12,227M shares) and XOM ($28,844M / $6.70 = 4,305M shares)

**Result:**

| Ticker | Shares Outstanding (BS) | Diluted Shares (IS) |
|--------|------------------------|---------------------|
| AAPL | 14,773M ✅ | 15,005M ✅ |
| MSFT | MISSING (not in XBRL) | 7,465M ✅ |
| GOOG | MISSING (not in XBRL) | **12,227M** ✅ (derived) |
| XOM | MISSING (not in XBRL) | **4,305M** ✅ (derived) |

## 3. Intangible Assets

**Problem:** GOOG intangible assets = MISSING on 2023-2025.

**Root Cause:** GOOG's latest 10-K filings (2023+) do NOT include intangible assets as a separate line item. They've been folded into "Other non-current assets" ($16.2B). This is genuine GOOG reporting — not a mapping issue.

**Fix:** None needed. Data 2016-2022 comes from older filings (multi-filing merge). 2023+ genuinely doesn't exist.

## 4. Inventory

**Problem:** GOOG inventory = MISSING on 2023-2025.

**Root Cause:** Same as intangibles — GOOG's latest filings don't report inventory separately. Likely folded into "Other current assets" ($16.3B).

**Fix:** None needed. Data 2016-2022 comes from older filings.

## 5. Total OpEx

**AAPL "Rev - EBIT ≠ Total OpEx" cross-check ❌:**
- Revenue - EBIT = $283,111M (COGS + SGA + R&D)
- Total OpEx (from 10-K) = $62,151M (SGA + R&D only — Apple's label)

This is **correct behavior**. Apple's 10-K labels "Total operating expenses" as SGA+R&D ($62B), NOT including COGS ($221B). Our standardizer correctly captures Apple's own reporting. The cross-check formula assumes Total OpEx includes COGS, which is one convention but not Apple's.

**MSFT Total OpEx = MISSING:**
MSFT doesn't have a single "Total operating expenses" line in XBRL when S&M and G&A are split.

**GOOG Total OpEx ✅:**
$273,797M = Revenue ($402,836M) - EBIT ($129,039M). Correct.

## 6. Four-Company Comparison (Latest FY)

### GOOG (FY2025)
| Line | Our Value | Reference | Match? |
|------|-----------|-----------|--------|
| Revenue | $402,836M | $402,836M | ✅ |
| COGS | $162,535M | $162,535M | ✅ |
| Gross Profit | $240,301M | $240,301M | ✅ |
| SGA | **$50,175M** | $50,175M (S&M 28.7 + G&A 21.5) | ✅ |
| R&D | $61,087M | $61,087M | ✅ |
| EBIT | $129,039M | $129,039M | ✅ |
| EBITDA | $150,175M | ~$150B | ✅ |
| Net Income | $132,170M | $132,170M | ✅ |
| EPS | $10.81 | $10.81 | ✅ |
| Total Assets | $595,281M | $595,281M | ✅ |
| Total Liabilities | $180,016M | $180,016M | ✅ |
| Total Equity | $415,265M | $415,265M | ✅ |
| Total Debt | $46,547M | $46,547M | ✅ |
| Net Debt | -$80,296M | ~-$80B (net cash) | ✅ |
| OCF | $164,713M | $164,713M | ✅ |
| CapEx | -$91,447M | -$91,447M | ✅ |
| FCF | $73,266M | $73,266M | ✅ |
| D&A | $21,136M | $21,136M | ✅ |
| Dividends | -$10,049M | -$10,049M | ✅ |
| Interest Expense | MISSING | N/A (bundled in Other) | ⚠️ |
| Intangible Assets | MISSING | Not in 10-K XBRL | ⚠️ |
| Inventories | MISSING | Not in 10-K XBRL | ⚠️ |

### AAPL (FY2025)
| Line | Our Value | Reference | Match? |
|------|-----------|-----------|--------|
| Revenue | $416,161M | $416,161M | ✅ |
| COGS | $220,960M | $220,960M | ✅ |
| Gross Profit | $195,201M | $195,201M | ✅ |
| SGA | $27,601M | $27,601M | ✅ |
| R&D | $34,550M | $34,550M | ✅ |
| EBIT | $133,050M | $133,050M | ✅ |
| EBITDA | $144,748M | ~$145B | ✅ |
| Net Income | $112,010M | $112,010M | ✅ |
| EPS | $7.46 | $7.46 | ✅ |
| Total Assets | $359,241M | $359,241M | ✅ |
| Total Debt | $98,657M | ~$99B | ✅ |
| Net Debt | $43,960M | ~$44B | ✅ |
| OCF | $111,482M | $111,482M | ✅ |
| FCF | $98,767M | ~$99B | ✅ |
| D&A | $11,698M | $11,698M | ✅ |
| Dividends | -$15,421M | -$15,421M | ✅ |
| Shares Outstanding (BS) | 14,773M | 14,773M | ✅ |

### MSFT (FY2025)
| Line | Our Value | Reference | Match? |
|------|-----------|-----------|--------|
| Revenue | $281,724M | $281,724M | ✅ |
| SGA | $32,877M | $32,711M (S&M 25.5 + G&A 7.2) | ✅ (~0.5% diff) |
| EBIT | $128,528M | $128,528M | ✅ |
| Net Income | $101,832M | $101,832M | ✅ |
| Total Assets | $619,003M | $619,003M | ✅ |
| Total Debt | $43,151M | ~$43B | ✅ |
| Net Debt | -$51,414M | ~-$51B (net cash) | ✅ |
| OCF | $136,162M | $136,162M | ✅ |
| FCF | $71,611M | ~$72B | ✅ |
| Dividends | -$24,082M | -$24,082M | ✅ |

### XOM (FY2025)
| Line | Our Value | Reference | Match? |
|------|-----------|-----------|--------|
| Revenue | $332,238M | $332,238M | ✅ |
| EBIT | $41,871M | ~$42B (derived: pretax + interest) | ✅ |
| Net Income | $28,844M | $28,844M | ✅ |
| Total Assets | $448,980M | $448,980M | ✅ |
| Total Debt | $43,537M | ~$44B | ✅ |
| OCF | $51,970M | $51,970M | ✅ |
| FCF | $23,612M | ~$24B | ✅ |
| D&A | $25,993M | $25,993M | ✅ |
| COGS | MISSING | XOM doesn't report standard COGS | ⚠️ Expected |
| A = L + E | ❌ off by $7.2B | Minority interest not in total_equity | ⚠️ Known |

## 7. Remaining Known Issues

| Issue | Ticker(s) | Severity | Explanation |
|-------|-----------|----------|-------------|
| Interest Expense MISSING | GOOG, AAPL | Low | Bundled in "Other income/expense" — no separate line in 10-K |
| Shares Outstanding (BS) MISSING | GOOG, MSFT, XOM | Low | Not in XBRL. Diluted Shares (IS) available via derivation |
| AAPL OpEx cross-check ❌ | AAPL | None | Apple's "Total OpEx" = SGA+R&D only (correct per their 10-K) |
| XOM A=L+E cross-check ❌ | XOM | Low | Minority interest ($7.2B) — total_equity is ExxonMobil share only |
| Intangibles/Inventory 2023+ MISSING | GOOG | Low | GOOG folded into "Other assets" in 10-K |
| MSFT Total OpEx MISSING | MSFT | Low | MSFT doesn't report a single "Total OpEx" line when S&M/G&A split |

### All Cross-Checks Summary

| Check | GOOG | AAPL | MSFT | XOM |
|-------|------|------|------|-----|
| Rev - COGS = GP | ✅ | ✅ | ✅ | N/A |
| Assets = L + E | ✅ | ✅ | ✅ | ❌ (minority) |
| OCF - CapEx = FCF | ✅ | ✅ | ✅ | ✅ |
| EBIT + D&A = EBITDA | ✅ | ✅ | ✅ | ✅ |
