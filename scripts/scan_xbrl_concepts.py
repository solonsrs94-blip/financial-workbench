"""Scan 50 companies to collect ALL XBRL concepts used in EDGAR filings."""

import sys, os, json
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.data.providers.edgar_xbrl import fetch_xbrl_statements
import pandas as pd

# 10 primary + 40 secondary
TICKERS = [
    # Primary 10
    "AAPL", "MSFT", "GOOG", "AMZN", "XOM", "WMT", "PG", "JNJ", "META", "NVDA",
    # Tech
    "ORCL", "ADBE", "CRM", "INTC", "AMD", "CSCO", "AVGO",
    # Healthcare
    "PFE", "MRK", "ABT", "TMO", "LLY", "ABBV",
    # Consumer
    "HD", "MCD", "NKE", "COST", "SBUX", "TGT",
    # Financials (reference)
    "GS", "BAC", "C", "BRK-B",
    # Energy
    "CVX", "COP", "SLB",
    # Industrials
    "GE", "HON", "UNP", "RTX", "LMT", "DE",
    # Utilities
    "NEE", "DUK", "SO",
    # Real Estate
    "AMT", "PLD", "O",
    # Telecom
    "T", "VZ", "TMUS",
]

# Collect: {statement_type: {xbrl_concept: {labels: set, tickers: set, sample_value: float}}}
all_concepts = {
    "income": defaultdict(lambda: {"labels": set(), "tickers": set(), "sample_value": None}),
    "balance": defaultdict(lambda: {"labels": set(), "tickers": set(), "sample_value": None}),
    "cashflow": defaultdict(lambda: {"labels": set(), "tickers": set(), "sample_value": None}),
}

# Also collect label-only items (concept=None)
none_concepts = {
    "income": defaultdict(lambda: {"tickers": set(), "sample_value": None}),
    "balance": defaultdict(lambda: {"tickers": set(), "sample_value": None}),
    "cashflow": defaultdict(lambda: {"tickers": set(), "sample_value": None}),
}

failed = []

for i, ticker in enumerate(TICKERS):
    print(f"[{i+1}/{len(TICKERS)}] {ticker}...", end=" ", flush=True)
    try:
        xbrl = fetch_xbrl_statements(ticker)
        if not xbrl:
            print("NO DATA")
            failed.append(ticker)
            continue

        for stmt in ["income", "balance", "cashflow"]:
            df = xbrl.get(stmt)
            if df is None or not isinstance(df, pd.DataFrame):
                continue

            for _, row in df.iterrows():
                concept = row.get("concept")
                sc = row.get("standard_concept")
                label = str(row.get("label", "") or "")
                is_abstract = row.get("abstract", False)

                if is_abstract or not label.strip():
                    continue

                # Get latest non-NaN value
                sample = None
                for c in reversed(list(df.columns)):
                    if c not in ("standard_concept", "label", "parent_concept",
                                 "abstract", "dimension", "concept"):
                        v = row.get(c)
                        if pd.notna(v) and str(v) != "None":
                            try:
                                sample = float(v)
                            except (ValueError, TypeError):
                                pass
                            break

                # Use the raw XBRL concept (not edgartools standard_concept)
                xbrl_concept = str(concept) if concept and str(concept) != "None" else None

                if xbrl_concept and not xbrl_concept.startswith("us-gaap_"):
                    # It's an actual concept
                    info = all_concepts[stmt][xbrl_concept]
                    info["labels"].add(label)
                    info["tickers"].add(ticker)
                    if sample is not None and info["sample_value"] is None:
                        info["sample_value"] = sample
                elif xbrl_concept and xbrl_concept.startswith("us-gaap_"):
                    # Strip prefix
                    clean = xbrl_concept.replace("us-gaap_", "")
                    info = all_concepts[stmt][clean]
                    info["labels"].add(label)
                    info["tickers"].add(ticker)
                    if sample is not None and info["sample_value"] is None:
                        info["sample_value"] = sample
                else:
                    # No concept — track by label
                    info = none_concepts[stmt][label]
                    info["tickers"].add(ticker)
                    if sample is not None and info["sample_value"] is None:
                        info["sample_value"] = sample

                # Also track edgartools standard_concept
                if sc and str(sc) != "None":
                    sc_clean = str(sc).strip()
                    info2 = all_concepts[stmt][f"SC:{sc_clean}"]
                    info2["labels"].add(label)
                    info2["tickers"].add(ticker)
                    if sample is not None and info2["sample_value"] is None:
                        info2["sample_value"] = sample

        print("OK")
    except Exception as e:
        print(f"ERROR: {e}")
        failed.append(ticker)

# Serialize
def serialize(d):
    out = {}
    for k, v in d.items():
        out[k] = {
            "labels": sorted(v["labels"]) if isinstance(v.get("labels"), set) else [],
            "tickers": sorted(v["tickers"]) if isinstance(v.get("tickers"), set) else [],
            "count": len(v.get("tickers", set())),
            "sample_value": v.get("sample_value"),
        }
    return out

result = {
    "concepts": {stmt: serialize(d) for stmt, d in all_concepts.items()},
    "none_labels": {stmt: serialize(d) for stmt, d in none_concepts.items()},
    "failed": failed,
    "total_tickers": len(TICKERS) - len(failed),
}

# Summary
for stmt in ["income", "balance", "cashflow"]:
    concepts = all_concepts[stmt]
    # Filter to real concepts (not SC: prefixed)
    real = {k: v for k, v in concepts.items() if not k.startswith("SC:")}
    sc_only = {k: v for k, v in concepts.items() if k.startswith("SC:")}
    none_count = len(none_concepts[stmt])
    print(f"\n{stmt.upper()}: {len(real)} raw concepts, {len(sc_only)} standard_concepts, {none_count} label-only items")

    # Most common concepts
    by_count = sorted(real.items(), key=lambda x: len(x[1]["tickers"]), reverse=True)
    print(f"  Top 20 by company count:")
    for concept, info in by_count[:20]:
        labels = ", ".join(sorted(info["labels"])[:3])
        print(f"    {concept:60s} ({len(info['tickers'])} cos) [{labels}]")

out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "xbrl_concept_scan.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, default=str)
print(f"\nSaved to {out_path}")
print(f"Failed: {failed}")
