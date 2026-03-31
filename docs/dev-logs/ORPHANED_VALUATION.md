# Orphaned Valuation Files — Audit

**Date:** 2026-03-26
**Files examined:** 5

---

## 1. `lib/analysis/valuation.py` (rót) — ☠️ DAUTT / ORPHANED

**Lýsing:** Gamla V1 valuation vélin. Importar `WACCInputs` og `DCFAssumptions` úr `models/valuation.py` — en þessir dataclassar hafa verið eyddir. **Import crashar.**

### Föll

#### `calc_capm(rf, beta, mrp) -> float`
- **Docstring:** Cost of equity via CAPM: rE = Rf + beta * MRP
- **Input:** 3 floats (risk-free rate, beta, market risk premium)
- **Output:** float (cost of equity)
- **Staða:** Virkar einangrað en endurtekið — betri útgáfa í `valuation/wacc.py`

#### `calc_wacc(inputs: WACCInputs) -> float`
- **Docstring:** Weighted average cost of capital
- **Input:** `WACCInputs` dataclass (existerar ekki lengur)
- **Output:** float
- **Staða:** **BROTIÐ** — `WACCInputs` hefur verið eytt úr models

#### `build_fcf_table(base_revenue, base_da, assumptions: DCFAssumptions) -> pd.DataFrame`
- **Docstring:** Build projected FCF table for n_years. Returns DataFrame with columns: Year, Revenue, EBIT, NOPAT, D&A, CapEx, dNWC, FCF
- **Input:** 2 floats + `DCFAssumptions` dataclass (existerar ekki lengur)
- **Output:** DataFrame (7 dálkar)
- **Staða:** **BROTIÐ** — einfaldari en V2 (engin SBC, engin NWC from days, ekkert per-year margin)

#### `calc_terminal_value(last_fcf, last_ebitda, assumptions: DCFAssumptions) -> float`
- **Docstring:** Calculate terminal value using selected method
- **Input:** 2 floats + `DCFAssumptions`
- **Output:** float
- **Staða:** **BROTIÐ** — sama rökfræði og V2 en bundið við DCFAssumptions

#### `run_dcf(base_revenue, base_da, net_debt, shares, current_price, assumptions: DCFAssumptions) -> DCFResult`
- **Docstring:** Run full DCF valuation. Returns DCFResult.
- **Input:** 5 floats + `DCFAssumptions`
- **Output:** `DCFResult` (en gamalt format — nýtt model hefur `bridge`, `wacc_result`, `warnings`)
- **Staða:** **BROTIÐ** — V1 DCFResult átti `net_debt`, `shares_outstanding` fields sem eru ekki í nýja modelinu

#### `sensitivity_table(base_revenue, base_da, net_debt, shares, current_price, assumptions, wacc_steps, growth_steps) -> pd.DataFrame`
- **Docstring:** 2D sensitivity: implied price at various WACC / terminal growth combos
- **Input:** 5 floats + `DCFAssumptions` + 2 ints
- **Output:** DataFrame (5×5 grid)
- **Staða:** **BROTIÐ** — kallar `run_dcf` sem er brotið

### Import keðja
```
valuation.py → models.valuation.WACCInputs    ← EXISTERAR EKKI
             → models.valuation.DCFAssumptions ← EXISTERAR EKKI
             → models.valuation.DCFResult      ← existerar en hefur breyst
```

### Hver importar þessa skrá?
**Enginn.** Ekkert í `pages/` eða `lib/` importar `lib.analysis.valuation` (rót). Einungis gamalt reference í `.claude/settings.local.json` pre-commit hook.

---

## 2. `lib/analysis/valuation/dcf.py` — ✅ VIRKT, fullþroskað

**Lýsing:** V2 DCF vélin. IB-standard (Wall Street Prep stíll) — per-year assumptions, SBC deduction, NWC frá days, equity bridge, sanity warnings.

### Föll

#### `build_fcf_table(base_revenue, n_years, growth_rates, ebit_margins, tax_rate, capex_pcts, da_pcts, sbc_pcts, dso, dio, dpo, base_cogs_pct) -> pd.DataFrame`
- **Docstring:** Build FCF projection table using the same formula for Simple and Complex. All list inputs should have length n_years. Returns DataFrame with full line items per year.
- **Input:** 1 float (base_revenue), 1 int (n_years), 8 lists (per-year rates), 1 float (cogs_pct)
- **Output:** DataFrame with 12 dálkar: Year, Revenue, Growth, EBIT, EBIT_Margin, NOPAT, D&A, CapEx, dNWC, SBC, FCF, EBITDA
- **Staða:** ✅ **Fullþroskað** — miklu betra en V1 (per-year margins, SBC, NWC from DSO/DIO/DPO)

#### `calc_terminal_value(last_fcf, last_ebitda, terminal_growth, wacc, method, exit_multiple) -> float`
- **Docstring:** Calculate terminal value. method: 'gordon' | 'exit_multiple' | 'average'
- **Input:** 4 floats + 1 str + 1 optional float
- **Output:** float
- **Staða:** ✅ Virkar — sama rökfræði og V1 en hreinni (ekki bundið við dataclass)

#### `run_dcf(fcf_table, wacc_result, terminal_growth, terminal_method, exit_multiple, net_debt, shares, current_price, minority_interest, preferred_equity) -> DCFResult`
- **Docstring:** Run DCF from a built FCF table. Returns DCFResult.
- **Input:** DataFrame + WACCResult + 6 floats + 2 optional floats
- **Output:** `DCFResult` (nýtt model: bridge, wacc_result, implied_exit_multiple, revenue_cagr, terminal_margin, warnings)
- **Staða:** ✅ **Fullþroskað** — equity bridge (EV → net debt → minority → preferred → equity), sanity warnings (TV >75%, exit >25x, g >4%)

### Import keðja
```
valuation/dcf.py → models.valuation.DCFResult     ✅
                 → models.valuation.EquityBridge   ✅
                 → models.valuation.WACCResult     ✅
```

### Hver importar þessa skrá?
- `scripts/test_dcf.py` ✅
- `scripts/test_dcf_v2.py` ✅
- `scripts/optimize_dcf.py` ✅
- `lib/analysis/valuation/sensitivity.py` ✅
- **Enginn page** ❌ — pages/valuation/ importar hana ekki enn

---

## 3. `lib/analysis/valuation/wacc.py` — ✅ VIRKT, fullþroskað

**Lýsing:** WACC vél með smart defaults. Notar adjusted beta, interest/debt for Rd, market weights.

### Föll

#### `adjusted_beta(raw_beta) -> float`
- **Docstring:** Blume adjustment: 2/3 * raw + 1/3 * 1.0
- **Input:** float (raw beta)
- **Output:** float (adjusted beta)
- **Staða:** ✅ Standard Blume adjustment

#### `calc_capm(rf, beta, erp, size_premium, crp) -> float`
- **Docstring:** Cost of equity: Re = Rf + beta×ERP + size_premium + CRP
- **Input:** 5 floats (rf, beta, erp, size_premium default 0, crp default 0)
- **Output:** float (cost of equity)
- **Staða:** ✅ **Betri en V1** — hefur size premium og country risk premium

#### `cost_of_debt_from_interest(interest_expense, total_debt) -> float`
- **Docstring:** Method A: Interest Expense / Total Debt
- **Input:** 2 floats
- **Output:** float (pre-tax cost of debt, fallback 5%)
- **Staða:** ✅

#### `auto_wacc(rf, raw_beta, market_cap, total_debt, interest_expense, tax_rate, erp) -> WACCResult`
- **Docstring:** Calculate WACC with smart defaults. Uses: adjusted beta, interest/debt for Rd, market weights. Returns WACCResult with all intermediates for display.
- **Input:** 7 params (5 floats + 2 optional with defaults frá config/constants.py)
- **Output:** `WACCResult` dataclass (12 fields: rf, beta, erp, Re, Rd_pretax, tax, Rd_aftertax, rd_method, e_weight, d_weight, wacc)
- **Staða:** ✅ **Fullþroskað** — smart fallbacks (beta=1 ef missing, Rd=Rf+200bps ef no interest data)

### Import keðja
```
valuation/wacc.py → models.valuation.WACCResult    ✅
                  → config.constants.DEFAULT_MRP    ✅
                  → config.constants.DEFAULT_TAX_RATE ✅
```

### Hver importar þessa skrá?
- `scripts/test_dcf.py` ✅
- `scripts/test_dcf_v2.py` ✅
- `scripts/optimize_dcf.py` ✅
- **Enginn page** ❌

---

## 4. `lib/analysis/valuation/sensitivity.py` — ✅ VIRKT, einfalt

**Lýsing:** 2D sensitivity tafla — WACC vs terminal growth, 5×5 grid.

### Föll

#### `sensitivity_table(fcf_table, wacc_result, terminal_growth, terminal_method, exit_multiple, net_debt, shares, current_price, minority, preferred) -> pd.DataFrame`
- **Docstring:** 2D sensitivity: implied price across WACC / terminal growth combos
- **Input:** DataFrame + WACCResult + 8 floats/strings
- **Output:** DataFrame (5×5 grid, rows = WACC levels, cols = growth levels)
- **Staða:** ✅ Virkar — kallar `run_dcf` í loop, range ±2% WACC, ±1% growth

### Import keðja
```
valuation/sensitivity.py → models.valuation.WACCResult  ✅
                         → valuation/dcf.run_dcf        ✅ (lazy import)
```

### Hver importar þessa skrá?
- **Enginn** ❌ — enn ekki tengd við neinn page

---

## 5. `lib/analysis/peers.py` — ✅ VIRKT, í notkun

**Lýsing:** Peer comparison — finnur og ber saman fyrirtæki í sömu atvinnugrein.

### Föll

#### `_find_peer_tickers(sector, industry, exclude_ticker) -> list[str]`
- **Docstring:** Find peer tickers via screener, filtering duplicates
- **Input:** 3 strings (sector, industry, ticker to exclude)
- **Output:** list[str] (up to 15 tickers)
- **Staða:** ✅ — notar `yfinance.screener.EquityQuery`, filtrar foreign listings og depositary receipts

#### `fetch_peers(sector, industry, exclude_ticker) -> list[dict]`
- **Docstring:** Fetch peer companies in the same industry with key metrics. All values converted to USD.
- **Input:** 3 strings
- **Output:** list[dict] (up to 6 peers, each with: ticker, name, price, market_cap, pe, pb, profit_margin, roe, div_yield)
- **Staða:** ✅ **Vel útfærð** — screener + known peers fallback, currency conversion, ratio sanity (pe/pb range checks)

#### `_get_usd_rate(currency, rate_cache) -> float`
- **Docstring:** Get exchange rate: how many units of currency per 1 USD
- **Input:** str + dict (cache)
- **Output:** float
- **Staða:** ✅ — notar `{CURRENCY}=X` Yahoo ticker

### Known peers fallback
```python
_KNOWN_PEERS = {
    "Internet Content & Information": ["META", "GOOG", ...],
    "Semiconductors": ["NVDA", "AMD", "INTC", ...],
    "Software - Infrastructure": ["MSFT", "ORCL", ...],
    "Software - Application": ["ADBE", "CRM", ...],
    "Consumer Electronics": ["AAPL", "SONY", ...],
    "E-Commerce": ["AMZN", "BABA", ...],
    "Social Media": ["META", "SNAP", ...],
}
```

### Hver importar þessa skrá?
- `pages/company/header.py` (línu 68) ✅
- `pages/company/peers_tab.py` (línu 43) ✅

---

## Heildarsamantekt

| Skrá | Staða | Pages import? | Brotið? | Ráðlegging |
|------|-------|---------------|---------|------------|
| `lib/analysis/valuation.py` | ☠️ DAUTT — V1 | ❌ Nei | ✅ Já — crashar á import | **Eyða** |
| `lib/analysis/valuation/dcf.py` | ✅ V2, fullþroskað | ❌ Bara scripts | ❌ Nei | Tengja við pages þegar DCF Steps 3-6 eru byggð |
| `lib/analysis/valuation/wacc.py` | ✅ V2, fullþroskað | ❌ Bara scripts | ❌ Nei | Tengja við pages |
| `lib/analysis/valuation/sensitivity.py` | ✅ V2, virkt | ❌ Enginn | ❌ Nei | Tengja við DCF Step 6 |
| `lib/analysis/peers.py` | ✅ Virkt, í notkun | ✅ 2 pages | ❌ Nei | Ekkert þarf að breyta |

### V1 vs V2 samanburður

| Eiginleiki | V1 (`valuation.py`) | V2 (`valuation/dcf.py`) |
|------------|---------------------|-------------------------|
| Per-year assumptions | ❌ Einn margin/growth | ✅ Listar per ár |
| SBC deduction frá FCF | ❌ | ✅ |
| NWC from days (DSO/DIO/DPO) | ❌ Fixed % | ✅ Days-based |
| Equity bridge | ❌ Einfalt EV - net debt | ✅ Minority + preferred |
| Sanity warnings | ❌ | ✅ TV%, exit multiple, growth |
| EBITDA í output | ❌ | ✅ |
| Adjusted beta | ❌ | ✅ Blume |
| Size/country premium | ❌ | ✅ |
| Smart Rd fallback | ❌ | ✅ Rf + 200bps |
| Model compatibility | ❌ Crashar | ✅ Notar virkt WACCResult/DCFResult |
