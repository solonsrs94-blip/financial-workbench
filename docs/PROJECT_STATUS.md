# Financial Workbench — Heildarstaða og Sýn

*Síðast uppfært: 26. mars 2026*

---

## 1. Hvað er þetta?

Financial Workbench er persónulegt fjármálagreiningartæki sem sameinar faglega fjárhagsgreiningu, sjálfvirka gagnaöflun og (á endanum) gervigreind. Hugmyndin er einföld: gefa einstaklingi sem fjárfestir eigin peninga sömu tæki og sérfræðingur hjá fjárfestingarbanka hefur — en á fríum gögnum og án þess að þurfa að kunna forritun.

Appið er byggt á Python og Streamlit (vefviðmót) og notar frí gögn frá Yahoo Finance, SEC EDGAR, og SimFin. Allt keyrir á tölvunni þinni — engin áskrift, enginn þriðji aðili sér gögnin þín.

---

## 2. Heildar sýnin — hvað á þetta að verða?

Appið þróast í 6 áföngum (phases). Lokaútgáfan verður fullkomin fjármálagreiningarstofa með:

### Áfangi 1: Grunnur (Streamlit) — **~80% klárt**
- Fyrirtækjayfirlit (Company Overview) — skoða hvaða fyrirtæki sem er
- Virðismat (Valuation) — DCF, Comps, DDM, Historical Multiples
- Gagnaöflun frá Yahoo Finance, EDGAR, SimFin
- SQLite cache svo gögnin hleðst hratt

### Áfangi 2: Fleiri síður
- Screener (finna fyrirtæki eftir skilyrðum)
- Portfolio tracking (fylgjast með eigin fjárfestingum)
- Macro Dashboard (efnahagsleg gögn frá FRED)
- Technical charting (tæknigreining)

### Áfangi 3: Gervigreind
- AI chat (spyrja Claude um fyrirtæki og fá greiningu)
- Sandbox (lýsa hugmynd á mannamáli, Claude skrifar kóða og sýnir niðurstöðu)
- Document reader (AI les 10-K skýrslur og dregur út lykilupplýsingar)
- Sjálfvirk normalization á fjárhagsupplýsingum

### Áfangi 4: Menntun
- Innbyggt námskerfi um fjármálagreiningu
- Hugtakaútskýringar við hliðina á hverju verkfæri
- Æfingar og dæmi

### Áfangi 5: Viðbætur
- Earnings call transcription (hljóðupptaka → texti)
- Heatmaps, samanburðarverkfæri, options greining

### Áfangi 6: Nútímavefur
- Skipta Streamlit út fyrir React (hraðari, fallegri)
- Cloud deployment (aðgengilegt á netinu)
- Notendaaðgangur og deiling (deila greiningum með vinum/fjölskyldu)

---

## 3. Hvað er búið — á mannamáli

### 3.1 Company Overview (Fyrirtækjayfirlit) — ✅ Klárt

Þetta er fyrsta síðan í appinu. Þú slærð inn ticker (t.d. AAPL, MSFT, GOOG) og færð strax:

**Haus:** Nafn fyrirtækis, núverandi verð, dagleg breyting, markaðsvirði, analyst price target, og 8-10 lykilmælikvarðar (P/E, EV/EBITDA, margins, o.fl.).

**Verðgraf:** 5 ára verðsaga sem sjálfgefið, hægt að skipta á milli 1 mánaðar og hámarks. Sýnir earnings dates og arðgreiðsludaga á grafinu.

**7 flipar (tabs):**
1. **Detail** — Lykiltölur á einum stað: P/E, P/B, P/S, arðsávöxtun, beta, o.fl.
2. **Financials** — Rekstrarreikningur, efnahagsreikningur, og sjóðstreymisyfirlit. Hægt að sjá "Show all" til að fá allar línur eða bara yfirlit. Annual og TTM (trailing twelve months).
3. **Ownership** — Hlutfall innherja og stofnanafjárfesta. Nýlegustu viðskipti innherja.
4. **Analysts** — Consensus frá greiningaraðilum: Buy/Hold/Sell, price target, EPS áætlanir.
5. **News** — Nýjustu fréttir um fyrirtækið.
6. **About** — Lýsing á fyrirtækinu, geiri, starfsmannafjöldi, vefsíða.
7. **Peers** — Sambærileg fyrirtæki í sama geira með samanburð á valuation hlutföllum.

### 3.2 Gagnaöflun (Data Layer) — ✅ Klárt

Þetta er "vélin á bak við tjöldin" sem sækir og geymir gögn. Notandinn sér þetta ekki beint, en án þessa virkar ekkert.

**5 gagnaveitur:**
- **Yahoo Finance** — Aðalgögn: verð, fyrirtækjaupplýsingar, lykiltölur. Enginn API lykill þarf.
- **SEC EDGAR** — Bandaríska verðbréfaeftirlitið. Skilar 10+ árum af ársreikningum beint frá 10-K skráningum fyrirtækja. Þetta eru "official" tölur — beint frá fyrirtækinu sjálfu.
- **SimFin** — Annar gagnagrunnur með sögulegum fjárhagsupplýsingum. Frítt account, ótakmarkaðar fyrirspurnir.
- **Yahoo Financials** — Sérstök tenging við ársreikninga frá Yahoo (fallback ef EDGAR er ekki til).
- **Yahoo Valuation** — Framvirk verðmatsupplýsingar (forward P/E, PEG, analyst targets).

**Cache kerfi:** Öll gögn eru geymd á tölvunni þinni í SQLite gagnagrunni. Fyrsta skipti sem þú skoðar fyrirtæki tekur nokkrar sekúndur. Eftir það er allt strax tilbúið. Mismunandi gögn hafa mismunandi "freshness" — verð endurnýjast daglega, ársreikningar vikulega, fyrirtækjaupplýsingar mánaðarlega.

**4-layer standardization:** Mismunandi gagnaveitur nota mismunandi nöfn á sömu hlutina. "Net sales", "Revenue", "Total Revenue" — allt er sama. Kerfið mappar sjálfkrafa öll nöfn yfir í samræmt form í 4 skrefum:
1. XBRL taxonomy (SEC staðall)
2. Keyword matching (leita að lykilorðum í nafninu)
3. Hierarchy inference (nota staðsetningu í ársreikningi)
4. "Other" catch-all (ekkert tapast)

### 3.3 Valuation — DCF Step 1 (Söguleg gögn) — ✅ Klárt

Þetta er fyrsta skrefið í virðismatsferli: skoða og hreinsa söguleg gögn áður en þú spáir framtíðinni. Þetta er byggt eins og fagmaður á Wall Street myndi gera það:

**1a. Raw Financials (hráar tölur)**
Ársreikningar eins og fyrirtækið sjálft skráði þá hjá SEC. 10+ ár af rekstrarreikningi, efnahagsreikningi, og sjóðstreymisyfirliti. Þú getur scrollað á milli ára og séð hverja einustu línu. Ef flagging kerfið finnur eitthvað athugavert á tilteknu ári og línu, er viðkomandi reitur auðkenndur með lit.

**1b. Spreading & Normalization (greining og hreinsun)**
Áður en þú getur spáð framtíðinni þarftu að vita hvort söguleg gögn eru "hrein." Kerfið keyrir 31 greiningar sjálfkrafa og flaggar allt sem er óvenjulegt:

*Hvað kerfið finnur:*
- **One-off gjöld** — Ef margin hrynur á einu ári en tekjur eru stöðugar, er líklega um einskiptiskostnað að ræða (restructuring, málaferlakostnaður, niðurfærsla eigna).
- **Kaup og sölur (M&A)** — Ef tekjur og goodwill hoppa saman, keypti fyrirtækið líklega annað fyrirtæki. Kerfið greinir þetta og áætlar hvað organic vöxtur var.
- **Skattalagabreytingar** — TCJA 2017, COVID áhrif 2020, og fleiri þekktar breytingar eru sjálfkrafa greindar.
- **Bókhaldsbreytingar** — IFRS 16 (2019) breytti hvernig leigusamningar eru bókaðir. Ef skuldir og eignir hoppa saman 2019, greinir kerfið þetta.
- **CapEx sveiflur** — Ef fjárfestingaútgjöld hækka mikið (t.d. AI tölvuver hjá Google/Meta), flaggar kerfið þetta.
- **SBC þynning** — Ef stock-based compensation er >10% af tekjum, varar kerfið við hlutafjárþynningu.
- **Gæðamat á hagnaði** — Kerfið ber saman reported earnings við raunverulegt sjóðstreymi. Ef fyrirtæki rapportar mikinn hagnað en raunverulegt cash er mun lægra, er það viðvörun.
- **Cyclical greining** — Kerfið flokkar fyrirtæki sem stable, moderate, eða cyclical og aðlagar viðmiðin eftir því. Eðlilegt er að XOM hafi 20pp margin sveiflur, en óeðlilegt hjá WMT.
- **Mean reversion** — Ef margin er á sögulegu hámarki, varar kerfið við: "margins eru á 91st percentile af eigin sögu — íhuga hvort þær snúi við."

Hvert flag inniheldur þrennt:
- **Hvað** breyttist (t.d. "Net Margin dropped 12.6pp")
- **Af hverju** (t.d. "Revenue was stable but EBIT dropped — likely one-off charge")
- **Hvað gera** (t.d. "Remove estimated $8.1B charge from 2017 EBIT")

*AI placeholder:* Í Áfanga 3 mun gervigreind lesa 10-K footnotes og finna nákvæmlega hvað one-off gjöld voru, hvort yfirtökur voru greiddar með hlutabréfum eða reiðufé, o.fl. Þangað til notar kerfið rule-based greiningu.

**1c. Review & Override (yfirfara og leiðrétta)**
Þegar kerfið flaggar eitthvað, getur notandinn:
- Smellt á "Apply" til að samþykkja tillöguna (leiðréttingin fyllist sjálfkrafa inn)
- Smellt á "Dismiss" til að hunsa
- Bætt við handvirkum leiðréttingum (ef hann veit eitthvað sem kerfið veit ekki)

**1d. Standardized Financials (hreinsaðar tölur)**
Eftir leiðréttingar sýnir kerfið "hreinar" tölur í samræmdu formi. Þetta er grunnurinn sem allar framtíðarspár byggja á. Audit trail sýnir hvaðan hver tala kemur (EDGAR, Yahoo, eða SimFin) og hvaða leiðréttingar voru gerðar.

**1e. Ratios & Drivers (lykiltölur og trend)**
Reiknað úr hreinsuðum gögnum:
- **Margins:** Gross, EBIT, EBITDA, Net, FCF — per ár
- **Vöxtur:** Revenue growth, EPS growth — per ár
- **Efficiency:** DSO, DIO, DPO (hversu hratt fé flæðir í gegn)
- **Leverage:** Debt/EBITDA, Interest Coverage, D/E
- **Returns:** ROIC, ROE, ROA
- **Gæði:** FCF conversion, CapEx/D&A, SBC/Revenue

Plús tveir gröf: Revenue & FCF trend og Margin trend yfir tíma.

3yr meðaltöl á hverju birtast efst sem "dashboard" — þetta er það sem fæðir beint inn í DCF spár sem sjálfgefin gildi.

### 3.4 DCF Steps 2-6 — ⏳ Placeholders

Þessi skref eru skilgreind og skipulögð en ekki enn byggð:

**Step 2: Assumptions** — Hér setur notandinn inn forsendur: hversu hratt tekjur vaxa, hvert margins stefna, hversu mikið er fjárfest (CapEx), skattahlutfall, SBC, o.fl. Allt per ár í 5-10 ára spátímabili.

**Step 3: 3-Statement Model** — Rekstrarreikningur, efnahagsreikningur, og sjóðstreymi spáð fram í tímann. Allt tengist: tekjur fæða kostnað, kostnaður fæðir hagnað, hagnaður fæðir eigið fé, eigið fé fæðir efnahagsreikning, breytingar á efnahagsreikningi fæða sjóðstreymi. Free Cash Flow kemur úr þessu.

**Step 4: WACC** — Ávöxtunarkrafa (discount rate). CAPM fyrir eiginfjárkröfu (Rf + Beta × ERP), cost of debt, capital structure. 6 beta aðferðir, 4 cost of debt aðferðir, 4 capital structure aðferðir — allt eins og í faglegum módeli.

**Step 5: Terminal Value** — Virði eftir spátímabilið. Gordon Growth (eilíft FCF) eða Exit Multiple (EV/EBITDA). Cross-checks til að tryggja að niðurstaðan sé sanngjörn.

**Step 6: Output** — Implied verð per hlut, sensitivity töflur (WACC vs growth), scenario analysis (bull/base/bear), reverse DCF ("hvað er markaðurinn að verðleggja?"), og sanity checks.

### 3.5 Aðrar Valuation aðferðir — ⏳ Placeholders

- **Comps** — Samanburður við sambærileg fyrirtæki á markaði (P/E, EV/EBITDA)
- **DDM** — Dividend Discount Model (fyrir arðgreiðslufyrirtæki)
- **Historical Multiples** — Samanburður við eigin söguleg hlutföll
- **Summary** — "Football field" sem sameinar allar aðferðir á einn stað

---

## 4. Hvernig allt passar saman

```
┌──────────────────────────────────────────────────────────┐
│                    NOTANDI                                │
│    Velur fyrirtæki → skoðar → greinir → tekur ákvörðun   │
└──────────────────────────┬───────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────┐
│              SÍÐUR (pages/)                               │
│                                                          │
│  Company Overview          Valuation                     │
│  ┌─────────────────┐      ┌─────────────────────────┐   │
│  │ Yfirlit          │      │ DCF (6 skref)            │   │
│  │ Verð & graf      │      │ Comps                    │   │
│  │ 7 flipar         │      │ DDM                      │   │
│  │ (detail, fin,    │      │ Historical               │   │
│  │  analysts, etc.) │      │ Summary                  │   │
│  └─────────────────┘      └─────────────────────────┘   │
│                                                          │
│  [Screener] [Portfolio] [Macro] [Technical]  ← Áfangi 2  │
│  [AI Chat]  [Sandbox]   [Education]          ← Áfangi 3+ │
└──────────────────────────┬───────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────┐
│            GREININGARVÉLAR (lib/analysis/)                │
│                                                          │
│  Ratios & Drivers    │  Flagging (31 reglur)             │
│  DCF Engine          │  WACC Calculator                  │
│  Peer Comparison     │  Earnings Quality                 │
│  Sensitivity         │  Cyclicality Classification       │
└──────────────────────────┬───────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────┐
│              GÖGN (lib/data/)                             │
│                                                          │
│  Middleware (cache → provider → standardize → cache)     │
│                                                          │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐           │
│  │ Yahoo  │ │ EDGAR  │ │ SimFin │ │ FRED   │           │
│  │ (verð, │ │ (10-K, │ │ (sögu- │ │ (macro │           │
│  │  info) │ │  10+ár)│ │  legt) │ │  data) │           │
│  └────────┘ └────────┘ └────────┘ └────────┘           │
│                                                          │
│  SQLite Cache (geymir allt locally)                      │
└──────────────────────────────────────────────────────────┘
```

**Mikilvæg regla:** `lib/` (greiningarvélar og gögn) veit ekkert um Streamlit (viðmótið). Þetta þýðir að í Áfanga 6, þegar við skiptum Streamlit út fyrir React, breytist **ekkert** í greiningarvélunum eða gagnaöfluninni. Bara viðmótið breytist.

---

## 5. Hvað gerir þetta öðruvísi?

**Miðað við Bloomberg/Capital IQ:** Þessi verkfæri kosta $15,000-24,000 á ári. Okkar app notar fríar gagnaveitur og nær ~80-85% af sömu gögnum. Megingapið er live bond data og segment financials — en fyrir einstaklingafjárfesti er þetta nóg.

**Miðað við Excel DCF:** Flestir gera DCF í Excel. Okkar app automaterar gagnaöflunina (þú þarft ekki að slá inn tölur handvirkt), greinir sjálfkrafa anomalies, og sýnir allt gagnvirkt. Excel krefst klukkutíma vinnu bara til að setja upp — hér ertu byrjaður á sekúndum.

**Miðað við önnur frítt verkfæri (Finviz, Macrotrends):** Þau sýna gögn en leyfa ekki greiningu. Okkar app leyfir þér að breyta forsendum og sjá strax hvernig virðismatið breytist. Plús 31 sjálfvirkar anomaly flags sem engin þessara verkfæra hafa.

---

## 6. Af hverju er þetta mikilvægt?

Tilgangurinn er ekki að búa til "enn eitt fjármálaappið." Tilgangurinn er að gefa sjálfstæðum fjárfesti — einum sem er með BS í hagfræði og er í M.Fin náminu — verkfæri til að taka betri fjárfestingarákvarðanir. Verkfæri sem:

1. **Sýnir sömu gögn** og sérfræðingur sér
2. **Varar við vandamálum** sem byrjandi myndi missa af (one-offs, accounting tricks, dilution)
3. **Kennir um leið** — hvers vegna þessi tala skiptir máli, hvað þýðir þetta ratio
4. **Stækkar með þér** — byrjar einfalt, verður flóknara eftir því sem þú lærir meira
5. **Er þitt eigið** — keyrr á þinni tölvu, þú stjórnar

Og á endanum verður þetta deilt með vinum og fjölskyldu sem vilja líka fjárfesta betur.
