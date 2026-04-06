"""Test international index constituent availability from Wikipedia."""
import pandas as pd
import requests
from io import StringIO

indices = {
    "S&P_500": "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
    "STOXX_600": "https://en.wikipedia.org/wiki/STOXX_Europe_600",
    "FTSE_100": "https://en.wikipedia.org/wiki/FTSE_100_Index",
    "DAX_40": "https://en.wikipedia.org/wiki/DAX",
    "CAC_40": "https://en.wikipedia.org/wiki/CAC_40",
    "Nikkei_225": "https://en.wikipedia.org/wiki/Nikkei_225",
    "Hang_Seng": "https://en.wikipedia.org/wiki/Hang_Seng_Index",
    "KOSPI_50": "https://en.wikipedia.org/wiki/KOSPI_50",
    "S&P_TSX_60": "https://en.wikipedia.org/wiki/S%26P/TSX_60",
}

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

for name, url in indices.items():
    print(f"\n{'='*70}")
    print(f"=== {name} ===")
    print(f"{'='*70}")

    try:
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            print(f"  HTTP {r.status_code} -- FAILED")
            continue

        tables = pd.read_html(StringIO(r.text))
        # Find the biggest table (most likely constituents)
        biggest = max(tables, key=lambda t: len(t))

        print(f"  Tables found: {len(tables)}")
        print(f"  Biggest table: {len(biggest)} rows x {len(biggest.columns)} cols")
        print(f"  Columns: {list(biggest.columns)}")

        # Find ticker/symbol column
        symbol_cols = [c for c in biggest.columns
                       if any(kw in str(c).lower()
                              for kw in ['symbol', 'ticker', 'code', 'epic',
                                         'stock code', 'bloomberg'])]
        # Also check for columns that might just be called "Company" with ticker-like data
        if not symbol_cols:
            for c in biggest.columns:
                sample = biggest[c].dropna().head(5).astype(str)
                # Check if values look like tickers (short, uppercase)
                if all(len(v) <= 10 and v.replace('.', '').replace('-', '').isalnum()
                       for v in sample):
                    symbol_cols.append(f"{c} (inferred)")
                    break

        print(f"  Symbol columns: {symbol_cols}")

        # Find industry/sector column
        industry_cols = [c for c in biggest.columns
                         if any(kw in str(c).lower()
                                for kw in ['industry', 'sector', 'gics', 'sub', 'icb'])]
        print(f"  Industry columns: {industry_cols}")

        # Show sample rows
        show_cols = list(biggest.columns)[:5]
        print(f"\n  Sample (first 5 rows):")
        print(biggest[show_cols].head().to_string())

        # Show ticker samples if found
        if symbol_cols:
            col = symbol_cols[0].replace(' (inferred)', '')
            if col in biggest.columns:
                tickers_sample = biggest[col].dropna().head(10).tolist()
                print(f"\n  Ticker samples: {tickers_sample}")

        # Industry uniqueness
        if industry_cols:
            for ic in industry_cols:
                nuniq = biggest[ic].nunique()
                print(f"\n  Unique '{ic}': {nuniq}")
                print(f"  Top 5:")
                print(biggest[ic].value_counts().head(5).to_string())

    except Exception as e:
        print(f"  ERROR: {e}")
