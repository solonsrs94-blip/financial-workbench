# Damodaran Fetch — Diagnosis & Runbook

## TL;DR
Damodaran URLs, parsing, and cache all work correctly. The UI warning banners
("Damodaran ERP fetch failed", "Credit spread unavailable") are caused by
transient network failures or a cold cache on a slow link — not a broken
endpoint or changed file format.

## Verified 2026-04-08

| URL | Status | Size | Parses |
|---|---|---|---|
| `https://pages.stern.nyu.edu/~adamodar/pc/implprem/ERPbymonth.xlsx` | 200 | 46 KB | ✅ col 9 "ERP (T12m)" |
| `https://pages.stern.nyu.edu/~adamodar/pc/ratings.xlsx` | 200 | 29 KB | ✅ rows 18–32 (large/financial), 37–51 (small) |
| `https://pages.stern.nyu.edu/~adamodar/pc/datasets/ctryprem.xlsx` | 200 | 379 KB | ✅ sheet "ERPs by country" |

Direct provider calls:

```
fetch_erp()                    → 0.0477   (Apr 2026, latest month)
fetch_spread(5.0, 'large')     → ('A2/A', 0.0078)
fetch_crp('United States')     → 0.00233
```

ERP tail from ERPbymonth.xlsx col 9:
`[0.0399, 0.0423, 0.0425, 0.0437, 0.0477]` — i.e. Dec 2025 / Jan 2026 / Feb
2026 / Mar 2026 / Apr 2026. Jan 2026 = **4.25%**, latest = **4.77%**.

## Hardening applied
`lib/data/providers/damodaran.py` `_download_excel` now:
- Uses `_TIMEOUT = 30` (up from 15; ctryprem.xlsx is 379 KB).
- Sends `User-Agent: Mozilla/5.0 (Vision Financial Workbench)` (some Stern
  servers throttle `python-requests/*`).
- Retries once on `RequestException` before giving up.
- Logs at `ERROR` (not `WARNING`) on final failure so ops notices.

`lib/analysis/valuation/wacc.py` `auto_wacc` no longer accepts
`erp: float = DEFAULT_MRP`. `erp` is a required positional argument; passing
`None` raises `ValueError`. This kills the 5.50% ghost value that used to
leak into the UI when the ERP fetch silently failed.

`config/constants.py`: `DEFAULT_MRP` removed.

## Runbook — if banner persists

1. Clear the Damodaran cache:
   ```
   rm data/cache/damodaran_*
   ```
2. Verify outbound HTTPS to `pages.stern.nyu.edu`:
   ```
   python -c "import requests; print(requests.get('https://pages.stern.nyu.edu/~adamodar/pc/implprem/ERPbymonth.xlsx', timeout=30).status_code)"
   ```
3. Run the provider directly:
   ```
   python -c "from lib.data.providers import damodaran; print(damodaran.fetch_erp(), damodaran.fetch_spread(5.0,'large'))"
   ```
4. If `fetch_erp()` returns None, check stderr for the `ERROR` log line with
   the underlying exception. Common causes: corporate proxy, DNS, firewall
   blocking `.nyu.edu`, or Stern server downtime (rare).
5. Fallback: enter ERP manually in the DCF/DDM Ke UI. The app will no longer
   silently substitute 5.5%.
