"""EDGAR quarterly data provider — 10+ years from SEC Company Facts API.
No API key needed. Handles: concept fallbacks, temporal merging,
deduplication, cumulative-to-quarterly D&A, Q4 derivation.
"""

import logging
import time
from collections import defaultdict
from datetime import datetime
from typing import Optional

import pandas as pd
import requests

from lib.data.providers.edgar_concept_map import FIELD_CONCEPTS

logger = logging.getLogger(__name__)

_HEADERS = {"User-Agent": "FinancialWorkbench research@test.com"}
_TIMEOUT = 10
_RATE_DELAY = 0.12  # seconds between API calls

# Module-level caches
_cik_map: dict = {}  # ticker → CIK (loaded once)
_concept_cache: dict = {}  # (cik, taxonomy, concept) → facts list


# ── Public API ────────────────────────────────────────────────


def get_edgar_quarterly(ticker: str) -> Optional[dict]:
    """Fetch all 8 financial fields as quarterly pd.Series.

    Returns dict of field_name → pd.Series (index=date str, vals=float),
    or None if CIK lookup fails.
    """
    cik = get_cik(ticker)
    if not cik:
        logger.warning("No CIK found for %s", ticker)
        return None

    result = {}
    for field_name, config in FIELD_CONCEPTS.items():
        series = _fetch_field(cik, config)
        result[field_name] = series

    return result


def get_cik(ticker: str) -> Optional[str]:
    """Convert ticker to zero-padded 10-digit CIK."""
    global _cik_map
    if not _cik_map:
        _load_cik_map()
    # Handle BRK-B → BRK.B style differences
    for variant in [ticker, ticker.replace("-", "."), ticker.replace(".", "-")]:
        cik = _cik_map.get(variant.upper())
        if cik:
            return cik
    return None


# ── CIK lookup ────────────────────────────────────────────────


def _load_cik_map() -> None:
    """Load SEC ticker→CIK mapping (one-time, ~2MB)."""
    global _cik_map
    url = "https://www.sec.gov/files/company_tickers.json"
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            _cik_map = {
                entry["ticker"].upper(): str(entry["cik_str"]).zfill(10)
                for entry in data.values()
            }
            logger.info("Loaded %d CIK mappings", len(_cik_map))
    except Exception as exc:
        logger.warning("CIK lookup failed: %s", exc)


# ── Concept fetching ──────────────────────────────────────────


def _fetch_concept(cik: str, taxonomy: str, concept: str) -> list:
    """Fetch all facts for one concept. Returns list of dicts."""
    cache_key = (cik, taxonomy, concept)
    if cache_key in _concept_cache:
        return _concept_cache[cache_key]

    url = (
        f"https://data.sec.gov/api/xbrl/companyconcept/"
        f"CIK{cik}/{taxonomy}/{concept}.json"
    )
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
        time.sleep(_RATE_DELAY)
        if resp.status_code != 200:
            _concept_cache[cache_key] = []
            return []
        data = resp.json()
        units = data.get("units", {})
        facts = (
            units.get("USD")
            or units.get("shares")
            or units.get("USD/shares", [])
        )
        if not facts and units:
            facts = list(units.values())[0]
        # Pre-compute period days
        for f in facts:
            s, e = f.get("start"), f.get("end")
            if s and e:
                d0 = datetime.strptime(s, "%Y-%m-%d")
                d1 = datetime.strptime(e, "%Y-%m-%d")
                f["_days"] = (d1 - d0).days
            else:
                f["_days"] = 0
        _concept_cache[cache_key] = facts
        return facts
    except Exception as exc:
        logger.warning("EDGAR fetch %s/%s: %s", taxonomy, concept, exc)
        _concept_cache[cache_key] = []
        return []


# ── Field fetching (merge across concepts) ────────────────────


def _fetch_field(cik: str, config: dict) -> pd.Series:
    """Try all concepts for a field, merge into longest series."""
    is_flow = config["type"] == "flow"
    is_cumulative = config.get("cumulative", False)
    combined_q: dict = {}   # end_date → value
    combined_a: list = []   # annual entries for Q4 calc

    for taxonomy, concept in config["concepts"]:
        facts = _fetch_concept(cik, taxonomy, concept)
        if not facts:
            continue

        if is_flow:
            if is_cumulative:
                for item in _dedup_flow_cumulative(facts):
                    if item["end"] not in combined_q:
                        combined_q[item["end"]] = item["val"]
            else:
                for item in _dedup_flow(facts):
                    if item["end"] not in combined_q:
                        combined_q[item["end"]] = item["val"]
            combined_a.extend(_extract_annual(facts))
        else:
            for item in _dedup_stock(facts):
                if item["end"] not in combined_q:
                    combined_q[item["end"]] = item["val"]

    # Q4 = annual - Q1 - Q2 - Q3 (flow items only)
    if is_flow:
        _fill_q4(combined_q, _dedup_annual_entries(combined_a))

    if not combined_q:
        return pd.Series(dtype=float)
    return pd.Series(combined_q).sort_index()


# ── Deduplication ─────────────────────────────────────────────


def _dedup_flow(facts: list) -> list:
    """Flow items: single-quarter entries (75-110 day period)."""
    by_end: dict = defaultdict(list)
    for f in facts:
        if f.get("form") not in ("10-Q", "10-K"):
            continue
        if 75 <= f["_days"] <= 110:
            by_end[f["end"]].append(f)
    return [
        max(v, key=lambda x: x.get("filed", ""))
        for v in by_end.values()
    ]


def _dedup_flow_cumulative(facts: list) -> list:
    """Derive quarterly D&A from YTD cumulative CF entries.
    Q1 direct, Q2=H1-Q1, Q3=9M-H1, Q4 via _fill_q4.
    """
    entries = [
        f for f in facts
        if f.get("form") in ("10-Q", "10-K") and f["_days"] >= 60
    ]
    if not entries:
        return []
    single = _dedup_flow(facts)

    # Group cumulative (>120d) entries by fiscal year start
    by_start: dict = defaultdict(list)
    for e in entries:
        if e.get("start") and e["_days"] > 120:
            by_start[e["start"]].append(e)

    derived = []
    for fy_start, fy_ents in by_start.items():
        buckets: dict = {}
        for e in fy_ents:
            d = e["_days"]
            bk = "H1" if 150 <= d <= 220 else ("9M" if 240 <= d <= 310 else None)
            if bk and (bk not in buckets or e.get("filed", "") > buckets[bk].get("filed", "")):
                buckets[bk] = e

        q1_val = next((s["val"] for s in single if s.get("start") == fy_start), None)
        if "H1" in buckets and q1_val is not None:
            derived.append({"end": buckets["H1"]["end"], "val": buckets["H1"]["val"] - q1_val})
        if "9M" in buckets and "H1" in buckets:
            derived.append({"end": buckets["9M"]["end"], "val": buckets["9M"]["val"] - buckets["H1"]["val"]})

    return single + derived


def _dedup_stock(facts: list) -> list:
    """Stock items: all 10-Q/10-K entries, dedup by end date."""
    by_end: dict = defaultdict(list)
    for f in facts:
        if f.get("form") not in ("10-Q", "10-K"):
            continue
        by_end[f["end"]].append(f)
    return [
        max(v, key=lambda x: x.get("filed", ""))
        for v in by_end.values()
    ]


def _extract_annual(facts: list) -> list:
    """Get full-year entries (350-380 day period) from 10-K."""
    return [
        f for f in facts
        if f.get("form") == "10-K" and 350 <= f["_days"] <= 380
    ]


def _dedup_annual_entries(entries: list) -> list:
    """Deduplicate annual entries by end date, keep latest filing."""
    by_end: dict = defaultdict(list)
    for f in entries:
        by_end[f["end"]].append(f)
    return [
        max(v, key=lambda x: x.get("filed", ""))
        for v in by_end.values()
    ]


# ── Q4 derivation ────────────────────────────────────────────


def _fill_q4(combined_q: dict, annual: list) -> None:
    """Derive Q4 = annual − Q1 − Q2 − Q3. Modifies combined_q."""
    for a in annual:
        a_end = a["end"]
        a_start = a.get("start", "")
        a_val = a["val"]
        if not a_start or a_end in combined_q:
            continue

        # Find quarters within this fiscal year
        q_vals = [
            v for d, v in combined_q.items()
            if a_start < d < a_end
        ]
        if len(q_vals) == 3:
            q4 = a_val - sum(q_vals)
            combined_q[a_end] = q4


def clear_cache() -> None:
    """Clear concept cache (call on ticker change)."""
    _concept_cache.clear()
