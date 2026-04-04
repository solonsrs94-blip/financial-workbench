"""Quick inspection of the test export JSON."""
import json

with open("AAPL_analysis_test.json") as f:
    d = json.load(f)

print("=== META ===")
for k, v in d["meta"].items():
    if isinstance(v, str) and len(v) > 60:
        print(f"  {k}: {v[:60]}...")
    else:
        print(f"  {k}: {v}")

print("\n=== DESCRIPTION ===")
desc = d.get("company_description") or ""
print(f"  {desc[:150]}..." if desc else "  None")

print("\n=== RATIOS ===")
for k, v in (d.get("ratios") or {}).items():
    print(f"  {k}: {v}")

print("\n=== HISTORICAL FINANCIALS ===")
hf = d.get("historical_financials") or {}
print(f"  Years: {hf.get('years')}")
for stmt in ["income_statement", "balance_sheet", "cash_flow"]:
    s = hf.get(stmt, {})
    if s:
        yr = list(s.keys())[-1]
        fields = list(s[yr].keys())
        print(f"  {stmt} ({yr}): {len(fields)} fields")
        for fk in fields[:5]:
            print(f"    {fk}: {s[yr][fk]}")
        if len(fields) > 5:
            print(f"    ... and {len(fields)-5} more")

print("\n=== DCF ===")
dcf = d.get("dcf", {})
print(f"  Sector: {dcf.get('sector_template')}")
print(f"  WACC: {dcf.get('wacc', {}).get('wacc')}")
for s in ["base", "bull", "bear"]:
    sc = dcf.get("scenarios", {}).get(s, {})
    r = sc.get("results", {})
    c2 = bool(sc.get("commentary_step2"))
    c4 = bool(sc.get("commentary_step4"))
    print(f"  {s}: implied=${r.get('implied_price')}, commentary_step2={c2}, step4={c4}")
wacc_c = dcf.get("commentary_wacc")
step5_c = dcf.get("commentary_step5")
print(f"  WACC commentary: {bool(wacc_c)}")
print(f"  Step5 commentary: {bool(step5_c)}")

print("\n=== DDM ===")
ddm = d.get("ddm", {})
print(f"  Ke: {ddm.get('ke', {}).get('ke')}")
for s in ["base", "bull", "bear"]:
    sc = ddm.get("scenarios", {}).get(s, {})
    r = sc.get("results", {})
    print(f"  {s}: implied=${r.get('implied_price')}, commentary={bool(sc.get('commentary_step2'))}")
print(f"  Alt model: {ddm.get('alternate_model', {}).get('implied_price')}")

print("\n=== COMPS ===")
comps = d.get("comps", {})
print(f"  Target: {comps.get('target', {}).get('ticker')}")
print(f"  Peers: {len(comps.get('peers', []))}")
print(f"  Is financial: {comps.get('is_financial')}")
for s in ["base", "bull", "bear"]:
    sc = comps.get("scenarios", {}).get(s, {})
    print(f"  {s}: implied=${sc.get('implied_price')}, mult={sc.get('final_multiple')}x")

print("\n=== HISTORICAL MULTIPLES ===")
hm = d.get("historical_multiples", {})
stats = hm.get("statistics", {})
print(f"  Stats multiples: {list(stats.keys()) if stats else 'None'}")
for s in ["base", "bull", "bear"]:
    sc = hm.get("scenarios", {}).get(s, {})
    print(f"  {s}: implied=${sc.get('implied_price')}, mult_key={sc.get('multiple_used')}")

print("\n=== SUMMARY ===")
sm = d.get("summary", {})
print(f"  Models used: {sm.get('models_used')}")
print(f"  Football field keys: {list(sm.get('football_field', {}).keys())}")
print(f"  Commentary: {bool(sm.get('commentary'))}")

print("\n=== OVERRIDES ===")
ov = d.get("overrides", {})
print(f"  Has overrides: {ov.get('has_overrides')}")

print(f"\n=== TOTAL SECTIONS: {list(d.keys())} ===")
