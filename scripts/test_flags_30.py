"""Test flagging system on 30 companies with known events."""

import sys
import yfinance as yf
from lib.data.historical import get_raw_statements, get_standardized_history
from lib.analysis.historical import (
    build_income_table, build_balance_table,
    build_cashflow_table, build_ratios_table,
)
from lib.analysis.historical_flags import detect_flags
from lib.analysis.historical_flags_smart import (
    compute_earnings_quality, classify_cyclicality,
)

TICKERS = {
    "MSFT": ["2015: Nokia write-down", "2022: Activision"],
    "GOOG": ["2017: EU fines"],
    "META": ["2021: Reality Labs", "High SBC"],
    "NVDA": ["2023: Margin compression"],
    "ORCL": ["2022: Cerner acquisition"],
    "CRM": ["High SBC"],
    "CRWD": ["High SBC"],
    "JNJ": ["2023: Kenvue spinoff"],
    "PFE": ["2023: Revenue collapse"],
    "ABBV": ["2023: Humira cliff"],
    "LLY": ["2023: GLP-1 boom"],
    "KO": ["2017: TCJA"],
    "WMT": ["Stable"],
    "COST": ["Stable"],
    "MO": ["Declining volumes"],
    "CAT": ["Cyclical"],
    "HON": ["2018: Spinoffs"],
    "GE": ["2018: Restructuring"],
    "AMZN": ["2022: Rivian write-down"],
    "TSLA": ["2023: Price cuts"],
    "NKE": ["2023: Inventory issues"],
    "MCD": ["Negative equity"],
    "V": ["2016: Visa Europe"],
    "SPGI": ["2022: IHS Markit merger"],
    "XOM": ["2020: Oil crash"],
    "CVX": ["2020: Oil crash"],
    "DIS": ["2020: Disney+ costs"],
    "NFLX": ["2022: Subscriber loss"],
    "T": ["2022: WarnerMedia spinoff"],
    "LIN": ["2018: Praxair merger"],
}

print(f"Testing {len(TICKERS)} companies...")
print(f"{'Ticker':<6} {'Flg':>3} {'H':>2} {'M':>2} {'L':>2} | {'EQ':>2} {'Cyc':<10} | Notes")
print("-" * 85)
sys.stdout.flush()

total_exp = 0
total_found = 0
failures = []
eq_scores = []

for ticker, expected in TICKERS.items():
    try:
        info = yf.Ticker(ticker).info
        sector = info.get("sector", "")

        raw = get_raw_statements(ticker)
        if not raw:
            failures.append((ticker, "no raw data"))
            print(f"{ticker:<6} FAILED: no raw data")
            sys.stdout.flush()
            continue
        std = get_standardized_history(ticker, raw_data=raw)
        if not std:
            failures.append((ticker, "no std data"))
            print(f"{ticker:<6} FAILED: no std data")
            sys.stdout.flush()
            continue

        years = std["years"]
        is_t = build_income_table(std, years)
        bs_t = build_balance_table(std, years)
        cf_t = build_cashflow_table(std, years)
        ratios = build_ratios_table(is_t, bs_t, cf_t)
        flags = detect_flags(
            ratios, is_table=is_t, bs_table=bs_t, cf_table=cf_t,
            sector=sector, ticker=ticker,
        )
        eq = compute_earnings_quality(ratios, is_t, cf_t)
        cyc = classify_cyclicality(ratios, sector)
        eq_scores.append((ticker, eq["score"]))

        high = len([f for f in flags if f["severity"] == "high"])
        med = len([f for f in flags if f["severity"] == "medium"])
        low = len([f for f in flags if f["severity"] == "low"])

        missed = []
        for e in expected:
            if "stable" in e.lower():
                continue
            total_exp += 1
            year_in = e.split(":")[0].strip() if ":" in e else ""
            match = False
            if year_in and len(year_in) == 4:
                match = any(year_in in f.get("year", "") for f in flags)
            if not match:
                kws = [w.lower() for w in e.replace(":", " ").split() if len(w) > 3]
                for f in flags:
                    ww = (f.get("what", "") + " " + f.get("why", "")).lower()
                    if any(kw in ww for kw in kws):
                        match = True
                        break
            if match:
                total_found += 1
            else:
                missed.append(e)

        notes = ""
        if missed:
            notes = "MISSED: " + "; ".join(m[:35] for m in missed[:2])

        print(
            f"{ticker:<6} {len(flags):>3} {high:>2} {med:>2} {low:>2} "
            f"| {eq['score']:>2} {cyc['classification']:<10} | {notes}"
        )
        sys.stdout.flush()

    except Exception as e:
        failures.append((ticker, str(e)[:60]))
        print(f"{ticker:<6} ERROR: {str(e)[:60]}")
        sys.stdout.flush()

print(f"\n{'='*85}")
cov = total_found / total_exp * 100 if total_exp > 0 else 0
print(f"COVERAGE: {total_found}/{total_exp} ({cov:.0f}%)")
print(f"Failed: {len(failures)}")
for t, err in failures:
    print(f"  {t}: {err}")
print(f"\nEQ scores:")
eq_sorted = sorted(eq_scores, key=lambda x: x[1])
print(f"  Low:  {', '.join(f'{t}({s})' for t,s in eq_sorted[:5])}")
print(f"  High: {', '.join(f'{t}({s})' for t,s in eq_sorted[-5:])}")
sys.stdout.flush()
