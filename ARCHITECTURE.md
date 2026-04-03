# Financial Workbench — Architecture

Lifandi skjal sem lýsir uppbyggingu appsins. Uppfært eftir því sem appið þróast.

---

## Meginreglur

1. **`lib/` veit ekkert um UI.** Engin `import streamlit` í lib/ skrám — aldrei.
2. **`pages/` notar `components/` og `lib/`.** Aldrei öfugt.
3. **`providers/` tala aldrei saman.** Mellanlags-skrár (`market.py`, `fundamentals.py`, `macro.py`) tengja þau.
4. **`strategies/` eru viðbætur.** Appið virkar án þeirra — þær bæta við greiningaraðferðum.
5. **`storage/` er abstraction.** Appið veit ekki hvort gögn eru local eða cloud.
6. **`config/settings.py` les úr `.env`.** Engir lyklar í kóða.
7. **Skrár fara ekki yfir 300 línur.** (Framfylgt af pre-commit hook.) Ef svo, skipta í undirhluta.
8. **Undirmöppur í `pages/` verða til þegar þörf er á.** Ekki fyrr.
9. **Ný gagnaveitur** → ný skrá í `providers/`, uppfæra mellanlags-skrá.
10. **Nýjar aðferðir** → ný skrá í `strategies/`.
11. **Nýir skjáir** → ný skrá í `pages/`.

---

## Lagskipting — hvernig allt tengist

```
pages/           veit um →  components/ og lib/
components/      veit um →  lib/
lib/education/   veit um →  lib/ai/, lib/data/, lib/analysis/ og models/
lib/ai/          veit um →  lib/data/, lib/analysis/ og models/
lib/analysis/    veit um →  lib/data/ og models/
lib/data/        veit um →  lib/storage/ og providers/
lib/storage/     veit um →  ekkert annað
```

Þetta tryggir að hvert lag er sjálfstætt. Hægt er að skipta út UI laginu (Streamlit → React) án þess að snerta `lib/`.

---

## Gagnaflæði

### Almennt gagnaflæði
```
Notandi opnar skjá
    ↓
pages/X.py — kallar á components/ fyrir UI og lib/ fyrir gögn
    ↓
lib/data/market.py (eða fundamentals.py, macro.py) — mellanlags-lag
    ↓
lib/cache.py — er þetta í cache?
    ├── JÁ → skilar gögnum strax
    └── NEI → kallar á provider
              ↓
              lib/data/providers/yahoo.py (eða annan provider)
              ↓
              Gögn fara í gegnum models/ → staðlað form
              ↓
              Gögn vistuð í cache
              ↓
              Skilað til skjás
    ↓
components/charts.py (eða tables.py, o.fl.) — sýnir gögnin
```

### Financial Preparation gagnaflæði
```
Normal companies:
  yfinance (income_stmt, balance_sheet, cashflow)
      ↓
  lib/data/yfinance_standardizer.py  →  standardized dict (original)
      ↓
  lib/data/override_utils.py         →  apply user overrides (if any)
      ↓
  lib/analysis/historical.py         →  IS/BS/CF tables
      ↓
  lib/analysis/historical_ratios.py  →  ratios per year
      ↓
  lib/analysis/historical_flags.py   →  anomaly flags + 3yr averages
      ↓
  st.session_state["prepared_data"]  →  used by DCF Steps 2-5

Override cascade: user edits value → override_utils merges with original
  → tables/ratios/flags/averages all rebuilt → charts + DCF update

Banks/Insurance:
  SimFin → lib/data/financial_data.py → same prepared_data format
```

---

## Möppuskipulag

```
Vision/
│
├── app.py                              ← Ræsir appið
│
│
│   ╔═══════════════════════════════════════╗
│   ║           SKJÁIR (UI LAG)            ║
│   ╚═══════════════════════════════════════╝
│
├── pages/                              ← Hver skjár er sín skrá
│   ├── 1_company.py                    ← Fyrirtækjayfirlit
│   ├── 2_financials.py                 ← Ársreikningar
│   ├── 3_valuation.py                  ← Virðismat (DCF, comps)
│   ├── 4_screener.py                   ← Almenn hlutabréfasía
│   ├── 5_analysis.py                   ← Greiningarvinnusvæði
│   ├── 6_chart.py                      ← Tæknigraf og sjónræn greining
│   ├── 7_macro.py                      ← Þjóðhagsyfirlit
│   ├── 8_portfolio.py                  ← Eignasafn
│   ├── 9_sandbox.py                    ← AI tilraunastöð
│   ├── 10_watchlist.py                 ← Vaktlistar
│   ├── 11_comparison.py                ← Hlið við hlið samanburður
│   ├── 12_heatmap.py                   ← Hitakort markaðarins
│   ├── 13_calendar.py                  ← Afkoma + efnahagsdagatal
│   ├── 14_options.py                   ← Valréttargreining
│   ├── 15_backtest.py                  ← Prófun á aðferðum
│   ├── 16_risk.py                      ← Áhættugreining
│   ├── 17_insiders.py                  ← Innherjaviðskipti
│   ├── 18_chat.py                      ← AI spjall — spyrðu gögnin hvað sem er
│   └── 19_learn.py                     ← Námsmiðstöð / Academy
│
│   (Undirhlutar — verða til þegar skjár stækka)
│   ├── valuation/
│   │   ├── preparation.py              ← Financial Preparation (runs before all tabs)
│   │   ├── preparation_display.py      ← Charts, tables, ratios display
│   │   ├── preparation_editor.py       ← Editable data_editor for override values
│   │   ├── preparation_overrides.py    ← Rebuild cascade after overrides
│   │   ├── dcf_tab.py                  ← DCF tab orchestrator (Steps 2-5)
│   │   ├── dcf_step2_assumptions.py    ← Step 2: Assumptions + controls
│   │   ├── dcf_step2_table.py          ← Step 2: Historical data + projection math
│   │   ├── dcf_step2_output.py         ← Step 2: Calculated FCF output rendering
│   │   ├── dcf_step3_wacc.py           ← Step 3: WACC orchestrator
│   │   ├── dcf_step3_ke.py            ← Step 3A: Cost of Equity (Ke)
│   │   ├── dcf_step3_kd.py            ← Step 3B: Cost of Debt (Kd)
│   │   ├── dcf_step3_structure.py     ← Step 3C: Capital Structure + WACC output
│   │   ├── dcf_step3_peers.py        ← Step 3: Peer Group Beta (table + add/remove)
│   │   ├── dcf_step4_terminal.py       ← Step 4: Terminal Value orchestrator
│   │   ├── dcf_step4_methods.py       ← Step 4: Gordon Growth + Exit Multiple renderers
│   │   ├── dcf_step5_output.py         ← Step 5: DCF Output orchestrator (EV, bridge, price)
│   │   ├── dcf_step5_bridge.py        ← Step 5: Equity Bridge with overrides
│   │   ├── dcf_step5_sensitivity.py   ← Step 5: Sensitivity tables (WACC×g, WACC×multiple)
│   │   ├── comps_tab.py                ← Comps tab orchestrator (3 steps)
│   │   ├── comps_step1_peers.py       ← Step 1: Peer Selection (candidate gen + picks)
│   │   ├── comps_step1_table.py       ← Step 1: Candidate table rendering
│   │   ├── comps_step2_table.py       ← Step 2: Comps Table (data + summary logic)
│   │   ├── comps_step2_render.py      ← Step 2: HTML table renderer
│   │   ├── comps_step3_valuation.py   ← Step 3: Implied Valuation (EV bridge + implied prices)
│   │   ├── comps_step3_football.py   ← Step 3: Football Field chart (Plotly horizontal bars)
│   │   ├── ddm_tab.py                  ← DDM tab (placeholder, recommended for banks)
│   │   ├── historical_tab.py           ← Historical tab (placeholder)
│   │   └── summary_tab.py             ← Summary tab (placeholder)
│   ├── chart/
│   │   ├── candlestick.py              ← Kertastjakagraf
│   │   ├── indicators.py              ← RSI, MACD, Volume panels
│   │   ├── overlays.py                ← SMA, EMA, Bollinger á grafinu
│   │   ├── comparison.py              ← Bera saman mörg hlutabréf
│   │   └── drawing.py                 ← Trendlínur, stuðningur/viðnám
│   ├── screener/
│   │   ├── filters.py                  ← Síunarviðmót
│   │   └── results.py                  ← Niðurstöðubirting
│   ├── sandbox/
│   │   ├── input.py                    ← Textainnsláttarsvæði
│   │   ├── results.py                  ← Niðurstöðubirting
│   │   └── history.py                  ← Tilraunasaga
│   └── learn/
│       ├── curriculum.py              ← Námsleiðayfirlit
│       ├── lesson.py                  ← Einn kennslutími
│       └── exercises.py               ← Gagnvirkar æfingar
│
│
│   ╔═══════════════════════════════════════╗
│   ║        SAMEIGINLEGIR UI HLUTAR       ║
│   ╚═══════════════════════════════════════╝
│
├── components/                         ← Endurnýtanlegir UI hlutar
│   ├── ticker_search.py                ← Leitarstika (notuð á öllum skjám)
│   ├── charts.py                       ← Almenn gröf og sjónræn framsetning
│   ├── technical_chart.py              ← Kertastjakar, indicators, overlays
│   ├── tables.py                       ← Stöðluð töfluframsetning
│   ├── annotations.py                  ← Textaboxar fyrir rökstuðning
│   ├── layout.py                       ← Sameiginlegt útlit (header, sidebar)
│   ├── explainer.py                    ← ? hnappur við hverja tölu/forsendu
│   │                                      • Stig 1-3 útskýring
│   │                                      • "Spyrðu AI" hnappur með tilbúnu prompt
│   │                                      • Promptið inniheldur fullt samhengi
│   │                                        (fyrirtæki, tölur, forsendur, skjár)
│   └── guided_mode.py                  ← Leiðsögn í gegnum skjái (tutorial)
│
│
│   ╔═══════════════════════════════════════╗
│   ║       KJARNINN (ENGIN UI KÓÐI)       ║
│   ╚═══════════════════════════════════════╝
│
├── lib/
│   │
│   │   ── GAGNAÖFLUN ──
│   │
│   ├── data/
│   │   ├── providers/                  ← Einstakar gagnaveitur
│   │   │   ├── yahoo.py                ← Verð, fjárhagur, hlutföll, arðir, options
│   │   │   ├── yahoo_valuation.py      ← BS/CF/IS smáatriði + analyst estimates
│   │   │   ├── damodaran.py            ← ERP, beta, CRP, spreads ✅
│   │   │   ├── peer_beta.py           ← Peer suggestions + beta/D/E/tax data
│   │   │   ├── comps_peers.py         ← Finnhub peers + S&P 500 universe + candidate info
│   │   │   ├── comps_data.py          ← Comps multiples data (trailing + forward + EBIT)
│   │   │   ├── peer_universe.py       ← Global peer universe (S&P 500 + Euro STOXX 50 + CAC 40 + FTSE 100 + TSX 60 + Hang Seng)
│   │   │   ├── industry_map.py        ← Yahoo→Damodaran industry name mapping (pure data)
│   │   │   ├── gics_yf_map.py         ← GICS Sub-Industry ↔ yfinance industry mapping (111 industries)
│   │   │   ├── edgar_provider.py       ← Raw EDGAR 10-K (kept, not active)
│   │   │   ├── edgar_xbrl.py           ← XBRL EDGAR (kept, not active)
│   │   │   ├── simfin_provider.py      ← SimFin (banks, insurance, general)
│   │   │   ├── simfin_maps.py          ← SimFin column → standard key mappings
│   │   │   ├── simfin_utils.py         ← SimFin extraction + derived fields
│   │   │   ├── fred.py                 ← Vextir, verðbólga, atvinnuleysi
│   │   │   ├── news.py                 ← RSS feeds og fréttir
│   │   │   ├── insiders.py             ← Innherjaviðskipti (SEC)
│   │   │   ├── earnings_calendar.py    ← Afkomudagsetningar
│   │   │   └── economic_calendar.py    ← Efnahagsdagatal (FOMC, CPI, o.fl.)
│   │   │
│   │   ├── yfinance_standardizer.py    ← PRIMARY: yfinance → prepared_data mapping
│   │   ├── yfinance_maps.py            ← yfinance IS/BS/CF key mappings (pure data)
│   │   ├── override_utils.py           ← Apply/count user overrides (no Streamlit)
│   │   ├── standardizer.py             ← EDGAR standardizer (kept, not active)
│   │   ├── standardizer_engine.py      ← Search engine (kept, not active)
│   │   ├── standardizer_utils.py       ← Derived fields + cross-checks (kept)
│   │   ├── template.py                 ← 35 template lines (kept)
│   │   ├── template_is.py              ← IS search rules (kept)
│   │   ├── template_bs.py              ← BS search rules (kept)
│   │   ├── template_cf.py              ← CF search rules (kept)
│   │   ├── concept_maps.py             ← XBRL concept mappings (kept)
│   │   ├── concept_maps_*.py           ← Split by IS/BS/CF + keywords (kept)
│   │   ├── historical.py               ← Table builders: standardized → IS/BS/CF tables
│   │   ├── financial_data.py           ← Middleware for SimFin (banks/insurance)
│   │   ├── market.py                   ← Mellanlags-lag: verð, söguleg gögn
│   │   ├── fundamentals.py             ← Mellanlags-lag: fjárhagur, hlutföll
│   │   ├── valuation_data.py           ← Mellanlags-lag: virðismat (Rf, Damodaran, BS/CF)
│   │   ├── peer_data.py                ← Mellanlags-lag: peer fjárhagsgögn
│   │   └── macro.py                    ← Mellanlags-lag: þjóðhagsgögn
│   │
│   │   ── ÚTREIKNINGAR OG GREINING ──
│   │
│   ├── analysis/
│   │   ├── company_classifier.py       ← Flokkar: normal / financial / dividend_stable
│   │   ├── flags.py                    ← 15-rule flagging (anomaly detection)
│   │   ├── flags_rules.py              ← Flag rules 8-15
│   │   ├── flags_helpers.py            ← Flag utilities + known events
│   │   ├── historical.py               ← Build IS/BS/CF tables + ratios
│   │   ├── historical_ratios.py        ← Ratio calculations (margins, growth, etc.)
│   │   ├── historical_averages.py      ← 3-year averages
│   │   ├── historical_flags.py         ← Flag orchestrator (calls flags.py)
│   │   ├── valuation/                  ← Virðismatsundirmappa (DCF steps 2-5)
│   │   │   ├── wacc.py                 ← WACC (CAPM, beta, cost of debt)
│   │   │   ├── simple_dcf.py           ← Simple DCF (3-phase growth)
│   │   │   ├── complex_dcf.py          ← Complex DCF (IB-grade)
│   │   │   ├── three_stmt.py           ← 3-Statement model (IS/BS/CF)
│   │   │   ├── terminal.py             ← Terminal value calculations
│   │   │   ├── equity_bridge.py        ← EV → equity per share
│   │   │   ├── sensitivity.py          ← Sensitivity + scenario + reverse DCF
│   │   │   └── sanity.py               ← Implied metrics + warnings
│   │   ├── comps.py                    ← Peer multiples + implied prices
│   │   ├── comps_metrics.py            ← Operating metrics + football field
│   │   ├── scoring.py                  ← Almennt scoring/einkunnakerfi
│   │   ├── screener.py                 ← Síunarreglur og leit
│   │   ├── technicals.py              ← RSI, SMA, EMA, MACD, Bollinger
│   │   ├── portfolio.py                ← Ávöxtun, áhætta, samanburður
│   │   ├── risk.py                     ← VaR, Monte Carlo, stress test
│   │   ├── options.py                  ← Greeks, payoff, implied vol
│   │   ├── backtester.py              ← Prófun aðferða á sögulegum gögnum
│   │   ├── sectors.py                  ← Geiragreining, sector rotation
│   │   ├── sentiment.py               ← AI sentiment á fréttum
│   │   └── strategies/                 ← Aðferðir sem viðbætur (plugins)
│   │       ├── canslim.py              ← CAN SLIM
│   │       ├── value.py                ← Value investing
│   │       └── dividend.py             ← Arðgreiðslugreining
│   │
│   │   ── AI OG TILRAUNIR ──
│   │
│   ├── ai/                             ← Allir AI eiginleikar (Claude API)
│   │   ├── chat.py                     ← Spjall við gögnin ("spyrðu hvað sem er")
│   │   ├── document_reader.py          ← Les og greinir 10-K, 10-Q, PDF
│   │   ├── earnings_analyzer.py        ← Afkomusímtöl: Whisper + greining
│   │   ├── news_digest.py              ← Fréttasamantekt og sentiment
│   │   ├── thesis_challenger.py        ← Ögrar þinni fjárfestingarþesis
│   │   ├── chart_vision.py             ← Mynsturgreining á gröfum (vision)
│   │   ├── narrator.py                 ← Útskýrir tölur á mannamáli
│   │   ├── translator.py              ← Íslensku/ensku þýðingar
│   │   ├── learning.py                 ← Námsaðstoðari í samhengi
│   │   ├── smart_alerts.py             ← Snjall-viðvaranir með útskýringum
│   │   ├── nl_screener.py              ← Náttúruleg málsía ("finndu mér...")
│   │   └── tutor.py                    ← AI kennari (persónuleg kennsla)
│   │
│   ├── workspace/                      ← Greiningarvinnusvæði
│   │   ├── session.py                  ← Ein greining: gögn + forsendur + aths.
│   │   ├── annotations.py             ← Rökstuðningur og athugasemdir
│   │   └── narrative.py               ← AI skrifar skýrslu (notar ai/narrator.py)
│   │
│   ├── sandbox/                        ← AI tilraunastöð
│   │   ├── engine.py                   ← Claude API tenging og kóðagerð
│   │   ├── executor.py                 ← Keyrir AI-gerðan kóða í sandkassa
│   │   └── experiments.py              ← Vistar/sækir tilraunir
│   │
│   │   ── VIÐVARANIR ──
│   │
│   ├── alerts/                         ← Viðvörunarkerfi
│   │   ├── engine.py                   ← Athugar skilyrði reglulega
│   │   ├── conditions.py              ← "Verð > X", "RSI > 70", o.fl.
│   │   └── notifications.py           ← Email, push, webhook
│   │
│   │   ── ÚTFLUTNINGUR ──
│   │
│   ├── exports/                        ← Skýrslugerð
│   │   ├── pdf.py                      ← PDF skýrslur
│   │   ├── excel.py                    ← Excel útflutningur
│   │   └── templates/                  ← Sniðmát fyrir skýrslur
│   │       ├── valuation_report.py     ← Virðismatsskýrsla
│   │       ├── company_overview.py     ← Fyrirtækjayfirlit
│   │       └── custom.py              ← Sérsniðið sniðmát
│   │
│   │   ── GAGNAGEYMSLA ──
│   │
│   ├── storage/                        ← Abstraction lag
│   │   ├── base.py                     ← Interface — skilgreinir hvað geymsla gerir
│   │   ├── local.py                    ← SQLite á tölvunni (fase 1)
│   │   └── cloud.py                    ← Firebase/PostgreSQL (fase 2)
│   │
│   │   ── NOTENDAAUÐKENNING ──
│   │
│   ├── auth/                           ← Notendaauðkenning (fase 6)
│   │   └── __init__.py                 ← Tómt í byrjun
│   │
│   │   ── SAMSKIPTI ──
│   │
│   ├── social/                         ← Samskipti milli notenda (fase 6)
│   │   ├── chat.py                     ← Skilaboð milli notenda
│   │   ├── sharing.py                  ← Deila greiningum, gröfum, vaktlistum
│   │   └── notifications.py            ← Tilkynningar ("Anna deildi greiningu")
│   │
│   │   ── MENNTUN ──
│   │
│   ├── education/                      ← Menntunarkjarninn
│   │   ├── curriculum.py               ← Námsleiðir og uppbygging
│   │   ├── concepts.py                 ← Gagnagrunnur fjármálahugtaka
│   │   ├── exercises.py                ← Gagnvirkar æfingar
│   │   ├── progress.py                 ← Hvar er notandinn í náminu
│   │   └── prompt_builder.py           ← Býr til samhengis-prompt fyrir AI
│   │                                      úr gögnum á skjánum (fyrirtæki,
│   │                                      tölur, forsendur, stig notanda)
│   │
│   │   ── GRUNNÞJÓNUSTUR ──
│   │
│   ├── cache.py                        ← SQLite caching lag
│   ├── helpers.py                      ← Sameiginleg smáföll
│   └── logger.py                       ← Villumeðhöndlun og logging
│
│
│   ╔═══════════════════════════════════════╗
│   ║          GAGNALÍKÖN (MODELS)          ║
│   ╚═══════════════════════════════════════╝
│
├── models/                             ← Skilgreiningar á gagnagerðum
│   ├── company.py                      ← Hvað er "fyrirtæki"
│   ├── portfolio.py                    ← Hvað er "eignasafn"
│   ├── experiment.py                   ← Hvað er "sandbox tilraun"
│   ├── analysis_session.py             ← Hvað er "greining" (gögn + rökstuðn.)
│   ├── watchlist.py                    ← Hvað er "vaktlisti"
│   ├── alert.py                        ← Hvað er "viðvörun"
│   ├── backtest.py                     ← Hvað er "backtest niðurstaða"
│   └── learner.py                      ← Námsframvinda notanda
│
│
│   ╔═══════════════════════════════════════╗
│   ║         FRAMTÍÐAR-API LAG            ║
│   ╚═══════════════════════════════════════╝
│
├── api/                                ← Þunt lag milli lib/ og React (fase 2)
│   └── __init__.py                     ← Tómt í byrjun
│
│
│   ╔═══════════════════════════════════════╗
│   ║          STAÐBUNDIN GEYMSLA          ║
│   ╚═══════════════════════════════════════╝
│
├── data/                               ← Öll staðbundin gögn
│   ├── cache/                          ← API cache (SQLite, CSV)
│   ├── portfolio/                      ← Þínar eignir og viðskipti
│   ├── experiments/                    ← Vistaðar sandbox tilraunir
│   ├── sessions/                       ← Vistaðar greiningar
│   └── education/                      ← Námsframvinda og efni
│       ├── progress/                   ← Hvar notandinn er í hverri námsleið
│       └── content/                    ← Námsefni (ef ekki AI-generated)
│
│
│   ╔═══════════════════════════════════════╗
│   ║          STILLINGAR OG ÚTLIT         ║
│   ╚═══════════════════════════════════════╝
│
├── assets/
│   ├── styles/
│   │   └── custom.css                  ← Sérsniðið CSS
│   └── education/                      ← Myndir og skýringarmyndir
│       └── diagrams/                   ← T.d. "hvernig DCF virkar"
│
├── config/
│   ├── settings.py                     ← API lyklar (les úr .env)
│   └── constants.py                    ← Kortlagningar, fastar, enum
│
│
│   ╔═══════════════════════════════════════╗
│   ║          TÆKNISKJÖLUN                ║
│   ╚═══════════════════════════════════════╝
│
├── docs/                               ← Handbók fyrir forritara
│   ├── overview.md                     ← Heildaryfirlit — byrjaðu hér
│   ├── data_layer.md                   ← Gagnaöflun, providers, cache
│   ├── analysis_layer.md              ← Útreikningar, formúlur, aðferðir
│   ├── ai_layer.md                     ← AI eiginleikar, Claude API, sandbox
│   ├── education_layer.md             ← Menntunarkerfið, námsleiðir
│   ├── storage_layer.md               ← Gagnageymsla, local vs cloud
│   ├── ui_guide.md                     ← UI lag, pages, components
│   ├── api_reference.md               ← Öll föll og hvað þau skila
│   └── deployment.md                   ← Uppsetning, keyrsla, umhverfisbreytur
│
│
│   ╔═══════════════════════════════════════╗
│   ║          VIÐHALD OG PRÓFANIR         ║
│   ╚═══════════════════════════════════════╝
│
├── scripts/                            ← Viðhaldsverkfæri
│   ├── clear_cache.py                  ← Hreinsa gamla cache
│   ├── update_damodaran.py             ← Uppfæra Damodaran töflur
│   └── backup_data.py                  ← Backup á portfolio/experiments
│
├── tests/                              ← Prófanir
│   ├── test_data/                      ← Prófa gagnaöflun
│   ├── test_analysis/                  ← Prófa útreikninga
│   └── test_cache.py                   ← Prófa caching
│
│
│   ╔═══════════════════════════════════════╗
│   ║            RÓTARSKRÁR                ║
│   ╚═══════════════════════════════════════╝
│
├── .env                                ← API lyklar (ALDREI í git)
├── .gitignore                          ← Hvað fer ekki á GitHub
├── requirements.txt                    ← Python pakkar
├── VISION.md                           ← Hugmynd og heimspeki
├── CLAUDE.md                           ← Leiðbeiningar fyrir Claude Code
└── ARCHITECTURE.md                     ← ÞETTA SKJAL
```

---

## Eiginleikalisti — hvað appið getur gert

### Fyrirtækjagreining
- [x] Fyrirtækjayfirlit (verð, lykiltölur, fréttir)
- [x] Ársreikningar (rekstrarreikn., efnahagsreikn., sjóðstreymi)
- [x] Virðismat (Simple DCF, Complex DCF, 3-Statement, WACC með aðferðavalkostum, Comps, Football Field)
- [x] Innherjaviðskipti (kaup/sala stjórnenda)
- [ ] Arðgreiðslusaga og yield

### Markaðsgreining
- [ ] Tæknigröf (kertastjakar, indicators, overlays, teikning)
- [ ] Hitakort markaðarins (geirar, stærð, breyting)
- [ ] Geiragreining og sector rotation
- [ ] Þjóðhagsyfirlit (vextir, verðbólga, atvinnuleysi)
- [ ] Efnahagsdagatal (FOMC, CPI, atvinnuskýrslur)
- [ ] Afkomudagatal (hvenær fyrirtæki tilkynna)

### Leit og síun
- [x] Nafnaleit og ticker leit
- [x] Browse mode (screener flokkar)
- [ ] Almenn hlutabréfasía (hvaða forsendur sem er)
- [ ] Full browse/sía (svæði, land, geirur, kauphöll) — React
- [ ] Hlið við hlið samanburður (2+ fyrirtæki)
- [ ] Quant scoring / einkunnakerfi
- [ ] Vaktlistar

### Greiningaraðferðir (viðbætur)
- [ ] CAN SLIM
- [ ] Value investing
- [ ] Arðgreiðslugreining
- [ ] (Fleiri bætast við eftir þörfum)

### Eignasafn og áhætta
- [ ] Eignasafnsrakning (ávöxtun, skipting, viðmið)
- [ ] Áhættugreining (VaR, Monte Carlo, stress test)
- [ ] Valréttargreining (Greeks, payoff, implied vol)
- [ ] Backtesting (prófun aðferða á sögulegum gögnum)

### AI og tilraunir
- [ ] Sandbox tilraunastöð (lýsa hugmynd → fá niðurstöður)
- [ ] Greiningarvinnusvæði (gögn + rökstuðningur + AI skýrsla)
- [ ] AI spjall — spyrðu gögnin þín hvað sem er á náttúrulegu máli
- [ ] AI-skrifaðar skýrslur á mannamáli
- [ ] Náttúruleg málsía ("Finndu mér lítil fyrirtæki sem vaxa hratt...")
- [ ] Þesis-aðstoðari (AI ögrar forsendum, finnur blinda bletti)
- [ ] Sjálfvirk athugasemd á gröfum (AI útskýrir hvað gerðist og af hverju)
- [ ] Áhættuskýring á mannamáli ("Þú gætir tapað X ef...")
- [ ] Námsaðstoðari (útskýrir hugtök í samhengi við gögnin)

### AI skjalagreining
- [ ] 10-K / 10-Q lestur og samantekt
- [ ] Afkomusímtöl: Whisper umritun + greining + samanburður
- [ ] Fréttasamantekt og sentiment
- [ ] Mynsturgreining á gröfum (AI vision)
- [ ] Tungumál: íslensku/ensku þýðingar á skýrslum og gögnum

### AI viðvaranir
- [ ] Snjall-viðvaranir (AI útskýrir af hverju eitthvað gerðist)
- [ ] "3 fyrirtæki í vaktlistanum eru komin undir þitt verðmat"
- [ ] Afkomugreining sjálfkrafa þegar fyrirtæki tilkynnir

### Menntun og nám
- [ ] ? hnappur við hverja tölu/forsendu (stig 1-3 útskýringar)
- [ ] Tilbúin AI prompt með fullu samhengi ("Spyrðu AI" hnappur)
- [ ] Námsmiðstöð / Academy (skipulagðar námsleiðir)
- [ ] Námsleiðir: Grunn fjármál, Virðismat, Tæknigreining, Áhætta, Hagfræði
- [ ] Gagnvirkar æfingar ("Breyttu forsendu og sjáðu hvað gerist")
- [ ] AI kennari (persónulegar útskýringar á þínu stigi)
- [ ] Leiðsögn í gegnum skjái (guided mode / tutorial)
- [ ] Námsframvinda (hvar ertu og hvað kemur næst)

### Viðvaranir og tilkynningar
- [ ] Verðviðvaranir ("AAPL yfir $200")
- [ ] Tæknilegar viðvaranir ("RSI > 70")
- [ ] Afkomuviðvaranir
- [ ] Email / push / webhook

### Útflutningur
- [ ] PDF skýrslur (virðismat, yfirlit)
- [ ] Excel útflutningur
- [ ] Sérsniðin sniðmát

### Samskipti og deiling
- [ ] Spjall milli notenda (chat)
- [ ] Deila greiningum, gröfum, vaktlistum með öðrum
- [ ] Tilkynningar ("Anna deildi greiningu með þér")

---

## Fasar — í hvaða röð við byggjum

### Fase 1 — Grunnur (Streamlit + yfinance) ✅ LOKIÐ
- ✅ Möppubygging og grunnkóði
- ✅ Data layer: yfinance provider + SQLite cache + fallback
- ✅ Company model (CompanyInfo, CompanyPrice, CompanyRatios)
- ✅ Fyrirtækjayfirlit (pages/1_company.py)
  - ✅ Search + Browse tabs (nafnaleit, screener flokkar)
  - ✅ Verðgraf (line, candlestick, area) + volume
  - ✅ Period/interval val (1mo-max, daily/weekly/monthly)
  - ✅ Key metrics með litum (grænt/rautt)
  - ✅ 52-week range bar (sjónræn stika)
  - ✅ Analyst price target bar (upside %)
  - ✅ Tabs: Detail, Financials, Ownership, Peers, Analysts, News, About
  - ✅ Revenue/earnings graf í Financials
  - ✅ Margin trend graf í Detail
  - ✅ Insider net activity samantekt
  - ✅ Peer comparison (USD conversion)
  - ✅ Analyst consensus litastika
  - ✅ URL persistence (ticker í query params)
- ✅ Custom CSS (metric cards, full width, hide branding)
- ✅ Leitarstika (components/ticker_search.py)
- ✅ Almenn gröf (components/charts.py)
- ✅ config/settings.py + constants.py
- ✅ .env.example, .gitignore, requirements.txt

### Fase 2 — Kjarnaskjáir
- ✅ Virðismat — Simple DCF (3-phase), Complex DCF (12-step IB-grade), 3-Statement Model, WACC (5 beta-aðferðir, 3 Rd-aðferðir, 4 cap-structure leiðir), Comps (operating metrics + football field), Damodaran integration
- Tæknigröf (kertastjakar, RSI, MACD)
- Hlutabréfasía
- Vaktlistar
- Samanburðartæki

### Fase 3 — Sandbox og grunn-AI (þarf Claude API lykil)
- Claude API tenging (lib/ai/)
- Sandbox tilraunastöð (lýsa hugmynd → fá niðurstöður)
- AI spjall við gögnin (pages/18_chat.py)
- Greiningarvinnusvæði (gögn + rökstuðningur)
- AI skýrslugerð á mannamáli

### Fase 4 — Fleiri gagnaveitur og eiginleikar
- FRED þjóðhagsgögn (þarf API lykil)
- SEC EDGAR innherjaviðskipti
- Hitakort, afkomudagatal, efnahagsdagatal
- Eignasafnsrakning
- Áhættugreining, backtesting, valréttir

### Fase 5 — Menntun og fullkomnun AI
- ? hnappur (explainer) við allar tölur og forsendur
- Tilbúin AI prompt með samhengi ("Spyrðu AI" hnappur)
- Námsmiðstöð / Academy (námsleiðir, æfingar, framvinda)
- AI kennari (persónulegar útskýringar)
- Leiðsögn í gegnum skjái (guided mode)
- 10-K / 10-Q skjalagreining
- Afkomusímtöl: Whisper umritun + AI greining
- Fréttasamantekt og sentiment
- Þesis-aðstoðari (AI ögrar forsendum)
- Náttúruleg málsía
- Mynsturgreining á gröfum (vision)
- Snjall-viðvaranir með AI útskýringum
- Sjálfvirk athugasemd á gröfum
- Íslensku/ensku þýðingar

### Fase 6 — Deiling og útlit
- Notendaauðkenning (auth)
- Cloud storage (Firebase/PostgreSQL)
- React framendi (fallegt UI)
- Viðvaranir og tilkynningar
- Spjall milli notenda (chat)
- Deiling greiningum, gröfum, vaktlistum
- Samskiptatilkynningar

---

## React skipti (fase 6) — hvað breytist

```
HENDUM:          pages/, components/     (Streamlit UI)
BÆTUM VIÐ:       api/, frontend/         (FastAPI + React)
BREYTIST EKKI:   lib/, models/, config/   (allur kjarninn, þ.m.t. lib/ai/)
```

Þetta virkar vegna þess að `lib/` (þ.m.t. allir AI eiginleikar) inniheldur engan UI kóða.

---

*Síðast uppfært: 2026-03-31*
