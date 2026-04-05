"""International flagging test — 60+ non-US companies."""
import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import yfinance as yf
from lib.data.yfinance_standardizer import standardize_yfinance
from lib.analysis.historical import (
    build_income_table, build_balance_table,
    build_cashflow_table, build_ratios_table,
)
from lib.analysis.flags import detect_flags
from lib.analysis.company_classifier import classify_company
from lib.data.valuation_data import get_industry_averages

COMPANIES = {
    # === UK (FTSE 100) ===
    "SHEL": ("Energy", "oil & gas integrated"),            # Shell
    "BP":   ("Energy", "oil & gas integrated"),             # BP
    "AZN":  ("Healthcare", "drug manufacturers - general"), # AstraZeneca
    "HSBA.L": ("Financial Services", "banks - diversified"), # HSBC
    "ULVR.L": ("Consumer Defensive", "household & personal products"), # Unilever
    "GSK":  ("Healthcare", "drug manufacturers - general"), # GSK
    "RIO":  ("Basic Materials", "other industrial metals & mining"), # Rio Tinto
    "BHP":  ("Basic Materials", "other industrial metals & mining"), # BHP
    "LSEG.L": ("Financial Services", "financial data & stock exchanges"), # London Stock Exch
    "DGE.L": ("Consumer Defensive", "beverages - brewers"), # Diageo
    "BA.L": ("Industrials", "aerospace & defense"),         # BAE Systems
    "REL.L": ("Communication Services", "publishing"),      # RELX
    "VOD.L": ("Communication Services", "telecom services"), # Vodafone
    "LLOY.L": ("Financial Services", "banks - regional"),   # Lloyds
    "BARC.L": ("Financial Services", "banks - diversified"), # Barclays
    "NG.L":  ("Utilities", "utilities - regulated gas"),    # National Grid

    # === Europe (Euro STOXX / CAC / DAX) ===
    "ASML": ("Technology", "semiconductor equipment & materials"), # ASML (Netherlands)
    "MC.PA": ("Consumer Cyclical", "luxury goods"),          # LVMH (France)
    "SAP":  ("Technology", "software - application"),        # SAP (Germany)
    "SIE.DE": ("Industrials", "specialty industrial machinery"), # Siemens
    "TTE":  ("Energy", "oil & gas integrated"),              # TotalEnergies
    "SAN.PA": ("Consumer Defensive", "household & personal products"), # Sanofi
    "OR.PA": ("Consumer Defensive", "household & personal products"), # L'Oreal
    "ALV.DE": ("Financial Services", "insurance - diversified"), # Allianz
    "BNP.PA": ("Financial Services", "banks - diversified"), # BNP Paribas
    "NVO":  ("Healthcare", "drug manufacturers - general"),  # Novo Nordisk
    "NOVN.SW": ("Healthcare", "drug manufacturers - general"), # Novartis
    "NESN.SW": ("Consumer Defensive", "packaged foods"),     # Nestle
    "ROG.SW": ("Healthcare", "drug manufacturers - general"), # Roche
    "ENEL.MI": ("Utilities", "utilities - regulated electric"), # Enel (Italy)
    "ISP.MI": ("Financial Services", "banks - diversified"), # Intesa Sanpaolo
    "SU.PA": ("Industrials", "specialty industrial machinery"), # Schneider Electric

    # === Canada (TSX) ===
    "RY":   ("Financial Services", "banks - diversified"),   # Royal Bank of Canada
    "TD":   ("Financial Services", "banks - diversified"),   # TD Bank
    "ENB":  ("Energy", "oil & gas midstream"),               # Enbridge
    "CNQ":  ("Energy", "oil & gas exploration & production"),# Canadian Natural
    "SU":   ("Energy", "oil & gas integrated"),              # Suncor
    "BMO":  ("Financial Services", "banks - diversified"),   # Bank of Montreal
    "BCE":  ("Communication Services", "telecom services"),  # BCE (Bell Canada)
    "CP":   ("Industrials", "railroads"),                    # Canadian Pacific

    # === Japan ===
    "7203.T": ("Consumer Cyclical", "auto manufacturers"),   # Toyota
    "6758.T": ("Technology", "consumer electronics"),         # Sony
    "8306.T": ("Financial Services", "banks - diversified"),  # MUFG
    "9984.T": ("Technology", "internet content & information"), # SoftBank Group
    "6861.T": ("Technology", "scientific & technical instruments"), # Keyence
    "4502.T": ("Healthcare", "drug manufacturers - general"), # Takeda

    # === Australia ===
    "CBA.AX": ("Financial Services", "banks - diversified"), # Commonwealth Bank
    "BHP.AX": ("Basic Materials", "other industrial metals & mining"), # BHP (ASX)
    "CSL.AX": ("Healthcare", "drug manufacturers - specialty & generic"), # CSL
    "WBC.AX": ("Financial Services", "banks - diversified"), # Westpac

    # === Hong Kong / China ===
    "9988.HK": ("Consumer Cyclical", "internet retail"),     # Alibaba
    "0700.HK": ("Communication Services", "internet content & information"), # Tencent
    "1299.HK": ("Financial Services", "insurance - life"),   # AIA Group
    "0005.HK": ("Financial Services", "banks - diversified"), # HSBC HK

    # === Other / Edge cases ===
    "VALE": ("Basic Materials", "other industrial metals & mining"), # Vale (Brazil)
    "BABA": ("Consumer Cyclical", "internet retail"),        # Alibaba (US ADR)
    "TSM":  ("Technology", "semiconductors"),                # TSMC (US ADR)
    "TM":   ("Consumer Cyclical", "auto manufacturers"),     # Toyota (US ADR)
    "UL":   ("Consumer Defensive", "household & personal products"), # Unilever (US ADR)
    "NVS":  ("Healthcare", "drug manufacturers - general"),  # Novartis (US ADR)
    "STLA": ("Consumer Cyclical", "auto manufacturers"),     # Stellantis
    "MBG.DE": ("Consumer Cyclical", "auto manufacturers"),   # Mercedes-Benz
    "RACE": ("Consumer Cyclical", "auto manufacturers"),     # Ferrari
}

results = {}
errors = []
for ticker, (sector, sub_industry) in COMPANIES.items():
    print(f"Processing {ticker}...", end=" ", flush=True)
    try:
        t = yf.Ticker(ticker)
        std = standardize_yfinance(t.income_stmt, t.balance_sheet, t.cashflow)
        if std is None:
            print("NO DATA")
            errors.append(ticker)
            continue
        years = std["years"]
        is_t = build_income_table(std, years)
        bs_t = build_balance_table(std, years)
        cf_t = build_cashflow_table(std, years)
        ratios = build_ratios_table(is_t, bs_t, cf_t)
        ct = classify_company(ticker, sector, sub_industry, ratios)
        ind_avg = get_industry_averages(sub_industry)
        flags = detect_flags(
            ratios, is_table=is_t, bs_table=bs_t, cf_table=cf_t,
            sector=sector, ticker=ticker,
            industry=sub_industry, company_type=ct.get("type", ""),
            industry_averages=ind_avg,
        )
        r = ratios[-1] if ratios else {}
        eq = bs_t[-1].get("total_equity") if bs_t else None
        results[ticker] = {
            "sector": sector,
            "sub_industry": sub_industry,
            "classification": ct.get("type", ""),
            "industry_match": ind_avg.get("industry_name") if ind_avg else None,
            "n_firms": ind_avg.get("n_firms") if ind_avg else None,
            "metrics": {
                "ebit_margin": round(r.get("ebit_margin") or 0, 4) or None,
                "net_margin": round(r.get("net_margin") or 0, 4) or None,
                "debt_ebitda": round(r.get("debt_ebitda") or 0, 2) or None,
                "payout_ratio": round(r.get("payout_ratio") or 0, 4) or None,
                "roe": round(r.get("roe") or 0, 4) or None,
                "equity": round(eq / 1e9, 1) if eq else None,
            },
            "flag_count": len(flags),
            "flags": [
                {"severity": f["severity"], "year": f["year"],
                 "category": f["category"], "what": f["what"]}
                for f in flags
            ],
        }
        print(f"OK — {len(flags)} flags")
    except Exception as e:
        print(f"ERROR: {e}")
        errors.append(ticker)
    time.sleep(0.3)

out_dir = os.path.join(os.path.dirname(__file__), "..", "test_results")
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, "flags_test_intl.json"), "w") as f:
    json.dump(results, f, indent=2)

print(f"\n{'='*90}")
print(f"{'TICKER':<10} {'TYPE':<16} {'INDUSTRY':<35} {'FLAGS':>5}")
print(f"{'='*90}")
for ticker, d in results.items():
    print(f"{ticker:<10} {d['classification']:<16} "
          f"{(d['industry_match'] or '?'):<35} {d['flag_count']:>5}")

print(f"\n{'='*90}")
print("DETAILED FLAGS")
print(f"{'='*90}")
for ticker, d in results.items():
    if not d.get("flags"):
        continue
    m = d["metrics"]
    print(f"\n{ticker} ({d['classification']}, {d.get('industry_match','?')}):")
    parts = []
    if m.get("ebit_margin"): parts.append(f"EBIT={m['ebit_margin']*100:.1f}%")
    if m.get("debt_ebitda"): parts.append(f"D/EBITDA={m['debt_ebitda']:.1f}x")
    if m.get("payout_ratio"): parts.append(f"Pay={m['payout_ratio']*100:.0f}%")
    if m.get("roe"): parts.append(f"ROE={m['roe']*100:.1f}%")
    if m.get("equity") is not None: parts.append(f"Eq=${m['equity']:.1f}B")
    if parts: print(f"  {', '.join(parts)}")
    for f in d["flags"]:
        print(f"  [{f['severity']:6s}] {f['year']} {f['category']:8s} | {f['what']}")

if errors:
    print(f"\nERRORS/SKIPPED: {', '.join(errors)}")
print(f"\nTotal: {len(results)} processed, {sum(d['flag_count'] for d in results.values())} flags")
