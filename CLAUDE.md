# Financial Workbench

Personal financial analysis workbench with AI-powered features and educational tools.
Read VISION.md for project philosophy. Read ARCHITECTURE.md for full structure, features, and phases.

## Tech Stack
- Python 3.11+
- Streamlit (UI framework — fase 1, React later)
- yfinance (market data — no API key needed)
- fredapi (macro data — needs API key, fase 4)
- edgartools (SEC filings)
- Plotly (interactive charts — preferred over Matplotlib)
- SQLite (local data cache — fase 1, cloud later)
- Claude API / Anthropic SDK (AI features — needs API key, fase 3)
- Whisper (earnings call transcription — fase 5)

## Project Structure
```
app.py              → Main Streamlit entry point
pages/              → Streamlit pages (one screen = one file)
components/         → Reusable UI components (ticker search, charts, tables, explainer)
lib/                → Core logic — NO Streamlit imports allowed here
  lib/data/         → Data fetching (providers/ + middleware)
  lib/analysis/     → Calculations (valuation, technicals, risk, etc.)
  lib/ai/           → AI features (chat, document reader, tutor, etc.)
  lib/education/    → Education system (curriculum, concepts, prompt builder)
  lib/workspace/    → Analysis sessions (data + reasoning + AI narrative)
  lib/sandbox/      → AI experiment station (code generation + execution)
  lib/alerts/       → Alert system (conditions + notifications)
  lib/exports/      → Report generation (PDF, Excel, templates)
  lib/storage/      → Storage abstraction (local SQLite now, cloud later)
  lib/auth/         → User authentication (fase 6)
models/             → Data models (company, portfolio, experiment, etc.)
data/               → Local storage (cache, portfolio, experiments, sessions, education)
assets/             → CSS styles and educational diagrams
config/             → Settings and constants
docs/               → Technical documentation for each layer
scripts/            → Maintenance (clear cache, update Damodaran, backup)
tests/              → Tests for data, analysis, and cache
```

## Critical Rules — NEVER break these

### 1. Layer separation
- `lib/` must NEVER import Streamlit. No `import streamlit` or `st.` anywhere in lib/.
- `pages/` calls `components/` for UI and `lib/` for data/logic. Never the reverse.
- `providers/` never call each other. Middleware files (market.py, fundamentals.py, macro.py) coordinate between them.

### 2. Data flow
- ALL data fetching goes through `lib/data/`, never directly from pages/.
- Always check `lib/cache.py` before making API calls.
- Data passes through `models/` for standardized format.
- Handle API failures gracefully — show cached data if available, clear error message if not.

### 3. File size
- No file should exceed ~200 lines. If it does, split into submodules.
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
- When comparing companies across currencies, convert to USD using `{CURRENCY}=X` Yahoo ticker.

## CSS
- Custom CSS in `assets/styles/custom.css` — loaded by both app.py and page files.
- `max-width: 100%` on `.block-container` for full-width layout.
- Metric cards have subtle background and border via `[data-testid="stMetric"]`.
- Streamlit branding (header, footer, MainMenu) is hidden.

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
