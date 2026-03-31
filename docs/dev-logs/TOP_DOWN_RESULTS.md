# Top-Down Standardizer — Results

**Date:** 2026-03-26

---

## 1. 10-Ticker Summary (Latest Year)

| Ticker | Revenue | OCF | FCF | NI | D&A | EPS | Dividends | XC Fail | L4 | Template |
|--------|---------|-----|-----|-----|-----|-----|-----------|---------|-----|----------|
| AAPL | $416,161M | $111,482M | $98,767M | $112,010M | $11,698M | $7.46 | -$15,421M | 0 | 0 | 56/62 |
| MSFT | $281,724M | $136,162M | $71,611M | $101,832M | $34,153M | $13.64 | -$24,082M | 0 | 0 | 58/62 |
| GOOG | $402,836M | $164,713M | $73,266M | $132,170M | $21,136M | $10.81 | -$10,049M | 0 | 0 | 50/62 |
| AMZN | $716,924M | $139,514M | $7,695M | $77,670M | $65,756M | $7.17 | — | 11 | 0 | 52/62 |
| XOM | $332,238M | $51,970M | $23,612M | $28,844M | $25,993M | $6.70 | -$17,231M | 5 | 0 | 45/62 |
| WMT | $706,413M | $41,565M | $14,923M | $21,893M | $14,203M | $2.73 | -$7,507M | 3 | 0 | 50/62 |
| PG | $84,284M | $17,817M | $14,044M | $15,974M | $2,847M | $6.51 | -$9,872M | 0 | 0 | 49/62 |
| JNJ | $94,193M | $24,530M | $19,698M | $26,804M | $7,503M | $11.03 | -$12,381M | 0 | 0 | 55/62 |
| META | $200,966M | $115,800M | $46,109M | $60,458M | $18,616M | $23.49 | -$5,324M | 0 | 0 | 50/62 |
| NVDA | $215,938M | $102,718M | $96,676M | $120,067M | $2,843M | $4.90 | -$974M | 0 | 0 | 55/62 |

**Key achievement: Layer 4 items = 0 for ALL 10 companies.** The top-down approach only outputs template-defined lines — no catch-all buckets.

## 2. GOOG Ratios (2015–2025)

```
Ratio                     2015    2016    2017    2018    2019    2020    2021    2022    2023    2024    2025
revenue_growth              —   20.4%   22.8%   23.4%   18.3%   12.8%   41.2%    9.8%    8.7%   13.9%   15.1%
ebitda_margin               —      —      —      —      —      —   34.5%   31.2%   31.3%   36.5%   37.3%
gross_margin             62.4%   61.1%   58.9%   56.5%   55.6%   53.6%   56.9%   55.4%   56.6%   58.2%   59.7%
ebit_margin              25.8%   26.3%   23.6%   20.1%   21.1%   22.6%   30.6%   26.5%   27.4%   32.1%   32.0%
net_margin               21.8%   21.6%   11.4%   22.5%   21.2%   22.1%   29.5%   21.2%   24.0%   28.6%   32.8%
fcf_margin               22.2%   28.6%   21.6%   16.7%   19.1%   23.5%   26.0%   21.2%   22.6%   20.8%   18.2%
effective_tax_rate       16.8%   19.3%   53.4%   12.0%      —      —      —   15.9%   13.9%   16.4%   16.8%
capex_pct                13.3%   11.3%   11.9%   18.4%   14.5%   12.2%    9.6%   11.1%   10.5%   15.0%   22.7%
da_pct                      —      —      —      —      —      —    4.0%    4.8%    3.9%    4.4%    5.2%
debt_ebitda                 —      —      —      —      —      —    0.2x    0.2x    0.1x    0.1x    0.3x
roic                        —   14.7%    8.4%   14.7%   14.4%   15.5%   25.3%   25.3%   26.8%   30.1%   24.9%
roe                         —   14.0%    8.3%   17.3%   17.0%   18.1%   30.2%   23.4%   26.0%   30.8%   31.8%
fcf_conversion          101.7%  132.6%  188.8%   74.3%   90.2%  106.4%   88.1%  100.1%   94.2%   72.7%   55.4%

Coverage: 136/165 (82.4%)
```

**GOOG EBITDA 2015–2020 gap persists.** EDGAR XBRL for GOOG doesn't include D&A before 2021 — the concept `Depreciation` only has values for 2021+. This is an EDGAR data issue, not a mapping issue.

## 3. OCF/FCF Verification

| Ticker | V3 OCF | V2 OCF | Match? | V3 FCF | V2 FCF | Match? |
|--------|--------|--------|--------|--------|--------|--------|
| AAPL | $111,482M | $111,482M | ✅ | $98,767M | $98,767M | ✅ |
| MSFT | $136,162M | $136,162M | ✅ | $71,611M | $71,611M | ✅ |
| GOOG | $164,713M | $164,713M | ✅ | $73,266M | $73,266M | ✅ |
| XOM | $51,970M | $51,970M | ✅ | $23,612M | $23,612M | ✅ |

All OCF/FCF values identical to V2.

## 4. Cross-Checks

| Check | Passing | Failing | Notes |
|-------|---------|---------|-------|
| Revenue - COGS = GP | AAPL, MSFT, GOOG, PG, JNJ, META, NVDA | — | XOM/WMT/AMZN don't have standard COGS |
| Assets = L + E | AAPL, MSFT, GOOG, PG, JNJ, META, NVDA | XOM (5yr), AMZN (11yr), WMT (3yr) | Minority interest / total_equity definition |
| OCF - CapEx = FCF | All 10 | — | ✅ |
| EBITDA = EBIT + D&A | All with D&A | — | ✅ |

## 5. AAPL Improvement vs V2

| Ratio | V2 (2015) | V3 (2015) | New? |
|-------|-----------|-----------|------|
| dso | — | 21d | ✅ BS delta |
| roic | — | 49.1% | ✅ |
| debt_ebitda | — | 0.1x | ✅ |

AAPL coverage improved: **93.3% → 96.7%** (6 fewer gaps).

## 6. Source Audit — GOOG 2025 vs 2015

| Line | 2025 Value | 2025 Source | 2015 Value | 2015 Source |
|------|-----------|-------------|-----------|-------------|
| revenue | $402,836M | concept | $74,989M | concept |
| cogs | $170,720M | concept | $28,164M | concept |
| gross_profit | $232,116M | concept | $46,825M | concept |
| sga | $50,175M | combination | $18,010M | concept |
| rd | $53,063M | concept | $12,282M | concept |
| ebit | $128,878M | concept | $19,360M | concept |
| ebitda | $150,014M | cross_stmt | — | — |
| pretax_income | $152,780M | concept | $22,889M | concept |
| tax_provision | $20,610M | concept | $3,303M | concept |
| net_income | $132,170M | concept | $16,348M | concept |
| diluted_eps | $10.81 | keyword | — | — |
| diluted_shares | 12,226M | concept | 14,802M | concept |
| depreciation_amortization | $21,136M | concept | — | — (not in XBRL) |
| operating_cash_flow | $164,713M | sc_subtotal | $26,572M | sc_subtotal |
| capital_expenditure | -$91,448M | concept | -$9,950M | concept |
| free_cash_flow | $73,266M | derived | $16,622M | derived |
| dividends_paid | -$10,049M | keyword | — | — |
| stock_repurchases | -$36,858M | concept | — | — |

## 7. Architecture Summary

**Old (V1/V2 — bottom-up):** For each row in EDGAR → find matching key. Result: many unmapped rows land in "other" buckets.

**New (V3 — top-down):** For each template line → search EDGAR rows for it. Result: only template-defined lines in output. Zero "other" items. If a line can't be found, it's simply absent (not misclassified).

### Files

| File | Purpose | Lines |
|------|---------|-------|
| `lib/data/template.py` | Template + search rules (35 lines, 45 rules) | ~650 |
| `lib/data/standardizer.py` | Search engine (5-pass) | ~350 |
| `lib/data/concept_maps.py` | Raw concept → key lookup (retained for reference) | ~1530 |
| `lib/data/standardizer_utils.py` | Cross-checks (retained) | ~220 |
| `lib/data/standardizer_v2.py` | Old v2 (backup, can delete) | ~235 |

### Search Engine Flow

```
Pass 1: Direct lookups (concept + keyword)    → finds ~85% of lines
Pass 2: Combinations (S&M + G&A → SGA)        → finds ~3%
Pass 3: Derived (EBITDA = EBIT + D&A, etc.)   → finds ~8%
Pass 4: Cross-statement (D&A from CF → EBITDA) → finds ~2%
Pass 5: BS delta (change in receivables)       → finds ~2%
```
