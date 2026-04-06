"""Explore SimFin free tier — what data is actually available?"""

import simfin as sf
from simfin.names import *
import pandas as pd
import os, json, traceback

sf.set_api_key('free')
sf.set_data_dir(os.path.expanduser('~/simfin_data/'))

results = {}

def try_load(name, func, **kwargs):
    """Try loading a dataset, capture results or error."""
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    try:
        df = func(**kwargs)
        if df is None or (hasattr(df, 'empty') and df.empty):
            print("  EMPTY or None")
            results[name] = {"works": False, "error": "Empty/None"}
            return None
        print(f"  Shape: {df.shape}")
        print(f"  Index names: {df.index.names}")
        print(f"  Columns: {list(df.columns)}")

        # Count unique tickers and years
        if 'Ticker' in df.index.names:
            tickers = df.index.get_level_values('Ticker').unique()
            print(f"  Unique tickers: {len(tickers)}")
        if 'Fiscal Year' in df.columns:
            years = sorted(df['Fiscal Year'].dropna().unique())
            print(f"  Fiscal years: {years[0]:.0f}-{years[-1]:.0f} ({len(years)} years)")
        elif 'Report Date' in df.index.names:
            dates = df.index.get_level_values('Report Date')
            print(f"  Date range: {dates.min()} to {dates.max()}")

        results[name] = {
            "works": True,
            "shape": list(df.shape),
            "columns": list(df.columns),
            "index_names": list(df.index.names),
        }
        return df
    except Exception as e:
        print(f"  ERROR: {e}")
        traceback.print_exc()
        results[name] = {"works": False, "error": str(e)}
        return None


# 1. Income Statement
df_is = try_load("Income Statement (annual)", sf.load_income, variant='annual', market='us')
if df_is is not None:
    # AAPL details
    try:
        aapl = df_is.loc['AAPL']
        print(f"\n  AAPL rows: {len(aapl)}")
        if 'Fiscal Year' in aapl.columns:
            years = sorted(aapl['Fiscal Year'].dropna().unique())
            print(f"  AAPL years: {years[0]:.0f}-{years[-1]:.0f}")
        # Show latest 2 years
        latest = aapl.tail(2)
        print(f"\n  AAPL latest 2 rows:")
        for idx, row in latest.iterrows():
            print(f"\n  --- {idx} ---")
            for col in latest.columns:
                val = row[col]
                if pd.notna(val):
                    if isinstance(val, float) and abs(val) > 1000:
                        print(f"    {col:40s}: {val:>15,.0f}")
                    else:
                        print(f"    {col:40s}: {val}")
    except Exception as e:
        print(f"  AAPL lookup error: {e}")

# 2. Balance Sheet
df_bs = try_load("Balance Sheet (annual)", sf.load_balance, variant='annual', market='us')
if df_bs is not None:
    try:
        aapl = df_bs.loc['AAPL']
        print(f"\n  AAPL rows: {len(aapl)}")
        if 'Fiscal Year' in aapl.columns:
            years = sorted(aapl['Fiscal Year'].dropna().unique())
            print(f"  AAPL years: {years[0]:.0f}-{years[-1]:.0f}")
        latest = aapl.tail(1)
        print(f"\n  AAPL latest row:")
        for col in latest.columns:
            val = latest.iloc[0][col]
            if pd.notna(val):
                if isinstance(val, float) and abs(val) > 1000:
                    print(f"    {col:40s}: {val:>15,.0f}")
                else:
                    print(f"    {col:40s}: {val}")
    except Exception as e:
        print(f"  AAPL lookup error: {e}")

# 3. Cash Flow
df_cf = try_load("Cash Flow (annual)", sf.load_cashflow, variant='annual', market='us')
if df_cf is not None:
    try:
        aapl = df_cf.loc['AAPL']
        print(f"\n  AAPL rows: {len(aapl)}")
        if 'Fiscal Year' in aapl.columns:
            years = sorted(aapl['Fiscal Year'].dropna().unique())
            print(f"  AAPL years: {years[0]:.0f}-{years[-1]:.0f}")
        latest = aapl.tail(1)
        print(f"\n  AAPL latest row:")
        for col in latest.columns:
            val = latest.iloc[0][col]
            if pd.notna(val):
                if isinstance(val, float) and abs(val) > 1000:
                    print(f"    {col:40s}: {val:>15,.0f}")
                else:
                    print(f"    {col:40s}: {val}")
    except Exception as e:
        print(f"  AAPL lookup error: {e}")

# 4. Banks and Insurance
df_banks = try_load("Income Banks (annual)", sf.load_income_banks, variant='annual', market='us')
if df_banks is not None:
    try:
        jpm = df_banks.loc['JPM']
        print(f"\n  JPM rows: {len(jpm)}")
        latest = jpm.tail(1)
        print(f"\n  JPM latest:")
        for col in latest.columns:
            val = latest.iloc[0][col]
            if pd.notna(val):
                if isinstance(val, float) and abs(val) > 1000:
                    print(f"    {col:40s}: {val:>15,.0f}")
                else:
                    print(f"    {col:40s}: {val}")
    except Exception as e:
        print(f"  JPM lookup error: {e}")

df_ins = try_load("Income Insurance (annual)", sf.load_income_insurance, variant='annual', market='us')

# 5. Quarterly and TTM
df_q = try_load("Income Quarterly", sf.load_income, variant='quarterly', market='us')
if df_q is not None:
    try:
        aapl = df_q.loc['AAPL']
        print(f"  AAPL quarterly rows: {len(aapl)}")
    except:
        pass

df_ttm = try_load("Income TTM", sf.load_income, variant='ttm', market='us')

# 6. Share Prices
df_prices = try_load("Share Prices (daily)", sf.load_shareprices, variant='daily', market='us')
if df_prices is not None:
    try:
        aapl = df_prices.loc['AAPL']
        print(f"  AAPL price rows: {len(aapl)}")
        print(f"  AAPL date range: {aapl.index.get_level_values('Date').min()} to {aapl.index.get_level_values('Date').max()}")
    except Exception as e:
        print(f"  AAPL: {e}")
        # Try without multi-index
        try:
            dates = df_prices.index.get_level_values('Date') if 'Date' in df_prices.index.names else None
            if dates is not None:
                print(f"  Date range: {dates.min()} to {dates.max()}")
        except:
            pass

# 7. Derived Ratios
df_derived = try_load("Derived Ratios (annual)", sf.load_derived, variant='annual', market='us')

# 8. Share Price Ratios
df_price_ratios = try_load("Derived Share Prices (daily)", sf.load_derived_shareprices, variant='daily', market='us')

# 9. Full variants
df_full = try_load("Income Full (annual)", sf.load_income, variant='annual-full', market='us')

# 10. Companies
df_companies = try_load("Companies List", sf.load_companies, market='us')
if df_companies is not None:
    print(f"\n  Sample:")
    print(df_companies.head(5).to_string())

# 11. Other markets
df_de = try_load("Income Germany", sf.load_income, variant='annual', market='de')
df_gb = try_load("Income UK", sf.load_income, variant='annual', market='gb')

# Save summary
with open(os.path.expanduser('~/simfin_results.json'), 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults saved.")
