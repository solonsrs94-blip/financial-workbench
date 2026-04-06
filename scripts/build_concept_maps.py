"""Build concept_maps.py from XBRL scan data.

Reads xbrl_concept_scan.json and generates classified concept maps.
"""

import json, os, sys

scan_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "data", "xbrl_concept_scan.json")
with open(scan_path, "r") as f:
    scan = json.load(f)

# Manual classification of ALL concepts found across 50 companies.
# Format: xbrl_concept -> standardized_key
# Only include raw concepts (not SC: prefixed edgartools concepts)

# We'll print concepts grouped by statement type, sorted by company count,
# so we can classify them.

for stmt in ["income", "balance", "cashflow"]:
    concepts = scan["concepts"][stmt]
    # Filter to raw concepts only
    raw = {k: v for k, v in concepts.items() if not k.startswith("SC:")}
    by_count = sorted(raw.items(), key=lambda x: x[1]["count"], reverse=True)

    print(f"\n{'='*80}")
    print(f"  {stmt.upper()} — {len(raw)} concepts")
    print(f"{'='*80}")

    for concept, info in by_count:
        count = info["count"]
        labels = info.get("labels", [])[:3]
        sample = info.get("sample_value")
        labels_str = " | ".join(labels)
        sample_str = f" val={sample/1e6:,.0f}M" if sample and abs(sample) > 1e6 else f" val={sample}" if sample else ""
        print(f"  {concept:65s} ({count:2d} cos){sample_str}")
        if labels:
            print(f"    labels: {labels_str}")
