# Financial Workbench — Valuation Test Report
**Date:** 2026-04-04 12:58
**Run by:** Claude Code automated test
**Rf:** 4.3% (US 10Y) | **ERP:** 4.8%
**Total runtime:** 432s

## Summary
- Companies tested: **12**
- Modules with successful results: **Comps, DCF, DDM, Historical**
- Total errors/warnings: **0** (0 critical)
- Overall status: **PASS**

## Quick Overview

| Ticker | Price | DCF | DDM | Comps | Historical |
|--------|-------|-----|-----|-------|------------|
| AAPL | $255.92 | PASS | WARN | PASS | PASS |
| JPM | $294.60 | SKIP | PASS | PASS | PASS |
| XOM | $160.69 | PASS | PASS | PASS | PASS |
| NESN.SW | 78.37 CHF | PASS | PASS | PASS | PASS |
| SHEL.L | 3,543.50 GBp | PASS | PASS | PASS | PASS |
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
- rf: FAIL — 4.3% (US 10Y)
- Rf: 4.3% (US 10Y)
- *Fetch time: 0.6s*

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
- **Gordon sensitivity:** $12.69 — $251.85
- **2-Stage sensitivity:** $11.84 — $44.92
- **Sanity check:** ISSUES
  - Implied price is 0.10x current — very low
  - Implied price is 0.07x current — very low
- *Time: 0.1s*

#### Comps
- **Peers (6, GICS):** DELL, HPE, HPQ, NTAP, SNDK, STX
- **Median trailing_pe:** 18.71x → Implied: $148.03 (-42.2%)
- **Median ev_ebitda:** 11.56x → Implied: $118.81 (-53.6%)
- **Median ev_revenue:** 2.19x → Implied: $63.43 (-75.2%)
- **Sanity check:** PASS
- *Time: 0.0s*

#### Historical Multiples
- **Data source:** SEC EDGAR | Period: 2023-04-06 to 2026-04-02 (750 trading days)
- **pe:** Current=31.90, Median=31.77, Percentile=52th → Implied: $252.65
- **ev_ebitda:** Current=24.57, Median=23.83, Percentile=59th → Implied: $243.11
- **ev_revenue:** Current=8.63, Median=7.98, Percentile=65th → Implied: $231.80
- **Sanity check:** PASS
- *Time: 64.5s*

#### Summary / Football Field
- **DCF:** $106.84 (range: $75.00 — $188.72)
- **DDM (Gordon):** $24.58 (range: $12.69 — $251.85)
- **DDM (2-Stage):** $18.14 (range: $11.84 — $44.92)
- **Comps:** $118.81 (range: $63.43 — $148.03)
- **Historical:** $243.11 (range: $231.80 — $252.65)
- **Consensus (median):** $106.84
- **Full range:** $11.84 — $252.65
- **Overall upside:** -58.3%

---

### JPM — JPMorgan Chase
**Market Price:** $294.60 | **Market Cap:** $794.55B | **Currency:** USD

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh) (missing: ebit)
- historical_years: FAIL — 4
- rf: FAIL — 4.3% (US 10Y)
- Rf: 4.3% (US 10Y)
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
- **Gordon sensitivity:** $86.43 — $2,948.94
- **2-Stage sensitivity:** $78.69 — $324.96
- **Sanity check:** PASS
- *Time: 0.1s*

#### Comps
- **Peers (6, GICS):** AMP, APO, ARES, BAC, BLK, BX
- **Median trailing_pe:** 23.36x → Implied: $467.88 (+58.8%)
- **Median price_to_book:** 4.44x → Implied: $563.29 (+91.2%)
- **Median dividend_yield:** 0.02x → Implied: N/A ()
- **Sanity check:** PASS
- *Time: 0.0s*

#### Historical Multiples
- **Data source:** SEC EDGAR | Period: 2023-04-06 to 2026-04-02 (750 trading days)
- **pe:** Current=13.93, Median=11.16, Percentile=77th → Implied: $228.89
- **Sanity check:** PASS
- *Time: 60.9s*

#### Summary / Football Field
- **DDM (Gordon):** $197.53 (range: $86.43 — $2,948.94)
- **DDM (2-Stage):** $122.95 (range: $78.69 — $324.96)
- **Comps:** $515.59 (range: $467.88 — $563.29)
- **Historical:** $228.89 (range: $228.89 — $228.89)
- **Consensus (median):** $213.21
- **Full range:** $78.69 — $2,948.94
- **Overall upside:** -27.6%

---

### XOM — ExxonMobil
**Market Price:** $160.69 | **Market Cap:** $669.56B | **Currency:** USD

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- rf: FAIL — 4.3% (US 10Y)
- Rf: 4.3% (US 10Y)
- *Fetch time: 0.3s*

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
- **Gordon sensitivity:** $51.96 — $873.45
- **2-Stage sensitivity:** $56.58 — $809.12
- **Sanity check:** PASS
- *Time: 0.1s*

#### Comps
- **Peers (6, GICS):** CVX, TTE.PA, CCO.TO, CNQ.TO, CVE.TO, ENB.TO
- **Median trailing_pe:** 20.30x → Implied: $135.99 (-15.4%)
- **Median ev_ebitda:** 10.85x → Implied: $145.06 (-9.7%)
- **Median ev_revenue:** 3.23x → Implied: $241.18 (+50.1%)
- **Sanity check:** PASS
- *Time: 0.0s*

#### Historical Multiples
- **Data source:** SEC EDGAR | Period: 2023-04-06 to 2026-04-02 (750 trading days)
- **pe:** Current=23.21, Median=13.58, Percentile=99th → Implied: $93.73
- **ev_ebitda:** Current=9.95, Median=6.40, Percentile=99th → Implied: $97.37
- **ev_revenue:** Current=2.02, Median=1.32, Percentile=99th → Implied: $99.30
- **Sanity check:** PASS
- *Time: 60.5s*

#### Summary / Football Field
- **DCF:** $87.40 (range: $47.15 — $377.16)
- **DDM (Gordon):** $106.06 (range: $51.96 — $873.45)
- **DDM (2-Stage):** $106.06 (range: $56.58 — $809.12)
- **Comps:** $145.06 (range: $135.99 — $241.18)
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
- rf: FAIL — 4.3% (US 10Y)
- Rf: 4.3% (US 10Y)
- *Fetch time: 0.3s*

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
- **Gordon sensitivity:** $34.32 — $300.94
- **2-Stage sensitivity:** $37.32 — $273.76
- **Sanity check:** PASS
- *Time: 0.2s*

#### Comps
- **Peers (6, GICS):** CPB, CAG, GIS, HSY, HRL, KHC
- **Median trailing_pe:** 18.39x → Implied: $64.55 (-17.6%)
- **Median ev_ebitda:** 8.05x → Implied: $32.03 (-59.1%)
- **Median ev_revenue:** 1.33x → Implied: $26.41 (-66.3%)
- **Sanity check:** PASS
- *Time: 0.0s*

#### Historical Multiples
- **Data source:** Yahoo Finance | Period: 2023-04-06 to 2026-04-02 (747 trading days)
- **pe:** Current=22.32, Median=20.67, Percentile=71th → Implied: $72.59
- **ev_ebitda:** Current=15.66, Median=15.48, Percentile=54th → Implied: $77.25
- **ev_revenue:** Current=2.82, Median=3.00, Percentile=24th → Implied: $84.55
- **Sanity check:** PASS
- *Time: 3.4s*

#### Summary / Football Field
- **DCF:** $65.94 (range: $29.58 — $345.73)
- **DDM (Gordon):** $62.58 (range: $34.32 — $300.94)
- **DDM (2-Stage):** $62.58 (range: $37.32 — $273.76)
- **Comps:** $32.03 (range: $26.41 — $64.55)
- **Historical:** $77.25 (range: $72.59 — $84.55)
- **Consensus (median):** $62.58
- **Full range:** $26.41 — $345.73
- **Overall upside:** -20.2%

---

### SHEL.L — Shell plc
**Market Price:** 3,543.50 GBp | **Market Cap:** $198.65B | **Currency:** GBp

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- rf: FAIL — 4.3% (US 10Y)
- Rf: 4.3% (US 10Y)
- *Fetch time: 0.3s*

#### DCF
- **Assumptions:** Rev growth: 6.0% -> 3.2%, EBIT margin: 13.8%, Tax: 39.1%
- **WACC:** 7.6% (Ke: 9.1%, Beta: 1.00)
- **Terminal growth:** 2.5% | TV as % of EV: 79.0%
- **Enterprise Value:** $509.31B
- **Implied share price:** $8,247.65
- **Upside/Downside:** +132.8%
- **Sensitivity range:** $5,059.18 — $20,353.15
- Warning: Terminal value is 79% of EV — high forecast uncertainty
- **Sanity check:** PASS
- *Time: 0.0s*

#### DDM
- **Current DPS:** $1.11 | Ke: 9.1%
- **Dividend history:** 21 years paying, 4 years increasing
- **DPS CAGR:** 3Y=10.2%, 5Y=7.9%, 10Y=-1.4%
- **Gordon Growth:** g=6.0% → **$3,816.41** (+7.7%)
- **2-Stage DDM:** g1=7.9%, g2=3.0% → **$2,316.08** (-34.6%)
- **Gordon sensitivity:** $1,629.82 — $144,433.74
- **2-Stage sensitivity:** $1,469.98 — $6,377.23
- **Sanity check:** PASS
- *Time: 0.1s*

#### Comps
- **Peers (6, GICS):** CVX, XOM, TTE.PA, BP.L, CCO.TO, CNQ.TO
- **Median trailing_pe:** 23.98x → Implied: $5,420.29 (+53.0%)
- **Median ev_ebitda:** 10.85x → Implied: $8,411.31 (+137.4%)
- **Median ev_revenue:** 2.31x → Implied: $10,166.92 (+186.9%)
- **Sanity check:** PASS
- *Time: 0.0s*

#### Historical Multiples
- **Data source:** Yahoo Finance | Period: 2023-04-06 to 2026-04-02 (692 trading days)
- **pe:** Current=11.30, Median=9.21, Percentile=89th → Implied: $2,887.20
- **ev_ebitda:** Current=4.39, Median=3.49, Percentile=100th → Implied: $2,650.62
- **ev_revenue:** Current=0.93, Median=0.70, Percentile=90th → Implied: $2,458.40
- **Sanity check:** PASS
- *Time: 4.0s*

#### Summary / Football Field
- **DCF:** $8,247.65 (range: $5,059.18 — $20,353.15)
- **DDM (Gordon):** $3,816.41 (range: $1,629.82 — $144,433.74)
- **DDM (2-Stage):** $2,316.08 (range: $1,469.98 — $6,377.23)
- **Comps:** $8,411.31 (range: $5,420.29 — $10,166.92)
- **Historical:** $2,650.62 (range: $2,458.40 — $2,887.20)
- **Consensus (median):** $3,816.41
- **Full range:** $1,469.98 — $144,433.74
- **Overall upside:** +7.7%

---

### SAP.DE — SAP SE
**Market Price:** 148.90 EUR | **Market Cap:** $173.85B | **Currency:** EUR

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- rf: FAIL — 4.3% (US 10Y)
- Rf: 4.3% (US 10Y)
- *Fetch time: 0.3s*

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
- **Gordon sensitivity:** $41.10 — $827.81
- **2-Stage sensitivity:** $36.07 — $227.12
- **Sanity check:** PASS
- *Time: 0.1s*

#### Comps
- **Peers (6, GICS):** ADBE, APP, ADSK, ADP, CDNS, CRWD
- **Median trailing_pe:** 38.44x → Implied: $234.51 (+57.5%)
- **Median ev_ebitda:** 26.43x → Implied: $256.05 (+72.0%)
- **Median ev_revenue:** 10.62x → Implied: $336.57 (+126.0%)
- **Sanity check:** PASS
- *Time: 0.0s*

#### Historical Multiples
- **Data source:** Yahoo Finance | Period: 2023-04-06 to 2026-04-02 (696 trading days)
- **pe:** Current=24.28, Median=54.21, Percentile=1th → Implied: $332.49
- **ev_ebitda:** Current=14.25, Median=25.17, Percentile=1th → Implied: $261.84
- **ev_revenue:** Current=4.68, Median=6.49, Percentile=2th → Implied: $206.11
- **Sanity check:** PASS
- *Time: 3.6s*

#### Summary / Football Field
- **DCF:** $62.12 (range: $41.86 — $127.46)
- **DDM (Gordon):** $113.92 (range: $41.10 — $827.81)
- **DDM (2-Stage):** $60.01 (range: $36.07 — $227.12)
- **Comps:** $256.05 (range: $234.51 — $336.57)
- **Historical:** $261.84 (range: $206.11 — $332.49)
- **Consensus (median):** $113.92
- **Full range:** $36.07 — $827.81
- **Overall upside:** -23.5%

---

### 7203.T — Toyota Motor
**Market Price:** 3,255.00 JPY | **Market Cap:** $42.42T | **Currency:** JPY

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- rf: FAIL — 4.3% (US 10Y)
- Rf: 4.3% (US 10Y)
- *Fetch time: 0.4s*

#### DCF
- **Assumptions:** Rev growth: 6.0% -> 3.2%, EBIT margin: 13.0%, Tax: 25.3%
- **WACC:** 3.8% (Ke: 7.0%, Beta: 0.57)
- **Terminal growth:** 2.5% | TV as % of EV: 95.0%
- **Enterprise Value:** $121.90T
- **Implied share price:** $6,992.84
- **Upside/Downside:** +114.8%
- **Sensitivity range:** $437.39 — $46,050.22
- Warning: Terminal value is 95% of EV — consider whether growth/WACC assumptions are realistic
- **Sanity check:** PASS
- *Time: 0.0s*

#### DDM
- **Current DPS:** $95.00 | Ke: 7.0%
- **Dividend history:** 27 years paying, 6 years increasing
- **DPS CAGR:** 3Y=21.5%, 5Y=16.1%, 10Y=7.8%
- **Gordon Growth:** g=6.0% → **$9,698.92** (+198.0%)
- **2-Stage DDM:** g1=8.0%, g2=3.0% → **$3,021.86** (-7.2%)
- **Gordon sensitivity:** $1,960.99 — $268,165.19
- **2-Stage sensitivity:** $1,599.51 — $300,121.77
- **Sanity check:** PASS
- *Time: 0.1s*

#### Comps
- **Peers (6, GICS):** F, GM, TSLA, RNO.PA, STLAP.PA, ATD.TO
- **Median trailing_pe:** 22.18x → Implied: $6,302.77 (+93.6%)
- **Median ev_ebitda:** 13.98x → Implied: $4,696.36 (+44.3%)
- **Median ev_revenue:** 1.01x → Implied: $1,932.93 (-40.6%)
- **Sanity check:** PASS
- *Time: 0.0s*

#### Historical Multiples
- **Data source:** Yahoo Finance | Period: 2023-04-06 to 2026-04-03 (732 trading days)
- **pe:** Current=11.48, Median=8.68, Percentile=67th → Implied: $2,461.19
- **ev_ebitda:** Current=9.23, Median=7.45, Percentile=74th → Implied: $2,232.38
- **ev_revenue:** Current=1.37, Median=1.35, Percentile=54th → Implied: $3,188.36
- **Sanity check:** PASS
- *Time: 3.9s*

#### Summary / Football Field
- **DCF:** $6,992.84 (range: $437.39 — $46,050.22)
- **DDM (Gordon):** $9,698.92 (range: $1,960.99 — $268,165.19)
- **DDM (2-Stage):** $3,021.86 (range: $1,599.51 — $300,121.77)
- **Comps:** $4,696.36 (range: $1,932.93 — $6,302.77)
- **Historical:** $2,461.19 (range: $2,232.38 — $3,188.36)
- **Consensus (median):** $4,696.36
- **Full range:** $437.39 — $300,121.77
- **Overall upside:** +44.3%

---

### 005930.KS — Samsung Electronics
**Market Price:** 186,200.00 KRW | **Market Cap:** $1244.95T | **Currency:** KRW

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- rf: FAIL — 4.3% (US 10Y)
- Rf: 4.3% (US 10Y)
- *Fetch time: 0.3s*

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
- **Gordon sensitivity:** $19,446.27 — $49,051.95
- **2-Stage sensitivity:** $12,226.75 — $25,418.04
- **Sanity check:** ISSUES
  - Implied price is 0.08x current — very low
- *Time: 0.1s*

#### Comps
- **Peers (6, GICS):** AAPL, DELL, HPE, HPQ, NTAP, SNDK
- **Median trailing_pe:** 18.71x → Implied: N/A ()
- **Median ev_ebitda:** 11.56x → Implied: $192,729.76 (+3.5%)
- **Median ev_revenue:** 2.19x → Implied: $141,553.22 (-24.0%)
- **Sanity check:** PASS
- *Time: 0.0s*

#### Historical Multiples
- **Data source:** Yahoo Finance | Period: 2023-04-06 to 2026-04-03 (665 trading days)
- **pe:** Current=28.13, Median=17.93, Percentile=72th → Implied: $118,694.15
- **ev_ebitda:** Current=11.53, Median=5.21, Percentile=96th → Implied: $91,415.90
- **ev_revenue:** Current=3.47, Median=1.33, Percentile=97th → Implied: $79,612.65
- **Sanity check:** PASS
- *Time: 3.7s*

#### Summary / Football Field
- **DCF:** $45,839.54 (range: $33,805.48 — $75,301.43)
- **DDM (Gordon):** $26,121.15 (range: $19,446.27 — $49,051.95)
- **DDM (2-Stage):** $15,434.71 (range: $12,226.75 — $25,418.04)
- **Comps:** $167,141.49 (range: $141,553.22 — $192,729.76)
- **Historical:** $91,415.90 (range: $79,612.65 — $118,694.15)
- **Consensus (median):** $45,839.54
- **Full range:** $12,226.75 — $192,729.76
- **Overall upside:** -75.4%

---

### 0700.HK — Tencent Holdings
**Market Price:** 489.20 HKD | **Market Cap:** $4.42T | **Currency:** HKD

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- rf: FAIL — 4.3% (US 10Y)
- Rf: 4.3% (US 10Y)
- *Fetch time: 0.3s*

#### DCF
- **Assumptions:** Rev growth: 6.0% -> 3.2%, EBIT margin: 38.1%, Tax: 18.6%
- **WACC:** 8.0% (Ke: 8.4%, Beta: 0.87)
- **Terminal growth:** 2.5% | TV as % of EV: 77.3%
- **Enterprise Value:** $3.62T
- **Implied share price:** $367.08
- **Upside/Downside:** -25.0%
- **Sensitivity range:** $233.91 — $814.00
- Warning: Terminal value is 77% of EV — high forecast uncertainty
- **Sanity check:** PASS
- *Time: 0.0s*

#### DDM
- **Current DPS:** $5.30 | Ke: 8.4%
- **Dividend history:** 18 years paying, 3 years increasing
- **DPS CAGR:** 3Y=41.2%, 5Y=30.3%, 10Y=28.7%
- **Gordon Growth:** g=6.0% → **$229.60** (-53.1%)
- **2-Stage DDM:** g1=8.0%, g2=3.0% → **$124.35** (-74.6%)
- **Gordon sensitivity:** $85.50 — $1,280.61
- **2-Stage sensitivity:** $75.45 — $441.18
- **Sanity check:** PASS
- *Time: 0.1s*

#### Comps
- **Peers (5, GICS):** GOOGL, GOOG, META, BCE.TO, T.TO
- **Median trailing_pe:** 24.89x → Implied: $682.99 (+39.6%)
- **Median ev_ebitda:** 14.30x → Implied: $437.40 (-10.6%)
- **Median ev_revenue:** 7.25x → Implied: $605.24 (+23.7%)
- **Sanity check:** PASS
- *Time: 0.6s*

#### Historical Multiples
- **Data source:** Yahoo Finance | Period: 2023-04-06 to 2026-04-02 (734 trading days)
- **pe:** Current=79.85, Median=24.34, Percentile=83th → Implied: $149.12
- **ev_ebitda:** Current=19.71, Median=14.27, Percentile=100th → Implied: $98.24
- **ev_revenue:** Current=24.73, Median=6.13, Percentile=83th → Implied: $111.32
- **Sanity check:** PASS
- *Time: 4.6s*

#### Summary / Football Field
- **DCF:** $367.08 (range: $233.91 — $814.00)
- **DDM (Gordon):** $229.60 (range: $85.50 — $1,280.61)
- **DDM (2-Stage):** $124.35 (range: $75.45 — $441.18)
- **Comps:** $605.24 (range: $437.40 — $682.99)
- **Historical:** $111.32 (range: $98.24 — $149.12)
- **Consensus (median):** $229.60
- **Full range:** $75.45 — $1,280.61
- **Overall upside:** -53.1%

---

### JNJ — Johnson & Johnson
**Market Price:** $243.04 | **Market Cap:** $585.70B | **Currency:** USD

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- rf: FAIL — 4.3% (US 10Y)
- Rf: 4.3% (US 10Y)
- *Fetch time: 0.3s*

#### DDM
- **Current DPS:** $5.20 | Ke: 6.9%
- **Dividend history:** 64 years paying, 63 years increasing
- **DPS CAGR:** 3Y=4.9%, 5Y=5.2%, 10Y=5.7%
- **Gordon Growth:** g=5.2% → **$321.80** (+32.4%)
- **2-Stage DDM:** g1=5.2%, g2=3.0% → **$149.96** (-38.3%)
- **Gordon sensitivity:** $94.18 — $2,778.78
- **2-Stage sensitivity:** $79.05 — $1,253.22
- **Sanity check:** PASS
- *Time: 0.1s*

#### Comps
- **Peers (6, GICS):** ABBV, AMGN, BIIB, BMY, GILD, INCY
- **Median trailing_pe:** 20.38x → Implied: $224.78 (-7.5%)
- **Median ev_ebitda:** 11.90x → Implied: $155.01 (-36.2%)
- **Median ev_revenue:** 4.82x → Implied: $176.38 (-27.4%)
- **Sanity check:** PASS
- *Time: 0.0s*

#### Historical Multiples
- **Data source:** SEC EDGAR | Period: 2023-04-06 to 2026-04-02 (750 trading days)
- **pe:** Current=21.85, Median=18.31, Percentile=65th → Implied: $202.02
- **ev_ebitda:** Current=14.61, Median=14.39, Percentile=55th → Implied: $228.48
- **ev_revenue:** Current=6.22, Median=4.36, Percentile=98th → Implied: $160.10
- **Sanity check:** PASS
- *Time: 70.3s*

#### Summary / Football Field
- **DDM (Gordon):** $321.80 (range: $94.18 — $2,778.78)
- **DDM (2-Stage):** $149.96 (range: $79.05 — $1,253.22)
- **Comps:** $176.38 (range: $155.01 — $224.78)
- **Historical:** $202.02 (range: $160.10 — $228.48)
- **Consensus (median):** $189.20
- **Full range:** $79.05 — $2,778.78
- **Overall upside:** -22.2%

---

### KO — Coca-Cola Co
**Market Price:** $76.72 | **Market Cap:** $330.21B | **Currency:** USD

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- rf: FAIL — 4.3% (US 10Y)
- Rf: 4.3% (US 10Y)
- *Fetch time: 0.3s*

#### DDM
- **Current DPS:** $2.06 | Ke: 7.1%
- **Dividend history:** 64 years paying, 23 years increasing
- **DPS CAGR:** 3Y=5.0%, 5Y=4.5%, 10Y=4.4%
- **Gordon Growth:** g=4.5% → **$83.11** (+8.3%)
- **2-Stage DDM:** g1=4.5%, g2=3.0% → **$55.92** (-27.1%)
- **Gordon sensitivity:** $32.03 — $2,457.60
- **2-Stage sensitivity:** $29.91 — $4,135.30
- **Sanity check:** PASS
- *Time: 0.1s*

#### Comps
- **Peers (6, GICS):** KDP, MNST, PEP, DOL.TO, WN.TO, L.TO
- **Median trailing_pe:** 33.55x → Implied: $101.99 (+32.9%)
- **Median ev_ebitda:** 12.99x → Implied: $41.08 (-46.5%)
- **Median ev_revenue:** 2.96x → Implied: $25.49 (-66.8%)
- **Sanity check:** PASS
- *Time: 0.0s*

#### Historical Multiples
- **Data source:** SEC EDGAR | Period: 2023-04-06 to 2026-04-02 (750 trading days)
- **pe:** Current=25.17, Median=24.09, Percentile=68th → Implied: $73.21
- **ev_ebitda:** Current=22.28, Median=22.52, Percentile=48th → Implied: $69.96
- **ev_revenue:** Current=6.88, Median=6.08, Percentile=88th → Implied: $60.20
- **Sanity check:** PASS
- *Time: 61.1s*

#### Summary / Football Field
- **DDM (Gordon):** $83.11 (range: $32.03 — $2,457.60)
- **DDM (2-Stage):** $55.92 (range: $29.91 — $4,135.30)
- **Comps:** $41.08 (range: $25.49 — $101.99)
- **Historical:** $69.96 (range: $60.20 — $73.21)
- **Consensus (median):** $62.94
- **Full range:** $25.49 — $4,135.30
- **Overall upside:** -18.0%

---

### PG — Procter & Gamble
**Market Price:** $143.12 | **Market Cap:** $334.43B | **Currency:** USD

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- rf: FAIL — 4.3% (US 10Y)
- Rf: 4.3% (US 10Y)
- *Fetch time: 0.3s*

#### DDM
- **Current DPS:** $4.23 | Ke: 7.2%
- **Dividend history:** 64 years paying, 22 years increasing
- **DPS CAGR:** 3Y=5.0%, 5Y=6.0%, 10Y=4.7%
- **Gordon Growth:** g=6.0% → **$378.53** (+164.5%)
- **2-Stage DDM:** g1=6.0%, g2=3.0% → **$119.06** (-16.8%)
- **Gordon sensitivity:** $84.85 — $2,475.56
- **2-Stage sensitivity:** $64.44 — $2,525.65
- **Sanity check:** PASS
- *Time: 0.2s*

#### Comps
- **Peers (6, GICS):** CHD, CLX, CL, EL, KVUE, KMB
- **Median trailing_pe:** 22.55x → Implied: $152.46 (+6.5%)
- **Median ev_ebitda:** 13.36x → Implied: $131.28 (-8.3%)
- **Median ev_revenue:** 2.52x → Implied: $81.29 (-43.2%)
- **Sanity check:** PASS
- *Time: 0.0s*

#### Historical Multiples
- **Data source:** SEC EDGAR | Period: 2023-04-06 to 2026-04-02 (750 trading days)
- **pe:** Current=21.14, Median=24.40, Percentile=5th → Implied: $165.19
- **ev_ebitda:** Current=15.69, Median=17.65, Percentile=9th → Implied: $161.77
- **ev_revenue:** Current=4.25, Median=4.60, Percentile=13th → Implied: $155.30
- **Sanity check:** PASS
- *Time: 84.8s*

#### Summary / Football Field
- **DDM (Gordon):** $378.53 (range: $84.85 — $2,475.56)
- **DDM (2-Stage):** $119.06 (range: $64.44 — $2,525.65)
- **Comps:** $131.28 (range: $81.29 — $152.46)
- **Historical:** $161.77 (range: $155.30 — $165.19)
- **Consensus (median):** $146.53
- **Full range:** $64.44 — $2,525.65
- **Overall upside:** +2.4%

---

## Errors and Issues

No errors detected.

## Performance

| Ticker | Data | DCF | DDM | Comps | Historical | Total |
|--------|------|-----|-----|-------|------------|-------|
| AAPL | 0.6s | 0.0s | 0.1s | 0.0s | 64.5s | 65.3s |
| JPM | 0.3s | 0.0s | 0.1s | 0.0s | 60.9s | 61.4s |
| XOM | 0.3s | 0.0s | 0.1s | 0.0s | 60.5s | 61.0s |
| NESN.SW | 0.3s | 0.0s | 0.2s | 0.0s | 3.4s | 4.0s |
| SHEL.L | 0.3s | 0.0s | 0.1s | 0.0s | 4.0s | 4.5s |
| SAP.DE | 0.3s | 0.0s | 0.1s | 0.0s | 3.6s | 4.1s |
| 7203.T | 0.4s | 0.0s | 0.1s | 0.0s | 3.9s | 4.4s |
| 005930.KS | 0.3s | 0.0s | 0.1s | 0.0s | 3.7s | 4.2s |
| 0700.HK | 0.3s | 0.0s | 0.1s | 0.6s | 4.6s | 5.7s |
| JNJ | 0.3s | 0.0s | 0.1s | 0.0s | 70.3s | 70.8s |
| KO | 0.3s | 0.0s | 0.1s | 0.0s | 61.1s | 61.6s |
| PG | 0.3s | 0.0s | 0.2s | 0.0s | 84.8s | 85.4s |

## Conclusions

**Working well:** AAPL, JPM, XOM, NESN.SW, SHEL.L, SAP.DE, 7203.T, 005930.KS, 0700.HK, JNJ, KO, PG

## Changes Since v2

1. **Rf reverted to ^TNX:** All companies use US 10Y Treasury. Country risk via CRP (Damodaran).
2. **DCF/DDM/Comps currency conversion:** Implied prices now converted to listing currency via price_factor (fixes SHEL.L showing USD)
3. **100x sensitivity cap:** Gordon/2-Stage sensitivity values >100x current price excluded as asymptotic

---
*Report generated 2026-04-04 12:58 by test_all_valuations.py (v3)*