"""Test forward estimate availability from yfinance, FMP, and Finnhub."""
import yfinance as yf
import requests
import time
import json

tickers = ["AAPL", "MSFT", "JNJ", "CRWD", "SWK", "ETSY", "NESN.SW", "SAP.DE", "7203.T", "005930.KS"]

# ============================================================
# TEST 1: yfinance
# ============================================================
print("=" * 80)
print("TEST 1: yfinance")
print("=" * 80)

yf_results = []

for symbol in tickers:
    t = yf.Ticker(symbol)
    info = t.info

    print(f"\n{'='*60}")
    print(f"=== {symbol} ===")
    print(f"{'='*60}")

    # A. Forward fields in info
    print("\n--- info forward fields ---")
    for k in ["forwardEps", "forwardPE", "trailingEps", "trailingPE",
              "earningsGrowth", "revenueGrowth", "earningsQuarterlyGrowth"]:
        print(f"  {k}: {info.get(k)}")

    # B. earnings_estimate
    print("\n--- earnings_estimate ---")
    ee = None
    try:
        ee = t.earnings_estimate
        if ee is not None and not ee.empty:
            print(ee.to_string())
        else:
            print("  EMPTY or None")
    except Exception as e:
        print(f"  ERROR: {e}")

    # C. revenue_estimate
    print("\n--- revenue_estimate ---")
    re_est = None
    try:
        re_est = t.revenue_estimate
        if re_est is not None and not re_est.empty:
            print(re_est.to_string())
        else:
            print("  EMPTY or None")
    except Exception as e:
        print(f"  ERROR: {e}")

    # D. growth_estimates
    print("\n--- growth_estimates ---")
    try:
        ge = t.growth_estimates
        if ge is not None and not ge.empty:
            print(ge.to_string())
        else:
            print("  EMPTY or None")
    except Exception as e:
        print(f"  ERROR: {e}")

    # E. EBITDA keys in info
    print("\n--- EBITDA-related keys in info ---")
    ebitda_keys = {k: v for k, v in info.items() if 'ebitda' in k.lower()}
    print(f"  {ebitda_keys}")

    # Collect summary
    has_fwd_eps = info.get("forwardEps") is not None
    has_fwd_pe = info.get("forwardPE") is not None
    has_ee = ee is not None and not getattr(ee, 'empty', True)
    has_re = re_est is not None and not getattr(re_est, 'empty', True)
    # Check if revenue_estimate has dollar amounts
    has_re_dollars = False
    if has_re:
        for col in ['avg', 'mean', 'numberOfAnalysts']:
            if col in re_est.columns:
                pass
        has_re_dollars = 'avg' in re_est.columns

    yf_results.append({
        "ticker": symbol,
        "fwd_eps": has_fwd_eps,
        "fwd_pe": has_fwd_pe,
        "earnings_est": has_ee,
        "revenue_est": has_re,
        "rev_est_dollars": has_re_dollars,
    })

# ============================================================
# TEST 2: FMP
# ============================================================
print("\n\n" + "=" * 80)
print("TEST 2: FMP (Financial Modeling Prep)")
print("=" * 80)

from config.settings import FMP_API_KEY
FMP_KEY = FMP_API_KEY
fmp_results = []

for symbol in tickers:
    # FMP uses different ticker format for some exchanges
    fmp_sym = symbol
    url = f"https://financialmodelingprep.com/api/v3/analyst-estimates/{fmp_sym}?limit=3&apikey={FMP_KEY}"
    r = requests.get(url)
    print(f"\n=== FMP {symbol} (HTTP {r.status_code}) ===")

    row = {"ticker": symbol, "status": r.status_code, "has_data": False,
           "fwd_rev": False, "fwd_ebitda": False, "fwd_ebit": False,
           "fwd_eps": False, "fwd_ni": False, "n_analysts": None}

    if r.status_code == 200:
        data = r.json()
        if data and len(data) > 0:
            row["has_data"] = True
            print(f"  Fields: {list(data[0].keys())}")
            for entry in data[:2]:
                print(f"  {entry.get('date')}:")
                print(f"    Revenue avg:  {entry.get('estimatedRevenueAvg'):,.0f}" if entry.get('estimatedRevenueAvg') else "    Revenue avg:  None")
                print(f"    EBITDA avg:   {entry.get('estimatedEbitdaAvg'):,.0f}" if entry.get('estimatedEbitdaAvg') else "    EBITDA avg:   None")
                print(f"    EBIT avg:     {entry.get('estimatedEbitAvg'):,.0f}" if entry.get('estimatedEbitAvg') else "    EBIT avg:     None")
                print(f"    EPS avg:      {entry.get('estimatedEpsAvg')}")
                print(f"    Net Inc avg:  {entry.get('estimatedNetIncomeAvg'):,.0f}" if entry.get('estimatedNetIncomeAvg') else "    Net Inc avg:  None")
                print(f"    # analysts:   {entry.get('numberAnalystEstimatedRevenue')}")

            e0 = data[0]
            row["fwd_rev"] = e0.get("estimatedRevenueAvg") is not None and e0.get("estimatedRevenueAvg") != 0
            row["fwd_ebitda"] = e0.get("estimatedEbitdaAvg") is not None and e0.get("estimatedEbitdaAvg") != 0
            row["fwd_ebit"] = e0.get("estimatedEbitAvg") is not None and e0.get("estimatedEbitAvg") != 0
            row["fwd_eps"] = e0.get("estimatedEpsAvg") is not None
            row["fwd_ni"] = e0.get("estimatedNetIncomeAvg") is not None and e0.get("estimatedNetIncomeAvg") != 0
            row["n_analysts"] = e0.get("numberAnalystEstimatedRevenue")
        else:
            print("  EMPTY -- ticker not on free tier or no data")
    else:
        print(f"  Error: {r.text[:300]}")

    fmp_results.append(row)
    time.sleep(0.3)

# ============================================================
# TEST 3: Finnhub
# ============================================================
print("\n\n" + "=" * 80)
print("TEST 3: Finnhub")
print("=" * 80)

from config.settings import FINNHUB_API_KEY
FINNHUB_KEY = FINNHUB_API_KEY
test_tickers_fh = ["AAPL", "CRWD", "JNJ", "SWK"]
endpoints = ["eps-estimates", "revenue-estimates", "ebitda-estimates", "ebit-estimates"]

fh_results = []

for symbol in test_tickers_fh:
    row = {"ticker": symbol}
    for endpoint in endpoints:
        url = f"https://finnhub.io/api/v1/stock/{endpoint}?symbol={symbol}&freq=annual&token={FINNHUB_KEY}"
        r = requests.get(url)
        status = r.status_code
        key = endpoint.replace("-estimates", "").replace("-", "_")

        print(f"\n=== Finnhub {endpoint} {symbol} (HTTP {status}) ===")

        has_data = False
        if status == 200:
            data = r.json()
            if isinstance(data, dict) and 'data' in data and data['data']:
                entry = data['data'][0]
                print(f"  Period: {entry.get('period')}")
                print(f"  numberAnalysts: {entry.get('numberAnalysts')}")
                for fld in ['epsAvg', 'epsHigh', 'epsLow', 'revenueAvg', 'revenueHigh', 'revenueLow',
                            'ebitdaAvg', 'ebitdaHigh', 'ebitdaLow', 'ebitAvg', 'ebitHigh', 'ebitLow']:
                    val = entry.get(fld)
                    if val is not None:
                        if isinstance(val, (int, float)) and abs(val) > 1e6:
                            print(f"  {fld}: {val:,.0f}")
                        else:
                            print(f"  {fld}: {val}")
                has_data = True
            elif isinstance(data, dict) and data.get('error'):
                print(f"  Error: {data['error']}")
            else:
                print(f"  Empty/no data. Keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
        elif status == 403:
            print("  403 FORBIDDEN -- premium only")
        elif status == 429:
            print("  429 RATE LIMITED")
        else:
            print(f"  {r.text[:200]}")

        row[key] = has_data
        time.sleep(0.5)

    fh_results.append(row)

# ============================================================
# SUMMARY TABLES
# ============================================================
print("\n\n" + "=" * 80)
print("SUMMARY TABLES")
print("=" * 80)

print("\n--- yfinance ---")
print(f"{'ticker':<12} {'fwd_EPS':<10} {'fwd_PE':<10} {'earn_est':<10} {'rev_est':<10} {'rev_$':<10}")
for r in yf_results:
    def yn(v): return "Y" if v else "-"
    print(f"{r['ticker']:<12} {yn(r['fwd_eps']):<10} {yn(r['fwd_pe']):<10} {yn(r['earnings_est']):<10} {yn(r['revenue_est']):<10} {yn(r['rev_est_dollars']):<10}")

print("\n--- FMP ---")
print(f"{'ticker':<12} {'has_data':<10} {'fwd_rev':<10} {'fwd_ebitda':<10} {'fwd_ebit':<10} {'fwd_eps':<10} {'fwd_ni':<10} {'analysts':<10}")
for r in fmp_results:
    def yn(v): return "Y" if v else "-"
    print(f"{r['ticker']:<12} {yn(r['has_data']):<10} {yn(r['fwd_rev']):<10} {yn(r['fwd_ebitda']):<10} {yn(r['fwd_ebit']):<10} {yn(r['fwd_eps']):<10} {yn(r['fwd_ni']):<10} {str(r['n_analysts'] or '-'):<10}")

print("\n--- Finnhub (4 test tickers) ---")
print(f"{'ticker':<12} {'eps':<10} {'revenue':<10} {'ebitda':<10} {'ebit':<10}")
for r in fh_results:
    def yn(v): return "Y" if v else "-"
    print(f"{r['ticker']:<12} {yn(r.get('eps',False)):<10} {yn(r.get('revenue',False)):<10} {yn(r.get('ebitda',False)):<10} {yn(r.get('ebit',False)):<10}")
