# Prompt 3 Verification Report
**Date:** 2026-04-04 11:57

## 1. Multi-Currency Rf

| Currency | Rf | Label | Source |
|----------|-----|-------|--------|
| USD | 4.31% | US 10Y Treasury | yfinance |
| EUR | 2.50% | German 10Y Bund | static default |
| GBP | 4.50% | UK 10Y Gilt | static default |
| JPY | 1.40% | Japan 10Y JGB | static default |
| CHF | 0.50% | Swiss 10Y Gov Bond | static default |
| KRW | 3.00% | Korea 10Y KTB | static default |
| HKD | 4.31% | US 10Y (HKD peg) | yfinance |

### Rf per company

- **AAPL:** financialCurrency=USD, Rf=4.31% (US 10Y Treasury)
  - Currency match: PASS
- **7203.T:** financialCurrency=JPY, Rf=1.40% (Japan 10Y JGB)
  - Currency match: PASS
- **NESN.SW:** financialCurrency=CHF, Rf=0.50% (Swiss 10Y Gov Bond)
  - Currency match: PASS
- **SAP.DE:** financialCurrency=EUR, Rf=2.50% (German 10Y Bund)
  - Currency match: PASS
- **SHEL.L:** financialCurrency=USD, Rf=4.31% (US 10Y Treasury)
  - Currency match: UNEXPECTED (USD)
- **0700.HK:** financialCurrency=CNY, Rf=2.00% (China 10Y Gov Bond)
  - Currency match: UNEXPECTED (CNY)

## 2. Comps Peer Selection (GICS vs Yahoo)

### KO (Beverages - Non-Alcoholic)
- Yahoo recommended: ['PG', 'JNJ', 'DIS', 'VZ', 'JPM']
- GICS-filtered (8): ['KDP', 'MNST', 'PEP', 'DOL.TO', 'WN.TO', 'L.TO', 'MRU.TO', 'SAP.TO']
- Same industry (of top 6): 3/6

### XOM (Oil & Gas Integrated)
- Yahoo recommended: ['CVX', 'JNJ', 'WMT', 'PG', 'PFE']
- GICS-filtered (11): ['CVX', 'TTE.PA', 'CCO.TO', 'CNQ.TO', 'CVE.TO', 'ENB.TO', 'IMO.TO', 'PPL.TO']
- Same industry (of top 6): 3/6

### SAP.DE (Software - Application)
- Yahoo recommended: ['SIE.DE', 'ALV.DE', 'BAS.DE', 'DTE.DE', 'BAYN.DE']
- GICS-filtered (40): ['ADBE', 'APP', 'ADSK', 'ADP', 'CDNS', 'CRWD', 'DDOG', 'FICO']
- Same industry (of top 6): 4/6

## 3. TV% Warning

### 7203.T (Toyota) with JPY Rf=1.40%
- WACC: 2.23%
- TV as % of EV: 0%
- Warnings: []
- TV% is 0% (below 75%, no warning expected)
