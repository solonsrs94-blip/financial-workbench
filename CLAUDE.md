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
- SQLite (local data cache — fase 1, cloud later)
- Claude API / Anthropic SDK (AI features — needs API key, fase 3)
- Whisper (earnings call transcription — fase 5)

## Project Structure
```
app.py              → Main Streamlit entry point
pages/              → Streamlit pages (one screen = one file)
  pages/valuation/  → Valuation sub-pages (preparation, dcf steps 2-5, comps, ddm)
    preparation_editor.py → Editable data_editor for override values
    preparation_overrides.py → Rebuild cascade after overrides
    dcf_step2_table.py → Historical + projected FCF table
    dcf_step2_output.py → Calculated FCF output section
    dcf_step3_wacc.py → Step 3 WACC orchestrator
    dcf_step3_ke.py → Step 3A: Cost of Equity (CAPM, 3 beta methods)
    dcf_step3_kd.py → Step 3B: Cost of Debt (actual vs synthetic)
    dcf_step3_structure.py → Step 3C: Capital Structure + WACC output
    dcf_step3_peers.py → Peer Group Beta (table, add/remove, Hamada)
    dcf_step4_terminal.py → Step 4 TV orchestrator (method selector, cross-checks, warnings)
    dcf_step4_methods.py → Step 4 Gordon Growth + Exit Multiple renderers
    dcf_step5_output.py → Step 5 DCF Output orchestrator (EV, implied price, summary)
    dcf_step5_bridge.py → Step 5 Equity Bridge (EV → equity value, overridable)
    dcf_step5_sensitivity.py → Step 5 Sensitivity tables (WACC×growth, WACC×multiple)
    historical_tab.py → Historical Multiples orchestrator (period/multiple controls)
    historical_chart.py → Historical Multiples time series charts (Plotly, ±1σ bands)
    historical_summary.py → Summary statistics + implied value tables
    historical_football.py → Football field chart (10th-90th percentile range)
    ddm_tab.py → DDM orchestrator (Gordon Growth + 2-Stage)
    ddm_step1_ke.py → DDM Step 1: Cost of Equity (independent CAPM)
    ddm_step1_peers.py → DDM Step 1: Peer Group Beta (ddm_ session keys)
    ddm_step2_assumptions.py → DDM Step 2: Model selection + dividend projections
    ddm_step2_reference.py → DDM Step 2: Reference data, warnings, history
    ddm_step3_output.py → DDM Step 3: Implied price, sensitivity, football field
    summary_tab.py → Summary tab orchestrator (reads all model outputs)
    summary_table.py → Summary: Valuation overview table
    summary_football.py → Summary: Combined football field chart (all models)
components/         → Reusable UI components (ticker search, charts, tables, explainer)
lib/                → Core logic — NO Streamlit imports allowed here
  lib/data/         → Data fetching + standardization
    providers/      → Raw data sources (yahoo, simfin, damodaran, edgar, peer_beta)
      damodaran.py → ERP, CRP, spreads, industry betas (US/global/emerging)
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
    flags.py        → 15-rule flagging system (anomaly detection)
    company_classifier.py → normal / financial / dividend_stable
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
  lib/exports/      → Report generation (PDF, Excel, templates)
  lib/storage/      → Storage abstraction (local SQLite now, cloud later)
  lib/auth/         → User authentication (fase 6)
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
- API keys go in `.env`, read via `config/settings.py`.
- `.env` is in `.gitignore` — never committed.

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
- DDM session keys use `ddm_` prefix: `ddm_ke`, `ddm_assumptions`, `ddm_output`, `ddm_data_{ticker}`, `ddm_ke_peers`. Never collides with `dcf_`/`wacc_` keys.
- Summary tab reads from: `dcf_output` (implied_price, sensitivity_min/max, wacc, terminal_growth), `comps_valuation` (implied_prices with low/median/high per multiple), `historical_result` (implied_values with at_p10/at_median/at_p90 per multiple), `ddm_output` (implied_price, sensitivity_min/max, ke, g). Summary never writes to session_state — pure read-only.

## Sensitivity Rules
- Floor: Cells where g >= Ke (DDM) or implied price <= 0 (DCF) → NaN, displayed as "—" in UI.
- Cap: Implied price > 100x current price → NaN (excludes asymptotic Gordon values near g=Ke).
- Ranges (min/max): Exclude NaN cells. Football field and Summary use only valid positive values.

## Comps Peer Selection
- `filter_peer_universe()` uses GICS mapping for industry-matched peers — correct for valuation.
- `get_suggested_peers()` returns Yahoo "recommended" tickers (often wrong sector) — use only as fallback.

## Testing
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
