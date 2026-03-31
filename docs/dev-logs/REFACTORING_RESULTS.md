# Refactoring Results — Financial Preparation

**Date:** 2026-03-26

---

## 1. Company Classification

All 5 tickers classified correctly:

| Ticker | Sector | Sub-Industry | Expected | Actual | Match | Reason |
|--------|--------|-------------|----------|--------|-------|--------|
| AAPL | Technology | Consumer Electronics | normal | **normal** | OK | Standard operating company |
| JPM | Financial Services | Diversified Banks | financial | **financial** | OK | Financial institution -- revenue from interest/premiums, DCF not appropriate |
| NEE | Utilities | Electric Utilities | dividend_stable | **dividend_stable** | OK | Stable dividend payer -- DDM primary, DCF secondary |
| GOOG | Technology | Internet Content & Info | normal | **normal** | OK | Standard operating company |
| O | Real Estate | REIT - Retail | dividend_stable | **dividend_stable** | OK | Stable dividend payer -- DDM primary, DCF secondary |

### Recommended Methods

| Type | Method(s) | Tickers |
|------|-----------|---------|
| normal | DCF | AAPL, GOOG |
| financial | DDM | JPM |
| dividend_stable | DDM + DCF | NEE, O |

---

## 2. Financial Preparation Results

| Ticker | Source | Years | Flags | EBITDA | Net Debt | FCF |
|--------|--------|-------|-------|--------|----------|-----|
| AAPL | EDGAR | 12 (2014-2025) | 5 | $144.7B | $62.7B | $98.8B |
| JPM | EDGAR | 12 (2014-2025) | 18 | -$18.5B* | -$7.2B | N/A* |
| NEE | EDGAR | 12 (2014-2025) | 15 | $14.9B | $90.9B | $0.3B |
| GOOG | EDGAR | 11 (2015-2025) | 14 | $150.2B | -$80.3B | $73.3B |
| O | EDGAR | 11 (2015-2025) | 11 | $5.1B | $26.3B | N/A** |

*JPM: Negative EBITDA and no FCF are expected -- bank financials don't map to standard IS/CF templates. Standardizer produces garbage margins (200%+ net margin) because bank "revenue" is net interest income, not gross revenue. The classifier correctly flags JPM as "financial" so users see a warning.

**O: No FCF because REIT cash flows don't follow standard OCF-CapEx structure (AFFO is the correct metric for REITs).

### EDGAR Confirmation
All 5 tickers now use **EDGAR** (10+ years) instead of Yahoo (5 years). This was not a code change -- `edgartools` was installed via `pip install edgartools`.

### Derived Fields Verification

| Field | AAPL | GOOG | NEE |
|-------|------|------|-----|
| EBITDA = EBIT + D&A | $133.1B + $11.7B = $144.7B | $129.0B + $21.1B = $150.2B | $10.9B + $4.0B = $14.9B |
| Net Debt = Debt - Cash - STI | $98.7B - $35.9B - ? = $62.7B | $59.3B - $30.7B - $96.1B = -$80.3B (net cash) | $93.1B - $2.2B - ? = $90.9B |
| FCF = OCF - CapEx | $111.5B - $12.7B = $98.8B | $112.6B - $39.3B = $73.3B | $3.0B - $2.7B = $0.3B |

---

## 3. Tab Flow Verification

### DCF Tab
- AAPL/GOOG: Normal DCF flow, Steps 2-6 placeholders shown
- JPM: **Warning displayed**: "DCF is not recommended for financial institutions..."
- NEE/O: Normal flow (DCF is secondary method but still available)

### DDM Tab
- JPM: **"DDM is the recommended method"** (financial)
- NEE/O: **"DDM is the recommended method"** (dividend_stable)
- AAPL/GOOG: "DDM is not the primary method"

### Other Tabs
- Comps: Shows classification type, placeholder
- Historical: Placeholder
- Summary: Placeholder

### Data Flow
All tabs receive `prepared_data` from `st.session_state["prepared_data"]`. No tab loads its own data.

---

## 4. Dependency Diagram

```
User enters ticker
       |
       v
pages/3_valuation.py
       |
       |-- get_company(ticker)     --> Company model
       |-- get_valuation_data()    --> Risk-free rate, etc.
       |
       v
pages/valuation/preparation.py     <-- NEW: Financial Preparation
       |
       |-- get_raw_statements()    --> lib/data/historical.py (EDGAR/Yahoo)
       |-- get_standardized_history() --> lib/data/standardizer.py
       |-- build_income_table()    --> lib/analysis/historical.py
       |-- build_balance_table()
       |-- build_cashflow_table()
       |-- build_ratios_table()    --> lib/analysis/historical_ratios.py
       |-- detect_flags()          --> lib/analysis/flags.py (15 rules)
       |-- compute_averages()      --> lib/analysis/historical_averages.py
       |-- classify_company()      --> lib/analysis/company_classifier.py  <-- NEW
       |
       v
st.session_state["prepared_data"]
       |
       |-- UI: Classification banner
       |-- UI: Flags display
       |-- UI: 3yr Averages dashboard
       |-- UI: Revenue/FCF + Margin charts
       |-- UI: Raw Financials (collapsible)
       |-- UI: Standardized Financials (collapsible)
       |-- UI: Key Ratios (collapsible)
       |
       v
Valuation Tabs (all receive prepared_data)
       |
       |-- DCF Tab      --> pages/valuation/dcf_tab.py
       |                     (Steps 2-6, no data loading)
       |                     (warns if type == "financial")
       |
       |-- Comps Tab    --> pages/valuation/comps_tab.py
       |
       |-- DDM Tab      --> pages/valuation/ddm_tab.py
       |                     (recommended if financial/dividend_stable)
       |
       |-- Historical   --> pages/valuation/historical_tab.py
       |
       |-- Summary      --> pages/valuation/summary_tab.py
```

---

## 5. Files Deleted

| File | Reason |
|------|--------|
| `pages/valuation/dcf_step1_historical.py` | Moved to preparation.py + preparation_display.py |
| `pages/valuation/dcf_step1_flags.py` | Moved to preparation.py (new flag format) |
| `pages/valuation/dcf_step1_overrides.py` | Moved to preparation.py (will be rebuilt with DCF Steps 2-6) |
| `pages/valuation/dcf_step1_standardized.py` | Moved to preparation_display.py |
| `pages/valuation/dcf_step1_ratios.py` | Moved to preparation_display.py |
| `pages/valuation/dcf_step1_charts.py` | Moved to preparation_display.py |
| `lib/analysis/valuation.py` | V1 dead code -- crashed on import (used deleted dataclasses) |
| `pages/valuation/*.tmp.*` | Temporary files from previous edits |

**Verified:** No remaining imports reference any deleted file. `grep` for `dcf_step1_` and `from lib.analysis.valuation import` in `pages/` returns zero matches.

---

## 6. New Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `lib/analysis/company_classifier.py` | 62 | 3-category classifier (normal/financial/dividend_stable) |
| `pages/valuation/preparation.py` | 160 | Financial Preparation orchestrator + flag/avg display |
| `pages/valuation/preparation_display.py` | 199 | Charts, raw tables, standardized tables, ratios display |

---

## 7. Files Modified

| File | Change |
|------|--------|
| `pages/3_valuation.py` | New flow: Preparation -> Tabs. Removed fin_data loading. |
| `pages/valuation/dcf_tab.py` | Removed _load_step1_data, now receives prepared_data. Shows financial warning. |
| `pages/valuation/comps_tab.py` | New signature: render(prepared, ticker). Shows classification. |
| `pages/valuation/ddm_tab.py` | New signature: render(prepared, ticker). Shows method recommendation. |
| `pages/valuation/historical_tab.py` | New signature: render(prepared, ticker). |
| `pages/valuation/summary_tab.py` | New signature: render(prepared, ticker). |
