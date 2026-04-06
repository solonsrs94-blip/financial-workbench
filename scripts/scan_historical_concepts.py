"""Scan ALL years of EDGAR XBRL for 10 main companies.
Collect every concept that appears, per year, per statement.
Output: JSON with all concepts and which years they appear."""

import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.data.providers.edgar_xbrl import fetch_xbrl_statements
from lib.data.concept_maps import IS_CONCEPTS, BS_CONCEPTS, CF_CONCEPTS

TICKERS = ["AAPL", "MSFT", "GOOG", "AMZN", "XOM", "WMT", "PG", "JNJ", "META", "NVDA"]

all_concepts = {"income": {}, "balance": {}, "cashflow": {}}
missing_concepts = {"income": {}, "balance": {}, "cashflow": {}}
concept_map_lookup = {"income": IS_CONCEPTS, "balance": BS_CONCEPTS, "cashflow": CF_CONCEPTS}

for ticker in TICKERS:
    print(f"\n{'='*50} {ticker} {'='*50}")
    try:
        xbrl = fetch_xbrl_statements(ticker)
        if not xbrl:
            print(f"  No XBRL data")
            continue
    except Exception as e:
        print(f"  ERROR: {e}")
        continue

    for stmt_name in ["income", "balance", "cashflow"]:
        df = xbrl.get(stmt_name)
        if df is None or not hasattr(df, 'iterrows'):
            continue

        # Find year columns
        year_cols = [c for c in df.columns
                     if len(str(c)) >= 8 and str(c)[:4].isdigit()]

        for _, row in df.iterrows():
            raw_concept = str(row.get("concept", "") or "")
            if raw_concept.startswith("us-gaap_"):
                raw_concept = raw_concept[8:]
            sc = str(row.get("standard_concept", "") or "")
            label = str(row.get("label", "") or "")
            is_abstract = row.get("abstract", False)
            if is_abstract:
                continue

            # Which years does this concept have data?
            years_with_data = []
            for col in year_cols:
                yr = str(col)[:4]
                val = row.get(col)
                if str(val) != "nan" and str(val) != "None" and val is not None:
                    years_with_data.append(yr)

            if not years_with_data:
                continue

            # Track concept
            for concept_id in [raw_concept, sc]:
                if not concept_id or concept_id == "None":
                    continue

                key = f"{concept_id}"
                if key not in all_concepts[stmt_name]:
                    all_concepts[stmt_name][key] = {
                        "labels": set(),
                        "tickers": set(),
                        "years": set(),
                        "in_map": concept_id in concept_map_lookup[stmt_name],
                        "mapped_to": concept_map_lookup[stmt_name].get(concept_id),
                    }
                all_concepts[stmt_name][key]["labels"].add(label[:80])
                all_concepts[stmt_name][key]["tickers"].add(ticker)
                all_concepts[stmt_name][key]["years"].update(years_with_data)

    print(f"  Done")

# Find missing concepts (appear in data but not in map)
print(f"\n{'='*100}")
print("MISSING CONCEPTS (in EDGAR but not in concept map)")
print(f"{'='*100}")

for stmt_name in ["income", "balance", "cashflow"]:
    cmap = concept_map_lookup[stmt_name]
    missing = []
    for concept_id, info in all_concepts[stmt_name].items():
        if not info["in_map"] and concept_id != "None":
            missing.append({
                "concept": concept_id,
                "labels": list(info["labels"])[:3],
                "tickers": list(info["tickers"]),
                "years": sorted(info["years"]),
                "count": len(info["tickers"]),
            })

    # Sort by frequency (most common first)
    missing.sort(key=lambda x: -x["count"])

    print(f"\n--- {stmt_name.upper()} ({len(missing)} missing) ---")
    for m in missing[:50]:  # Top 50
        print(f"  {m['concept'][:55]:55s} | {m['count']} tickers | years: {m['years'][0]}-{m['years'][-1]} | {m['labels'][0][:50]}")

# Save full data
output = {}
for stmt_name in ["income", "balance", "cashflow"]:
    output[stmt_name] = {}
    for k, v in all_concepts[stmt_name].items():
        output[stmt_name][k] = {
            "labels": list(v["labels"]),
            "tickers": list(v["tickers"]),
            "years": sorted(v["years"]),
            "in_map": v["in_map"],
            "mapped_to": v["mapped_to"],
        }

out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "historical_concepts.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)
print(f"\nSaved to {out_path}")

# Summary
for stmt_name in ["income", "balance", "cashflow"]:
    total = len(all_concepts[stmt_name])
    in_map = sum(1 for v in all_concepts[stmt_name].values() if v["in_map"])
    missing = total - in_map
    print(f"\n{stmt_name.upper()}: {total} total concepts, {in_map} in map, {missing} missing")
