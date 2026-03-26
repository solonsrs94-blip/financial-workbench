"""Test flagging system on 100 DCF-suitable companies."""

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

# 100 DCF-suitable companies with known events
TICKERS = {
    # TECH (20)
    "MSFT": ["2015: Nokia write-down", "2022: Activision acquisition"],
    "AAPL": ["Negative equity"],
    "GOOG": ["2017: EU fines"],
    "META": ["2021: Reality Labs", "High SBC"],
    "NVDA": ["2023: Margin compression"],
    "CRM": ["High SBC"],
    "ADBE": ["Stable margins"],
    "ORCL": ["2022: Cerner acquisition"],
    "INTU": ["2022: Mailchimp acquisition"],
    "NOW": ["High SBC"],
    "SNPS": ["Stable"],
    "CDNS": ["Stable"],
    "PANW": ["High SBC"],
    "CRWD": ["High SBC"],
    "DDOG": ["High SBC"],
    "WDAY": ["High SBC"],
    "TTD": ["2022: Ad slowdown"],
    "TEAM": ["High SBC"],
    "ZS": ["High SBC"],
    "FTNT": ["Stable margins"],
    # HEALTHCARE (15)
    "JNJ": ["2023: Kenvue spinoff"],
    "UNH": ["Stable"],
    "LLY": ["2023: GLP-1 boom"],
    "ABBV": ["2023: Humira cliff"],
    "PFE": ["2023: Revenue collapse"],
    "MRK": ["Stable"],
    "TMO": ["2022: COVID testing decline"],
    "ABT": ["Stable"],
    "MDT": ["Stable"],
    "ISRG": ["Stable"],
    "DHR": ["2023: Veralto spinoff"],
    "BSX": ["Stable"],
    "SYK": ["Acquisition growth"],
    "REGN": ["High R&D"],
    "VRTX": ["Stable"],
    # CONSUMER DEFENSIVE (10)
    "KO": ["2017: TCJA"],
    "PEP": ["Stable"],
    "PG": ["Stable"],
    "COST": ["Stable"],
    "WMT": ["Stable"],
    "MO": ["Declining volumes"],
    "CL": ["Stable"],
    "KMB": ["Stable"],
    "MNST": ["High margins"],
    "GIS": ["2018: Blue Buffalo acquisition"],
    # INDUSTRIALS (10)
    "CAT": ["Cyclical"],
    "HON": ["2018: Two spinoffs"],
    "LMT": ["Stable defense"],
    "UNP": ["Stable railroad"],
    "DE": ["Cyclical"],
    "GE": ["2018: Restructuring"],
    "MMM": ["2023: Healthcare spinoff"],
    "RTX": ["2020: Raytheon merger"],
    "EMR": ["Stable"],
    "ITW": ["Stable margins"],
    # CONSUMER CYCLICAL (10)
    "AMZN": ["2022: Rivian write-down"],
    "TSLA": ["2023: Price cuts"],
    "HD": ["Stable"],
    "NKE": ["2023: Inventory issues"],
    "MCD": ["Negative equity"],
    "SBUX": ["Negative equity"],
    "LOW": ["Stable"],
    "TJX": ["Stable"],
    "BKNG": ["2020: COVID collapse"],
    "ORLY": ["Stable"],
    # FINANCIAL SERVICES (10)
    "V": ["2016: Visa Europe"],
    "MA": ["Stable"],
    "AXP": ["2020: COVID impact"],
    "SPGI": ["2022: IHS Markit merger"],
    "ICE": ["Stable"],
    "MCO": ["Stable"],
    "MSCI": ["Stable"],
    "CME": ["Stable"],
    "FIS": ["2023: Worldpay separation"],
    "ADP": ["Stable"],
    # ENERGY (5)
    "XOM": ["2020: Oil crash"],
    "CVX": ["2020: Oil crash"],
    "COP": ["Cyclical"],
    "EOG": ["Cyclical"],
    "SLB": ["Cyclical"],
    # COMMUNICATION (5)
    "DIS": ["2020: Disney+ costs"],
    "NFLX": ["2022: Subscriber loss"],
    "CMCSA": ["2018: Sky acquisition"],
    "T": ["2022: WarnerMedia spinoff"],
    "TMUS": ["2020: Sprint merger"],
    # MATERIALS (5)
    "LIN": ["2018: Praxair merger"],
    "APD": ["Stable"],
    "ECL": ["Stable"],
    "SHW": ["2017: Valspar acquisition"],
    "NEM": ["Cyclical gold"],
}

print(f"Testing {len(TICKERS)} companies...")
print(f"{'Ticker':<6} {'Flg':>3} {'H':>2} {'M':>2} {'L':>2} | {'EQ':>2} {'Cyc':<10} | Notes")
print("-" * 85)

total_exp = 0
total_found = 0
sector_stats = {}
eq_scores = []
failures = []

for ticker, expected in TICKERS.items():
    try:
        info = yf.Ticker(ticker).info
        sector = info.get("sector", "")

        raw = get_raw_statements(ticker)
        if not raw:
            failures.append((ticker, "no raw data"))
            continue
        std = get_standardized_history(ticker, raw_data=raw)
        if not std:
            failures.append((ticker, "no std data"))
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

        eq_scores.append((ticker, eq["score"], sector))

        high = len([f for f in flags if f["severity"] == "high"])
        med = len([f for f in flags if f["severity"] == "medium"])
        low = len([f for f in flags if f["severity"] == "low"])

        # Coverage check
        missed = []
        for e in expected:
            if any(kw in e.lower() for kw in ["stable", "very stable"]):
                continue
            total_exp += 1
            year_in = e.split(":")[0].strip() if ":" in e else ""
            match = False
            if year_in and len(year_in) == 4:
                match = any(year_in in f.get("year", "") for f in flags)
            if not match:
                keywords = [w.lower() for w in e.replace(":", " ").split() if len(w) > 3]
                for f in flags:
                    what_why = (f.get("what", "") + " " + f.get("why", "")).lower()
                    if sum(1 for kw in keywords if kw in what_why) >= 1:
                        match = True
                        break
            if match:
                total_found += 1
            else:
                missed.append(e)

        if sector not in sector_stats:
            sector_stats[sector] = {"n": 0, "flags": 0, "eq": 0, "high": 0}
        sector_stats[sector]["n"] += 1
        sector_stats[sector]["flags"] += len(flags)
        sector_stats[sector]["eq"] += eq["score"]
        sector_stats[sector]["high"] += high

        notes = ""
        if missed:
            notes = "MISSED: " + "; ".join(m[:35] for m in missed[:2])

        print(
            f"{ticker:<6} {len(flags):>3} {high:>2} {med:>2} {low:>2} "
            f"| {eq['score']:>2} {cyc['classification']:<10} | {notes}"
        )

    except Exception as e:
        failures.append((ticker, str(e)[:60]))

# Summary
print(f"\n{'='*85}")
cov_pct = total_found / total_exp * 100 if total_exp > 0 else 0
print(f"COVERAGE: {total_found}/{total_exp} ({cov_pct:.0f}%)")

print(f"\nFailed ({len(failures)}):")
for t, err in failures[:10]:
    print(f"  {t}: {err}")

print(f"\nSector summary:")
print(f"{'Sector':<25} {'N':>3} {'AvgFlg':>7} {'AvgEQ':>6} {'AvgHi':>6}")
for s in sorted(sector_stats.keys()):
    d = sector_stats[s]
    print(
        f"{s:<25} {d['n']:>3} {d['flags']/d['n']:>7.1f} "
        f"{d['eq']/d['n']:>6.1f} {d['high']/d['n']:>6.1f}"
    )

print(f"\nEarnings Quality:")
eq_sorted = sorted(eq_scores, key=lambda x: x[1])
print(f"  Lowest:  {', '.join(f'{t}({s})' for t,s,_ in eq_sorted[:8])}")
print(f"  Highest: {', '.join(f'{t}({s})' for t,s,_ in eq_sorted[-8:])}")
