# Vision Financial Workbench — Roadmap

Langtímaáætlun frá núverandi stöðu að "perfected personal tier" og lengra í Professional tier. Þetta skjal er uppfært eftir því sem áfangar klárast.

**Stöðustaða:** 2026-04-18 — Skeleton-first arkitektúr klárá (Chunks 1-4 í skeleton-viku). Fasi 1 eftir.

---

## Vision & strategy (quick refresher)

**Eitt app, tveir tiers, ein codebase.**

- **Personal tier** (aðalfókus) — full analytical toolkit fyrir sophisticated einstaklingsfjárfestir. Full DCF dýpt, valuation suite, screener, watchlist, portfolio + tax + planning, macro, journal, AI, academy.
- **Professional tier** (framtíðarfasi) — deal-oriented tools ofan á personal. LBO, M&A, SOTP, pitch-book output, collaboration.

**Gæðakrafa:** "Theoretically IB-grade" — engine-kjarninn er rétt útfærður svo fagmaður *gæti* notað hann í stað CapIQ/FactSet fyrir public equity analytical work.

**Gagnastefna:** Free + ódýr + Claude API pipelines. Engar institutional áskriftir (BBG, Refinitiv, FactSet aldrei). Sjá [project_data_strategy.md](../.claude/projects/memory/project_data_strategy.md).

---

## Núverandi staða (2026-04-18)

### ✅ Búið
- Firebase auth + approval flow
- Save/Load valuations (Firestore)
- Company Overview page með 7 tabs
- Financial Preparation með 22-rule flags, recommendations, industry benchmarks
- Valuation suite: DCF (partial), Comps, DDM, Historical, Summary — allir með Bull/Base/Bear scenarios
- Tier infrastructure (personal/professional flag, tier_guard, tier_badge)
- Status dashboard með `FEATURE_STATUS` single source of truth
- Enhanced `render_placeholder()` með phase/target/progress/tier kwargs
- `st.navigation()` grouped nav (Research / Portfolio / Context / Tools / Professional)
- 15 placeholder pages (Journal, Settings, Calendars, News + 8 existing + 3 professional)
- 13 pages/ subfolders með tab stubs
- 12 lib/ subfolders með ~70 NotImplementedError stubs
- CLAUDE.md uppfært með tier/placeholder/normalization rules

### 🟡 Partial
- DCF engine — core math virkar en 10+ IB-grade improvements eftir (sjá Fasi 1-2)
- Valuation Summary — football field virkar, vantar Monte Carlo distribution og audit trail

### 🚧 Placeholder (13 features)
Allir með `render_placeholder()` og í nav. Bygging í Fasa 3-6.

**Overall progress:** ~32% (6 done / 2 partial / 14 placeholder af 22 features)

---

# Fasar

## Fasi 1 — Grunnpólering (0-2 mán)

**Markmið:** Laga grunn DCF og arkitektúr áður en fleiri features bætast við. Án þess er restin byggð á brotinu grunn.

### Critical (real bug fixes)

- [ ] **Bridge safety — hard errors í stað silent fallbacks**
  - [dcf_step5_output.py:131-177](pages/valuation/dcf_step5_output.py#L131) notar `shares_raw ... or 1`, `net_debt or 0`
  - Ef Yahoo gögn vantar → kolrangt implied price án viðvörunar
  - Lagfæring: `None`-return úr lib/, UI handlar með user-facing warning

- [ ] **SBC GAAP/Non-GAAP toggle**
  - [dcf.py:73](lib/analysis/valuation/dcf.py#L73) dregur SBC frá FCF
  - Ef EBIT margin er GAAP (yfinance default) → SBC tvítalið → 2-4% skekkja fyrir tech
  - Lagfæring: UI toggle "EBIT basis: GAAP / Non-GAAP". GAAP → sbc_pct=0 default.

- [ ] **Marginal vs effective tax split**
  - [dcf.py:46](lib/analysis/valuation/dcf.py#L46) notar eina `tax_rate`
  - WACC á að nota marginal (21% US), NOPAT effective (15-20%)
  - Lagfæring: Nýtt `lib/data/normalization/taxes.py` (skeleton þegar til)

### Important (adds rigor)

- [ ] **Operating leases capitalization**
  - Vantar fyrir US-GAAP pre-2019 og þar sem ASC 842 er óháld
  - Fyrir retail/airlines/shipping → vanmetið debt + ofmetið margins
  - Lagfæring: `lib/data/normalization/financials.py` kapitaliserar `rent_expense × 7-8x`

- [ ] **Currency handling full audit**
  - `price_factor` notað í sumum stöðum, ekki öllum
  - Test case með GBp-ticker (Shell, BP) til að staðfesta

### Hygiene

- [ ] **Split 3 skráa á 300-línu mörkum**
  - [dcf_step2_table.py](pages/valuation/dcf_step2_table.py) — 300 línur
  - [summary_tab.py](pages/valuation/summary_tab.py) — 299 línur
  - [ddm_step1_ke.py](pages/valuation/ddm_step1_ke.py) — 299 línur
  - Skipta hvert í 2-3 sub-modules

- [ ] **Þrífa .tmp skrár** — 24 editor artifacts í pages/valuation/

### Útkoma Fasa 1
DCF er rétt og traustur fyrir alvöru notkun. Normalization layer byrjaður. Arkitektúr stendur á solid grunn fyrir Fasa 2.

**Tímamat:** 2-3 vikur focused.

---

## Fasi 2 — DCF engine IB-grade (2-5 mán)

**Markmið:** DCF vélin er theoretically IB-grade — engine-kjarninn er óaðgreinanlegur frá Excel-módelum Goldman/Morgan Stanley.

### Methodology expansions

- [ ] **Mid-year convention + stub period**
  - `discount = 1 / (1+WACC)^(t − 0.5)` með UI toggle
  - `days_to_next_fyend` → ár 1 með stub fraction
  - IB default; gefur ~(1+WACC)^0.5 hærri EV

- [ ] **Iterative WACC ↔ equity value**
  - Markaðsþyngdir D/V nota núverandi market cap, en DCF framleiðir implied equity value
  - Iteratívur solver — endurreikna þar til D/V breytist < 0.1%

- [ ] **Unlevered/relevered own beta**
  - Unlever Yahoo beta með current D/E, relever með target D/E
  - Forðar mismatch þegar notandi notar target capital structure

- [ ] **Target vs current capital structure toggle**
  - Input `target_d_v`; WACC notar target, bridge notar current net debt
  - Nauðsynlegt fyrir LBO-target valuations eða restructurings

- [ ] **Maintenance vs growth CapEx split**
  - Terminal FCF ætti að nota maintenance capex (= D&A í steady-state)
  - Growth capex fer í 0 á terminal

- [ ] **ROIC-consistent terminal value (Value Driver formula)**
  - `TV = NOPAT × (1 − g/ROIC) / (WACC − g)` við hlið Gordon + Exit Multiple
  - Tryggir að reinvestment rate er samræmd við g og ROIC

- [ ] **H-model / 3-stage DCF**
  - Explicit → fade → terminal
  - Fyrir hávaxtarfyrirtæki sem hoppa ekki beint í 2.5% terminal

- [ ] **APV method toggle**
  - Alternative til WACC-DCF fyrir breytilega kapitalstrúktúr
  - Unlevered firm value + PV of tax shield separately

### New analytical tools

- [ ] **Reverse DCF**
  - Solve fyrir implied growth eða implied WACC given market price
  - "What needs to be believed" analysis — IB pitch-book staple

- [ ] **Monte Carlo simulation**
  - Dreifingar á revenue growth, margin, WACC → 10,000 iterations
  - Skilar 90% confidence interval, ekki bara point estimate

- [ ] **Tornado diagram**
  - Sensitivity af hverjum input sérstaklega
  - Raðað eftir áhrifum — sýnir hvað skiptir mestu

### Validation layer

- [ ] **Cross-method consistency checks**
  - Reinvestment rate sanity (`g = reinvestment × ROIC`)
  - DCF implied multiple vs current trading multiple
  - Industry benchmark warnings (WACC, CAGR, margin vs Damodaran)

### Útkoma Fasa 2
DCF er theoretically IB-grade. Allar methodology expansions og validation layer til staðar. Personal tier valuation suite er nú á sama stigi og junior IB analyst Excel módel.

**Tímamat:** 3-4 mán focused.

---

## Fasi 3 — Missing personal-tier pages (5-15 mán)

**Markmið:** Allar personal-tier síður virkar — ekki lengur placeholders. A-Ö fjárfestingatól.

Skipt í 6 sub-fasa sem hægt er að keyra quasi-parallelt eða í röð.

### Fasi 3a — Discovery & Tracking (3-4 mán)

- [ ] **Technical Charts** ([4_charts.py](pages/4_charts.py))
  - OHLC/candlestick með Plotly, multi-timeframe
  - Indicators: SMA/EMA/RSI/MACD/Bollinger
  - Drawing tools (trend lines, S/R, Fibonacci)
  - Pattern recognition (candlestick + chart patterns)

- [ ] **Screener** ([5_screener.py](pages/5_screener.py))
  - Fundamental filters (PE, margin, growth, debt)
  - Technical filters (breakouts, patterns)
  - Thematic baskets (AI, dividend aristocrats, recession-resistant)
  - IPO calendar + screener
  - Saved screens

- [ ] **Watchlist** ([6_watchlist.py](pages/6_watchlist.py))
  - Multiple named watchlists
  - Per-stock alerts (price, earnings, filings, flag triggers)
  - Alert engine í `lib/alerts/`

- [ ] **Portfolio Tracker** ([7_portfolio.py](pages/7_portfolio.py))
  - Transaction log með cost basis (FIFO/LIFO/specific-lot)
  - Holdings, daily P&L, weighted returns
  - Risk analytics (beta, vol, max drawdown, Sharpe, correlation, factor exposure)
  - Rebalancing suggestions (target vs actual allocation)
  - Corporate actions handler (splits, spinoffs, mergers)
  - Multi-account aggregation

### Fasi 3b — Tax & Planning (2-3 mán)

- [ ] **Tax-loss harvesting** (Portfolio tab)
  - Identify positions í loss fyrir harvest
  - Wash-sale rule tracker
  - Tax-lot optimizer

- [ ] **Realized gains/losses reports**
  - Per fiscal year, for tax filing
  - US + Iceland formats

- [ ] **Dividend income tracker**
  - History, yield on cost, dividend growth
  - Tax classification (qualified vs ordinary í US)

- [ ] **Retirement calculator**
  - Savings rate, withdrawal rate, runway
  - Separett accounts (401k/IRA, Séreign í IS context)

- [ ] **Goal-based planning**
  - "I want $X by age Y"
  - Cash flow projections (dividends, tax liability)

### Fasi 3c — Calendars & Events (1-2 mán)

- [ ] **Earnings calendar** ([13_calendars.py](pages/13_calendars.py))
  - Before/after market, expected EPS/revenue
  - Watchlist integration

- [ ] **Economic calendar**
  - Fed meetings, CPI, NFP, GDP sourced frá FRED
  - Configurable country filter

- [ ] **SEC filings alerts**
  - 8-K, 10-K/Q, insider Form 4
  - Per-watchlist filtering

- [ ] **Ex-dividend calendar**

- [ ] **IPO calendar** (líka í Screener Fasa 3a)

### Fasi 3d — Macro & News (2 mán)

- [ ] **Macro Overview** ([8_macro.py](pages/8_macro.py))
  - FRED integration (macro dashboard)
  - Sector rotation view
  - Yield curve visualizer (interactive multi-date)
  - Currencies (DXY, majors, ISK crosses)
  - Commodities (oil, gold, copper, ag)
  - Sentiment indicators (VIX, put/call, AAII, Fear & Greed)

- [ ] **News Feed** ([14_news.py](pages/14_news.py))
  - Per-ticker feeds
  - Macro news
  - Thematic subscribing
  - AI-powered summarization (Claude API)
  - Sentiment tagging

### Fasi 3e — Asset Class Expansions (2-3 mán)

- [ ] **ETF analysis**
  - Holdings, expense ratio, overlap með öðrum ETFs
  - Factor tilt

- [ ] **Bond analysis (light)**
  - YTM, duration, credit for holdings
  - TRACE integration

- [ ] **Options basics**
  - Covered calls, cash-secured puts screener
  - Options chain viewer
  - Greeks, IV

- [ ] **REIT-specific metrics**
  - FFO, AFFO, occupancy, NAV

### Fasi 3f — AI, Learning, Journal (2-3 mán)

- [ ] **AI Assistant** ([9_ai.py](pages/9_ai.py))
  - Chat interface með Claude API
  - Research assistant með context injection (portfolio + holdings)
  - Document reader (10-K summarizer, filing parsing)
  - Sandbox (code generation)

- [ ] **Investment Journal** ([11_journal.py](pages/11_journal.py))
  - Per-stock notes (markdown, searchable)
  - Thesis templates með tracking
  - Ideas queue
  - Research library (articles + annotations)

- [ ] **Academy** ([10_academy.py](pages/10_academy.py))
  - Structured learning paths (DCF 101, 10-K reading, ratios)
  - Glossary með AI-powered explanations
  - Interactive lessons

- [ ] **Comparison sheets**
  - Side-by-side fundamentals fyrir 2-5 companies

### Útkoma Fasa 3
Full A-Ö persónulegt fjárfestingatól. Allir placeholders orðnir real. Notandi getur gert research → valuation → decision → tracking → tax → planning í sama tóli.

**Tímamat:** 10-15 mán focused.

---

## Fasi 4 — Data depth (10-14 mán, overlaps with Fasi 3)

**Markmið:** Data stack keppir við pro-sumer tools (Koyfin, Simply Wall St, Stockanalysis.com). Bygging gerir Fasa 3 features dýpri.

### Free source integrations

- [ ] **FRED integration** — macro (Fasi 3d dependency)
- [ ] **FMP free tier** — estimates backup, global fundamentals
- [ ] **Finnhub free tier** — alternative data (Congress trading, lobbying)
- [ ] **FINRA TRACE** — US corporate bond data
- [ ] **Companies House (UK)** — if UK coverage important

### Accumulated data pipelines

- [ ] **13F parser og ownership tracker**
  - SEC EDGAR 13F/13D/Form 4 scraping
  - Quarterly accumulation, change tracking
  - "What does Buffett own?" view

- [ ] **Earnings transcript pipeline**
  - Seeking Alpha scraping (respecting ToS)
  - Whisper fallback fyrir coverage gaps
  - LLM parsing fyrir Q&A split + sentiment

- [ ] **Historical estimate revisions**
  - Wayback Machine backfill (3-5 ár aftur fyrir top 500 tickers)
  - Daily yfinance snapshot (accumulates going forward)
  - JS render workarounds (archive.ph, API endpoint sniffing)

- [ ] **Synthetic credit ratings**
  - Damodaran methodology (interest coverage → implied rating → spread)
  - Already partially in [wacc.py](lib/analysis/valuation/wacc.py) via `synthetic_kd`
  - Expand to full credit analysis output

### Optional paid addition ($200 eitt skipti)

- [ ] **Sharadar SF1 bulk download**
  - 1 mán subscribe via Nasdaq Data Link
  - Bulk download 20+ ár af US equity fundamentals
  - Store í local PostgreSQL
  - Cancel áskrift
  - **Gefur IB-grade historical fundamentals fyrir ~$200 eitt skipti**

### Útkoma Fasa 4
Data moat sem er sjaldgæfur í open-source landinu. Notandi fær dýpt sem réttlætir "theoretically IB-grade" fullyrðingu fyrir US public equity analytical work.

**Tímamat:** 3-4 mán focused (samhliða Fasa 3).

---

## Fasi 5 — Personal tier pólering (14-18 mán)

**Markmið:** Personal tier er "perfected" — notandi finnst ekkert vanta.

- [ ] **Quick mode toggle í DCF**
  - 5 inputs vs 50 — fyrir fljótlega skönnun
  - Available öllum notendum, ekki tier-gated

- [ ] **Keyboard shortcuts** — power users
- [ ] **Dark mode** — sophisticated retail expects this
- [ ] **PDF export pólering** — clean 1-pager
- [ ] **Saved templates** — "mínar default forsendur fyrir tech"
- [ ] **Performance optimization** — 10+ ára historical load < 3 sek
- [ ] **Comprehensive error handling** — no "oops something went wrong"
- [ ] **End-to-end test coverage** — regression tests fyrir DCF/DDM/Comps
- [ ] **Data freshness banners** — alls staðar sem data birtist

### Útkoma Fasa 5
Personal tier er production-quality. Tilbúið til að deila víðar eða markaðssetja.

**Tímamat:** 2-3 mán.

---

## Fasi 6+ — Professional tier (18+ mán)

**Markmið:** Professional tier features fara úr placeholder í real. Fagmaður *gæti* notað í stað CapIQ fyrir deal analytics.

### 6a — Deal modeling tools

- [ ] **LBO Modeling** ([20_lbo.py](pages/20_lbo.py))
  - Entry/exit IRR, debt schedule, MOIC
  - Reuses FCF projection frá DCF
  - Sensitivity grids (entry mult × debt ratio → IRR)

- [ ] **M&A Accretion/Dilution** ([21_ma.py](pages/21_ma.py))
  - Target + acquirer selection
  - Synergies model (revenue + cost, integration costs)
  - Pro-forma IS/BS/CF
  - EPS impact Year 1-3

- [ ] **SOTP Mode (DCF)**
  - Multiple segments per company
  - Segment-level DCF runs
  - Summa + holdco discount

### 6b — Data depth (Professional-only)

- [ ] **M&A Precedents Database** ([22_precedents.py](pages/22_precedents.py))
  - Stærsta data engineering verkefnið
  - EDGAR scraping (DEFM14A, 8-K)
  - LLM parsing með Claude API
  - US public-target coverage ~80-90%
  - 3-6 mán vinna

- [ ] **Bond-level debt analysis**
  - 10-K footnote parsing (LLM-aided)
  - Per-issue YTM, maturity, covenants
  - Debt maturity tower visualization

- [ ] **Industry-specific overlays**
  - SaaS metrics (ARR, CAC, LTV, NRR)
  - Banking (NIM, efficiency ratio, Tier 1)
  - Energy/E&P (reserves, finding cost, netback)

### 6c — Output & collaboration

- [ ] **Pitch-book PDF output**
  - 1-pager eða full deck
  - IB-style football field, tables, charts

- [ ] **Excel export með formúlum**
  - Ekki bara values — raunveruleg Excel með live formulas
  - Color-coded (blue input / black formula / green link)

- [ ] **Collaboration features**
  - Share valuation með link
  - Read-only snapshots
  - Comment/discussion per model

### Útkoma Fasa 6+
"Theoretically IB-grade" — fagmaður *gæti* notað fyrir 70-85% af klassískri analytical vinnu.

**Tímamat:** 6-12 mán focused (eftir að personal tier er klárt).

---

# Cross-cutting principles

Þessar reglur eiga við um **alla fasa** — sjá [CLAUDE.md](CLAUDE.md) fyrir nákvæmar útfærslur.

- **Layer separation:** `lib/` er án `streamlit`. `pages/` kallar á `lib/` og `components/`.
- **Middleware-first:** Allar data fetches fara í gegnum `lib/data/` (fundamentals, market, valuation_data, news, calendars).
- **Cache-first:** Allar API call fara í gegnum `lib/cache.py` með viðeigandi TTL.
- **Normalization-first:** Adjusted financials (lease, tax, cash) lesast úr `lib/data/normalization/`, aldrei inline.
- **No silent fallbacks:** Kritísk gögn → `None` + UI error, ekki `or 0`.
- **Status dashboard sync:** Hver feature change uppfærir `FEATURE_STATUS` FYRST (placeholder → partial → done).
- **Tier-aware UI:** Professional features með `require_professional()` guard, aldrei ad-hoc checks.
- **Data freshness visible:** Notandi sér alltaf hvenær gögn voru sótt.

---

# Heildartímamat

| Fasi | Time (part-time, 10-15h/viku) | Time (full-time) |
|------|-------------------------------|------------------|
| 1 — Grunnpólering | 2-3 vikur | 1 vika |
| 2 — DCF IB-grade | 3-4 mán | 6-8 vikur |
| 3 — Personal pages | 10-15 mán | 4-6 mán |
| 4 — Data depth | 3-4 mán (parallel) | 2 mán |
| 5 — Pólering | 2-3 mán | 1-2 mán |
| **Subtotal (Personal perfected)** | **20-28 mán** | **9-14 mán** |
| 6 — Professional tier | 6-12 mán | 3-6 mán |
| **Total to full vision** | **26-40 mán** | **12-20 mán** |

---

# Current focus (next 2-3 vikur)

**Fasi 1, fyrst:** Bridge safety + clean .tmp → quick win (hálfur dagur). Svo marginal/effective tax split + operating leases capitalization → nýja normalization lagið byrjað.

---

# Skjalstoð

- [CLAUDE.md](CLAUDE.md) — reglur fyrir AI assistant og kóða-staðla
- [ARCHITECTURE.md](ARCHITECTURE.md) — heildstæð uppbygging, möppuskipulag
- [VISION.md](VISION.md) — project philosophy
- [components/status_dashboard.py](components/status_dashboard.py) — live status tracker
- Memory files í `.claude/projects/.../memory/` — user preferences + project strategy

---

**Next update:** Eftir að Fasi 1 er kláraður, uppfæra stöðu og tick-a af tasks hér.
