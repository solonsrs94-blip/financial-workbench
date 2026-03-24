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
7. **Skrár fara ekki yfir ~200 línur.** Ef svo, skipta í undirhluta.
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
│   │   ├── assumptions.py              ← Forsendur UI
│   │   ├── dcf_panel.py                ← DCF útreikningur UI
│   │   ├── comps_panel.py              ← Comps tafla UI
│   │   └── results.py                  ← Niðurstöður og rökstuðningur
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
│   │   │   ├── damodaran.py            ← ERP, beta, CRP, spreads
│   │   │   ├── edgar.py                ← SEC skráningar, skuldir
│   │   │   ├── fred.py                 ← Vextir, verðbólga, atvinnuleysi
│   │   │   ├── news.py                 ← RSS feeds og fréttir
│   │   │   ├── insiders.py             ← Innherjaviðskipti (SEC)
│   │   │   ├── earnings_calendar.py    ← Afkomudagsetningar
│   │   │   └── economic_calendar.py    ← Efnahagsdagatal (FOMC, CPI, o.fl.)
│   │   │
│   │   ├── market.py                   ← Mellanlags-lag: verð, söguleg gögn
│   │   ├── fundamentals.py             ← Mellanlags-lag: fjárhagur, hlutföll
│   │   └── macro.py                    ← Mellanlags-lag: þjóðhagsgögn
│   │
│   │   ── ÚTREIKNINGAR OG GREINING ──
│   │
│   ├── analysis/
│   │   ├── valuation.py                ← CAPM, WACC, DCF, comps
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
│   ├── auth/                           ← Notendaauðkenning (fase 2)
│   │   └── __init__.py                 ← Tómt í byrjun
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
- [ ] Fyrirtækjayfirlit (verð, lykiltölur, fréttir)
- [ ] Ársreikningar (rekstrarreikn., efnahagsreikn., sjóðstreymi)
- [ ] Virðismat (DCF, WACC, CAPM, comps)
- [ ] Innherjaviðskipti (kaup/sala stjórnenda)
- [ ] Arðgreiðslusaga og yield

### Markaðsgreining
- [ ] Tæknigröf (kertastjakar, indicators, overlays, teikning)
- [ ] Hitakort markaðarins (geirar, stærð, breyting)
- [ ] Geiragreining og sector rotation
- [ ] Þjóðhagsyfirlit (vextir, verðbólga, atvinnuleysi)
- [ ] Efnahagsdagatal (FOMC, CPI, atvinnuskýrslur)
- [ ] Afkomudagatal (hvenær fyrirtæki tilkynna)

### Leit og síun
- [ ] Almenn hlutabréfasía (hvaða forsendur sem er)
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

---

## Fasar — í hvaða röð við byggjum

### Fase 1 — Grunnur (Streamlit + yfinance)
- Möppubygging og grunnkóði
- Data layer: yfinance provider + SQLite cache
- Fyrirtækjayfirlit (pages/1_company.py)
- Ársreikningar (pages/2_financials.py)
- Leitarstika (components/ticker_search.py)
- Almenn gröf (components/charts.py)

### Fase 2 — Kjarnaskjáir
- Virðismat (flytja úr gamla appi, endurskipuleggja)
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

---

## React skipti (fase 6) — hvað breytist

```
HENDUM:          pages/, components/     (Streamlit UI)
BÆTUM VIÐ:       api/, frontend/         (FastAPI + React)
BREYTIST EKKI:   lib/, models/, config/   (allur kjarninn, þ.m.t. lib/ai/)
```

Þetta virkar vegna þess að `lib/` (þ.m.t. allir AI eiginleikar) inniheldur engan UI kóða.

---

*Síðast uppfært: 2026-03-24*
