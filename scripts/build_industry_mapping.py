"""Build GICS Sub-Industry <-> yfinance industry mapping.

Fetches S&P 500 from Wikipedia, then yfinance industry for each ticker.
Outputs mapping dicts + raw CSV.
"""

import sys
import time
from io import StringIO

import pandas as pd
import requests
import yfinance as yf

sys.path.insert(0, ".")


def main():
    # Step 1: S&P 500 from Wikipedia
    print("Fetching S&P 500 from Wikipedia...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    resp = requests.get(
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        headers=headers,
    )
    tables = pd.read_html(StringIO(resp.text))
    sp500 = tables[0]
    print(f"  Got {len(sp500)} constituents\n")

    # Step 2: Fetch yfinance industry per ticker
    print("Fetching yfinance industry for each ticker...")
    results = []
    errors = []
    t_start = time.time()

    for i, (_, row) in enumerate(sp500.iterrows()):
        symbol = str(row["Symbol"]).strip()
        # Fix tickers with dots (BRK.B -> BRK-B for yfinance)
        yf_symbol = symbol.replace(".", "-")
        gics_sub = str(row.get("GICS Sub-Industry", ""))
        gics_sector = str(row.get("GICS Sector", ""))

        try:
            info = yf.Ticker(yf_symbol).info
            yf_industry = info.get("industry", "Unknown")
            yf_sector = info.get("sector", "Unknown")
            results.append({
                "symbol": symbol,
                "gics_sector": gics_sector,
                "gics_sub_industry": gics_sub,
                "yf_industry": yf_industry,
                "yf_sector": yf_sector,
            })
        except Exception as e:
            errors.append({"symbol": symbol, "error": str(e)})
            results.append({
                "symbol": symbol,
                "gics_sector": gics_sector,
                "gics_sub_industry": gics_sub,
                "yf_industry": "ERROR",
                "yf_sector": "ERROR",
            })

        if (i + 1) % 50 == 0:
            elapsed = time.time() - t_start
            rate = (i + 1) / elapsed
            eta = (len(sp500) - i - 1) / rate
            print(
                f"  Progress: {i+1}/{len(sp500)} "
                f"({elapsed:.0f}s elapsed, ~{eta:.0f}s remaining)"
            )

    df = pd.DataFrame(results)
    valid = df[df["yf_industry"] != "ERROR"]
    print(f"\n  Done: {len(valid)} valid, {len(errors)} errors")
    if errors:
        print(f"  Errors: {[e['symbol'] for e in errors]}")

    # Save raw CSV
    csv_path = "scripts/industry_mapping_raw.csv"
    df.to_csv(csv_path, index=False)
    print(f"  Saved raw data to {csv_path}")

    # Step 3: Build mappings
    print("\nBuilding mappings...")

    # GICS -> list of yfinance industries
    gics_to_yf = {}
    for gics_sub, group in valid.groupby("gics_sub_industry"):
        counts = group["yf_industry"].value_counts()
        gics_to_yf[gics_sub] = list(counts.index)

    # yfinance -> list of GICS sub-industries
    yf_to_gics = {}
    for yf_ind, group in valid.groupby("yf_industry"):
        counts = group["gics_sub_industry"].value_counts()
        yf_to_gics[yf_ind] = list(counts.index)

    # Step 4: Print results
    print(f"\n{'='*70}")
    print("GICS Sub-Industry -> yfinance industry")
    print(f"{'='*70}")
    for gics, yf_list in sorted(gics_to_yf.items()):
        marker = "" if len(yf_list) == 1 else f" ({len(yf_list)} yf industries)"
        print(f"  {gics}{marker}")
        for yf_ind in yf_list:
            count = len(valid[
                (valid["gics_sub_industry"] == gics)
                & (valid["yf_industry"] == yf_ind)
            ])
            print(f"    -> {yf_ind} ({count})")

    print(f"\n{'='*70}")
    print("yfinance industry -> GICS Sub-Industry")
    print(f"{'='*70}")
    for yf_ind, gics_list in sorted(yf_to_gics.items()):
        marker = "" if len(gics_list) == 1 else f" ({len(gics_list)} GICS)"
        print(f"  {yf_ind}{marker}")
        for gics in gics_list:
            count = len(valid[
                (valid["yf_industry"] == yf_ind)
                & (valid["gics_sub_industry"] == gics)
            ])
            print(f"    -> {gics} ({count})")

    # Step 5: Summary stats
    n_gics = len(gics_to_yf)
    n_yf = len(yf_to_gics)
    n_1to1_gics = sum(1 for v in gics_to_yf.values() if len(v) == 1)
    n_1tomany_gics = sum(1 for v in gics_to_yf.values() if len(v) > 1)
    n_1to1_yf = sum(1 for v in yf_to_gics.values() if len(v) == 1)
    n_1tomany_yf = sum(1 for v in yf_to_gics.values() if len(v) > 1)

    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"  GICS Sub-Industries: {n_gics}")
    print(f"    1:1 mapping: {n_1to1_gics}")
    print(f"    1:many mapping: {n_1tomany_gics}")
    print(f"  yfinance industries: {n_yf}")
    print(f"    1:1 mapping: {n_1to1_yf}")
    print(f"    1:many mapping: {n_1tomany_yf}")

    # Step 6: Generate Python dict file
    py_path = "scripts/industry_mapping_output.py"
    with open(py_path, "w", encoding="utf-8") as f:
        f.write('"""GICS Sub-Industry <-> yfinance industry mapping.\n\n')
        f.write("Auto-generated from S&P 500 data.\n")
        f.write(f"Valid tickers: {len(valid)}, Errors: {len(errors)}\n")
        f.write(f"GICS Sub-Industries: {n_gics}\n")
        f.write(f"yfinance industries: {n_yf}\n")
        f.write('"""\n\n')

        f.write("# yfinance industry -> list of GICS Sub-Industries\n")
        f.write("YF_TO_GICS: dict[str, list[str]] = {\n")
        for yf_ind in sorted(yf_to_gics.keys()):
            gics_list = yf_to_gics[yf_ind]
            f.write(f"    {yf_ind!r}: {gics_list!r},\n")
        f.write("}\n\n")

        f.write("# GICS Sub-Industry -> list of yfinance industries\n")
        f.write("GICS_TO_YF: dict[str, list[str]] = {\n")
        for gics in sorted(gics_to_yf.keys()):
            yf_list = gics_to_yf[gics]
            f.write(f"    {gics!r}: {yf_list!r},\n")
        f.write("}\n")

    print(f"\n  Saved Python dict to {py_path}")
    print(f"\n  Total time: {time.time() - t_start:.0f}s")


if __name__ == "__main__":
    main()
