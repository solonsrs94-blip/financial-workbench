# Financial Workbench — Project Status Report V2

**Generated:** 2026-03-31 | **Updated:** 2026-04-04 (valuation testing complete)
**Branch:** master (main branch: main)
**Total project lines:** 10,255 (excluding scripts, venv, data, __pycache__)
**Total with scripts:** 13,702

---

## 1. Complete File Inventory

### app.py (Entry Point)
| File | Lines | Status |
|------|------:|--------|
| `app.py` | 35 | Active — Streamlit entry point |

### components/
| File | Lines | Imported By |
|------|------:|-------------|
| `__init__.py` | 0 | — |
| `chart_events.py` | 79 | pages/company/detail_tab.py |
| `charts.py` | 174 | pages/company/detail_tab.py |
| `confidence.py` | 32 | **ORPHAN** — not imported anywhere |
| `financial_table.py` | 127 | pages/valuation/preparation_display.py |
| `layout.py` | 127 | app.py, pages/*.py |
| `statement_table.py` | 134 | pages/company/financials_tab.py |
| `ticker_search.py` | 168 | pages/1_company.py, pages/3_valuation.py |

### config/
| File | Lines | Purpose |
|------|------:|---------|
| `__init__.py` | 0 | — |
| `constants.py` | 111 | Cache TTLs, chart colors, valuation defaults, Damodaran URLs |
| `settings.py` | 39 | Env vars, paths, app config |

### models/
| File | Lines | Purpose |
|------|------:|---------|
| `__init__.py` | 0 | — |
| `company.py` | 96 | CompanyInfo, CompanyPrice, CompanyRatios, Company dataclasses |
| `valuation.py` | 66 | WACCResult, EquityBridge, DCFResult dataclasses |

### lib/cache.py
| File | Lines | Purpose |
|------|------:|---------|
| `cache.py` | 143 | SQLite-backed cache with TTL, stale fallback, provider-level clearing |

### lib/logger.py
| File | Lines | Purpose |
|------|------:|---------|
| `logger.py` | 22 | Logging setup |

### lib/data/ (Data Layer)
| File | Lines | Status | Purpose |
|------|------:|--------|---------|
| `__init__.py` | 0 | — | — |
| `concept_maps.py` | 31 | Active | Aggregator — imports from concept_maps_*.py |
| `concept_maps_bs.py` | 278 | Active | Balance sheet XBRL concept -> key mappings |
| `concept_maps_cf.py` | 124 | Active | Cash flow concept mappings |
| `concept_maps_cf_inv.py` | 252 | Active | CF investing section concept mappings |
| `concept_maps_is.py` | 175 | Active | Income statement concept mappings |
| `concept_maps_kw_bs.py` | 149 | Active | BS keyword fallback mappings |
| `concept_maps_kw_cf.py` | 234 | Active | CF keyword fallback mappings |
| `concept_maps_kw_is.py` | 144 | Active | IS keyword fallback mappings |
| `concept_maps_util.py` | 6 | Active | Shared concept map utilities |
| `financial_data.py` | 19 | Active | Middleware for SimFin bank/insurance data |
| `fundamentals.py` | 235 | Active | Middleware: get_company(), get_financials() |
| `historical.py` | 269 | Active | Middleware: EDGAR raw + standardized history |
| `label_maps.py` | 220 | Active | Legacy label -> key mappings (used by historical.py) |
| `market.py` | 69 | Active | Middleware: price history |
| `search.py` | 27 | Active | Ticker search middleware |
| `serialization.py` | 50 | Active | DataFrame <-> JSON serialization for cache |
| `standardizer.py` | 267 | Active | Top-down 5-pass standardizer (current engine) |
| `standardizer_engine.py` | 222 | Active | Search engine: concept/keyword/derived/combination/bs_delta |
| `standardizer_utils.py` | 217 | Active | Cross-checks, quality scoring |
| `standardizer_v2.py` | 258 | **ORPHAN** | Older v2 approach — not imported by anything |
| `template.py` | 63 | Active | Template aggregator (imports template_*.py) |
| `template_bs.py` | 195 | Active | Balance sheet template + search rules |
| `template_cf.py` | 245 | Active | Cash flow template + search rules |
| `template_is.py` | 235 | Active | Income statement template + search rules |
| `valuation_data.py` | 78 | Active | Middleware: risk-free rate, valuation data, analyst estimates |

### lib/data/providers/
| File | Lines | Status | Purpose |
|------|------:|--------|---------|
| `__init__.py` | 0 | — | — |
| `edgar_provider.py` | 129 | Active | EDGAR 10-K statement fetcher |
| `edgar_xbrl.py` | 182 | Active | EDGAR XBRL-specific fetcher (standard_concept column) |
| `simfin_maps.py` | 153 | Active | SimFin field name -> standard key mappings |
| `simfin_provider.py` | 204 | Active | SimFin API: bank + insurance financials |
| `simfin_utils.py` | 97 | Active | SimFin helper functions |
| `yahoo.py` | 165 | Active | Yahoo Finance: fetch_all_info() |
| `yahoo_financials.py` | 139 | Active | Yahoo: income/balance/cashflow DataFrames |
| `yahoo_valuation.py` | 200 | Active | Yahoo: detailed valuation data, analyst estimates |

### lib/analysis/
| File | Lines | Status | Purpose |
|------|------:|--------|---------|
| `__init__.py` | 0 | — | — |
| `company_classifier.py` | 83 | Active | 3-category classifier: normal/financial/dividend_stable |
| `flags.py` | 235 | Active | 15-rule anomaly detector (rules 1-7 + orchestrator) |
| `flags_helpers.py` | 77 | Active | Flag helpers: _g, _pct_change, _flag, KNOWN_EVENTS |
| `flags_rules.py` | 300 | Active | Rules 8-15 + suppression logic |
| `historical.py` | 240 | Active | Build IS/BS/CF tables from standardized data |
| `historical_averages.py` | 34 | Active | 3yr/5yr ratio averages |
| `historical_flags.py` | 12 | Active | Thin re-export wrapper for flags.py + averages |
| `historical_ratios.py` | 167 | Active | 25+ ratios: margins, growth, efficiency, returns, leverage |
| `peers.py` | 184 | Active | Peer discovery via yfinance screener + known peers |

### lib/analysis/valuation/
| File | Lines | Status | Purpose |
|------|------:|--------|---------|
| `__init__.py` | 1 | — | — |
| `dcf.py` | 195 | Active | DCF engine: build_fcf_table, calc_terminal_value, run_dcf |
| `sensitivity.py` | 39 | Active | 2D sensitivity table (WACC vs terminal growth) |
| `wacc.py` | 75 | Active | WACC: adjusted beta, CAPM, auto_wacc |

### pages/
| File | Lines | Status | Purpose |
|------|------:|--------|---------|
| `1_company.py` | 154 | Active | Company Overview page |
| `3_valuation.py` | 107 | Active | Valuation page — orchestrates preparation + 5 tabs |

### pages/company/
| File | Lines | Status |
|------|------:|--------|
| `__init__.py` | 0 | — |
| `about_tab.py` | 19 | Active |
| `analysts_tab.py` | 72 | Active |
| `detail_tab.py` | 119 | Active |
| `financials_helpers.py` | 93 | Active |
| `financials_tab.py` | 147 | Active |
| `header.py` | 155 | Active |
| `news_tab.py` | 68 | Active |
| `ownership_tab.py` | 114 | Active |
| `peers_tab.py` | 44 | Active |

### pages/valuation/
| File | Lines | Status |
|------|------:|--------|
| `__init__.py` | 0 | — |
| `comps_tab.py` | 13 | **Placeholder** — "under construction" |
| `dcf_step2_assumptions.py` | 23 | **Placeholder** |
| `dcf_step3_model.py` | 34 | **Placeholder** |
| `dcf_step4_wacc.py` | 35 | **Placeholder** |
| `dcf_step5_terminal.py` | 29 | **Placeholder** |
| `dcf_step6_output.py` | 38 | **Placeholder** |
| `dcf_tab.py` | 67 | Active — orchestrates steps 2-6 (all placeholders) |
| `ddm_tab.py` | 22 | **Placeholder** |
| `historical_tab.py` | 11 | **Placeholder** |
| `preparation.py` | 283 | Active — Financial Preparation (data load, standardize, flag, classify) |
| `preparation_display.py` | 271 | Active — Charts, raw tables, standardized tables, ratios, audit trail |
| `summary_tab.py` | 11 | **Placeholder** |

### scripts/ (Development/Test Scripts — not part of app)
| File | Lines | Purpose |
|------|------:|---------|
| `broad_verification.py` | 191 | Multi-company standardization test |
| `build_concept_maps.py` | 38 | Generate concept maps from XBRL data |
| `explore_simfin.py` | 190 | SimFin API exploration |
| `investigate_gaps.py` | 244 | Gap analysis in standardized output |
| `optimize_dcf.py` | 422 | DCF optimization experiments |
| `professional_check.py` | 156 | Validate standardization against known values |
| `run_flags.py` | 75 | Run flag detection |
| `run_standardization.py` | 80 | Run standardizer |
| `scan_historical_concepts.py` | 127 | Scan EDGAR for historical concepts |
| `scan_xbrl_concepts.py` | 165 | Scan XBRL concept namespaces |
| `test_dcf.py` | 224 | DCF engine tests |
| `test_dcf_v2.py` | 239 | DCF v2 tests |
| `test_flags_100.py` | 221 | Flag detection on 100 companies |
| `test_flags_30.py` | 139 | Flag detection on 30 companies |
| `test_flags_rebuild.py` | 82 | Flag rebuild validation |
| `test_historical_ratios.py` | 120 | Ratio calculation tests |
| `test_mapping_fixes.py` | 144 | EDGAR mapping fix verification |
| `test_refactoring.py` | 113 | Post-refactor regression tests |
| `test_standardization_fixes.py` | 176 | Standardization fix verification |
| `test_standardizer_v2.py` | 157 | Standardizer v2 tests |
| `verify_standardization.py` | 144 | Standardization verification |

---

## 2. Architecture & Dependency Chain

### Valuation Page Flow

```
pages/3_valuation.py
  -> components/ticker_search (ticker input)
  -> lib/data/fundamentals.get_company() (Company model)
  -> lib/data/valuation_data.get_valuation_data() (risk-free rate, etc.)
  -> pages/valuation/preparation.render_preparation()
      -> lib/data/historical.get_raw_statements()
          -> providers/edgar_provider.fetch_statements()  [primary]
          -> providers/yahoo_financials.fetch_financials() [fallback]
      -> lib/data/historical.get_standardized_history()
          -> providers/edgar_xbrl.fetch_xbrl_statements()  [for L1 concept mapping]
          -> lib/data/standardizer.standardize_all()         [5-pass engine]
              -> standardizer_engine (concept/keyword/derived/combination/bs_delta)
              -> template.py -> template_is/bs/cf.py (search rules)
              -> concept_maps.py -> concept_maps_is/bs/cf/kw_*.py
          -> lib/data/standardizer_utils.run_cross_checks()
      -> lib/analysis/historical.build_income/balance/cashflow_table()
      -> lib/analysis/historical_ratios.build_ratios_table()
      -> lib/analysis/historical_flags.detect_flags() -> flags.py (15 rules)
      -> lib/analysis/historical_averages.compute_averages()
      -> lib/analysis/company_classifier.classify_company()
      -> pages/valuation/preparation_display (charts, tables, audit)
  -> [If preparation succeeds] Show 5 tabs:
      -> dcf_tab.render() -> steps 2-6 (ALL PLACEHOLDERS)
      -> comps_tab.render() (PLACEHOLDER)
      -> ddm_tab.render() (PLACEHOLDER)
      -> historical_tab.render() (PLACEHOLDER)
      -> summary_tab.render() (PLACEHOLDER)
```

### Company Page Flow

```
pages/1_company.py
  -> components/ticker_search (ticker input)
  -> lib/data/fundamentals.get_company()
      -> providers/yahoo.fetch_all_info()
      -> lib/cache (SQLite)
  -> pages/company/header.py (price bar, key metrics)
  -> Tabs: Detail | Financials | Analysts | Ownership | News | About | Peers
      -> lib/data/market.get_price_history()
      -> lib/analysis/peers.fetch_peers()
```

### Data Source Priority

| Source | Used For | Companies |
|--------|----------|-----------|
| EDGAR (edgartools) | Raw 10-K statements, XBRL concepts | US companies |
| Yahoo Finance (yfinance) | Market data, fallback financials, valuation data | All |
| SimFin | Bank + insurance financials | Financial institutions |

---

## 3. Standardization Engine (Current)

The standardizer uses a **top-down, 5-pass architecture** defined in `lib/data/standardizer.py`:

1. **Pass 1 — Direct lookups:** XBRL concept match (`standard_concept` column from EDGAR XBRL) or keyword match on label text
2. **Pass 2 — Combinations:** e.g., `gross_profit = revenue - cogs`
3. **Pass 3 — Derived:** Parent-child relationships (e.g., EBIT from pretax + interest)
4. **Pass 4 — Cross-statement:** EBITDA = EBIT + D&A (D&A from CF statement)
5. **Pass 5 — BS delta fallbacks:** e.g., change_in_receivables from BS AR delta

Search rules are defined in `template_is.py`, `template_bs.py`, `template_cf.py` (total ~675 lines of search rules). Concept maps live in 8 files under `concept_maps_*.py` (~1,362 lines of XBRL -> key mappings).

**Quality:** Cross-checks validate IS totals (revenue - cogs = gross_profit, etc.) and report discrepancies.

---

## 4. Flagging System

15 rules across 2 files (`flags.py` + `flags_rules.py`, total 535 lines):

| # | Rule | Severity | Category |
|---|------|----------|----------|
| 1 | Margin drop (>5pp) | medium/high | margin |
| 2 | Margin jump (>5pp) | medium/high | margin |
| 3 | Debt spike (>100% & >$1B) | high | debt |
| 4 | Tax anomaly (<10% or >35% ETR) | medium | tax |
| 5 | Known event (hardcoded per ticker) | medium | event |
| 6 | CapEx spike (>50% increase) | medium | capex |
| 7 | Acquisition fingerprint | medium/high | m_and_a |
| 8 | FCF/NI divergence | medium/high | quality |
| 9 | Working capital trend | medium | quality |
| 10 | Interest rate spike | medium | debt |
| 11 | Goodwill impairment | medium/high | m_and_a |
| 12 | Margin mean-reversion | medium | margin |
| 13 | Long trend reversal | medium | margin |
| 14 | Major dilution | medium/high | dilution |
| 15 | Earnings quality | medium | quality |

Each flag outputs: `{category, severity, year, what, possible_causes, impact_mn, line_item}`.
Suppression logic removes duplicates and noise.

---

## 5. Valuation Engine Status — ALL MODULES COMPLETE AND TESTED

**Updated 2026-04-04** after 3-cycle testing (v1→v2→v3) on 12 companies (US, Europe, Asia).

### lib/analysis/valuation/ (Engine Layer)

| Component | File | Status |
|-----------|------|--------|
| FCF Table Builder | `dcf.py` | **Complete** — builds projected FCF from assumptions |
| Terminal Value | `dcf.py` | **Complete** — Gordon Growth, Exit Multiple, Average |
| DCF Runner | `dcf.py` | **Complete** — discounts FCFs, equity bridge, 85%+ TV warning |
| WACC Calculator | `wacc.py` | **Complete** — adjusted beta, CAPM, market-weight WACC |
| DCF Sensitivity | `sensitivity.py` | **Complete** — 2D WACC×growth + WACC×multiple, NaN floor |
| DDM Engine | `ddm.py` | **Complete** — Gordon Growth, 2-Stage, sensitivity grid |

### pages/valuation/ (UI Layer) — ALL CONNECTED

| Tab | Key Files | Status |
|-----|-----------|--------|
| DCF Step 2 | `dcf_step2_table.py`, `dcf_step2_output.py` | **Complete** — historical + projected FCF |
| DCF Step 3 | `dcf_step3_wacc.py`, `dcf_step3_ke.py`, `dcf_step3_kd.py`, `dcf_step3_structure.py`, `dcf_step3_peers.py` | **Complete** — CAPM, 3 beta methods, cost of debt, capital structure |
| DCF Step 4 | `dcf_step4_terminal.py`, `dcf_step4_methods.py` | **Complete** — Gordon + Exit Multiple with cross-checks |
| DCF Step 5 | `dcf_step5_output.py`, `dcf_step5_bridge.py`, `dcf_step5_sensitivity.py` | **Complete** — EV, equity bridge, sensitivity, currency conversion |
| Comps | `comps_step1_peers.py`, `comps_step2_table.py`, `comps_step2_render.py`, `comps_step3_valuation.py`, `comps_step3_football.py` | **Complete** — GICS peers, financial company support |
| DDM | `ddm_tab.py`, `ddm_step1_ke.py`, `ddm_step1_peers.py`, `ddm_step2_assumptions.py`, `ddm_step2_reference.py`, `ddm_step3_output.py` | **Complete** — independent Ke, Gordon + 2-Stage |
| Historical | `historical_tab.py`, `historical_chart.py`, `historical_summary.py`, `historical_football.py` | **Complete** — EDGAR + yfinance, ±1σ bands |
| Summary | `summary_tab.py`, `summary_table.py`, `summary_football.py` | **Complete** — all models combined |

### lib/data/providers/ (Data Layer)

| Provider | File | Status |
|----------|------|--------|
| Damodaran | `damodaran.py` | **Complete** — ERP, CRP, spreads, industry betas (US/global/emerging) |
| Peer Beta | `peer_beta.py` | **Complete** — Yahoo recommended + beta/D/E/tax per peer |
| Comps Data | `comps_data.py` | **Complete** — multiples, `_clean_numeric()` for Infinity guard |
| Comps Peers | `comps_peers.py` | **Complete** — Finnhub + GICS-filtered universe |
| Peer Universe | `peer_universe.py` | **Complete** — 6 indices, ~823 companies |
| Historical Multiples | `historical_multiples.py`, `_yf.py`, `_calc.py` | **Complete** — EDGAR/yfinance, price_factor, is_quarterly |
| EDGAR Quarterly | `edgar_quarterly.py`, `edgar_concept_map.py` | **Complete** — 10+ year quarterly, 49 XBRL concepts |
| DDM | `ddm_provider.py` | **Complete** — DPS history, CAGR, streaks, currency metadata |

### Testing Summary (v3 — 2026-04-04)

| Metric | Result |
|--------|--------|
| Companies tested | 12 (3 US, 3 US-DDM, 3 Europe, 3 Asia) |
| Overall status | **PASS** (0 critical errors) |
| Modules working | DCF, DDM, Comps, Historical, Summary |
| Bugs found and fixed (v1→v3) | 8 |

Bugs fixed: GBp currency (price_factor), annual-only implied values, Comps Infinity string, 2-Stage DDM sensitivity, sensitivity NaN floor/cap, multi-currency Rf (tested and reverted to ^TNX+CRP), GICS peer selection confirmed correct.

Test reports: `test_results/valuation_test_report_v1.md`, `v2.md`, `v3.md`

---

## 6. Models (Dataclasses)

### models/company.py (96 lines)
- `CompanyInfo` — ticker, name, sector, industry, country, currency, etc.
- `CompanyPrice` — price, change, market_cap, beta, analyst targets, dividend
- `CompanyRatios` — PE, PB, PS, EV/EBITDA, margins, growth, leverage
- `Company` — composite of Info + Price + Ratios + optional DataFrames

### models/valuation.py (66 lines)
- `WACCResult` — rf, beta, erp, Re, Rd, weights, WACC (all intermediates)
- `EquityBridge` — EV, net debt, minorities, preferred, equity value, implied price
- `DCFResult` — FCF table, terminal value, PVs, bridge, sanity metrics, warnings

**Note:** DDM and sensitivity engines exist as pure functions (dict returns). Comps, Historical, and Summary use dicts, not dataclasses.

---

## 7. Cache System

**Implementation:** `lib/cache.py` (143 lines), SQLite-backed (`data/cache/cache.db`).

| Operation | Method |
|-----------|--------|
| Get fresh | `get(key)` — returns None if expired |
| Get stale | `get_stale(key)` — returns data up to 90 days old |
| Store | `store(key, data, provider, ttl_key)` |
| Delete | `delete(key)`, `clear_provider()`, `clear_expired()`, `clear_all()` |

**TTLs (from config/constants.py):**
| Category | TTL |
|----------|-----|
| price_intraday | 1 hour |
| price_daily, ratios, macro, news, insider, sec_filings | 24 hours |
| financials | 7 days |
| company_info, damodaran | 30 days |

**Stale data policy:** If API fails, stale cache (up to 90 days) is returned as fallback with a warning banner.

---

## 8. Orphaned Files

| File | Lines | Evidence |
|------|------:|----------|
| `lib/data/standardizer_v2.py` | 258 | Not imported by any project file. Older approach superseded by the current top-down standardizer. Also listed as untracked in git. |
| `components/confidence.py` | 32 | Not imported anywhere. Likely leftover from a removed feature. |

**Note:** The git status shows many **deleted** files that were removed from the working tree but not yet committed (e.g., `lib/analysis/historical_flags_advanced.py`, `lib/analysis/valuation.py`, `lib/data/xbrl_concept_map.py`, and 14 others). These were old implementations replaced during the standardizer rebuild.

---

## 9. File Size Violations

CLAUDE.md rule: "No file should exceed ~200 lines."

**18 files exceed 200 lines:**

| File | Lines | Over By |
|------|------:|--------:|
| `lib/analysis/flags_rules.py` | 300 | 100 |
| `pages/valuation/preparation.py` | 283 | 83 |
| `lib/data/concept_maps_bs.py` | 278 | 78 |
| `pages/valuation/preparation_display.py` | 271 | 71 |
| `lib/data/historical.py` | 269 | 69 |
| `lib/data/standardizer.py` | 267 | 67 |
| `lib/data/standardizer_v2.py` | 258 | 58 |
| `lib/data/concept_maps_cf_inv.py` | 252 | 52 |
| `lib/data/template_cf.py` | 245 | 45 |
| `lib/analysis/historical.py` | 240 | 40 |
| `lib/data/template_is.py` | 235 | 35 |
| `lib/data/fundamentals.py` | 235 | 35 |
| `lib/analysis/flags.py` | 235 | 35 |
| `lib/data/concept_maps_kw_cf.py` | 234 | 34 |
| `lib/data/standardizer_engine.py` | 222 | 22 |
| `lib/data/label_maps.py` | 220 | 20 |
| `lib/data/standardizer_utils.py` | 217 | 17 |
| `lib/data/providers/simfin_provider.py` | 204 | 4 |

**Mitigation:** Many of these (concept_maps_*, template_*, label_maps) are data-heavy files with no logic — just mappings. The real concerns are `flags_rules.py` (300), `preparation.py` (283), and `preparation_display.py` (271).

---

## 10. Architecture Compliance

### Layer Separation (CLAUDE.md Critical Rule #1)

| Check | Status |
|-------|--------|
| No `import streamlit` in `lib/` | PASS — zero violations |
| No direct provider imports in `pages/` | PASS — zero violations |
| Providers don't call each other | PASS |
| All data through middleware | PASS |

### Data Flow (Critical Rule #2)

| Check | Status |
|-------|--------|
| All data fetching through `lib/data/` | PASS |
| Cache checked before API calls | PASS |
| API failures use stale cache fallback | PASS |
| Data flows through models | PARTIAL — historical data flows as dicts, not dataclasses |

### Other Rules

| Check | Status |
|-------|--------|
| No hardcoded secrets | PASS — all in .env via settings.py |
| Storage abstraction | NOT IMPLEMENTED — cache.py uses SQLite directly, no base/local/cloud split |

---

## 11. What Works End-to-End

### Company Overview Page (pages/1_company.py) — FULLY FUNCTIONAL
- Ticker search with URL persistence
- Company header with price, change, market cap, beta
- 7 tabs: Detail (price chart + key stats), Financials (IS/BS/CF tables), Analysts, Ownership, News, About, Peers

### Valuation Page — Financial Preparation — FULLY FUNCTIONAL
- Loads 10+ years of EDGAR data for US companies
- XBRL-aware standardization (5-pass engine)
- 25+ financial ratios calculated
- 15-rule anomaly detection with severity, impact, causes
- Company classification (normal/financial/dividend_stable)
- 3yr average dashboard
- Revenue/FCF bar chart + margin trend chart
- Raw financials display (as-reported)
- Standardized financials with audit trail (shows XBRL/Keyword/Derived source)
- Cross-check validation
- Financial institution routing to SimFin

### Valuation Page — All 5 Tabs — COMPLETE AND TESTED (2026-04-04)
- **DCF (Steps 2-5):** Editable assumptions, WACC (3 beta methods, cost of debt), terminal value (Gordon + Exit Multiple), equity bridge, 2D sensitivity, currency conversion
- **Comps (3 steps):** GICS-filtered peer selection, trailing + forward multiples, implied valuation, financial company support (P/Book, P/TBV, Div Yield)
- **DDM (3 steps):** Independent Ke, Gordon Growth + 2-Stage, DPS history analysis, sensitivity grid
- **Historical Multiples:** EDGAR (US, 10+ years) + yfinance fallback (non-US, ~3.5 years), daily TTM multiples, summary stats, implied values
- **Summary/Football Field:** Combines all models, overview table, combined football field chart
- **Cross-currency support:** GBp, CHF, EUR, JPY, KRW, HKD all tested via price_factor conversion

---

## 12. Untracked/Uncommitted Files

### Untracked Documentation (17 .md files)
These appear to be development logs from the standardizer rebuild work:
`BROAD_VERIFICATION.md`, `EDGAR_MAPPING_FIXES.md`, `EDGAR_MERGE_FIX.md`, `FLAG_REBUILD_RESULTS.md`, `FLAG_RESULTS.md`, `HISTORICAL_CONCEPTS.md`, `ORPHANED_VALUATION.md`, `PROFESSIONAL_CHECK.md`, `REFACTORING_RESULTS.md`, `REMAINING_GAPS.md`, `SIMFIN_BANK_INTEGRATION.md`, `SIMFIN_EXPLORATION.md`, `STANDARDIZATION_FIXES.md`, `STANDARDIZATION_OUTPUT.md`, `STANDARDIZATION_VERIFICATION.md`, `STANDARDIZER_V2_RESULTS.md`, `TOP_DOWN_RESULTS.md`, `V2_FINAL_FIXES.md`

**Recommendation:** These are development artifacts. They should either be moved to a `docs/dev-logs/` folder or added to `.gitignore` if they are not meant to be committed.

### Untracked Code
- `lib/data/standardizer_v2.py` — orphaned, can be deleted
- `scripts/` — 21 test/exploration scripts (3,447 lines total)
- `data/` — local cache and data directory

### Deleted from Working Tree (not yet committed)
14 files deleted from the old standardizer/flags system:
- `lib/analysis/historical_flags_advanced.py` (and 7 more variants)
- `lib/analysis/valuation.py` (old monolithic valuation)
- `lib/data/xbrl_concept_map.py` (old concept mapping)
- `pages/valuation/dcf_step1_*.py` (6 old Step 1 sub-files)

---

## Summary (Updated 2026-04-04)

**What is solid:**
- Company Overview page is fully functional
- Financial Preparation (standardization + flagging + classification) works end-to-end with 10+ years of EDGAR data
- **ALL 5 valuation tabs fully built, connected to UI, and tested on 12 companies (US, Europe, Asia)**
- DCF, DDM, Comps, Historical Multiples, Summary/Football Field — all working
- Cross-currency support (GBp, CHF, EUR, JPY, KRW, HKD) via price_factor
- Architecture rules are fully complied with (no layer violations)
- Cache system works well with TTL + stale fallback

**What is not yet built:**
- Storage abstraction (base/local/cloud) from CLAUDE.md — not implemented
- AI features (chat, tutor, document reader) — fase 3
- Education system — fase 4
- Alert system, report export — fase 5+

**Known limitations (not bugs):**
- Low-beta companies (e.g. Toyota) get high TV% with US Rf — analyst sees 85%+ warning
- DDM gives WARN for low-dividend companies (e.g. AAPL) — correct behavior
- Gordon Growth is inherently explosive near g=Ke — 100x cap excludes asymptotic cells
- Rf is US ^TNX for all companies — CRP adds country risk, analyst can override

**What needs cleanup:**
- 17 untracked .md dev-log files cluttering the root
- 1 orphaned code file (standardizer_v2.py)
- 1 orphaned component (confidence.py)
- Historical data uses plain dicts, not typed dataclasses
