# Flag Detection Results

**Date:** 2026-03-26
**Tickers:** AAPL, GOOG, XOM, WMT
**Method:** `detect_flags()` called identically to `dcf_tab.py`

---

## AAPL — Apple Inc.

**Sector:** Technology | **Years:** 2014–2025

### Summary

| Metric | Count |
|--------|-------|
| **Total flags** | **24** |
| High severity | 1 |
| Medium severity | 11 |
| Low severity | 12 |

| Category | Count |
|----------|-------|
| quality | 15 |
| one_off | 8 |
| investment_cycle | 0 |
| m_and_a | 0 |
| tax | 0 |

### All Flags

| # | Year | Severity | Category | What | Why | Action | Line Item | Impact ($M) |
|---|------|----------|----------|------|-----|--------|-----------|-------------|
| 1 | 2017 | **high** | one_off | Total debt jumped 1327% ($8.1B -> $115.7B) | Major debt increase -- likely debt-funded acquisition, recapitalization, or leveraged buyback | Check if debt increase is permanent (new capital structure) or temporary. Affects WACC and cost of debt. | total_debt | 107,575 |
| 2 | 2014 | medium | quality | Gross Margin 38.6% is outside Technology typical range (50-85%) | May indicate business model difference, accounting, or data issue | Verify GM is correct. If real, understand why it differs from peers. | gross_profit | — |
| 3 | 2014 | medium | one_off | Known event: 7:1 stock split | Share count 7x — check per-share metrics | Adjust for 7:1 stock split impact when normalizing. | ebit | — |
| 4 | 2015 | low | one_off | Diluted shares decreased 5.4% | Aggressive share buyback program | Consider whether buyback pace is sustainable. | diluted_shares | — |
| 5 | 2016 | low | one_off | Diluted shares decreased 5.1% | Aggressive share buyback program | Consider whether buyback pace is sustainable. | diluted_shares | — |
| 6 | 2016 | medium | quality | Gross Margin 39.1% is outside Technology typical range (50-85%) | May indicate business model difference, accounting, or data issue | Verify GM is correct. If real, understand why it differs from peers. | gross_profit | — |
| 7 | 2017 | medium | quality | Gross Margin 38.5% is outside Technology typical range (50-85%) | May indicate business model difference, accounting, or data issue | Verify GM is correct. If real, understand why it differs from peers. | gross_profit | — |
| 8 | 2018 | medium | quality | Gross Margin 38.3% is outside Technology typical range (50-85%) | May indicate business model difference, accounting, or data issue | Verify GM is correct. If real, understand why it differs from peers. | gross_profit | — |
| 9 | 2019 | low | one_off | Diluted shares decreased 7.0% | Aggressive share buyback program | Consider whether buyback pace is sustainable. | diluted_shares | — |
| 10 | 2019 | medium | quality | Revenue Growth reversed after 3yr acceleration | Multi-year improving trend broke — investigate if structural or temporary | Determine if Revenue Growth decline is one-off or start of new trend. | revenue | — |
| 11 | 2019 | medium | quality | Gross Margin 37.8% is outside Technology typical range (50-85%) | May indicate business model difference, accounting, or data issue | Verify GM is correct. If real, understand why it differs from peers. | gross_profit | — |
| 12 | 2020 | low | one_off | Diluted shares decreased 5.7% | Aggressive share buyback program | Consider whether buyback pace is sustainable. | diluted_shares | — |
| 13 | 2020 | medium | quality | Gross Margin 38.2% is outside Technology typical range (50-85%) | May indicate business model difference, accounting, or data issue | Verify GM is correct. If real, understand why it differs from peers. | gross_profit | — |
| 14 | 2020 | medium | one_off | Known event: 4:1 stock split | Share count 4x — check per-share metrics | Adjust for 4:1 stock split impact when normalizing. | ebit | — |
| 15 | 2021 | medium | one_off | EBIT Margin jumped 5.6pp (24.1% -> 29.8%) | Revenue grew 33% with operating leverage | Consider removing $20.6B one-off gain from 2021 EBIT. Check 10-K. | ebit | 20,614 |
| 16 | 2021 | low | quality | EBIT Margin reversed after 3yr decline (+5.6pp) | Multi-year declining trend broke — possible turnaround | Positive signal if sustainable. Check if driven by one-off or restructuring. | ebit | — |
| 17 | 2021 | medium | quality | Cash Conversion Cycle lengthened 28 days over 4 years | Company needs increasingly more working capital per $ of revenue | Model higher NWC in projections. Check if DSO, DIO, or DPO is the driver. | accounts_receivable | — |
| 18 | 2022 | medium | quality | Revenue Growth reversed after 3yr acceleration | Multi-year improving trend broke — investigate if structural or temporary | Determine if Revenue Growth decline is one-off or start of new trend. | revenue | — |
| 19 | 2024 | low | quality | Revenue Growth reversed after 3yr deceleration | Multi-year declining trend broke — possible turnaround | Positive signal if sustainable. Check if driven by one-off or restructuring. | revenue | — |
| 20 | 2025 | low | quality | Net Margin reversed after 3yr decline (+2.9pp) | Multi-year declining trend broke — possible turnaround | Positive signal if sustainable. Check if driven by one-off or restructuring. | net | — |
| 21 | 2025 | low | quality | Gross Margin at 100th percentile of own history (46.9% vs avg 41.1%) | Margins at historical high — may not be sustainable long-term | Consider mean-reversion in terminal year. Historical range: 37.8%-46.9% | gross_margin | — |
| 22 | 2025 | low | quality | EBIT Margin at 100th percentile of own history (32.0% vs avg 28.5%) | Margins at historical high — may not be sustainable long-term | Consider mean-reversion in terminal year. Historical range: 24.1%-32.0% | ebit_margin | — |
| 23 | 2025 | low | quality | Net Margin at 100th percentile of own history (26.9% vs avg 23.2%) | Margins at historical high — may not be sustainable long-term | Consider mean-reversion in terminal year. Historical range: 20.9%-26.9% | net_margin | — |
| 24 | 2025 | low | quality | Capital allocation: Invest — CapEx is 100% of capital deployed (3yr) | Company in investment/growth mode — building capacity | Expect elevated CapEx to continue. Model gradual normalization. | capital_expenditure | — |

---

## GOOG — Alphabet Inc.

**Sector:** Technology | **Years:** 2015–2025

### Summary

| Metric | Count |
|--------|-------|
| **Total flags** | **30** |
| High severity | 11 |
| Medium severity | 12 |
| Low severity | 7 |

| Category | Count |
|----------|-------|
| m_and_a | 7 |
| one_off | 10 |
| quality | 9 |
| tax | 1 |
| investment_cycle | 2 |
| accounting_change | 0 |

### All Flags

| # | Year | Severity | Category | What | Why | Action | Line Item | Impact ($M) |
|---|------|----------|----------|------|-----|--------|-----------|-------------|
| 1 | 2016 | **high** | m_and_a | Acquisition fingerprint detected (3 signals: Revenue +20%, Acquisition spend $1.0B) | Multiple balance sheet and income signals point to material acquisition | Calculate organic growth excluding acquisition. Check 10-K for deal details. | revenue | — |
| 2 | 2017 | **high** | one_off | Net Margin dropped 10.2pp (21.6% -> 11.4%) | Revenue grew 23% but margin dropped -- possible M&A integration costs | Consider adding back $11.3B to 2017 NET_INCOME if one-off. Check 10-K. | net_income | 11,257 |
| 3 | 2017 | **high** | m_and_a | Acquisition fingerprint detected (3 signals: Revenue +23%, Acquisition spend $0.3B) | Multiple balance sheet and income signals point to material acquisition | Calculate organic growth excluding acquisition. Check 10-K for deal details. | revenue | — |
| 4 | 2018 | **high** | one_off | Net Margin jumped 11.0pp (11.4% -> 22.5%) | Revenue grew 23% with operating leverage | Consider removing $15.1B one-off gain from 2018 NET_INCOME. Check 10-K. | net_income | 15,108 |
| 5 | 2018 | **high** | m_and_a | Acquisition fingerprint detected (3 signals: Revenue +23%, Acquisition spend $1.5B) | Multiple balance sheet and income signals point to material acquisition | Calculate organic growth excluding acquisition. Check 10-K for deal details. | revenue | — |
| 6 | 2020 | **high** | one_off | Total debt jumped 206% ($4.6B -> $13.9B) | Major debt increase -- likely debt-funded acquisition, recapitalization, or leveraged buyback | Check if debt increase is permanent (new capital structure) or temporary. Affects WACC and cost of debt. | total_debt | 9,378 |
| 7 | 2020 | **high** | m_and_a | Acquisition fingerprint detected (3 signals: Debt +206%, Acquisition spend $0.7B) | Multiple balance sheet and income signals point to material acquisition | Calculate organic growth excluding acquisition. Check 10-K for deal details. | revenue | — |
| 8 | 2021 | **high** | m_and_a | Acquisition fingerprint detected (3 signals: Revenue +41%, Acquisition spend $2.6B) | Multiple balance sheet and income signals point to material acquisition | Calculate organic growth excluding acquisition. Check 10-K for deal details. | revenue | — |
| 9 | 2022 | **high** | m_and_a | Acquisition fingerprint detected (4 signals: Goodwill +26%, Acquisition spend $7.0B) | Multiple balance sheet and income signals point to material acquisition | Calculate organic growth excluding acquisition. Check 10-K for deal details. | revenue | — |
| 10 | 2025 | **high** | one_off | Total debt jumped 328% ($10.9B -> $46.5B) | Major debt increase -- likely debt-funded acquisition, recapitalization, or leveraged buyback | Check if debt increase is permanent (new capital structure) or temporary. Affects WACC and cost of debt. | total_debt | 35,664 |
| 11 | 2025 | **high** | m_and_a | Acquisition fingerprint detected (3 signals: Debt +328%, Acquisition spend $1.6B) | Multiple balance sheet and income signals point to material acquisition | Calculate organic growth excluding acquisition. Check 10-K for deal details. | revenue | — |
| 12 | 2015 | medium | one_off | Known event: Alphabet restructuring | Segment reporting changed | Adjust for Alphabet restructuring impact when normalizing. | ebit | — |
| 13 | 2017 | medium | tax | Effective tax rate 53.4% | TCJA Tax Reform (Dec 2017) -- one-time deemed repatriation tax | Use normalized post-TCJA rate (~21-25%) for projections. | tax_provision | — |
| 14 | 2017 | medium | one_off | Known event: EU antitrust fine €2.4B | One-off charge on EBIT | Adjust for EU antitrust fine €2.4B impact when normalizing. | ebit | — |
| 15 | 2018 | medium | investment_cycle | CapEx jumped to 18.4% of revenue (from 11.9%) | Investment cycle -- new capacity, data centers, or expansion | Determine if temporary (normalize) or structural (new baseline). | capital_expenditure | — |
| 16 | 2018 | low | quality | Net Margin reversed after 3yr decline (+11.0pp) | Multi-year declining trend broke — possible turnaround | Positive signal if sustainable. Check if driven by one-off or restructuring. | net | — |
| 17 | 2018 | medium | one_off | Known event: EU antitrust fine €4.3B | One-off charge on EBIT | Adjust for EU antitrust fine €4.3B impact when normalizing. | ebit | — |
| 18 | 2019 | medium | quality | Revenue Growth reversed after 3yr acceleration | Multi-year improving trend broke — investigate if structural or temporary | Determine if Revenue Growth decline is one-off or start of new trend. | revenue | — |
| 19 | 2019 | medium | one_off | Known event: EU antitrust fine €1.5B | One-off charge on EBIT | Adjust for EU antitrust fine €1.5B impact when normalizing. | ebit | — |
| 20 | 2021 | medium | one_off | EBIT Margin jumped 8.0pp (22.6% -> 30.6%) | Revenue grew 41% with operating leverage | Consider removing $20.5B one-off gain from 2021 EBIT. Check 10-K. | ebit | 20,526 |
| 21 | 2021 | medium | one_off | Net Margin jumped 7.4pp (22.1% -> 29.5%) | Revenue grew 41% with operating leverage | Consider removing $19.2B one-off gain from 2021 NET_INCOME. Check 10-K. | net_income | 19,193 |
| 22 | 2021 | low | quality | Gross Margin reversed after 3yr decline (+3.4pp) | Multi-year declining trend broke — possible turnaround | Positive signal if sustainable. Check if driven by one-off or restructuring. | gross | — |
| 23 | 2022 | medium | one_off | Net Margin dropped 8.3pp (29.5% -> 21.2%) | Net Margin changed significantly -- review 10-K for details | Consider adding back $23.5B to 2022 NET_INCOME if one-off. Check 10-K. | net_income | 23,498 |
| 24 | 2022 | medium | quality | EBIT Margin reversed after 3yr improvement (-4.1pp) | Multi-year improving trend broke — investigate if structural or temporary | Determine if EBIT Margin decline is one-off or start of new trend. | ebit | — |
| 25 | 2022 | medium | one_off | Known event: 20:1 stock split | Share count 20x | Adjust for 20:1 stock split impact when normalizing. | ebit | — |
| 26 | 2024 | low | quality | Revenue Growth reversed after 3yr deceleration | Multi-year declining trend broke — possible turnaround | Positive signal if sustainable. Check if driven by one-off or restructuring. | revenue | — |
| 27 | 2025 | medium | investment_cycle | CapEx jumped to 22.7% of revenue (from 15.0%) | Investment cycle -- new capacity, data centers, or expansion | Determine if temporary (normalize) or structural (new baseline). | capital_expenditure | — |
| 28 | 2025 | low | quality | EBIT Margin at 90th percentile of own history (32.0% vs avg 26.2%) | Margins at historical high — may not be sustainable long-term | Consider mean-reversion in terminal year. Historical range: 20.1%-32.1% | ebit_margin | — |
| 29 | 2025 | low | quality | Net Margin at 100th percentile of own history (32.8% vs avg 23.3%) | Margins at historical high — may not be sustainable long-term | Consider mean-reversion in terminal year. Historical range: 11.4%-32.8% | net_margin | — |
| 30 | 2025 | low | quality | Capital allocation: Invest — CapEx is 97% of capital deployed (3yr) | Company in investment/growth mode — building capacity | Expect elevated CapEx to continue. Model gradual normalization. | capital_expenditure | — |

---

## XOM — ExxonMobil

**Sector:** Energy | **Years:** 2014–2025

### Summary

| Metric | Count |
|--------|-------|
| **Total flags** | **2** |
| High severity | 0 |
| Medium severity | 1 |
| Low severity | 1 |

| Category | Count |
|----------|-------|
| one_off | 1 |
| quality | 1 |

### All Flags

| # | Year | Severity | Category | What | Why | Action | Line Item | Impact ($M) |
|---|------|----------|----------|------|-----|--------|-----------|-------------|
| 1 | 2024 | medium | one_off | Known event: Pioneer Natural Resources acquisition $60B | Major M&A | Adjust for Pioneer Natural Resources acquisition $60B impact when normalizing. | ebit | — |
| 2 | 2025 | low | quality | Capital allocation: Invest — CapEx is 100% of capital deployed (3yr) | Company in investment/growth mode — building capacity | Expect elevated CapEx to continue. Model gradual normalization. | capital_expenditure | — |

---

## WMT — Walmart Inc.

**Sector:** Consumer Defensive | **Years:** 2015–2026

### Summary

| Metric | Count |
|--------|-------|
| **Total flags** | **8** |
| High severity | 2 |
| Medium severity | 3 |
| Low severity | 3 |

| Category | Count |
|----------|-------|
| m_and_a | 1 |
| one_off | 1 |
| tax | 1 |
| quality | 5 |

### All Flags

| # | Year | Severity | Category | What | Why | Action | Line Item | Impact ($M) |
|---|------|----------|----------|------|-----|--------|-----------|-------------|
| 1 | 2019 | **high** | m_and_a | Acquisition fingerprint detected (4 signals: Goodwill +71%, Acquisition spend $14.7B) | Multiple balance sheet and income signals point to material acquisition | Calculate organic growth excluding acquisition. Check 10-K for deal details. | revenue | — |
| 2 | 2020 | **high** | one_off | Total debt jumped 443% ($1.9B -> $10.2B) | Major debt increase -- likely debt-funded acquisition, recapitalization, or leveraged buyback | Check if debt increase is permanent (new capital structure) or temporary. Affects WACC and cost of debt. | total_debt | 8,304 |
| 3 | 2019 | medium | tax | High tax rate (37.4%) | Possible write-down, repatriation, or geographic mix shift | Use normalized rate for projections. | tax_provision | — |
| 4 | 2019 | medium | quality | FCF ($17.4B) is 2.6x Net Income ($6.7B) | Large non-cash charges (D&A, SBC) inflating FCF vs earnings. Common in asset-heavy or high-SBC companies. | Consider whether high FCF conversion is sustainable. | free_cash_flow | — |
| 5 | 2021 | low | quality | Revenue Growth reversed after 3yr deceleration | Multi-year declining trend broke — possible turnaround | Positive signal if sustainable. Check if driven by one-off or restructuring. | revenue | — |
| 6 | 2023 | medium | quality | Implied interest rate rose 13.9pp (5.6% -> 19.5%) | Refinancing at higher rates or new expensive debt. Affects cost of debt in WACC. | Update Kd assumption in WACC. Check debt maturity schedule. | interest_expense | — |
| 7 | 2026 | low | quality | Net Margin at 91th percentile of own history (3.1% vs avg 2.5%) | Margins at historical high — may not be sustainable long-term | Consider mean-reversion in terminal year. Historical range: 1.3%-3.4% | net_margin | — |
| 8 | 2026 | low | quality | Capital allocation: Invest — CapEx is 97% of capital deployed (3yr) | Company in investment/growth mode — building capacity | Expect elevated CapEx to continue. Model gradual normalization. | capital_expenditure | — |

---

## Cross-Company Summary

| Ticker | Total | High | Medium | Low |
|--------|-------|------|--------|-----|
| AAPL | 24 | 1 | 11 | 12 |
| GOOG | 30 | 11 | 12 | 7 |
| XOM | 2 | 0 | 1 | 1 |
| WMT | 8 | 2 | 3 | 3 |
| **Total** | **64** | **14** | **27** | **23** |

| Category | AAPL | GOOG | XOM | WMT | Total |
|----------|------|------|-----|-----|-------|
| quality | 15 | 9 | 1 | 5 | 30 |
| one_off | 8 | 10 | 1 | 1 | 20 |
| m_and_a | 0 | 7 | 0 | 1 | 8 |
| investment_cycle | 0 | 2 | 0 | 0 | 2 |
| tax | 0 | 1 | 0 | 1 | 2 |

---

## Claude Code Analysis

### 1. Likely False Positives

1. **AAPL Gross Margin "outside Technology range" (flags 2, 6, 7, 8, 11, 13) — 6 flags, ALL false positives.** The "Technology" sector range of 50-85% is calibrated for software/SaaS companies. Apple is a hardware manufacturer with 37-47% GM — that is perfectly normal and well-known. This rule is too blunt for sector classification. These 6 flags add zero value.

2. **GOOG acquisition fingerprint in 2016, 2017, 2018, 2021 — partially false.** Google had 20-40% organic revenue growth in this period. The rule fires because revenue grew fast + there was *some* acquisition spend, but Google's growth was overwhelmingly organic. The acquisition spend ($0.3B-$2.6B) is immaterial vs $100B+ revenue. The 2022 flag (Mandiant $7B) is legitimate; the others are noise.

3. **GOOG 2017 Net Margin drop / 2018 Net Margin jump — paired false positive.** The 2017 margin drop was driven by TCJA one-time repatriation tax (correctly flagged separately as tax flag). Then 2018 "jumped back" to normal. The system flags both as separate one-off events, but it's really one event (TCJA) creating two years of noise. The tax flag is sufficient.

4. **AAPL 2021 EBIT Margin +5.6pp flagged as "one-off gain"** — This was COVID-era demand + Services mix shift, not a one-off. The system sees a margin jump and assumes it's non-recurring, but Apple's margins genuinely stepped up and stayed elevated.

5. **AAPL 2017 debt jump 1327%** — Technically true but misleading. Apple started with very low debt and was executing a well-known capital return program (debt-funded buybacks). The 1327% number sounds alarming but Apple's debt/equity was still modest.

6. **"Capital allocation: Invest" flags on ALL four companies** — Every single company gets this flag because CapEx is most of their capital deployment. For capital-intensive businesses (XOM, WMT) this is completely expected. Even for AAPL/GOOG it's not really a "flag" — it's just describing normal operations.

### 2. Repetitive / Low-Information Flags

1. **"Revenue Growth reversed after Xyr acceleration/deceleration"** — Fires on AAPL (3 times), GOOG (2 times), WMT (1 time). This is what revenue growth does — it oscillates. Flagging every inflection point generates noise. A 3-year trend break in revenue growth is too sensitive for most companies.

2. **"Margin at Xth percentile of own history"** — Fires on latest year for every company (AAPL: 3 flags for GM/EBIT/Net all at 100th pctl; GOOG: 2 flags; WMT: 1 flag). By definition, a growing company will often be at its historical high margin. This is only interesting if margins are *far* above sustainable levels.

3. **"Capital allocation: Invest"** — Fires on ALL four companies identically. Says nothing differentiating.

4. **AAPL buyback flags (2015, 2016, 2019, 2020)** — Same flag 4 times for the same ongoing buyback program. One flag with a note about the multi-year trend would suffice.

### 3. Rules to Cut (if limiting to top 15)

**Rules I would REMOVE** (ordered by noise-to-signal ratio):

1. **Industry GM range check** — Too blunt. Sector classification is too broad (AAPL ≠ Microsoft). Remove entirely or reclassify to sub-industry.
2. **Capital allocation pattern** — Fires on everyone. Useless as a flag; better as a metadata label.
3. **Revenue growth trend reversal (3yr)** — Too sensitive. Every company oscillates. Raise threshold to 5yr or require magnitude > 10pp change.
4. **Margin at Nth percentile of history** — Remove the "low" severity version entirely. Keep only if margin is >2 standard deviations above mean.
5. **Share buyback (< 5% decrease)** — Known program, not a "flag." Only flag if >10% or if it's the first buyback after years of dilution.
6. **Acquisition fingerprint with immaterial spend** — Remove if acquisition spend < 5% of revenue. Currently fires on $0.3B acquisitions for a $100B+ company.
7. **Paired margin drop/jump from known tax event** — If a tax flag already fires, suppress the margin-change flags for the same year.

**Rules I would KEEP (the best 15):**

1. Debt spike > 100% (meaningful restructuring signal)
2. EBIT/Net margin jump > 5pp with impact quantification
3. EBIT/Net margin drop > 5pp with impact quantification
4. Known events (stock splits, EU fines, major M&A) — these are genuinely useful
5. TCJA / abnormal tax rate detection
6. CapEx investment cycle jump (> 50% increase in CapEx/Rev)
7. Acquisition fingerprint — but only with spend > 5% of revenue
8. FCF vs Net Income divergence (> 2x)
9. CCC lengthening trend (working capital flag)
10. Implied interest rate spike
11. High tax rate (> 35%) outside known events
12. Goodwill impairment detection
13. Net margin mean-reversion warning (only at > 95th pctl AND > 2 std dev)
14. EBIT margin trend reversal (only after 4+ years, not 3)
15. Share count change > 10% (filters out routine buybacks)
