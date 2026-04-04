# Financial Workbench — Valuation Test Report
**Date:** 2026-04-04 10:46
**Run by:** Claude Code automated test
**Risk-free rate:** 4.3% | **ERP:** 4.8%
**Total runtime:** 603s

## Summary
- Companies tested: **12**
- Modules with successful results: **Comps, DCF, DDM, Historical**
- Total errors/warnings: **1** (1 critical)
- Overall status: **PARTIAL**

## Quick Overview

| Ticker | Price | DCF | DDM | Comps | Historical |
|--------|-------|-----|-----|-------|------------|
| AAPL | $255.92 | PASS | WARN | PASS | PASS |
| JPM | $294.60 | SKIP | PASS | PASS | PASS |
| XOM | $160.69 | PASS | PASS | PASS | PASS |
| NESN.SW | 78.37 CHF | PASS | PASS | PASS | WARN |
| SHEL.L | 3,543.50 GBp | WARN | WARN | ERR | PASS |
| SAP.DE | 148.90 EUR | PASS | PASS | PASS | PASS |
| 7203.T | 3,255.00 JPY | PASS | PASS | PASS | PASS |
| 005930.KS | 186,200.00 KRW | PASS | WARN | PASS | PASS |
| 0700.HK | 489.20 HKD | PASS | PASS | PASS | PASS |
| JNJ | $243.04 | — | PASS | PASS | PASS |
| KO | $76.72 | — | PASS | PASS | PASS |
| PG | $143.12 | — | PASS | PASS | PASS |

---

## Detailed Results

### AAPL — Apple Inc.
**Market Price:** $255.92 | **Market Cap:** $3.76T | **Currency:** USD

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- *Fetch time: 0.7s*

#### DCF
- **Assumptions:** Rev growth: 6.0% -> 3.2%, EBIT margin: 30.9%, Tax: 15.6%
- **WACC:** 9.3% (Ke: 9.4%, Beta: 1.07)
- **Terminal growth:** 2.5% | TV as % of EV: 73.1%
- **Enterprise Value:** $1.63T
- **Implied share price:** $106.84
- **Upside/Downside:** -58.3%
- **Sensitivity range:** $75.00 — $188.72
- **Sanity check:** PASS
- *Time: 0.0s*

#### DDM
- **Current DPS:** $1.04 | Ke: 9.4%
- **Dividend history:** 14 years paying, 14 years increasing
- **DPS CAGR:** 3Y=4.2%, 5Y=5.0%, 10Y=7.3%
- **Gordon Growth:** g=5.0% → **$24.58** (-90.4%)
- **2-Stage DDM:** g1=5.0%, g2=3.0% → **$18.14** (-92.9%)
- **Sensitivity range:** $12.69 — $251.85
- **Sanity check:** ISSUES
  - Implied price is 0.10x current — very low
  - Implied price is 0.07x current — very low
- *Time: 0.1s*

#### Comps
- **Peers (5):** AMZN, TSLA, GOOG, META, MSFT
- **Median trailing_pe:** 27.24x → Implied: $215.47 (-15.8%)
- **Median ev_ebitda:** 16.02x → Implied: $165.20 (-35.4%)
- **Median ev_revenue:** 8.69x → Implied: $256.36 (+0.2%)
- **Sanity check:** PASS
- *Time: 11.4s*

#### Historical Multiples
- **Data source:** SEC EDGAR | Period: 2023-04-06 to 2026-04-02 (750 trading days)
- **pe:** Current=31.90, Median=31.77, Percentile=52th → Implied: $252.65
- **ev_ebitda:** Current=24.57, Median=23.83, Percentile=59th → Implied: $243.11
- **ev_revenue:** Current=8.63, Median=7.98, Percentile=65th → Implied: $231.80
- **Sanity check:** PASS
- *Time: 102.3s*

#### Summary / Football Field
- **DCF:** $106.84 (range: $75.00 — $188.72)
- **DDM (Gordon):** $24.58 (range: $12.69 — $251.85)
- **DDM (2-Stage):** $18.14 (range: N/A — N/A)
- **Comps:** $215.47 (range: $165.20 — $256.36)
- **Historical:** $243.11 (range: $231.80 — $252.65)
- **Consensus (median):** $106.84
- **Full range:** $12.69 — $256.36
- **Overall upside:** -58.3%

---

### JPM — JPMorgan Chase
**Market Price:** $294.60 | **Market Cap:** $794.55B | **Currency:** USD

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh) (missing: ebit)
- historical_years: FAIL — 4
- *Fetch time: 0.3s*

#### DCF
- *Skipped: Financial company — DCF not standard*
- *Time: 0.0s*

#### DDM
- **Current DPS:** $6.00 | Ke: 9.2%
- **Dividend history:** 42 years paying, 15 years increasing
- **DPS CAGR:** 3Y=11.5%, 5Y=9.0%, 10Y=12.7%
- **Gordon Growth:** g=6.0% → **$197.53** (-32.9%)
- **2-Stage DDM:** g1=8.0%, g2=3.0% → **$122.95** (-58.3%)
- **Sensitivity range:** $0.00 — $2,948.94
- **Sanity check:** PASS
- *Time: 0.7s*

#### Comps
- **Peers (5):** C, BAC, WFC, GS, KO
- **Median trailing_pe:** 16.46x → Implied: $329.78 (+11.9%)
- **Median price_to_book:** 1.52x → Implied: $192.41 (-34.7%)
- **Median dividend_yield:** 0.02x → Implied: N/A ()
- **Sanity check:** PASS
- *Time: 6.5s*

#### Historical Multiples
- **Data source:** SEC EDGAR | Period: 2023-04-06 to 2026-04-02 (750 trading days)
- **pe:** Current=13.93, Median=11.16, Percentile=77th → Implied: $228.89
- **Sanity check:** PASS
- *Time: 59.7s*

#### Summary / Football Field
- **DDM (Gordon):** $197.53 (range: $0.00 — $2,948.94)
- **DDM (2-Stage):** $122.95 (range: N/A — N/A)
- **Comps:** $261.10 (range: $192.41 — $329.78)
- **Historical:** $228.89 (range: $228.89 — $228.89)
- **Consensus (median):** $213.21
- **Full range:** $192.41 — $2,948.94
- **Overall upside:** -27.6%

---

### XOM — ExxonMobil
**Market Price:** $160.69 | **Market Cap:** $669.56B | **Currency:** USD

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- *Fetch time: 1.6s*

#### DCF
- **Assumptions:** Rev growth: 6.0% -> 3.2%, EBIT margin: 15.8%, Tax: 27.9%
- **WACC:** 6.5% (Ke: 6.8%, Beta: 0.53)
- **Terminal growth:** 2.5% | TV as % of EV: 83.5%
- **Enterprise Value:** $404.27B
- **Implied share price:** $87.40
- **Upside/Downside:** -45.6%
- **Sensitivity range:** $47.15 — $377.16
- Warning: Terminal value is 83% of EV — high forecast uncertainty
- **Sanity check:** PASS
- *Time: 0.0s*

#### DDM
- **Current DPS:** $4.12 | Ke: 6.8%
- **Dividend history:** 64 years paying, 42 years increasing
- **DPS CAGR:** 3Y=4.1%, 5Y=2.8%, 10Y=3.3%
- **Gordon Growth:** g=2.8% → **$106.06** (-34.0%)
- **2-Stage DDM:** g1=2.8%, g2=2.8% → **$106.06** (-34.0%)
- **Sensitivity range:** $0.00 — $873.45
- **Sanity check:** PASS
- *Time: 0.8s*

#### Comps
- **Peers (5):** CVX, JNJ, WMT, PG, PFE
- **Median trailing_pe:** 22.03x → Implied: $147.63 (-8.1%)
- **Median ev_ebitda:** 14.52x → Implied: $197.32 (+22.8%)
- **Median ev_revenue:** 3.44x → Implied: $258.01 (+60.6%)
- **Sanity check:** PASS
- *Time: 16.6s*

#### Historical Multiples
- **Data source:** SEC EDGAR | Period: 2023-04-06 to 2026-04-02 (750 trading days)
- **pe:** Current=23.21, Median=13.58, Percentile=99th → Implied: $93.73
- **ev_ebitda:** Current=9.95, Median=6.40, Percentile=99th → Implied: $97.37
- **ev_revenue:** Current=2.02, Median=1.32, Percentile=99th → Implied: $99.30
- **Sanity check:** PASS
- *Time: 61.7s*

#### Summary / Football Field
- **DCF:** $87.40 (range: $47.15 — $377.16)
- **DDM (Gordon):** $106.06 (range: $0.00 — $873.45)
- **DDM (2-Stage):** $106.06 (range: N/A — N/A)
- **Comps:** $197.32 (range: $147.63 — $258.01)
- **Historical:** $97.37 (range: $93.73 — $99.30)
- **Consensus (median):** $106.06
- **Full range:** $47.15 — $873.45
- **Overall upside:** -34.0%

---

### NESN.SW — Nestlé
**Market Price:** 78.37 CHF | **Market Cap:** $201.58B | **Currency:** CHF

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- *Fetch time: 1.7s*

#### DCF
- **Assumptions:** Rev growth: 6.0% -> 3.2%, EBIT margin: 14.8%, Tax: 24.6%
- **WACC:** 6.4% (Ke: 7.5%, Beta: 0.68)
- **Terminal growth:** 2.5% | TV as % of EV: 83.5%
- **Enterprise Value:** $223.42B
- **Implied share price:** $65.94
- **Upside/Downside:** -15.9%
- **Sensitivity range:** $29.58 — $345.73
- Warning: Terminal value is 84% of EV — high forecast uncertainty
- **Sanity check:** PASS
- *Time: 0.0s*

#### DDM
- **Current DPS:** $3.10 | Ke: 7.5%
- **Dividend history:** 24 years paying, 23 years increasing
- **DPS CAGR:** 3Y=2.9%, 5Y=2.5%, 10Y=3.3%
- **Gordon Growth:** g=2.5% → **$62.58** (-20.2%)
- **2-Stage DDM:** g1=2.5%, g2=2.5% → **$62.58** (-20.2%)
- **Sensitivity range:** $34.32 — $300.94
- **Sanity check:** PASS
- *Time: 0.6s*

#### Comps
- **Peers (5):** NOVN.SW, ZURN.SW, SREN.SW, UBSG.SW, OR.PA
- **Median trailing_pe:** 16.72x → Implied: $58.68 (-25.1%)
- **Median ev_ebitda:** 8.86x → Implied: $37.31 (-52.4%)
- **Median ev_revenue:** 3.33x → Implied: $96.30 (+22.9%)
- **Sanity check:** PASS
- *Time: 16.0s*

#### Historical Multiples
- **Data source:** Yahoo Finance | Period: 2023-04-06 to 2026-04-02 (747 trading days)
- **pe:** Current=22.32, Median=20.67, Percentile=71th → Implied: $324.62
- **ev_ebitda:** Current=15.66, Median=15.48, Percentile=54th → Implied: $393.46
- **ev_revenue:** Current=2.82, Median=3.00, Percentile=24th → Implied: $410.94
- **Sanity check:** ISSUES
  - Implied price is 5.0x current — very high
  - Implied price is 5.2x current — very high
- *Time: 3.9s*

#### Summary / Football Field
- **DCF:** $65.94 (range: $29.58 — $345.73)
- **DDM (Gordon):** $62.58 (range: $34.32 — $300.94)
- **DDM (2-Stage):** $62.58 (range: N/A — N/A)
- **Comps:** $58.68 (range: $37.31 — $96.30)
- **Historical:** $393.46 (range: $324.62 — $410.94)
- **Consensus (median):** $62.58
- **Full range:** $29.58 — $410.94
- **Overall upside:** -20.2%

---

### SHEL.L — Shell plc
**Market Price:** 3,543.50 GBp | **Market Cap:** $198.65B | **Currency:** GBp

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- *Fetch time: 1.5s*

#### DCF
- **Assumptions:** Rev growth: 6.0% -> 3.2%, EBIT margin: 13.8%, Tax: 39.1%
- **WACC:** 7.6% (Ke: 9.1%, Beta: 1.00)
- **Terminal growth:** 2.5% | TV as % of EV: 79.0%
- **Enterprise Value:** $509.31B
- **Implied share price:** $82.48
- **Upside/Downside:** -97.7%
- **Sensitivity range:** $50.59 — $203.53
- Warning: Terminal value is 79% of EV — high forecast uncertainty
- **Sanity check:** ISSUES
  - Implied price is 0.02x current — very low
- *Time: 0.0s*

#### DDM
- **Current DPS:** $1.11 | Ke: 9.1%
- **Dividend history:** 21 years paying, 4 years increasing
- **DPS CAGR:** 3Y=10.2%, 5Y=7.9%, 10Y=-1.4%
- **Gordon Growth:** g=6.0% → **$38.16** (-98.9%)
- **2-Stage DDM:** g1=7.9%, g2=3.0% → **$23.16** (-99.3%)
- **Sensitivity range:** $0.00 — $1,444.34
- **Sanity check:** ISSUES
  - Implied price is 0.01x current — very low
  - Implied price is 0.01x current — very low
- *Time: 0.6s*

#### Comps
- **ERROR:** '>' not supported between instances of 'str' and 'int'
- *Time: 15.9s*

#### Historical Multiples
- **Data source:** Yahoo Finance | Period: 2023-04-06 to 2026-04-02 (692 trading days)
- **pe:** Current=1,130.35, Median=920.53, Percentile=89th → Implied: $2,885.73
- **ev_ebitda:** Current=356.65, Median=274.54, Percentile=100th → Implied: $2,725.82
- **ev_revenue:** Current=75.72, Median=56.11, Percentile=91th → Implied: $2,623.61
- **Sanity check:** PASS
- *Time: 2.7s*

#### Summary / Football Field
- **DCF:** $82.48 (range: $50.59 — $203.53)
- **DDM (Gordon):** $38.16 (range: $0.00 — $1,444.34)
- **DDM (2-Stage):** $23.16 (range: N/A — N/A)
- **Historical:** $2,725.82 (range: $2,623.61 — $2,885.73)
- **Consensus (median):** $60.32
- **Full range:** $50.59 — $2,885.73
- **Overall upside:** -98.3%

---

### SAP.DE — SAP SE
**Market Price:** 148.90 EUR | **Market Cap:** $173.85B | **Currency:** EUR

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- *Fetch time: 1.9s*

#### DCF
- **Assumptions:** Rev growth: 6.0% -> 3.2%, EBIT margin: 20.1%, Tax: 28.7%
- **WACC:** 8.2% (Ke: 8.3%, Beta: 0.84)
- **Terminal growth:** 2.5% | TV as % of EV: 77.2%
- **Enterprise Value:** $72.28B
- **Implied share price:** $62.12
- **Upside/Downside:** -58.3%
- **Sensitivity range:** $41.86 — $127.46
- Warning: Terminal value is 77% of EV — high forecast uncertainty
- **Sanity check:** PASS
- *Time: 0.0s*

#### DDM
- **Current DPS:** $2.50 | Ke: 8.3%
- **Dividend history:** 27 years paying, 2 years increasing
- **DPS CAGR:** 3Y=-1.4%, 5Y=8.3%, 10Y=7.9%
- **Gordon Growth:** g=6.0% → **$113.92** (-23.5%)
- **2-Stage DDM:** g1=8.0%, g2=3.0% → **$60.01** (-59.7%)
- **Sensitivity range:** $0.00 — $827.81
- **Sanity check:** PASS
- *Time: 0.6s*

#### Comps
- **Peers (5):** SIE.DE, ALV.DE, BAS.DE, DTE.DE, BAYN.DE
- **Median trailing_pe:** 18.42x → Implied: $112.39 (-24.5%)
- **Median ev_ebitda:** 7.76x → Implied: $76.44 (-48.7%)
- **Median ev_revenue:** 1.51x → Implied: $49.36 (-66.9%)
- **Sanity check:** PASS
- *Time: 16.5s*

#### Historical Multiples
- **Data source:** Yahoo Finance | Period: 2023-04-06 to 2026-04-02 (696 trading days)
- **pe:** Current=24.28, Median=54.21, Percentile=1th → Implied: $332.49
- **ev_ebitda:** Current=14.25, Median=25.17, Percentile=1th → Implied: $261.84
- **ev_revenue:** Current=4.68, Median=6.49, Percentile=2th → Implied: $206.11
- **Sanity check:** PASS
- *Time: 2.5s*

#### Summary / Football Field
- **DCF:** $62.12 (range: $41.86 — $127.46)
- **DDM (Gordon):** $113.92 (range: $0.00 — $827.81)
- **DDM (2-Stage):** $60.01 (range: N/A — N/A)
- **Comps:** $76.44 (range: $49.36 — $112.39)
- **Historical:** $261.84 (range: $206.11 — $332.49)
- **Consensus (median):** $76.44
- **Full range:** $41.86 — $827.81
- **Overall upside:** -48.7%

---

### 7203.T — Toyota Motor
**Market Price:** 3,255.00 JPY | **Market Cap:** $42.42T | **Currency:** JPY

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- *Fetch time: 1.8s*

#### DCF
- **Assumptions:** Rev growth: 6.0% -> 3.2%, EBIT margin: 13.0%, Tax: 25.3%
- **WACC:** 3.8% (Ke: 7.0%, Beta: 0.57)
- **Terminal growth:** 2.5% | TV as % of EV: 95.0%
- **Enterprise Value:** $121.90T
- **Implied share price:** $6,992.84
- **Upside/Downside:** +114.8%
- **Sensitivity range:** $-1,877.96 — $46,050.22
- Warning: Terminal value is 95% of EV — high forecast uncertainty
- **Sanity check:** PASS
- *Time: 0.0s*

#### DDM
- **Current DPS:** $95.00 | Ke: 7.0%
- **Dividend history:** 27 years paying, 6 years increasing
- **DPS CAGR:** 3Y=21.5%, 5Y=16.1%, 10Y=7.8%
- **Gordon Growth:** g=6.0% → **$9,698.92** (+198.0%)
- **2-Stage DDM:** g1=8.0%, g2=3.0% → **$3,021.86** (-7.2%)
- **Sensitivity range:** $0.00 — $268,165.19
- **Sanity check:** PASS
- *Time: 0.6s*

#### Comps
- **Peers (5):** 7267.T, 6758.T, 8306.T, 7201.T, 8058.T
- **Median trailing_pe:** 16.25x → Implied: $4,617.94 (+41.9%)
- **Median ev_ebitda:** 21.16x → Implied: $8,116.29 (+149.3%)
- **Median ev_revenue:** 1.06x → Implied: $2,153.57 (-33.8%)
- **Sanity check:** PASS
- *Time: 17.4s*

#### Historical Multiples
- **Data source:** Yahoo Finance | Period: 2023-04-06 to 2026-04-03 (732 trading days)
- **pe:** Current=11.48, Median=8.68, Percentile=67th → Implied: $2,461.19
- **ev_ebitda:** Current=9.23, Median=7.45, Percentile=74th → Implied: $2,232.38
- **ev_revenue:** Current=1.37, Median=1.35, Percentile=54th → Implied: $3,188.36
- **Sanity check:** PASS
- *Time: 2.4s*

#### Summary / Football Field
- **DCF:** $6,992.84 (range: $-1,877.96 — $46,050.22)
- **DDM (Gordon):** $9,698.92 (range: $0.00 — $268,165.19)
- **DDM (2-Stage):** $3,021.86 (range: N/A — N/A)
- **Comps:** $4,617.94 (range: $2,153.57 — $8,116.29)
- **Historical:** $2,461.19 (range: $2,232.38 — $3,188.36)
- **Consensus (median):** $4,617.94
- **Full range:** $-1,877.96 — $268,165.19
- **Overall upside:** +41.9%

---

### 005930.KS — Samsung Electronics
**Market Price:** 186,200.00 KRW | **Market Cap:** $1244.95T | **Currency:** KRW

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- *Fetch time: 1.7s*

#### DCF
- **Assumptions:** Rev growth: 6.0% -> 3.2%, EBIT margin: 12.0%, Tax: 8.6%
- **WACC:** 9.6% (Ke: 9.8%, Beta: 1.14)
- **Terminal growth:** 2.5% | TV as % of EV: 73.5%
- **Enterprise Value:** $286.00T
- **Implied share price:** $45,839.54
- **Upside/Downside:** -75.4%
- **Sensitivity range:** $33,805.48 — $75,301.43
- **Sanity check:** PASS
- *Time: 0.0s*

#### DDM
- **Current DPS:** $2,264.00 | Ke: 9.8%
- **Dividend history:** 20 years paying, 2 years increasing
- **DPS CAGR:** 3Y=4.9%, 5Y=-11.0%, 10Y=14.8%
- **Gordon Growth:** g=1.0% → **$26,121.15** (-86.0%)
- **2-Stage DDM:** g1=-11.0%, g2=1.0% → **$15,434.71** (-91.7%)
- **Sensitivity range:** $19,446.27 — $49,051.95
- **Sanity check:** ISSUES
  - Implied price is 0.08x current — very low
- *Time: 0.6s*

#### Comps
- **Peers (5):** 000660.KS, 005380.KS, 035420.KS, 066570.KS, 035720.KS
- **Median ev_ebitda:** 9.36x → Implied: $159,269.37 (-14.5%)
- **Median ev_revenue:** 2.17x → Implied: $140,247.57 (-24.7%)
- **Sanity check:** PASS
- *Time: 16.9s*

#### Historical Multiples
- **Data source:** Yahoo Finance | Period: 2023-04-06 to 2026-04-03 (665 trading days)
- **pe:** Current=28.13, Median=17.93, Percentile=72th → Implied: $118,694.15
- **ev_ebitda:** Current=11.53, Median=5.21, Percentile=96th → Implied: $91,415.90
- **ev_revenue:** Current=3.47, Median=1.33, Percentile=97th → Implied: $79,612.65
- **Sanity check:** PASS
- *Time: 2.1s*

#### Summary / Football Field
- **DCF:** $45,839.54 (range: $33,805.48 — $75,301.43)
- **DDM (Gordon):** $26,121.15 (range: $19,446.27 — $49,051.95)
- **DDM (2-Stage):** $15,434.71 (range: N/A — N/A)
- **Comps:** $149,758.47 (range: $140,247.57 — $159,269.37)
- **Historical:** $91,415.90 (range: $79,612.65 — $118,694.15)
- **Consensus (median):** $45,839.54
- **Full range:** $19,446.27 — $159,269.37
- **Overall upside:** -75.4%

---

### 0700.HK — Tencent Holdings
**Market Price:** 489.20 HKD | **Market Cap:** $4.42T | **Currency:** HKD

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- *Fetch time: 1.6s*

#### DCF
- **Assumptions:** Rev growth: 6.0% -> 3.2%, EBIT margin: 38.1%, Tax: 18.6%
- **WACC:** 8.0% (Ke: 8.4%, Beta: 0.87)
- **Terminal growth:** 2.5% | TV as % of EV: 77.3%
- **Enterprise Value:** $3.62T
- **Implied share price:** $367.06
- **Upside/Downside:** -25.0%
- **Sensitivity range:** $233.90 — $813.95
- Warning: Terminal value is 77% of EV — high forecast uncertainty
- **Sanity check:** PASS
- *Time: 0.0s*

#### DDM
- **Current DPS:** $5.30 | Ke: 8.4%
- **Dividend history:** 18 years paying, 3 years increasing
- **DPS CAGR:** 3Y=41.2%, 5Y=30.3%, 10Y=28.7%
- **Gordon Growth:** g=6.0% → **$229.59** (-53.1%)
- **2-Stage DDM:** g1=8.0%, g2=3.0% → **$124.35** (-74.6%)
- **Sensitivity range:** $0.00 — $1,280.54
- **Sanity check:** PASS
- *Time: 0.5s*

#### Comps
- **Peers (5):** 9988.HK, 0388.HK, 3690.HK, 2318.HK, 1810.HK
- **Median trailing_pe:** 19.50x → Implied: $534.97 (+9.4%)
- **Median ev_ebitda:** 16.45x → Implied: $503.07 (+2.8%)
- **Median ev_revenue:** 1.59x → Implied: $134.77 (-72.5%)
- **Sanity check:** PASS
- *Time: 16.6s*

#### Historical Multiples
- **Data source:** Yahoo Finance | Period: 2023-04-06 to 2026-04-02 (734 trading days)
- **pe:** Current=79.85, Median=24.35, Percentile=83th → Implied: $149.17
- **ev_ebitda:** Current=19.71, Median=14.27, Percentile=100th → Implied: $98.23
- **ev_revenue:** Current=24.73, Median=6.13, Percentile=83th → Implied: $111.31
- **Sanity check:** PASS
- *Time: 2.3s*

#### Summary / Football Field
- **DCF:** $367.06 (range: $233.90 — $813.95)
- **DDM (Gordon):** $229.59 (range: $0.00 — $1,280.54)
- **DDM (2-Stage):** $124.35 (range: N/A — N/A)
- **Comps:** $503.07 (range: $134.77 — $534.97)
- **Historical:** $111.31 (range: $98.23 — $149.17)
- **Consensus (median):** $229.59
- **Full range:** $98.23 — $1,280.54
- **Overall upside:** -53.1%

---

### JNJ — Johnson & Johnson
**Market Price:** $243.04 | **Market Cap:** $585.70B | **Currency:** USD

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- *Fetch time: 0.3s*

#### DDM
- **Current DPS:** $5.20 | Ke: 6.9%
- **Dividend history:** 64 years paying, 63 years increasing
- **DPS CAGR:** 3Y=4.9%, 5Y=5.2%, 10Y=5.7%
- **Gordon Growth:** g=5.2% → **$321.80** (+32.4%)
- **2-Stage DDM:** g1=5.2%, g2=3.0% → **$149.96** (-38.3%)
- **Sensitivity range:** $0.00 — $2,778.78
- **Sanity check:** PASS
- *Time: 0.2s*

#### Comps
- **Peers (5):** PG, PFE, MRK, KO, XOM
- **Median trailing_pe:** 21.17x → Implied: $233.52 (-3.9%)
- **Median ev_ebitda:** 12.07x → Implied: $157.38 (-35.2%)
- **Median ev_revenue:** 4.22x → Implied: $152.74 (-37.2%)
- **Sanity check:** PASS
- *Time: 3.8s*

#### Historical Multiples
- **Data source:** SEC EDGAR | Period: 2023-04-06 to 2026-04-02 (750 trading days)
- **pe:** Current=21.85, Median=18.31, Percentile=65th → Implied: $202.02
- **ev_ebitda:** Current=14.61, Median=14.39, Percentile=55th → Implied: $228.48
- **ev_revenue:** Current=6.22, Median=4.36, Percentile=98th → Implied: $160.10
- **Sanity check:** PASS
- *Time: 60.4s*

#### Summary / Football Field
- **DDM (Gordon):** $321.80 (range: $0.00 — $2,778.78)
- **DDM (2-Stage):** $149.96 (range: N/A — N/A)
- **Comps:** $157.38 (range: $152.74 — $233.52)
- **Historical:** $202.02 (range: $160.10 — $228.48)
- **Consensus (median):** $179.70
- **Full range:** $152.74 — $2,778.78
- **Overall upside:** -26.1%

---

### KO — Coca-Cola Co
**Market Price:** $76.72 | **Market Cap:** $330.21B | **Currency:** USD

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- *Fetch time: 2.2s*

#### DDM
- **Current DPS:** $2.06 | Ke: 7.1%
- **Dividend history:** 64 years paying, 23 years increasing
- **DPS CAGR:** 3Y=5.0%, 5Y=4.5%, 10Y=4.4%
- **Gordon Growth:** g=4.5% → **$83.11** (+8.3%)
- **2-Stage DDM:** g1=4.5%, g2=3.0% → **$55.92** (-27.1%)
- **Sensitivity range:** $0.00 — $2,457.60
- **Sanity check:** PASS
- *Time: 0.9s*

#### Comps
- **Peers (5):** PG, JNJ, DIS, VZ, JPM
- **Median trailing_pe:** 14.71x → Implied: $44.71 (-41.7%)
- **Median ev_ebitda:** 12.89x → Implied: $40.71 (-46.9%)
- **Median ev_revenue:** 3.29x → Implied: $29.14 (-62.0%)
- **Sanity check:** PASS
- *Time: 4.5s*

#### Historical Multiples
- **Data source:** SEC EDGAR | Period: 2023-04-06 to 2026-04-02 (750 trading days)
- **pe:** Current=25.17, Median=24.09, Percentile=68th → Implied: $73.21
- **ev_ebitda:** Current=22.28, Median=22.52, Percentile=48th → Implied: $69.96
- **ev_revenue:** Current=6.88, Median=6.08, Percentile=88th → Implied: $60.20
- **Sanity check:** PASS
- *Time: 70.5s*

#### Summary / Football Field
- **DDM (Gordon):** $83.11 (range: $0.00 — $2,457.60)
- **DDM (2-Stage):** $55.92 (range: N/A — N/A)
- **Comps:** $40.71 (range: $29.14 — $44.71)
- **Historical:** $69.96 (range: $60.20 — $73.21)
- **Consensus (median):** $62.94
- **Full range:** $29.14 — $2,457.60
- **Overall upside:** -18.0%

---

### PG — Procter & Gamble
**Market Price:** $143.12 | **Market Cap:** $334.43B | **Currency:** USD

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- *Fetch time: 1.7s*

#### DDM
- **Current DPS:** $4.23 | Ke: 7.2%
- **Dividend history:** 64 years paying, 22 years increasing
- **DPS CAGR:** 3Y=5.0%, 5Y=6.0%, 10Y=4.7%
- **Gordon Growth:** g=6.0% → **$378.53** (+164.5%)
- **2-Stage DDM:** g1=6.0%, g2=3.0% → **$119.06** (-16.8%)
- **Sensitivity range:** $0.00 — $2,475.56
- **Sanity check:** PASS
- *Time: 0.9s*

#### Comps
- **Peers (5):** JNJ, KO, MRK, HD, VZ
- **Median trailing_pe:** 22.03x → Implied: $148.95 (+4.1%)
- **Median ev_ebitda:** 15.39x → Implied: $152.87 (+6.8%)
- **Median ev_revenue:** 5.15x → Implied: $177.86 (+24.3%)
- **Sanity check:** PASS
- *Time: 3.9s*

#### Historical Multiples
- **Data source:** SEC EDGAR | Period: 2023-04-06 to 2026-04-02 (750 trading days)
- **pe:** Current=21.14, Median=24.40, Percentile=5th → Implied: $165.19
- **ev_ebitda:** Current=15.69, Median=17.65, Percentile=9th → Implied: $161.77
- **ev_revenue:** Current=4.25, Median=4.60, Percentile=13th → Implied: $155.30
- **Sanity check:** PASS
- *Time: 61.9s*

#### Summary / Football Field
- **DDM (Gordon):** $378.53 (range: $0.00 — $2,475.56)
- **DDM (2-Stage):** $119.06 (range: N/A — N/A)
- **Comps:** $152.87 (range: $148.95 — $177.86)
- **Historical:** $161.77 (range: $155.30 — $165.19)
- **Consensus (median):** $157.32
- **Full range:** $148.95 — $2,475.56
- **Overall upside:** +9.9%

---

## Errors and Issues

| # | Ticker | Module | Issue | Severity |
|---|--------|--------|-------|----------|
| 1 | SHEL.L | Comps | Exception: '>' not supported between instances of 'str' and 'int' | Critical |

## Performance

| Ticker | Data | DCF | DDM | Comps | Historical | Total |
|--------|------|-----|-----|-------|------------|-------|
| AAPL | 0.7s | 0.0s | 0.1s | 11.4s | 102.3s | 114.4s |
| JPM | 0.3s | 0.0s | 0.7s | 6.5s | 59.7s | 67.3s |
| XOM | 1.6s | 0.0s | 0.8s | 16.6s | 61.7s | 80.8s |
| NESN.SW | 1.7s | 0.0s | 0.6s | 16.0s | 3.9s | 22.4s |
| SHEL.L | 1.5s | 0.0s | 0.6s | 15.9s | 2.7s | 20.6s |
| SAP.DE | 1.9s | 0.0s | 0.6s | 16.5s | 2.5s | 21.4s |
| 7203.T | 1.8s | 0.0s | 0.6s | 17.4s | 2.4s | 22.3s |
| 005930.KS | 1.7s | 0.0s | 0.6s | 16.9s | 2.1s | 21.4s |
| 0700.HK | 1.6s | 0.0s | 0.5s | 16.6s | 2.3s | 21.0s |
| JNJ | 0.3s | 0.0s | 0.2s | 3.8s | 60.4s | 64.7s |
| KO | 2.2s | 0.0s | 0.9s | 4.5s | 70.5s | 78.1s |
| PG | 1.7s | 0.0s | 0.9s | 3.9s | 61.9s | 68.5s |

## Conclusions

**Working well:** AAPL, JPM, XOM, NESN.SW, SAP.DE, 7203.T, 005930.KS, 0700.HK, JNJ, KO, PG
**Issues found:**
- SHEL.L: Exception: '>' not supported between instances of 'str' and 'int'

---
*Report generated 2026-04-04 10:46 by test_all_valuations.py*