"""Extract full standardization output for AAPL and dump to JSON."""

import sys, os, json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.data.historical import get_raw_statements, get_standardized_history

ticker = "AAPL"

print(f"Fetching raw statements for {ticker}...")
raw = get_raw_statements(ticker)

print(f"Running standardization...")
std = get_standardized_history(ticker, raw_data=raw)

if std is None:
    print("ERROR: standardization returned None")
    sys.exit(1)

# --- 1. Structure overview ---
print("\n=== OUTPUT STRUCTURE ===")
for k, v in std.items():
    t = type(v).__name__
    if isinstance(v, dict):
        print(f"  {k}: dict with {len(v)} keys -> {list(v.keys())[:5]}...")
    elif isinstance(v, list):
        print(f"  {k}: list with {len(v)} items")
    elif isinstance(v, str):
        print(f"  {k}: str = '{v}'")
    else:
        print(f"  {k}: {t}")

# --- 2. Collect all unique keys per statement ---
def all_keys(audit_dict):
    keys = set()
    for yr, fields in audit_dict.items():
        keys.update(fields.keys())
    return sorted(keys)

is_keys = all_keys(std.get("income_audit", {}))
bs_keys = all_keys(std.get("balance_audit", {}))
cf_keys = all_keys(std.get("cashflow_audit", {}))

print(f"\nIS keys ({len(is_keys)}): {is_keys}")
print(f"BS keys ({len(bs_keys)}): {bs_keys}")
print(f"CF keys ({len(cf_keys)}): {cf_keys}")

# --- 3. Dump everything ---
output = {
    "ticker": ticker,
    "years": std["years"],
    "source": std.get("source", "unknown"),
    "structure": {},
    "income": std.get("income", {}),
    "balance": std.get("balance", {}),
    "cashflow": std.get("cashflow", {}),
    "income_audit": std.get("income_audit", {}),
    "balance_audit": std.get("balance_audit", {}),
    "cashflow_audit": std.get("cashflow_audit", {}),
    "cross_checks": std.get("cross_checks", []),
    "is_keys": is_keys,
    "bs_keys": bs_keys,
    "cf_keys": cf_keys,
}

for k, v in std.items():
    if isinstance(v, dict):
        output["structure"][k] = f"dict({len(v)} keys)"
    elif isinstance(v, list):
        output["structure"][k] = f"list({len(v)} items)"
    else:
        output["structure"][k] = f"{type(v).__name__}: {v}"

out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "standardization_output.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, default=str)

print(f"\nDone. Written to {out_path}")
