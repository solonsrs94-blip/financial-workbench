# Financial Workbench

Personal financial analysis workbench with AI-powered features and educational tools.
Read VISION.md for project philosophy. Read ARCHITECTURE.md for full structure, features, and phases.

## Tech Stack
- Python 3.11+
- Streamlit (UI framework — fase 1, React later)
- yfinance (PRIMARY: financial statements + market data — no API key needed)
- edgartools (SEC filings — kept in repo, not active for Financial Preparation)
- simfin (bank/insurance financials — free tier, 5 years)
- fredapi (macro data — needs API key, fase 4)
- Plotly (interactive charts — preferred over Matplotlib)
- Firebase Admin SDK (auth + Firestore cloud storage)
- SQLite (local data cache — fase 1, cloud later)
- Claude API / Anthropic SDK (AI features — needs API key, fase 3)
- Whisper (earnings call transcription — fase 5)

## Project Structure
```
app.py              → Main Streamlit entry point
pages/              → Streamlit pages (one screen = one file)
  2_saved.py        → Saved Valuations page (browse, load, delete saved analyses)
  pages/valuation/  → Valuation sub-pages (preparation, dcf steps 2-5, comps, ddm)
    preparation_editor.py → Editable data_editor for override values
    preparation_overrides.py → Rebuild cascade after overrides
    preparation_recommendations.py → Recommendations & Considerations UI panel
    dcf_step2_scenarios.py → Step 2 Bull/Base/Bear tab orchestration
    dcf_step2_table.py → Historical + projected FCF table
    dcf_step2_output.py → Calculated FCF output section
    dcf_step3_wacc.py → Step 3 WACC orchestrator
    dcf_step3_ke.py → Step 3A: Cost of Equity (CAPM, 3 beta methods)
    dcf_step3_kd.py → Step 3B: Cost of Debt (actual vs synthetic)
    dcf_step3_structure.py → Step 3C: Capital Structure + WACC output
    dcf_step3_peers.py → Peer Group Beta (table, add/remove, Hamada)
    dcf_step4_terminal.py → Step 4 TV orchestrator (method selector, cross-checks, warnings)
    dcf_step4_methods.py → Step 4 Gordon Growth + Exit Multiple renderers
    dcf_step4_scenarios.py → Step 4 Bull/Base/Bear terminal value tabs
    dcf_step5_output.py → Step 5 DCF Output orchestrator (EV, implied price, summary)
    dcf_step5_display.py → Step 5 display helpers (summary, EV breakdown, implied price)
    dcf_step5_scenarios.py → Step 5 Bull/Base/Bear comparison + per-scenario output
    dcf_step5_bridge.py → Step 5 Equity Bridge (EV → equity value, overridable)
    dcf_step5_sensitivity.py → Step 5 Sensitivity tables (WACC×growth, WACC×multiple)
    historical_tab.py → Historical Multiples orchestrator (period/multiple controls)
    historical_scenarios.py → Historical Bull/Base/Bear scenario valuation tabs
    historical_chart.py → Historical Multiples time series charts (Plotly, ±1σ bands)
    historical_summary.py → Summary statistics + implied value tables
    historical_football.py → Football field chart (10th-90th percentile range)
    ddm_tab.py → DDM orchestrator (Gordon Growth + 2-Stage)
    ddm_step1_ke.py → DDM Step 1: Cost of Equity (independent CAPM)
    ddm_step1_peers.py → DDM Step 1: Peer Group Beta (ddm_ session keys)
    ddm_step2_assumptions.py → DDM Step 2: Model selection + dividend projections
    ddm_step2_scenarios.py → DDM Step 2: Bull/Base/Bear tab orchestration
    ddm_step2_reference.py → DDM Step 2: Reference data, warnings, history
    ddm_step3_output.py → DDM Step 3: Orchestrator + rendering helpers
    ddm_step3_scenarios.py → DDM Step 3: Bull/Base/Bear comparison + per-scenario output
    summary_tab.py → Summary tab orchestrator (reads all model outputs)
    summary_table.py → Summary: Valuation overview table
    summary_football.py → Summary: Combined football field chart (all models)
    summary_helpers.py → Summary: DCF scenario format handling + re-exports
    summary_weights.py → Summary: Model weighting inputs + weighted fair value + stats
components/         → Reusable UI components (ticker search, charts, tables, explainer, commentary, save_button)
  auth_guard.py     → require_auth() guard + show_user_sidebar() (call at top of every page)
  auth_forms.py     → Login/sign-up forms (email/password, tabs)
  commentary_templates/ → Sector-specific commentary templates (tech, industrials, consumer, healthcare, energy, real estate, dcf_step4, dcf_step5)
lib/                → Core logic — NO Streamlit imports allowed here
  lib/data/         → Data fetching + standardization
    providers/      → Raw data sources (yahoo, simfin, damodaran, edgar, peer_beta)
      damodaran.py → ERP, CRP, spreads, industry betas (US/global/emerging)
      damodaran_industry.py → Industry averages (margins, leverage, payout, ROE)
      peer_beta.py → Yahoo recommended peers + beta/D/E/tax per peer
      industry_map.py → Yahoo→Damodaran industry name mapping (pure data, 109+ entries)
      historical_multiples.py → EDGAR + yfinance router, module caches
      historical_multiples_yf.py → yfinance quarterly/annual extraction helpers
      historical_multiples_calc.py → Daily TTM builder, summary stats, implied values
      edgar_quarterly.py → SEC EDGAR Company Facts API (10+ year quarterly data)
      edgar_concept_map.py → XBRL concept mappings (49 concepts, 55 companies tested)
      ddm_provider.py → DDM dividend data (DPS history, CAGR, streaks, cuts)
    yfinance_standardizer.py → PRIMARY: yfinance → prepared_data mapping
    yfinance_maps.py → yfinance key mappings (IS/BS/CF, pure data)
    override_utils.py → Apply/count user overrides on standardized data
    historical.py   → Table builders: standardized → IS/BS/CF tables
    valuation_data.py → Middleware for WACC data (Damodaran, peers, Rf, valuation, DDM)
    financial_data.py → Middleware for SimFin (banks/insurance)
    standardizer.py → EDGAR standardizer (kept, not active)
  lib/analysis/     → Calculations (valuation, technicals, risk, etc.)
    flags.py        → 22-rule flagging system (rules 1-7 + orchestrator)
    flags_rules.py  → Rules 8-15 (sector-aware skips for financials/REITs)
    flags_rules_v2.py → Rules 16-20 (sector-aware: payout, unusual items, coverage, leverage, margin history)
    flags_industry.py → Rules 21-23 (industry-relative: margins, ROE, leverage vs Damodaran)
    flags_helpers.py → _g(), _flag(), _get_company_category(), suppress(), KNOWN_EVENTS
    company_classifier.py → normal / financial / dividend_stable
    recommendations.py → Recommendation engine orchestrator (generate_recommendations)
    recommendations_rules.py → Model assessment rules (DCF, DDM, Comps, Historical)
    recommendations_risks.py → Attention items + risk rules (flags, dividend, industry)
    historical.py   → Build IS/BS/CF tables + ratios
    valuation/wacc.py → CAPM, beta, cost of debt (shared by DCF + DDM)
    valuation/dcf.py → DCF engine (build FCF, terminal value, run DCF)
    valuation/ddm.py → DDM engine (Gordon Growth, 2-Stage, sensitivity)
    valuation/sensitivity.py → 2D sensitivity tables for DCF
  lib/ai/           → AI features (chat, document reader, tutor, etc.)
  lib/education/    → Education system (curriculum, concepts, prompt builder)
  lib/workspace/    → Analysis sessions (data + reasoning + AI narrative)
  lib/sandbox/      → AI experiment station (code generation + execution)
  lib/alerts/       → Alert system (conditions + notifications)
  lib/exports/      → Report generation (PDF, Excel, templates, JSON analysis export, save/load)
    analysis_export.py → build_export_json() — collects all session state into structured JSON for Claude report generation
    company_data.py → Company model extraction helpers (description, ratios, extended meta, historical financials)
    session_collector.py → collect_valuation_state() — session_state → JSON-safe dict for saving
    session_restorer.py → restore_valuation_state() — JSON-safe dict → session_state keys for loading
  lib/storage/      → Storage abstraction (local fallback + Firestore cloud)
    valuations.py   → Save/load/list/delete valuation JSON files (local fallback)
    firestore_valuations.py → Firestore CRUD: save/list/load/delete (users/{uid}/valuations/{id})
  lib/auth/         → Firebase authentication (pure Python, NO streamlit imports)
    firebase_init.py → Firebase Admin SDK singleton init
    firebase_auth.py → sign_up/sign_in (REST API), check_user_approved, create_user_profile
models/             → Data models (company, portfolio, experiment, etc.)
data/               → Local storage (cache, portfolio, simfin_cache, etc.)
assets/             → CSS styles and educational diagrams
config/             → Settings and constants
docs/               → Technical documentation for each layer
scripts/            → Maintenance + test scripts
tests/              → Tests for data, analysis, and cache
```

## Critical Rules — NEVER break these

### 1. Layer separation
- `lib/` must NEVER import Streamlit. No `import streamlit` or `st.` anywhere in lib/.
- `pages/` calls `components/` for UI and `lib/` for data/logic. Never the reverse.
- `providers/` never call each other. Middleware files (market.py, fundamentals.py, macro.py, valuation_data.py) coordinate between them.

### 2. Data flow
- ALL data fetching goes through `lib/data/`, never directly from pages/.
- Always check `lib/cache.py` before making API calls.
- Data passes through `models/` for standardized format.
- Handle API failures gracefully — show cached data if available, clear error message if not.

### 3. File size
- No file should exceed 300 lines (enforced by pre-commit hook). If it does, split into submodules.
- Pure data files (concept maps, templates) are split by statement type (IS/BS/CF).
- Pages that grow large get their own subfolder (e.g., pages/valuation/).

### 4. Adding new things
- New data source → new file in `lib/data/providers/`, update middleware file.
- New analysis method → new file in `lib/analysis/strategies/`.
- New screen → new file in `pages/`.
- New AI feature → new file in `lib/ai/`.

### 5. No hardcoded secrets
- API keys go in `st.secrets` (Streamlit Cloud) or `.env` (local dev), read via `config/settings.py._get_secret()`.
- `.env` and `.streamlit/secrets.toml` are in `.gitignore` — never committed.
- Firebase service account credentials go in `st.secrets["firebase_service_account"]` or `firebase-service-account.json` (local).

### 6. Storage abstraction
- `lib/storage/base.py` defines the interface.
- `lib/storage/local.py` implements SQLite (current).
- `lib/storage/cloud.py` implements Firebase/PostgreSQL (later).
- Nothing else in the app knows which storage backend is active.

## Commands
- `streamlit run app.py` — Run the app locally
- `pip install -r requirements.txt` — Install dependencies

## Language
- The user communicates in Icelandic. Respond in Icelandic unless asked otherwise.
- Code comments and variable names should be in English.
- UI text is in English (international finance language). Icelandic language toggle planned for later.

## Data Conventions — IMPORTANT
- Yahoo Finance returns `dividendYield` as already-percent (0.41 = 0.41%). Normalize to decimal in provider: `div_yield / 100` → 0.0041.
- All other Yahoo percentages (margins, ROE, ROA, growth) are decimal (0.27 = 27%). Do NOT double-normalize these.
- `format_percentage()` always multiplies by 100. So ALL values passed to it must be in decimal form.
- Yahoo `debtToEquity` is in percentage form (31.5 = 31.5%). Divide by 100 in provider: `de / 100` → 0.315.
- Damodaran ERP, CRP, spreads are all in decimal form (0.046 = 4.6%). No conversion needed.
- Industry name matching: `industry_map.py` handles Yahoo→Damodaran name translation. Add new entries there when mismatches are found.
- When comparing companies across currencies, convert to USD using `{CURRENCY}=X` Yahoo ticker.
- **Currency alignment (price_factor):** yfinance returns `currency` (listing, e.g. GBp) and `financialCurrency` (reporting, e.g. USD) which can differ. When they differ, compute `price_factor = marketCap / (currentPrice * shares)` to convert listing→financial currency. Historical multiples use price_factor in `_calc_row()`. DCF/DDM implied prices are converted back to listing currency via `/ price_factor` before display. Providers (`yahoo_valuation.py`, `ddm_provider.py`) return both `currency` and `financial_currency` fields.
- **GBp (pence sterling):** yfinance `.history()` and `currentPrice` are in GBp but `.info` financials (marketCap, revenue, EPS) and `.income_stmt/.balance_sheet` are in `financialCurrency` (USD for Shell). price_factor handles this automatically.
- **Annual-only stocks:** `compute_implied_values()` uses `is_quarterly` flag. When only annual data exists, uses last 1 row (not sum of 4) since annual data is already 12-month totals.
- **Risk-free rate:** `get_risk_free_rate()` always uses ^TNX (US 10Y Treasury) for all companies. Country risk is handled via CRP (Damodaran). Analyst can override Rf in the WACC UI.
- Yahoo `sharesOutstanding` may only report one share class (e.g. GOOGL Class A). Always prefer `impliedSharesOutstanding` (includes all classes) with `sharesOutstanding` as fallback. This is enforced in both `yahoo.py` and `yahoo_valuation.py`.
- GICS ↔ yfinance industry mapping: `gics_yf_map.py` handles Yahoo industry→GICS Sub-Industry translation for peer universe filtering. 111 yfinance industries mapped to 127 GICS Sub-Industries.
- Comps peer universe: `peer_universe.py` fetches 6 indices (S&P 500, Euro STOXX 50, CAC 40, FTSE 100, TSX 60, Hang Seng = ~823 companies). Cached 30 days via `get_peer_universe()`.
- Financial company detection: Company model lacks `sector` attribute, so `_is_financial()` in comps uses 3-tier fallback: prepared company_type → target industry keywords → yfinance candidate info sector.
- Comps financial multiples: Banks/insurance use P/E, P/Book, P/TBV, Div Yield instead of EV-based multiples. `comps_data.py` fetches `bookValue` (per share), tangible book from `balance_sheet["Tangible Book Value"]`, and `dividendYield / 100`.
- DDM dividend data: `ddm_provider.py` normalizes `dividendYield / 100` (same convention as Comps). DPS CAGR computed from `ticker.dividends` aggregated to annual. Dividend cuts detected as year-over-year decreases.
- DDM is independent from DCF: DDM has its own Ke calculation (same CAPM providers but separate UI/session keys). DDM does NOT require DCF WACC step to have been run.
- DDM session keys use `ddm_` prefix: `ddm_ke`, `ddm_data_{ticker}`, `ddm_ke_peers`. Never collides with `dcf_`/`wacc_` keys.
- DDM scenario keys: `ddm_scenarios` (dict with base/bull/bear assumption dicts), `ddm_scenarios_initialized` (set). Widget keys use `ddm_{scenario}_{field}` pattern. Ke is shared (single `ddm_ke`). Legacy `ddm_assumptions` auto-migrated to `ddm_scenarios['base']`.
- `ddm_output` uses scenario format: `{'base': {...}, 'bull': {...}, 'bear': {...}}`. Summary handles both scenario and legacy formats via `summary_helpers.py`.
- DCF scenario keys: `dcf_scenarios` (dict with base/bull/bear assumption dicts), `dcf_active_scenario`, `dcf_scenarios_initialized` (set), `dcf_scenarios_terminal` (dict with base/bull/bear terminal dicts). Widget keys use `dcf_{scenario}_{field}_{i}` pattern. Bridge keys use `bridge_{scenario}_{field}`. WACC is shared (single `dcf_wacc`). Legacy `dcf_assumptions` auto-migrated to `dcf_scenarios['base']`.
- `dcf_output` uses scenario format: `{'base': {...}, 'bull': {...}, 'bear': {...}}`. Summary tab handles both scenario and legacy (flat dict) formats via `summary_helpers.py`.
- Comps scenario keys: `comps_valuation` uses scenario format `{'base': {implied_price, applied_mult, premium, final_mult}, ...}` or legacy format `{implied_prices: {...}, method: ...}`. Scenario tabs in Step 3 with per-scenario applied multiples (defaults: 25th/median/75th percentile). Commentary: `commentary_comps_step3_{scenario}`, `commentary_comps_comparison`.
- Summary tab reads from: `dcf_output` (scenario or legacy), `comps_valuation` (scenario or legacy), `historical_result` (implied_values with at_p10/at_median/at_p90 per multiple), `ddm_output` (scenario or legacy). Summary never writes to session_state — pure read-only. All scenario formats handled via `summary_helpers.py`.
- Historical scenario keys: `historical_result` uses scenario format `{'base': {implied_price, applied_mult, mult_key}, ...}` plus `summary` and `implied_values` for backward compat. Scenario tabs with -1σ/mean/+1σ defaults. Commentary: `commentary_historical_{scenario}`, `commentary_historical_comparison`.
- Analyst Commentary keys use `commentary_` prefix. Standard: `commentary_dcf_step3`, `commentary_summary` via `render_commentary(key)`. Per-scenario: DCF `commentary_dcf_step2_{scenario}`, `commentary_dcf_step4_{scenario}`; DDM `commentary_ddm_step2_{scenario}`; Comps `commentary_comps_step3_{scenario}`; Historical `commentary_historical_{scenario}`. Shared comparison: `commentary_dcf_step5`, `commentary_ddm_step3`, `commentary_comps_comparison`, `commentary_historical_comparison`. Templates in `components/commentary_templates/` (sector files + dcf_step4/5 + ddm templates + comps + historical + non_dcf).
- DDM commentary uses 5 sector templates: Consumer/Aristocrat (`ddm_consumer.py`), Financial (`ddm_financial.py`), Utility (`ddm_utility.py`), REIT (`ddm_reit.py`), Cyclical (`ddm_cyclical.py`). Selector state: `ddm_sector_template`. Same UX pattern as DCF Step 2 sector selector.
- DDM anomaly detection: `ddm_provider.py` detects DPS spikes >3x vs both adjacent years (stock split artifacts). Returns `dps_anomalies`, `dps_cagr_clean`, `years_increasing_clean`, `dividend_cuts_clean`. Reference UI uses clean metrics by default.
- DDM Gordon Growth defaults: perpetual g = 2.5% (long-term nominal GDP proxy), NOT historical DPS CAGR. Historical CAGR shown as reference only. Warning when g > Ke - 2%.
- **Payout ratio (canonical):** Always `DPS / diluted_EPS`. yahoo.py computes this (not yfinance `payoutRatio`). DDM provider uses same formula. Historical ratios use aggregate `dividends_paid / net_income` for trend analysis only.
- **Model weighting:** Summary tab has per-model weight inputs (default equal, stored in `summary_weights` session key as `{dcf: 0.25, ...}`). Weighted fair value displayed alongside mean/median. Weights exported in JSON `summary.model_weights`.
- **Historical EPS basis:** Historical Multiples has EPS basis selector (Trailing/Forward/Manual). Scaling applied to P/E implied values only. `eps_basis` and `eps_used` stored in `historical_result` output when overridden.
- **JSON export includes:** `flags` section (from `prepared_data["flags"]`), `ebitda_ttm` + source in meta, `weighted_fair_value` + `model_weights` + `weighted_components` in summary, `industry_averages` (Damodaran benchmarks), `recommendations` (model suitability + risks), `company_category` in meta, DCF `projections` (per-year Revenue/EBIT/FCF/PV) + `sensitivity` (WACC×growth and WACC×multiple grids) per scenario, DDM `projections` (per-year DPS/PV + terminal) + `sensitivity` (Ke×growth grid) per scenario.

## Save-to-Summary Pattern
- Valuation modules (DCF, DDM, Comps, Historical) do NOT auto-write output to session_state.
- Each module has a "Save to Summary" button (`components/save_button.py`) that commits results when clicked.
- Summary tab and JSON export read only from committed session_state keys (`dcf_output`, `ddm_output`, `comps_valuation`, `historical_result`).
- The save button shows status: green check if saved matches current, warning if results changed since last save.
- `ddm_output_alt` is only shown in Summary when no scenario DDM output exists (prevents ghost entries).
- When adding a new valuation module, use `render_save_button(key, label, data)` from `components/save_button.py`.

## Save/Load Valuations
- **Save:** "Save Valuation" button on Summary tab. Collects all session state via `session_collector.collect_valuation_state()`, saves to Firestore `users/{uid}/valuations/{auto_id}` (or local JSON fallback if no auth). Never overwrites — each save creates a new document.
- **Load:** Saved Valuations page (`pages/2_saved.py`) lists all saves from Firestore grouped by ticker. Load button calls `session_restorer.restore_valuation_state()` → injects into `st.session_state` → `st.switch_page("pages/3_valuation.py")`.
- **Load guard:** `pages/3_valuation.py` checks for `_loaded_ticker` in session_state. If present and matches current ticker, skips cache clearing (prevents wiping loaded data).
- **Serialization:** `_make_json_safe()` handles sets (→ `__set__` marker), DataFrames (→ `__df__` marker), numpy types, NaN/Inf (→ None), dataclasses (→ dict with `__dataclass__` marker). Reverse: `_restore_types()`.
- **Company objects:** Serialized via `dataclasses.asdict()` with DataFrame fields set to None. On restore, reconstructed as Company dataclass (no DataFrames needed — valuation modules use `prepared_data` and `val_data`).
- **Storage:** `lib/storage/firestore_valuations.py` (Firestore CRUD, primary) or `lib/storage/valuations.py` (local JSON fallback).
- **When adding new session state keys** to any valuation module, add them to `_FIXED_KEYS` or `_TICKER_KEYS` in `session_collector.py` so they get saved.

## Authentication (Firebase)
- **Auth provider:** Firebase Auth (email/password). Admin SDK for server-side ops, REST API for client-side sign-in/sign-up.
- **Auth guard:** Every page calls `require_auth()` + `show_user_sidebar()` from `components/auth_guard.py`. Unauthenticated users are redirected to `app.py` (login page).
- **Approval flow:** New users get `approved: false` in Firestore `users/{uid}`. Admin sets `approved: true` via Firebase Console. App checks approval on every sign-in.
- **Session state keys:** `auth_uid`, `auth_email`, `auth_id_token`, `auth_refresh_token`, `auth_approved`. Cleared on sign-out.
- **Firebase init:** Singleton via `lib/auth/firebase_init.py`. Service account from `st.secrets["firebase_service_account"]` (cloud) or `firebase-service-account.json` (local).
- **Config:** All API keys read via `config/settings.py._get_secret()` which tries `st.secrets` first, then `.env` fallback.

## Sensitivity Rules
- Floor: Cells where g >= Ke (DDM) or implied price <= 0 (DCF) → NaN, displayed as "—" in UI.
- Cap: Implied price > 100x current price → NaN (excludes asymptotic Gordon values near g=Ke).
- Ranges (min/max): Exclude NaN cells. Football field and Summary use only valid positive values.

## Flagging System (22 rules)
- Rules 1-7 in `flags.py`, 8-15 in `flags_rules.py`, 16-20 in `flags_rules_v2.py`, 21-22 in `flags_industry.py`. Config in `flags_config.py`. Suppression in `flags_helpers.py`.
- **Knowledge base (`flags_config.py`):** Centralized skip lists and industry configs. `SKIP_RULES` dict maps each category to rules that should not fire. `LOW_MARGIN_INDUSTRIES` set prevents margin-below-industry flags for discount retailers/commodity businesses. `should_skip(rule_name, category)` replaces scattered if/else logic.
- **Industry-relative rules (21-22):** Rule 21 (margin_below_industry): EBIT/net margin vs Damodaran avg, 30%/50% gap. Skips LOW_MARGIN_INDUSTRIES. Rule 22 (roe_below_industry): ROE vs industry avg. Skips when equity is negative (meaningless ROE).
- **Industry data source:** `damodaran_industry.py` fetches 4 Damodaran Excel files (margin.xls, dbtfund.xls, divfund.xls, roe.xls). Cached 30 days. Middleware: `valuation_data.get_industry_averages(industry)`.
- **Industry-aware thresholds:** Rules 16 (payout) and 19 (leverage) use industry averages for thresholds when available, falling back to hardcoded tables. Rules 1-2 and 20 append industry context to messages.
- **Category system**: `_get_company_category()` maps sector/industry/company_type → category (default, financial, reit, utility, energy, dividend_stable). All rules check `should_skip()` from config.
- **Financial skip** (banks/insurance): 15 rules skip (margin, debt, FCF, leverage, etc.). Only tax (4), known events (5), M&A (7), goodwill (11), unusual items (17), and industry-relative (21-22) remain.
- **REIT skip**: Tax anomaly (pass-through entity), FCF/NI divergence, earnings quality, payout ratio, dividend coverage all skip. Margin thresholds widened to 5pp/10pp (property gains/losses). Dilution threshold 15%.
- **Utility skip**: FCF/NI divergence, earnings quality, dividend coverage skip (capex-heavy, FCF is wrong metric).
- **Energy**: Margin thresholds 5pp/10pp (cyclical). High-ETR threshold 50% (vs 35% default) — resource taxes and production-sharing make 35-50% ETR normal.
- **Mining**: High-ETR threshold 50% — same resource tax logic. Detected via industry keyword match (mining, metals, steel, gold). Config: `is_resource_company()` in `flags_config.py`.
- **Suppression**: Margin flags suppressed in years with tax anomaly (+next year), M&A, or material unusual items (the event explains the margin movement).
- `detect_flags()` accepts `industry_averages` kwarg. `classify_company()` must be called BEFORE `detect_flags()`.
- **Rule 4 (tax_anomaly):** Low-ETR: 3% for utilities (vs 10% default). High-ETR: 50% for energy/mining (vs 35% default).
- **Rule 6 (capex_spike):** Minimum capex/revenue of 1% required — prevents flagging trivial amounts.
- **Tested on 155 companies** (92 US via `test_flags_80.py` + 63 international via `test_flags_intl.py`). Zero false positives. 530 total flags across US + EMEA + Asia-Pacific + Americas.

## Recommendations System
- `generate_recommendations(prepared_data, dividend_data)` in `lib/analysis/recommendations.py` — orchestrator that builds analyst briefing.
- Model assessment rules in `recommendations_rules.py`: `assess_dcf`, `assess_ddm`, `assess_comps`, `assess_historical`. Each returns `{model, fit, headline, reasons, caveats}`.
- Attention items + risk rules in `recommendations_risks.py`: flag grouping, dividend health, SBC, cyclicality, industry risks, leverage, margin vs industry, growth deceleration.
- Output: `{model_suitability, limited_value_models, attention_items, risks}`.
- `_build_context()` derives signals from prepared_data: FCF analysis, margin stability, revenue volatility, negative equity, flag categories.
- Dividend data fetched at preparation time via `_get_dividend_data()` in `preparation.py` — reuses `ddm_data_{ticker}` session key shared with DDM tab.
- UI rendered by `pages/valuation/preparation_recommendations.py` — model cards with fit badges, attention items with severity, risk section with category tags.
- Tested on 14 companies (PEP, AAPL, JPM, MET, O, DUK, XOM, TSLA, INTC, AMZN, JNJ, GS, AMT, CAT). All produce specific, accurate recommendations.

## Comps Peer Selection
- `filter_peer_universe()` uses GICS mapping for industry-matched peers — correct for valuation.
- `get_suggested_peers()` returns Yahoo "recommended" tickers (often wrong sector) — use only as fallback.

## Testing
- Flagging test US: `scripts/test_flags_80.py` — 92 US companies, 0 FP.
- Flagging test intl: `scripts/test_flags_intl.py` — 63 non-US companies (UK, EU, Canada, Japan, Australia, HK/China, Brazil), 0 FP.
- Main test: `scripts/test_all_valuations.py` — 12 companies (US/Europe/Asia), all modules.
- Reports: `test_results/valuation_test_report_v1.md`, `v2.md`, `v3.md` (v3 is current).
- Verification scripts: `scripts/test_currency_fix.py`, `test_sensitivity_fix.py`, `test_prompt3.py`.
- v3 result: 12/12 PASS, 0 critical errors. All modules working across currencies.

## CSS
- Custom CSS in `assets/styles/custom.css` — loaded by both app.py and page files.
- `max-width: 100%` on `.block-container` for full-width layout.
- Metric cards have subtle background and border via `[data-testid="stMetric"]`.
- Streamlit branding (header, footer, MainMenu) is hidden.

## Self-Check After Every Feature — MANDATORY

**TRIGGER: Before telling the user "búið/done/endurnýrðu" or committing, ALWAYS run this checklist.**
The pre-commit hook catches rules 1-2 automatically. Rules 3-4 require manual verification.

After completing any feature or significant change, run this checklist BEFORE committing:

### Architecture Check
- [ ] Does any `lib/` file import streamlit? (MUST be zero)
- [ ] Does any `pages/` or `pages/company/` file import from `lib.data.providers` directly? (MUST be zero — use middleware)
- [ ] Are all new data fetches going through middleware with cache? (check fundamentals.py or market.py)
- [ ] When new fields are added to a provider, are they passed through middleware → model → page? (trace the full chain)

### Code Quality Check
- [ ] Is any file over 200 lines? If so, split it.
- [ ] Is there duplicated logic? (same dict, same function, same pattern in 2+ places)
- [ ] Are all percentages normalized consistently? (decimal form in models, format_percentage multiplies by 100)
- [ ] Are new data types being cached with appropriate TTL?

### Data Chain Check (for any new data field)
1. Provider returns it in dict ✓
2. Middleware passes it through cache ✓
3. Model has the field ✓
4. Page/component displays it ✓
If any link is missing, the data will silently disappear.

## Documentation Maintenance — AUTOMATIC

Whenever you make changes to the project, you MUST check if the following documents need updating. Do this automatically without the user asking:

1. **ARCHITECTURE.md** — Update if: new files/folders added, new features built, structure changed, new phases defined, feature list items completed.
2. **CLAUDE.md** — Update if: new rules established, new tools/packages added, new conventions agreed upon, project context changed.
3. **VISION.md** — Update if: project philosophy or goals change (rare).
4. **docs/*.md** — Update the relevant doc when building or changing any layer (e.g., update docs/data_layer.md when modifying lib/data/).

**Rule: If you change code, check docs. If docs are stale, update them in the same session. Never leave docs out of sync with code.**

## Context
- User has BS Economics, currently in M.Fin program.
- User does not write Python directly — Claude Code writes all code.
- User has an existing valuation app at `C:\Users\Notandi\Desktop\verkefni 1 - virðisgreining\app.py` with reusable data fetching and valuation functions.
- The app will be shared with others in the future — keep it general, not tied to specific methodologies.
