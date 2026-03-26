# Valuation Architecture — Stöðuskýrsla

*Heiðarleg staða 26. mars 2026. Ekki söluskjal.*

---

## 1. Valuation síðan eins og hún er núna

### 1.1 Skrár sem mynda valuation síðuna

**Aðalskrá:**
| Skrá | Línur | Lýsing |
|------|-------|--------|
| `pages/3_valuation.py` | 123 | Entry point — hleður fyrirtæki, sýnir 5 tabs (DCF, Comps, DDM, Historical, Summary) |
| `pages/valuation/dcf_tab.py` | 123 | DCF orchestrator — hleður gögn, kallar á Step 1-6 |

**Step 1 (virkar):**
| Skrá | Línur | Lýsing |
|------|-------|--------|
| `dcf_step1_historical.py` | 209 | Master Step 1 — tengir saman 1a-1e sub-sections |
| `dcf_step1_flags.py` | 128 | Sýnir flags (what/why/action) með Apply/Dismiss |
| `dcf_step1_overrides.py` | 68 | Applied adjustments + manual override input |
| `dcf_step1_standardized.py` | 216 | Standardized IS/BS/CF töflur með audit trail |
| `dcf_step1_ratios.py` | 48 | Key ratios tafla |
| `dcf_step1_charts.py` | 68 | Revenue/FCF chart + Margin trend chart (Plotly) |

**Steps 2-6 (ALLT PLACEHOLDER):**
| Skrá | Línur | Innihald |
|------|-------|----------|
| `dcf_step2_assumptions.py` | 23 | `st.info("Coming soon...")` |
| `dcf_step3_model.py` | 34 | `st.info("Coming soon...")` |
| `dcf_step4_wacc.py` | 35 | `st.info("Coming soon...")` |
| `dcf_step5_terminal.py` | 29 | `st.info("Coming soon...")` |
| `dcf_step6_output.py` | 38 | `st.info("Coming soon...")` |

**Aðrir valuation flipar (ALLT PLACEHOLDER):**
| Skrá | Línur | Innihald |
|------|-------|----------|
| `comps_tab.py` | 10 | Placeholder |
| `ddm_tab.py` | 9 | Placeholder |
| `historical_tab.py` | 9 | Placeholder |
| `summary_tab.py` | 9 | Placeholder |

### 1.2 Flæðið þegar notandi slær inn ticker

```
Notandi slær inn "GOOG" → pages/3_valuation.py
  │
  ├─> get_company("GOOG")                   → Company model (nafn, verð, sector, etc.)
  ├─> get_financials("GOOG")                → Yahoo financials (4 ár, fin_data dict)
  ├─> get_valuation_data("GOOG")            → Forward valuation data
  ├─> get_risk_free_rate()                   → 10yr Treasury yield
  │
  └─> dcf_tab.render(company, fin_data, ticker)
      │
      └─> _load_step1_data(ticker, sector)
          │
          ├─> get_raw_statements("GOOG")           [lib/data/historical.py]
          │   ├─> _try_edgar_raw("GOOG")           → EDGAR 10-K DataFrames (10+ ár)
          │   └─> _try_yahoo_raw("GOOG")           → Yahoo fallback (4 ár)
          │   └─> Returns: {income: DataFrame, balance: DataFrame, cashflow: DataFrame}
          │
          ├─> get_standardized_history("GOOG")     [lib/data/historical.py]
          │   └─> standardize_statement(df, "income")  [lib/data/standardizer.py]
          │       ├─> Layer 1: XBRL concept mapping
          │       ├─> Layer 2: Keyword matching
          │       ├─> Layer 3: Hierarchy inference
          │       └─> Layer 4: "Other" catch-all
          │   └─> compute_derived_fields()          → GP, EBIT, EBITDA, FCF
          │   └─> run_cross_checks()                → Assets = L + E, Rev - COGS = GP
          │   └─> Returns: {years, income, balance, cashflow, *_audit}
          │
          ├─> build_income_table(std, years)        [lib/analysis/historical.py]
          ├─> build_balance_table(std, years)
          ├─> build_cashflow_table(std, years)
          ├─> build_ratios_table(is_t, bs_t, cf_t)  [lib/analysis/historical_ratios.py]
          │
          ├─> detect_flags(ratios, is_t, bs_t, cf_t, sector, ticker)
          │   └─> Keyrir 31 reglu across 5 skrár   [lib/analysis/historical_flags*.py]
          │
          └─> compute_averages(ratios)              [lib/analysis/historical_averages.py]
              └─> 3yr meðaltöl á margins, growth, efficiency
```

### 1.3 Hvar gerist spreading/normalization?

**Spreading/normalization er í `lib/data/standardizer.py` og `lib/data/historical.py`** — aðskilið frá DCF flipanum. Þetta er í `lib/` sem þýðir:

- Engin Streamlit dependency
- Hvaða síða sem er getur notað þetta (Comps, DDM, etc.)
- Ef við skipum Streamlit út fyrir React, breytist ekkert

**Hins vegar** er standardizerinn KALLAÐUR frá `dcf_tab.py` núna. Ef Comps eða DDM þyrftu sömu gögn, þyrftu þau að kalla sama fall sjálfstætt. Ekkert sameiginlegt "data layer" sem allir tabs deila — hvert tab sækir sitt.

---

## 2. Flagging kerfið

### 2.1 Skrár

| Skrá | Línur | Fjöldi reglna |
|------|-------|---------------|
| `lib/analysis/historical_flags.py` | 111 | 0 (orchestrator — kallar aðrar) |
| `lib/analysis/historical_flags_rules.py` | 213 | 8 basic reglur |
| `lib/analysis/historical_flags_advanced.py` | 308 | 6 advanced reglur |
| `lib/analysis/historical_flags_extra.py` | 248 | 5 extra reglur |
| `lib/analysis/historical_flags_trends.py` | 392 | 7 trend reglur |
| `lib/analysis/historical_flags_smart.py` | 714 | 7 smart reglur (+ helpers) |
| **Samtals** | **1,986** | **~33 reglur** |

### 2.2 Allar reglur ER kallaðar

`detect_flags()` í `historical_flags.py` kallar **allar** rule functions. Ekkert er skilgreint en ekki kallað. Call chain:

```python
def detect_flags(ratios, is_table, bs_table, cf_table, sector, ticker):
    flags = []
    flags += rules.detect_margin_anomalies(ratios)
    flags += rules.detect_revenue_anomalies(ratios)
    flags += rules.detect_tax_anomalies(ratios)
    # ... 8 basic rules total
    flags += advanced.detect_fcf_ni_divergence(ratios, is_table, cf_table)
    flags += advanced.detect_goodwill_impairment(bs_table)
    # ... 6 advanced rules total
    flags += extra.detect_debt_spike(bs_table)
    # ... 5 extra rules total
    flags += trends.detect_trend_breaks(ratios)
    # ... 7 trend rules total
    flags += smart.detect_industry_margin_flags(ratios, sector)
    # ... 7 smart rules total
    return sorted(flags, key=lambda f: (f["severity"] != "high", f["year"]))
```

### 2.3 Dæmi um reglur sem virka

**Dæmi 1: Margin Anomaly (basic)**
```python
def detect_margin_anomalies(ratios):
    """Flaggar þegar gross/EBIT/net margin breytist >5pp milli ára."""
    flags = []
    for i in range(1, len(ratios)):
        for metric in ["gross_margin", "ebit_margin", "net_margin"]:
            curr = ratios[i].get(metric)
            prev = ratios[i-1].get(metric)
            if curr is not None and prev is not None:
                delta_pp = (curr - prev) * 100
                if abs(delta_pp) > 5:
                    direction = "jumped" if delta_pp > 0 else "dropped"
                    flags.append({
                        "category": "one_off",
                        "severity": "high" if abs(delta_pp) > 10 else "medium",
                        "year": str(ratios[i]["year"]),
                        "what": f"{metric} {direction} {abs(delta_pp):.1f}pp",
                        "why": _diagnose_margin(ratios, i, metric, delta_pp),
                        "action": _margin_action(metric, delta_pp, ratios[i]),
                        "impact_mn": ...,
                        "line_item": metric.replace("_margin", ""),
                    })
    return flags
```

**Dæmi 2: Known Macro Events (advanced)**
```python
def detect_known_events(ratios, is_table, bs_table):
    """Greinir þekkta macro atburði: COVID 2020, TCJA 2017, IFRS 16 2019."""
    flags = []
    for r in ratios:
        yr = str(r.get("year", ""))
        # TCJA 2017-2018
        if yr in ("2017", "2018"):
            etr = r.get("effective_tax_rate")
            if etr and etr > 0.35:
                flags.append({
                    "category": "tax",
                    "severity": "medium",
                    "year": yr,
                    "what": f"High tax rate ({etr*100:.1f}%)",
                    "why": "TCJA (Tax Cuts and Jobs Act) enacted Dec 2017...",
                    "action": "Use normalized 21% tax rate for projections",
                    ...
                })
    return flags
```

**Dæmi 3: Earnings Quality Score (smart)**
```python
def compute_earnings_quality(ratios, is_table, cf_table):
    """Sameinar 5 signals í einkunn 1-10."""
    scores = []
    # 1. FCF/NI ratio (>0.8 = good)
    # 2. OCF/EBITDA ratio (>0.6 = good)
    # 3. DSO stability (low variance = good)
    # 4. Revenue consistency (low variance = good)
    # 5. Margin stability (low variance = good)
    return {"score": avg_score, "components": {...}}
```

### 2.4 Hvað er EKKI enn virkt?

Allar 33 reglur eru kallaðar og virka. **Engin regla er skilgreind en ekki kölluð.**

Hinsvegar eru sumar reglur **veikari en aðrar:**
- `detect_known_company_events()` — hardcoded database fyrir ~15 fyrirtæki. Vantar coverage á flestum.
- `detect_revenue_mix_shift()` — erfitt að greina án segment data (sem vantar oft).
- `detect_acquisition_fingerprint()` — multi-signal er gott en false positive rate er enn hátt.

---

## 3. Standardization/Normalization

### 3.1 Hvernig virkar 4-layer kerfið í raun?

```
EDGAR 10-K XBRL DataFrame:
┌───────────────────────────┬──────────────────────┬────────────┐
│ standard_concept          │ label                │ value      │
├───────────────────────────┼──────────────────────┼────────────┤
│ Revenue                   │ Net sales            │ 391,035M   │
│ CostOfGoodsAndServicesSold│ Cost of products sold│ 210,000M   │
│ (none)                    │ Restructuring charges│ 1,200M     │
│ OperatingIncomeLoss       │ Operating income     │ 120,000M   │
└───────────────────────────┴──────────────────────┴────────────┘
                    │
                    ▼
        ┌─── Layer 1: XBRL Concept Mapping ───┐
        │ Revenue → "revenue" ✓               │
        │ CostOfGoods... → "cogs" ✓           │
        │ (none) → SKIP (no concept)          │
        │ OperatingIncomeLoss → "ebit" ✓      │
        └─────────────────────────────────────┘
                    │
                    ▼ (unmapped items only)
        ┌─── Layer 2: Keyword Matching ────────┐
        │ "Restructuring charges"              │
        │   → keyword "restructur" found       │
        │   → maps to "restructuring" ✓        │
        └──────────────────────────────────────┘
                    │
                    ▼ (still unmapped)
        ┌─── Layer 3: Hierarchy Inference ─────┐
        │ Uses parent_concept from XBRL tree   │
        │ If parent = "OperatingExpenses"      │
        │   → child is operating cost          │
        └──────────────────────────────────────┘
                    │
                    ▼ (still unmapped)
        ┌─── Layer 4: "Other" Catch-All ───────┐
        │ Contains "expense"? → other_op_exp   │
        │ Contains "income"? → other_income    │
        │ Default → other_item                 │
        │ EKKERT TAPAST                        │
        └──────────────────────────────────────┘
                    │
                    ▼
        ┌─── Derived Fields ───────────────────┐
        │ gross_profit = revenue - cogs        │
        │ ebitda = ebit + da                   │
        │ fcf = ocf - capex                    │
        │ net_debt = total_debt - cash         │
        └──────────────────────────────────────┘
                    │
                    ▼
        ┌─── Cross-Checks ────────────────────┐
        │ Revenue - COGS ≈ Gross Profit?       │
        │ Total Assets ≈ Total L + Total E?    │
        │ Ef EKKI → viðvörun                   │
        └──────────────────────────────────────┘
                    │
                    ▼
        Standardized output með audit trail:
        {
          "revenue": {
            "value": 391035000000,
            "raw_label": "Net sales",
            "source": "edgar",
            "layer": 1,
            "concept": "Revenue"
          }
        }
```

### 3.2 Gagnaveitur sem eru raunverulega tengdar

| Veita | Tengd? | Notuð hvar? | Athugasemd |
|-------|--------|-------------|------------|
| **Yahoo Finance** | ✅ Já | Company Overview, fallback í historical | Primary fyrir market data og non-US |
| **SEC EDGAR** | ✅ Já | Primary fyrir US historical financials | 10+ ár, XBRL structured |
| **SimFin** | ⚠️ Providerinn er skrifaður en EKKI importaður | Orphaned | Var fallback en er ekki kallað |
| **FRED** | ❌ Ekki enn | Planned fyrir macro/risk-free rate | Áfangi 2+ |

**Heiðarlegt mat:** SimFin provider er til (`lib/data/providers/simfin_provider.py`, 172 línur) en er **ekki importaður eða notaður** af neinu. Það var byggt sem fallback en EDGAR tók yfir sem primary fyrir US. Fyrir non-US fyrirtæki myndi SimFin þurfa að vera virkjað.

### 3.3 Er normalization bundið við DCF?

**Nei — kóðinn er í `lib/`** og er sjálfstæður frá Streamlit. Hins vegar er hann **kallaður** frá `dcf_tab.py` núna. Ef Comps eða DDM þyrftu sömu gögn, þyrftu þau að kalla `get_raw_statements()` og `get_standardized_history()` sjálfstætt.

**Vandamálið:** Ef bæði DCF og Comps kalla standardizerinn, gerist vinnan tvisvar. Betra væri að hafa sameiginlegan "data layer" á valuation síðunni sem hleður standardized gögn einu sinni og allir tabs deila þeim.

---

## 4. Dependency kort

```
pages/3_valuation.py
  │
  ├─> lib/data/fundamentals.py ──────> providers/yahoo.py
  │                                     providers/yahoo_valuation.py
  │
  ├─> lib/data/valuation_data.py ────> providers/yahoo_valuation.py
  │
  └─> pages/valuation/dcf_tab.py
      │
      ├─> lib/data/historical.py ◄── SPREADING/NORMALIZATION ENTRY POINT
      │   ├─> lib/data/providers/edgar_provider.py    (EDGAR 10-K)
      │   ├─> lib/data/providers/yahoo_financials.py  (Yahoo fallback)
      │   └─> lib/data/standardizer.py ◄── 4-LAYER STANDARDIZATION
      │       └─> lib/data/xbrl_concept_map.py        (concept + keyword maps)
      │
      ├─> lib/analysis/historical.py ◄── TABLE BUILDERS
      │   └─> lib/analysis/historical_ratios.py       (20+ ratios)
      │
      ├─> lib/analysis/historical_flags.py ◄── FLAG ORCHESTRATOR
      │   ├─> historical_flags_rules.py               (8 basic)
      │   ├─> historical_flags_advanced.py            (6 advanced)
      │   ├─> historical_flags_extra.py               (5 extra)
      │   ├─> historical_flags_trends.py              (7 trends)
      │   └─> historical_flags_smart.py               (7 smart)
      │
      ├─> lib/analysis/historical_averages.py         (3yr averages)
      │
      ├─> pages/valuation/dcf_step1_historical.py     (Step 1 master)
      │   ├─> dcf_step1_flags.py                      (flag UI)
      │   ├─> dcf_step1_overrides.py                  (adjustments UI)
      │   ├─> dcf_step1_standardized.py               (standardized tables)
      │   ├─> dcf_step1_ratios.py                     (ratios table)
      │   └─> dcf_step1_charts.py                     (Plotly charts)
      │
      ├─> dcf_step2_assumptions.py                    ← PLACEHOLDER
      ├─> dcf_step3_model.py                          ← PLACEHOLDER
      ├─> dcf_step4_wacc.py                           ← PLACEHOLDER
      ├─> dcf_step5_terminal.py                       ← PLACEHOLDER
      └─> dcf_step6_output.py                         ← PLACEHOLDER

  ORPHANED (til en ekki notað):
    lib/analysis/valuation.py          (DCF/WACC functions)
    lib/analysis/valuation/dcf.py      (alternative DCF)
    lib/analysis/valuation/wacc.py     (WACC calc)
    lib/analysis/valuation/sensitivity.py
    lib/analysis/peers.py              (peer finding)
    lib/data/providers/simfin_provider.py (SimFin)
    lib/data/label_maps.py             (legacy label maps)
```

---

## 5. Hvað vantar — heiðarlegt mat

### 5.1 DCF Steps 2-6: EKKERT kóðað

Öll 5 skrefin eru `st.info()` placeholder. Ekkert af eftirfarandi er byggt:
- Assumption inputs (growth, margins, capex per ár)
- 3-statement projection (IS → BS → CF tengingar)
- WACC calculator (CAPM, cost of debt, capital structure)
- Terminal value (Gordon Growth / Exit Multiple)
- Discounting, equity bridge, sensitivity, scenarios

### 5.2 Flagging kerfið — hvað treysti ég / treysti ekki

**Treysti (virkar vel):**
- Margin anomalies — prófað á 30+ fyrirtækjum, fangar rétt
- Tax anomalies — TCJA, COVID, repatriation flaggast
- Revenue anomalies — M&A og divestitures greinast
- Statistical outliers — aðlagast per fyrirtæki
- Earnings quality score — gefur nothæfa einkunn
- Cyclicality classification — flokkar rétt (XOM cyclical, WMT stable)

**Treysti miðlungs:**
- M&A fingerprinting — virkar en of mörg false positives (goodwill getur hækkað af öðrum ástæðum)
- Known company events — hardcoded, nær bara ~15 fyrirtæki
- Revenue mix shift — erfitt að greina án segment data

**Treysti ekki:**
- Deferred revenue trend — of fá fyrirtæki hafa þessi gögn í EDGAR
- Capital allocation pattern — flokkun er gróf
- Slow decline detection — þröskuldur er handstilltur, ekki prófaður á nógu mörgum

### 5.3 Standardization — hvað virkar / hvað ekki

**Virkar:**
- Layer 1 (XBRL) — fangar 85-90% af line items hjá US fyrirtækjum
- Derived fields — GP, EBITDA, FCF reiknaðar rétt
- Cross-checks — staðfesta balance equations
- Audit trail — notandi sér hvaðan hver tala kemur

**Virkar ekki / vantar:**
- **Fjármálafyrirtæki** (bankar, tryggingar) — allt annað IS template, standardizerinn skilar rugli
- **REITs** — FFO vantar, önnur BS structure
- **SimFin** — provider til en ekki tengdur
- **Non-US fyrirtæki** — EDGAR virkar ekki, Yahoo fallback gefur bara 4 ár
- **Some fields vantar** hjá sumum fyrirtækjum (CapEx, OCF, equity) — XBRL labels breytast milli fyrirtækja

### 5.4 Stóra spurningin

**Ætti spreading/normalization að vera sjálfstætt skref FYRIR valuation?**

Rök **fyrir:**
- Öll valuation tabs (DCF, Comps, DDM) þurfa sömu standardized gögn
- Núna keyrir hvert tab gagnaöflunina sjálfstætt → tvöföld vinna
- Step 1 er ekki DCF-specific — það er fundamental greining

Rök **á móti:**
- Þetta virkar "nógu vel" eins og er
- Ef við færum standardization út úr DCF tab, þarf refactoring

**Mín skoðun:** Já, spreading ætti að vera sameiginlegt skref sem allir valuation tabs deila. En þetta er arkitektúrbreyting, ekki bug fix.
