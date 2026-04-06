"""Test yfinance comps data availability across different ticker types."""
import yfinance as yf
import pandas as pd
import time

tickers = [
    "AAPL",      # US mega cap tech
    "MSFT",      # US mega cap tech
    "JNJ",       # US large cap pharma
    "CRWD",      # US mid cap cybersecurity
    "SWK",       # US mid cap industrials
    "ETSY",      # US small-mid cap e-commerce
    "NESN.SW",   # European (Nestlé, Switzerland)
    "SAP.DE",    # European (SAP, Germany)
    "7203.T",    # Asian (Toyota, Japan)
    "005930.KS", # Asian (Samsung, South Korea)
]

fields = [
    ("price", ["currentPrice", "regularMarketPrice"]),
    ("shares_outstanding", ["sharesOutstanding"]),
    ("market_cap", ["marketCap"]),
    ("enterprise_value", ["enterpriseValue"]),
    ("revenue_ttm", ["totalRevenue"]),
    ("ebitda_ttm", ["ebitda"]),
    ("operating_income_ttm", ["operatingIncome", "ebit"]),
    ("net_income_ttm", ["netIncomeToCommon"]),
    ("eps_ttm", ["trailingEps"]),
    ("total_debt", ["totalDebt"]),
    ("cash", ["totalCash"]),
    ("trailing_pe", ["trailingPE"]),
    ("forward_pe", ["forwardPE"]),
    ("ev_to_revenue", ["enterpriseToRevenue"]),
    ("ev_to_ebitda", ["enterpriseToEbitda"]),
    ("currency", ["currency"]),
    ("industry", ["industry"]),
    ("sector", ["sector"]),
    ("country", ["country"]),
]

results = []
start_total = time.time()

for symbol in tickers:
    print(f"Fetching {symbol}...")
    t0 = time.time()
    t = yf.Ticker(symbol)
    info = t.info
    elapsed = time.time() - t0

    row = {"ticker": symbol, "fetch_time_s": round(elapsed, 2)}
    for field_name, keys in fields:
        val = None
        for k in keys:
            val = info.get(k)
            if val is not None:
                break
        row[field_name] = val
    results.append(row)

total_time = time.time() - start_total
df = pd.DataFrame(results)

# --- 1. Coverage table ---
print("\n" + "="*80)
print("1. COVERAGE TABLE (✓ = has value, ✗ = None/NaN)")
print("="*80)

coverage_fields = [
    "price", "shares_outstanding", "market_cap", "enterprise_value",
    "revenue_ttm", "ebitda_ttm", "operating_income_ttm", "net_income_ttm",
    "eps_ttm", "total_debt", "cash", "trailing_pe", "forward_pe",
    "ev_to_revenue", "ev_to_ebitda"
]
short_names = [
    "price", "shares", "mcap", "EV", "rev", "ebitda", "ebit", "ni",
    "eps", "debt", "cash", "tPE", "fPE", "evRev", "evEBITDA"
]

header = f"{'ticker':<12}" + "".join(f"{n:<9}" for n in short_names)
print(header)
print("-" * len(header))
for _, r in df.iterrows():
    line = f"{r['ticker']:<12}"
    for f in coverage_fields:
        val = r[f]
        mark = "✓" if val is not None and (not isinstance(val, float) or not pd.isna(val)) else "✗"
        line += f"{mark:<9}"
    print(line)

# --- 2. Actual values ---
print("\n" + "="*80)
print("2. ACTUAL VALUES (formatted)")
print("="*80)

def fmt_num(val, decimals=1):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return "—"
    if abs(val) >= 1e12:
        return f"{val/1e12:.{decimals}f}T"
    if abs(val) >= 1e9:
        return f"{val/1e9:.{decimals}f}B"
    if abs(val) >= 1e6:
        return f"{val/1e6:.{decimals}f}M"
    return f"{val:,.{decimals}f}"

def fmt_ratio(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return "—"
    return f"{val:.1f}x"

for _, r in df.iterrows():
    print(f"\n--- {r['ticker']} ({r['currency'] or '?'}) ---")
    print(f"  Price: {fmt_num(r['price'], 2)}  |  Shares: {fmt_num(r['shares_outstanding'])}  |  MCap: {fmt_num(r['market_cap'])}  |  EV: {fmt_num(r['enterprise_value'])}")
    print(f"  Rev: {fmt_num(r['revenue_ttm'])}  |  EBITDA: {fmt_num(r['ebitda_ttm'])}  |  EBIT: {fmt_num(r['operating_income_ttm'])}  |  NI: {fmt_num(r['net_income_ttm'])}  |  EPS: {fmt_num(r['eps_ttm'], 2)}")
    print(f"  Debt: {fmt_num(r['total_debt'])}  |  Cash: {fmt_num(r['cash'])}")
    print(f"  P/E: {fmt_ratio(r['trailing_pe'])}  |  Fwd P/E: {fmt_ratio(r['forward_pe'])}  |  EV/Rev: {fmt_ratio(r['ev_to_revenue'])}  |  EV/EBITDA: {fmt_ratio(r['ev_to_ebitda'])}")
    print(f"  Industry: {r['industry']}  |  Sector: {r['sector']}  |  Country: {r['country']}")

# --- 3. TTM vs Fiscal Year check ---
print("\n" + "="*80)
print("3. TTM vs FISCAL YEAR CHECK")
print("="*80)
print("Comparing info['totalRevenue'] vs latest annual revenue from financials")

for symbol in tickers:
    t = yf.Ticker(symbol)
    info_rev = t.info.get("totalRevenue")
    try:
        annual_is = t.financials
        if annual_is is not None and not annual_is.empty:
            # financials has dates as columns, items as rows
            latest_col = annual_is.columns[0]
            rev_row = None
            for label in ["Total Revenue", "TotalRevenue"]:
                if label in annual_is.index:
                    rev_row = label
                    break
            if rev_row:
                annual_rev = annual_is.loc[rev_row, latest_col]
                match = "MATCH (fiscal)" if info_rev == annual_rev else "DIFFER (likely TTM)"
                print(f"  {symbol:<12} info={fmt_num(info_rev)}  annual={fmt_num(annual_rev)}  → {match}")
            else:
                print(f"  {symbol:<12} Revenue row not found in financials. Rows: {list(annual_is.index[:5])}")
        else:
            print(f"  {symbol:<12} No annual financials available")
    except Exception as e:
        print(f"  {symbol:<12} Error: {e}")

# --- 5. Timing ---
print("\n" + "="*80)
print("5. TIMING")
print("="*80)
for _, r in df.iterrows():
    print(f"  {r['ticker']:<12} {r['fetch_time_s']:.2f}s")
print(f"\n  TOTAL: {total_time:.1f}s for {len(tickers)} tickers ({total_time/len(tickers):.1f}s avg)")
