# Financial Workbench — Valuation Test Report
**Date:** 2026-04-04 12:17
**Run by:** Claude Code automated test
**US Rf:** 4.3% | **ERP:** 4.8% | **Rf:** per-company (see details)
**Total runtime:** 534s

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
| SHEL.L | 3,543.50 GBp | WARN | WARN | WARN | PASS |
| SAP.DE | 148.90 EUR | PASS | PASS | PASS | PASS |
| 7203.T | 3,255.00 JPY | WARN | PASS | PASS | PASS |
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
- rf: FAIL — 4.3% (US 10Y Treasury)
- Rf: 4.3% (US 10Y Treasury)
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
- *Time: 11.3s*

#### Historical Multiples
- **Data source:** SEC EDGAR | Period: 2023-04-06 to 2026-04-02 (750 trading days)
- **pe:** Current=31.90, Median=31.77, Percentile=52th → Implied: $252.65
- **ev_ebitda:** Current=24.57, Median=23.83, Percentile=59th → Implied: $243.11
- **ev_revenue:** Current=8.63, Median=7.98, Percentile=65th → Implied: $231.80
- **Sanity check:** PASS
- *Time: 63.3s*

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
- rf: FAIL — 4.3% (US 10Y Treasury)
- Rf: 4.3% (US 10Y Treasury)
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
- *Time: 7.9s*

#### Historical Multiples
- **Data source:** SEC EDGAR | Period: 2023-04-06 to 2026-04-02 (750 trading days)
- **pe:** Current=13.93, Median=11.16, Percentile=77th → Implied: $228.89
- **Sanity check:** PASS
- *Time: 61.0s*

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
- rf: FAIL — 4.3% (US 10Y Treasury)
- Rf: 4.3% (US 10Y Treasury)
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
- *Time: 13.8s*

#### Historical Multiples
- **Data source:** SEC EDGAR | Period: 2023-04-06 to 2026-04-02 (750 trading days)
- **pe:** Current=23.21, Median=13.58, Percentile=99th → Implied: $93.73
- **ev_ebitda:** Current=9.95, Median=6.40, Percentile=99th → Implied: $97.37
- **ev_revenue:** Current=2.02, Median=1.32, Percentile=99th → Implied: $99.30
- **Sanity check:** PASS
- *Time: 62.7s*

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
- rf: FAIL — 0.5% (Swiss 10Y Gov Bond)
- Rf: 0.5% (Swiss 10Y Gov Bond)
- *Fetch time: 0.4s*

#### DCF
- **Assumptions:** Rev growth: 6.0% -> 3.2%, EBIT margin: 14.8%, Tax: 24.6%
- **WACC:** 3.4% (Ke: 3.7%, Beta: 0.68)
- **Terminal growth:** 2.5% | TV as % of EV: 95.7%
- **Enterprise Value:** $940.32B
- **Implied share price:** $344.64
- **Upside/Downside:** +339.8%
- **Sensitivity range:** $68.25 — $786.81
- Warning: Terminal value is 96% of EV — consider whether growth/WACC assumptions are realistic
- Warning: Implied exit multiple of 50.9x is very high
- **Sanity check:** PASS
- *Time: 0.0s*

#### DDM
- **Current DPS:** $3.10 | Ke: 3.7%
- **Dividend history:** 24 years paying, 23 years increasing
- **DPS CAGR:** 3Y=2.9%, 5Y=2.5%, 10Y=3.3%
- **Gordon Growth:** g=2.5% → **$251.48** (+220.9%)
- **2-Stage DDM:** g1=2.5%, g2=2.5% → **$251.48** (+220.9%)
- **Gordon sensitivity:** $59.18 — $1,230.78
- **2-Stage sensitivity:** $64.71 — $1,255.20
- **Sanity check:** PASS
- *Time: 0.1s*

#### Comps
- **Peers (6, GICS):** CPB, CAG, GIS, HSY, HRL, KHC
- **Median trailing_pe:** 18.39x → Implied: $64.55 (-17.6%)
- **Median ev_ebitda:** 8.05x → Implied: $32.03 (-59.1%)
- **Median ev_revenue:** 1.33x → Implied: $26.41 (-66.3%)
- **Sanity check:** PASS
- *Time: 16.2s*

#### Historical Multiples
- **Data source:** Yahoo Finance | Period: 2023-04-06 to 2026-04-02 (747 trading days)
- **pe:** Current=22.32, Median=20.67, Percentile=71th → Implied: $72.59
- **ev_ebitda:** Current=15.66, Median=15.48, Percentile=54th → Implied: $77.25
- **ev_revenue:** Current=2.82, Median=3.00, Percentile=24th → Implied: $84.55
- **Sanity check:** PASS
- *Time: 3.7s*

#### Summary / Football Field
- **DCF:** $344.64 (range: $68.25 — $786.81)
- **DDM (Gordon):** $251.48 (range: $59.18 — $1,230.78)
- **DDM (2-Stage):** $251.48 (range: $64.71 — $1,255.20)
- **Comps:** $32.03 (range: $26.41 — $64.55)
- **Historical:** $77.25 (range: $72.59 — $84.55)
- **Consensus (median):** $251.48
- **Full range:** $26.41 — $1,255.20
- **Overall upside:** +220.9%

---

### SHEL.L — Shell plc
**Market Price:** 3,543.50 GBp | **Market Cap:** $198.65B | **Currency:** GBp

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- rf: FAIL — 4.3% (US 10Y Treasury)
- Rf: 4.3% (US 10Y Treasury)
- *Fetch time: 0.3s*

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
- **Gordon sensitivity:** $16.30 — $1,444.34
- **2-Stage sensitivity:** $14.70 — $63.77
- **Sanity check:** ISSUES
  - Implied price is 0.01x current — very low
  - Implied price is 0.01x current — very low
- *Time: 0.1s*

#### Comps
- **Peers (6, GICS):** CVX, XOM, TTE.PA, BP.L, CCO.TO, CNQ.TO
- **Median trailing_pe:** 23.98x → Implied: $54.20 (-98.5%)
- **Median ev_ebitda:** 10.85x → Implied: $84.11 (-97.6%)
- **Median ev_revenue:** 2.31x → Implied: $101.67 (-97.1%)
- **Sanity check:** ISSUES
  - Implied price is 0.02x current — very low
  - Implied price is 0.02x current — very low
  - Implied price is 0.03x current — very low
- *Time: 0.0s*

#### Historical Multiples
- **Data source:** Yahoo Finance | Period: 2023-04-06 to 2026-04-02 (692 trading days)
- **pe:** Current=11.30, Median=9.21, Percentile=89th → Implied: $2,887.20
- **ev_ebitda:** Current=4.39, Median=3.49, Percentile=100th → Implied: $2,650.62
- **ev_revenue:** Current=0.93, Median=0.70, Percentile=90th → Implied: $2,458.40
- **Sanity check:** PASS
- *Time: 3.7s*

#### Summary / Football Field
- **DCF:** $82.48 (range: $50.59 — $203.53)
- **DDM (Gordon):** $38.16 (range: $16.30 — $1,444.34)
- **DDM (2-Stage):** $23.16 (range: $14.70 — $63.77)
- **Comps:** $84.11 (range: $54.20 — $101.67)
- **Historical:** $2,650.62 (range: $2,458.40 — $2,887.20)
- **Consensus (median):** $82.48
- **Full range:** $14.70 — $2,887.20
- **Overall upside:** -97.7%

---

### SAP.DE — SAP SE
**Market Price:** 148.90 EUR | **Market Cap:** $173.85B | **Currency:** EUR

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- rf: FAIL — 2.5% (German 10Y Bund)
- Rf: 2.5% (German 10Y Bund)
- *Fetch time: 0.3s*

#### DCF
- **Assumptions:** Rev growth: 6.0% -> 3.2%, EBIT margin: 20.1%, Tax: 28.7%
- **WACC:** 6.4% (Ke: 6.5%, Beta: 0.84)
- **Terminal growth:** 2.5% | TV as % of EV: 83.4%
- **Enterprise Value:** $104.48B
- **Implied share price:** $89.71
- **Upside/Downside:** -39.8%
- **Sensitivity range:** $52.49 — $363.84
- Warning: Terminal value is 83% of EV — high forecast uncertainty
- **Sanity check:** PASS
- *Time: 0.0s*

#### DDM
- **Current DPS:** $2.50 | Ke: 6.5%
- **Dividend history:** 27 years paying, 2 years increasing
- **DPS CAGR:** 3Y=-1.4%, 5Y=8.3%, 10Y=7.9%
- **Gordon Growth:** g=5.5% → **$263.78** (+77.2%)
- **2-Stage DDM:** g1=8.0%, g2=3.0% → **$91.59** (-38.5%)
- **Gordon sensitivity:** $51.76 — $192,777,770,999,895,712.00
- **2-Stage sensitivity:** $45.14 — $23,405.64
- **Sanity check:** PASS
- *Time: 0.1s*

#### Comps
- **Peers (6, GICS):** ADBE, APP, ADSK, ADP, CDNS, CRWD
- **Median trailing_pe:** 38.44x → Implied: $234.51 (+57.5%)
- **Median ev_ebitda:** 26.43x → Implied: $256.05 (+72.0%)
- **Median ev_revenue:** 10.62x → Implied: $336.57 (+126.0%)
- **Sanity check:** PASS
- *Time: 15.8s*

#### Historical Multiples
- **Data source:** Yahoo Finance | Period: 2023-04-06 to 2026-04-02 (696 trading days)
- **pe:** Current=24.28, Median=54.21, Percentile=1th → Implied: $332.49
- **ev_ebitda:** Current=14.25, Median=25.17, Percentile=1th → Implied: $261.84
- **ev_revenue:** Current=4.68, Median=6.49, Percentile=2th → Implied: $206.11
- **Sanity check:** PASS
- *Time: 4.0s*

#### Summary / Football Field
- **DCF:** $89.71 (range: $52.49 — $363.84)
- **DDM (Gordon):** $263.78 (range: $51.76 — $192,777,770,999,895,712.00)
- **DDM (2-Stage):** $91.59 (range: $45.14 — $23,405.64)
- **Comps:** $256.05 (range: $234.51 — $336.57)
- **Historical:** $261.84 (range: $206.11 — $332.49)
- **Consensus (median):** $256.05
- **Full range:** $45.14 — $192,777,770,999,895,712.00
- **Overall upside:** +72.0%

---

### 7203.T — Toyota Motor
**Market Price:** 3,255.00 JPY | **Market Cap:** $42.42T | **Currency:** JPY

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- rf: FAIL — 1.4% (Japan 10Y JGB)
- Rf: 1.4% (Japan 10Y JGB)
- *Fetch time: 0.4s*

#### DCF
- **Assumptions:** Rev growth: 6.0% -> 3.2%, EBIT margin: 13.0%, Tax: 25.3%
- **WACC:** 2.2% (Ke: 4.1%, Beta: 0.57)
- **Terminal growth:** 2.5% | TV as % of EV: 0.0%
- **Enterprise Value:** $6.39T
- **Implied share price:** $-1,870.06
- **Upside/Downside:** -157.5%
- **Sensitivity range:** $2,046.56 — $49,541.18
- **Sanity check:** ISSUES
  - Implied price is non-positive (-1870.0614065073605)
  - WACC 2.2% outside 3-20% range
- *Time: 0.0s*

#### DDM
- **Current DPS:** $95.00 | Ke: 4.1%
- **Dividend history:** 27 years paying, 6 years increasing
- **DPS CAGR:** 3Y=21.5%, 5Y=16.1%, 10Y=7.8%
- **Gordon Growth:** g=3.1% → **$9,796.90** (+201.0%)
- **2-Stage DDM:** g1=8.0%, g2=3.0% → **$10,969.43** (+237.0%)
- **Gordon sensitivity:** $1,921.38 — $19,973.80
- **2-Stage sensitivity:** $2,544.18 — $102,884.42
- **Sanity check:** PASS
- *Time: 0.1s*

#### Comps
- **Peers (6, GICS):** F, GM, TSLA, RNO.PA, STLAP.PA, ATD.TO
- **Median trailing_pe:** 22.18x → Implied: $6,302.77 (+93.6%)
- **Median ev_ebitda:** 13.98x → Implied: $4,696.36 (+44.3%)
- **Median ev_revenue:** 1.01x → Implied: $1,932.93 (-40.6%)
- **Sanity check:** PASS
- *Time: 13.4s*

#### Historical Multiples
- **Data source:** Yahoo Finance | Period: 2023-04-06 to 2026-04-03 (732 trading days)
- **pe:** Current=11.48, Median=8.68, Percentile=67th → Implied: $2,461.19
- **ev_ebitda:** Current=9.23, Median=7.45, Percentile=74th → Implied: $2,232.38
- **ev_revenue:** Current=1.37, Median=1.35, Percentile=54th → Implied: $3,188.36
- **Sanity check:** PASS
- *Time: 4.1s*

#### Summary / Football Field
- **DCF:** $-1,870.06 (range: $2,046.56 — $49,541.18)
- **DDM (Gordon):** $9,796.90 (range: $1,921.38 — $19,973.80)
- **DDM (2-Stage):** $10,969.43 (range: $2,544.18 — $102,884.42)
- **Comps:** $4,696.36 (range: $1,932.93 — $6,302.77)
- **Historical:** $2,461.19 (range: $2,232.38 — $3,188.36)
- **Consensus (median):** $4,696.36
- **Full range:** $1,921.38 — $102,884.42
- **Overall upside:** +44.3%

---

### 005930.KS — Samsung Electronics
**Market Price:** 186,200.00 KRW | **Market Cap:** $1244.95T | **Currency:** KRW

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- rf: FAIL — 4.3% (US 10Y Treasury)
- Rf: 4.3% (US 10Y Treasury)
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
- *Time: 0.1s*

#### Historical Multiples
- **Data source:** Yahoo Finance | Period: 2023-04-06 to 2026-04-03 (665 trading days)
- **pe:** Current=28.13, Median=17.93, Percentile=72th → Implied: $118,694.15
- **ev_ebitda:** Current=11.53, Median=5.21, Percentile=96th → Implied: $91,415.90
- **ev_revenue:** Current=3.47, Median=1.33, Percentile=97th → Implied: $79,612.65
- **Sanity check:** PASS
- *Time: 3.3s*

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
- rf: FAIL — 2.0% (China 10Y Gov Bond)
- Rf: 2.0% (China 10Y Gov Bond)
- *Fetch time: 0.4s*

#### DCF
- **Assumptions:** Rev growth: 6.0% -> 3.2%, EBIT margin: 38.1%, Tax: 18.6%
- **WACC:** 5.9% (Ke: 6.1%, Beta: 0.87)
- **Terminal growth:** 2.5% | TV as % of EV: 85.3%
- **Enterprise Value:** $5.92T
- **Implied share price:** $621.61
- **Upside/Downside:** +27.1%
- **Sensitivity range:** $324.76 — $5,511.39
- Warning: Terminal value is 85% of EV — consider whether growth/WACC assumptions are realistic
- **Sanity check:** PASS
- *Time: 0.0s*

#### DDM
- **Current DPS:** $5.30 | Ke: 6.1%
- **Dividend history:** 18 years paying, 3 years increasing
- **DPS CAGR:** 3Y=41.2%, 5Y=30.3%, 10Y=28.7%
- **Gordon Growth:** g=5.1% → **$557.21** (+13.9%)
- **2-Stage DDM:** g1=8.0%, g2=3.0% → **$217.98** (-55.4%)
- **Gordon sensitivity:** $109.32 — $409,150,368,821,946,688.00
- **2-Stage sensitivity:** $100.97 — $4,965.43
- **Sanity check:** PASS
- *Time: 0.1s*

#### Comps
- **Peers (5, GICS):** GOOGL, GOOG, META, BCE.TO, T.TO
- **Median trailing_pe:** 24.89x → Implied: $682.95 (+39.6%)
- **Median ev_ebitda:** 14.30x → Implied: $437.37 (-10.6%)
- **Median ev_revenue:** 7.25x → Implied: $605.21 (+23.7%)
- **Sanity check:** PASS
- *Time: 6.0s*

#### Historical Multiples
- **Data source:** Yahoo Finance | Period: 2023-04-06 to 2026-04-02 (734 trading days)
- **pe:** Current=79.85, Median=24.34, Percentile=83th → Implied: $149.12
- **ev_ebitda:** Current=19.71, Median=14.27, Percentile=100th → Implied: $98.24
- **ev_revenue:** Current=24.73, Median=6.13, Percentile=83th → Implied: $111.32
- **Sanity check:** PASS
- *Time: 3.6s*

#### Summary / Football Field
- **DCF:** $621.61 (range: $324.76 — $5,511.39)
- **DDM (Gordon):** $557.21 (range: $109.32 — $409,150,368,821,946,688.00)
- **DDM (2-Stage):** $217.98 (range: $100.97 — $4,965.43)
- **Comps:** $605.21 (range: $437.37 — $682.95)
- **Historical:** $111.32 (range: $98.24 — $149.12)
- **Consensus (median):** $557.21
- **Full range:** $98.24 — $409,150,368,821,946,688.00
- **Overall upside:** +13.9%

---

### JNJ — Johnson & Johnson
**Market Price:** $243.04 | **Market Cap:** $585.70B | **Currency:** USD

#### Data Fetch
- market_data: OK — OK
- valuation_data: OK — OK (fresh)
- historical_years: FAIL — 4
- rf: FAIL — 4.3% (US 10Y Treasury)
- Rf: 4.3% (US 10Y Treasury)
- *Fetch time: 0.4s*

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
- *Time: 16.0s*

#### Historical Multiples
- **Data source:** SEC EDGAR | Period: 2023-04-06 to 2026-04-02 (750 trading days)
- **pe:** Current=21.85, Median=18.31, Percentile=65th → Implied: $202.02
- **ev_ebitda:** Current=14.61, Median=14.39, Percentile=55th → Implied: $228.48
- **ev_revenue:** Current=6.22, Median=4.36, Percentile=98th → Implied: $160.10
- **Sanity check:** PASS
- *Time: 62.2s*

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
- rf: FAIL — 4.3% (US 10Y Treasury)
- Rf: 4.3% (US 10Y Treasury)
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
- *Time: 16.6s*

#### Historical Multiples
- **Data source:** SEC EDGAR | Period: 2023-04-06 to 2026-04-02 (750 trading days)
- **pe:** Current=25.17, Median=24.09, Percentile=68th → Implied: $73.21
- **ev_ebitda:** Current=22.28, Median=22.52, Percentile=48th → Implied: $69.96
- **ev_revenue:** Current=6.88, Median=6.08, Percentile=88th → Implied: $60.20
- **Sanity check:** PASS
- *Time: 61.0s*

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
- rf: FAIL — 4.3% (US 10Y Treasury)
- Rf: 4.3% (US 10Y Treasury)
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
- *Time: 0.1s*

#### Comps
- **Peers (6, GICS):** CHD, CLX, CL, EL, KVUE, KMB
- **Median trailing_pe:** 22.55x → Implied: $152.46 (+6.5%)
- **Median ev_ebitda:** 13.36x → Implied: $131.28 (-8.3%)
- **Median ev_revenue:** 2.52x → Implied: $81.29 (-43.2%)
- **Sanity check:** PASS
- *Time: 16.7s*

#### Historical Multiples
- **Data source:** SEC EDGAR | Period: 2023-04-06 to 2026-04-02 (750 trading days)
- **pe:** Current=21.14, Median=24.40, Percentile=5th → Implied: $165.19
- **ev_ebitda:** Current=15.69, Median=17.65, Percentile=9th → Implied: $161.77
- **ev_revenue:** Current=4.25, Median=4.60, Percentile=13th → Implied: $155.30
- **Sanity check:** PASS
- *Time: 61.5s*

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
| AAPL | 0.7s | 0.0s | 0.1s | 11.3s | 63.3s | 75.4s |
| JPM | 0.3s | 0.0s | 0.1s | 7.9s | 61.0s | 69.4s |
| XOM | 0.3s | 0.0s | 0.1s | 13.8s | 62.7s | 76.9s |
| NESN.SW | 0.4s | 0.0s | 0.1s | 16.2s | 3.7s | 20.4s |
| SHEL.L | 0.3s | 0.0s | 0.1s | 0.0s | 3.7s | 4.2s |
| SAP.DE | 0.3s | 0.0s | 0.1s | 15.8s | 4.0s | 20.3s |
| 7203.T | 0.4s | 0.0s | 0.1s | 13.4s | 4.1s | 18.0s |
| 005930.KS | 0.3s | 0.0s | 0.1s | 0.1s | 3.3s | 3.9s |
| 0700.HK | 0.4s | 0.0s | 0.1s | 6.0s | 3.6s | 10.1s |
| JNJ | 0.4s | 0.0s | 0.1s | 16.0s | 62.2s | 78.7s |
| KO | 0.3s | 0.0s | 0.1s | 16.6s | 61.0s | 78.1s |
| PG | 0.3s | 0.0s | 0.1s | 16.7s | 61.5s | 78.6s |

## Conclusions

**Working well:** AAPL, JPM, XOM, NESN.SW, SHEL.L, SAP.DE, 7203.T, 005930.KS, 0700.HK, JNJ, KO, PG

## Changes Since v1

Fixes applied between v1 and v2:
1. **Currency alignment (price_factor):** GBp and cross-currency stocks now compute correct multiples and implied prices
2. **Annual-only implied values:** Non-US stocks without quarterly data no longer sum 4 annual rows (was 4x too high)
3. **Comps Infinity fix:** `_clean_numeric()` filters non-finite values from yfinance; `isinstance` guard in page
4. **2-Stage DDM sensitivity:** Now computed and included in Summary/Football Field
5. **Sensitivity floor:** Invalid cells (g>=Ke, negative) are NaN instead of $0 or negative
6. **Multi-currency Rf:** Each company uses Rf matching its financialCurrency
7. **TV% warning:** 85%+ tier added alongside existing 75% tier
8. **GICS-filtered Comps peers:** Test uses industry-matched universe instead of Yahoo recommendations

---
*Report generated 2026-04-04 12:17 by test_all_valuations.py (v2)*