# Data Layer — Technical Documentation

## Overview

The data layer is the foundation of the app. All data flows through it — no screen ever calls an API directly.

```
pages/ → lib/data/fundamentals.py (or market.py, macro.py) → lib/cache.py → lib/data/providers/yahoo.py
```

---

## Cache Strategy

### TTL (Time to Live) by Data Type

| Data Type | TTL | Reason |
|---|---|---|
| Price (daily) | 24 hours | Changes daily |
| Price (intraday) | 1 hour | Changes throughout the day |
| Financial statements | 7 days | Only changes quarterly |
| Ratios and metrics | 24 hours | Based on price which changes daily |
| Company info (sector, country) | 30 days | Rarely changes |
| Damodaran tables (ERP, beta, CRP) | 30 days | Updated monthly |
| Macro data (rates, CPI) | 24 hours | Changes daily/weekly |
| News (RSS) | 1 hour | New articles constantly |
| Insider transactions | 24 hours | New filings daily |
| Options chains | 1 hour | Changes rapidly |

Users can always force refresh to bypass cache.

### SQLite Schema

Single database file: `data/cache/cache.db`

```sql
CREATE TABLE cache_store (
    key         TEXT PRIMARY KEY,   -- "provider:ticker:datatype"
    data        TEXT NOT NULL,      -- JSON serialized data
    fetched_at  TEXT NOT NULL,      -- ISO timestamp when fetched
    expires_at  TEXT NOT NULL,      -- ISO timestamp when stale
    provider    TEXT NOT NULL       -- Which provider fetched this
);

CREATE INDEX idx_expires ON cache_store(expires_at);
CREATE INDEX idx_provider ON cache_store(provider);
```

### Cache Key Format

`{provider}:{ticker}:{data_type}`

Examples:
- `yahoo:AAPL:price_daily`
- `yahoo:AAPL:financials`
- `yahoo:AAPL:company_info`
- `damodaran:global:erp`
- `damodaran:global:industry_betas`
- `fred:US:treasury_10y`

---

## Provider Contract

All providers must return a **dict** with a predictable structure. The middleware layer (market.py, fundamentals.py, macro.py) converts these dicts into model objects.

```python
# What a provider returns (example: yahoo.py)
{
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "price": 178.50,
    "currency": "USD",
    "market_cap": 2800000000000,
    "pe_ratio": 28.5,
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "country": "United States",
    ...
}
```

### Data Normalization (IMPORTANT)

Yahoo returns percentages inconsistently:
- `dividendYield`: 0.41 means 0.41% → normalize in provider: `/ 100` → 0.0041
- `profitMargins`: 0.27 means 27% → already decimal, no change
- `returnOnEquity`: 1.52 means 152% → already decimal, no change

**Rule: All percentages stored as decimals. `format_percentage()` multiplies by 100.**

### Adding a New Provider

1. Create `lib/data/providers/newprovider.py`
2. Implement fetch functions that return dicts (return None on failure, never raise)
3. Update the relevant middleware file (market.py, fundamentals.py, or macro.py)
4. Add TTL entry in `config/constants.py` if needed
5. Nothing else changes — pages and components are unaware of providers

### Current yahoo.py Functions

- `search_companies(query)` → list of matching companies
- `fetch_company_info(ticker)` → basic info (name, sector, country)
- `fetch_price_data(ticker)` → current price, market cap, 52w range, analyst targets
- `fetch_ratios(ticker)` → P/E, margins, ROE, growth rates
- `fetch_price_history(ticker, period, interval)` → OHLCV DataFrame
- `fetch_financials(ticker)` → income statement, balance sheet, cash flow
- `fetch_holders(ticker)` → institutional holders, insider transactions
- `fetch_recommendations(ticker)` → analyst buy/hold/sell consensus
- `fetch_news(ticker)` → recent news articles

---

## Fallback Behavior

Three tiers of data availability:

### Tier 1 — Fresh data (normal)
Cache is valid and not expired. Return immediately. No API call needed.

### Tier 2 — Stale data with warning
API call failed, but expired cache exists. Return old data with a warning message:
`"Data from 2026-03-24 — could not fetch fresh data"`

### Tier 3 — No data with error
API call failed and no cache exists. Return error message:
`"Could not fetch data for AAPL. Check connection or try again."`

**The app never crashes due to missing data.** Every failure path has a graceful response.

---

## Full Request Flow

```
User enters "AAPL" on pages/1_company.py
    ↓
pages/1_company.py calls:
    lib/data/fundamentals.get_company("AAPL")
        ↓
    fundamentals.py calls:
        lib/cache.get("yahoo:AAPL:company")
            ↓
        ┌─ Cache HIT (not expired) → return data immediately
        │
        └─ Cache MISS (or expired) →
                lib/data/providers/yahoo.fetch_company("AAPL")
                    ↓
                ┌─ API SUCCESS → cache.store() → return data
                │
                └─ API FAILURE →
                        cache.get_stale("yahoo:AAPL:company")
                            ↓
                        ┌─ Stale data exists → return + warning
                        └─ Nothing exists → return error message
        ↓
    fundamentals.py: convert dict → Company model
        ↓
    return Company to pages/1_company.py
        ↓
pages/1_company.py uses components/ to display
```

---

## Cache Maintenance

- **On app startup:** Delete cache entries older than 90 days
- **Manual:** Run `scripts/clear_cache.py` to clear all or specific provider
- **Per-provider:** Can clear just Yahoo cache, just Damodaran, etc.

---

## cache.py Interface

```python
# Core functions that cache.py must provide:

get(key: str) -> dict | None
    # Returns cached data if valid (not expired), else None

get_stale(key: str) -> dict | None
    # Returns cached data even if expired (for fallback)

store(key: str, data: dict, ttl_seconds: int, provider: str) -> None
    # Stores data in cache with expiration

delete(key: str) -> None
    # Removes specific cache entry

clear_provider(provider: str) -> None
    # Removes all cache entries for a provider

clear_expired(max_age_days: int = 90) -> None
    # Removes entries older than max_age_days

force_refresh(key: str) -> None
    # Marks entry as expired (next get() will miss)
```

---

*Last updated: 2026-03-24*
