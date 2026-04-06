"""Test peer selection sources: yfinance, FMP, Finnhub, industry granularity, S&P 500."""
import yfinance as yf
import requests
import pandas as pd
import time

# ============================================================
# TEST 1: yfinance — what peer/industry data exists?
# ============================================================
print("=" * 80)
print("TEST 1: yfinance — industry info + any peer data")
print("=" * 80)

test_tickers = ["AAPL", "JNJ", "CRWD", "ETSY", "SAP.DE"]

for symbol in test_tickers:
    t = yf.Ticker(symbol)
    info = t.info

    print(f"\n--- {symbol} ---")
    print(f"  sector: {info.get('sector')}")
    print(f"  industry: {info.get('industry')}")
    print(f"  sectorKey: {info.get('sectorKey')}")
    print(f"  industryKey: {info.get('industryKey')}")
    print(f"  marketCap: {info.get('marketCap'):,.0f}" if info.get('marketCap') else "  marketCap: None")
    print(f"  country: {info.get('country')}")

    for attr in ['recommendations', 'recommendations_summary']:
        try:
            result = getattr(t, attr)
            if result is not None and not (hasattr(result, 'empty') and result.empty):
                print(f"  {attr}: {type(result).__name__}, shape={result.shape if hasattr(result, 'shape') else 'N/A'}")
                if hasattr(result, 'head'):
                    print(result.head(3).to_string())
            else:
                print(f"  {attr}: EMPTY")
        except Exception as e:
            print(f"  {attr}: ERROR - {e}")

# ============================================================
# TEST 2: FMP — stock peers endpoint
# ============================================================
print("\n\n" + "=" * 80)
print("TEST 2: FMP — stock peers")
print("=" * 80)

from config.settings import FMP_API_KEY
FMP_KEY = FMP_API_KEY

for symbol in ["AAPL", "JNJ", "CRWD", "ETSY", "SAP.DE"]:
    url = f"https://financialmodelingprep.com/stable/stock-peers?symbol={symbol}&apikey={FMP_KEY}"
    r = requests.get(url)
    print(f"\n=== FMP peers {symbol} (HTTP {r.status_code}) ===")
    if r.status_code == 200:
        data = r.json()
        if isinstance(data, list) and len(data) > 0:
            for entry in data:
                peers = entry.get('peersList', entry.get('peers', []))
                print(f"  Peers ({len(peers)}): {peers}")
        elif isinstance(data, dict):
            peers = data.get('peersList', data.get('peers', []))
            print(f"  Peers ({len(peers)}): {peers}")
        else:
            print(f"  Response: {str(data)[:400]}")
    else:
        print(f"  {r.status_code}: {r.text[:300]}")
    time.sleep(0.3)

# ============================================================
# TEST 3: Finnhub — company peers
# ============================================================
print("\n\n" + "=" * 80)
print("TEST 3: Finnhub — company peers")
print("=" * 80)

from config.settings import FINNHUB_API_KEY
FINNHUB_KEY = FINNHUB_API_KEY

for symbol in ["AAPL", "JNJ", "CRWD", "ETSY"]:
    url = f"https://finnhub.io/api/v1/stock/peers?symbol={symbol}&token={FINNHUB_KEY}"
    r = requests.get(url)
    print(f"\n=== Finnhub peers {symbol} (HTTP {r.status_code}) ===")
    if r.status_code == 200:
        body = r.text[:500]
        if body.strip().startswith('<'):
            print("  HTML page (not JSON) -- premium only")
        else:
            try:
                data = r.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"  Peers ({len(data)}): {data}")
                else:
                    print(f"  Response: {str(data)[:300]}")
            except:
                print(f"  Parse error: {body[:200]}")
    else:
        print(f"  {r.status_code}: {r.text[:200]}")
    time.sleep(0.5)

# ============================================================
# TEST 4: yfinance industry granularity
# ============================================================
print("\n\n" + "=" * 80)
print("TEST 4: yfinance industry granularity (20 tech tickers)")
print("=" * 80)

tech_sample = ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "AVGO", "ORCL", "CRM",
               "ADBE", "CSCO", "INTC", "AMD", "QCOM", "TXN", "NOW", "PANW",
               "CRWD", "SNOW", "PLTR", "SHOP"]

results = []
for symbol in tech_sample:
    try:
        t = yf.Ticker(symbol)
        info = t.info
        mc = info.get("marketCap")
        results.append({
            "ticker": symbol,
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "industryKey": info.get("industryKey"),
            "mcap_B": f"{mc/1e9:.0f}B" if mc else "?",
        })
    except Exception as e:
        results.append({"ticker": symbol, "sector": "ERROR", "industry": str(e)[:50]})

df = pd.DataFrame(results)
print("\n" + df[["ticker", "sector", "industry", "mcap_B"]].to_string())
print(f"\nUnique industries: {df['industry'].nunique()}")
print(f"\nIndustry counts:")
print(df['industry'].value_counts().to_string())

# ============================================================
# TEST 5: S&P 500 from Wikipedia
# ============================================================
print("\n\n" + "=" * 80)
print("TEST 5: S&P 500 from Wikipedia")
print("=" * 80)

try:
    tables = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    sp500 = tables[0]
    print(f"  Rows: {len(sp500)}")
    print(f"  Columns: {list(sp500.columns)}")

    gics_cols = [c for c in sp500.columns if 'gics' in c.lower() or 'sub' in c.lower()]
    print(f"  GICS columns: {gics_cols}")

    if len(gics_cols) >= 2:
        sector_col = gics_cols[0]
        sub_col = gics_cols[1]
        print(f"\n  Unique GICS Sectors: {sp500[sector_col].nunique()}")
        print(f"  Unique GICS Sub-Industries: {sp500[sub_col].nunique()}")

        print(f"\n  Sample (first 15):")
        print(sp500[['Symbol', sector_col, sub_col]].head(15).to_string())

        print(f"\n  Info Tech sub-industries:")
        it = sp500[sp500[sector_col] == 'Information Technology']
        print(it[sub_col].value_counts().to_string())
        print(f"\n  Health Care sub-industries:")
        hc = sp500[sp500[sector_col] == 'Health Care']
        print(hc[sub_col].value_counts().head(10).to_string())
except Exception as e:
    print(f"  Wikipedia ERROR: {e}")
