"""Extract everything the Workbench auto-fetches for MSFT.

Mirrors pages/valuation/preparation.py::_load_normal but without Streamlit,
then dumps WACC bundle, peers, historical multiples, dividend data,
flags, and recommendations to JSON.
"""
import sys, os, json, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf
import pandas as pd

from lib.data.yfinance_standardizer import standardize_yfinance
from lib.analysis.historical import (
    build_income_table, build_balance_table,
    build_cashflow_table, build_ratios_table,
)
from lib.analysis.historical_flags import detect_flags, compute_averages
from lib.analysis.company_classifier import classify_company
from lib.data.valuation_data import (
    get_industry_averages, get_valuation_data, get_risk_free_rate,
    get_erp, get_crp, get_industry_beta, get_spread,
    get_suggested_peers, get_peer_data, get_ddm_data, get_historical_multiples,
)
from lib.analysis.recommendations import generate_recommendations

TICKER = "MSFT"
out = {"ticker": TICKER, "errors": {}}

def safe(name, fn):
    try:
        return fn()
    except Exception as e:
        out["errors"][name] = f"{type(e).__name__}: {e}"
        traceback.print_exc()
        return None

def to_jsonable(o):
    if isinstance(o, dict):
        return {str(k): to_jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, set)):
        return [to_jsonable(v) for v in o]
    if isinstance(o, pd.DataFrame):
        return {"__df__": True, "columns": list(map(str, o.columns)),
                "index": list(map(str, o.index)),
                "data": [[None if pd.isna(x) else (float(x) if hasattr(x,'__float__') else str(x)) for x in row] for row in o.values.tolist()]}
    if isinstance(o, pd.Series):
        return {str(k): (None if pd.isna(v) else (float(v) if hasattr(v,'__float__') else str(v))) for k,v in o.items()}
    if hasattr(o, "item"):
        try: return o.item()
        except: pass
    if isinstance(o, (int, float, str, bool)) or o is None:
        if isinstance(o, float) and (o != o):
            return None
        return o
    return str(o)

# ── 1. yfinance raw + info ────────────────────────────────────
print("Fetching yfinance...")
t = yf.Ticker(TICKER)
info = safe("info", lambda: t.info) or {}
out["info"] = {k: info.get(k) for k in [
    "longName","sector","industry","country","currency","financialCurrency",
    "currentPrice","marketCap","sharesOutstanding","impliedSharesOutstanding",
    "beta","trailingPE","forwardPE","priceToBook","dividendRate","dividendYield",
    "trailingEps","forwardEps","payoutRatio","debtToEquity","returnOnEquity",
    "profitMargins","operatingMargins","grossMargins","ebitdaMargins",
    "totalRevenue","ebitda","totalDebt","totalCash",
]}
sector = info.get("sector", "")
sub_industry = info.get("industry", "")

# ── 2. Standardize ────────────────────────────────────────────
print("Standardizing...")
income_stmt = safe("income_stmt", lambda: t.income_stmt)
balance_sheet = safe("balance_sheet", lambda: t.balance_sheet)
cashflow = safe("cashflow", lambda: t.cashflow)
std = safe("standardize", lambda: standardize_yfinance(income_stmt, balance_sheet, cashflow))

if std:
    years = std["years"]
    is_t = build_income_table(std, years)
    bs_t = build_balance_table(std, years)
    cf_t = build_cashflow_table(std, years)
    ratios = build_ratios_table(is_t, bs_t, cf_t)
    company_type = classify_company(TICKER, sector, sub_industry, ratios)
    ind_avg = safe("industry_averages", lambda: get_industry_averages(sub_industry))
    flags = safe("flags", lambda: detect_flags(
        ratios, is_table=is_t, bs_table=bs_t, cf_table=cf_t,
        sector=sector, ticker=TICKER, industry=sub_industry,
        company_type=company_type.get("type", ""), industry_averages=ind_avg,
    )) or []
    avgs = compute_averages(ratios)

    prepared_data = {
        "ticker": TICKER, "company_type": company_type,
        "standardized": std, "original_standardized": std,
        "tables": {"income": is_t, "balance": bs_t, "cashflow": cf_t},
        "ratios": ratios, "flags": flags, "averages": avgs,
        "years": years, "industry_averages": ind_avg,
    }

    out["years"] = list(map(str, years))
    out["company_type"] = company_type
    out["income_table"] = to_jsonable(is_t)
    out["balance_table"] = to_jsonable(bs_t)
    out["cashflow_table"] = to_jsonable(cf_t)
    out["ratios_table"] = to_jsonable(ratios)
    out["averages"] = to_jsonable(avgs)
    out["industry_averages"] = to_jsonable(ind_avg)
    out["flags"] = to_jsonable(flags)
    out["flags_count"] = len(flags) if hasattr(flags, "__len__") else None

    # ── 3. WACC bundle ──────────────────────────────────────
    print("WACC bundle...")
    val_data, status = safe("valuation_data", lambda: get_valuation_data(TICKER)) or (None, "error")
    out["valuation_data_status"] = status
    out["valuation_data"] = to_jsonable(val_data)
    out["risk_free_rate"] = safe("rf", get_risk_free_rate)
    out["erp"] = safe("erp", get_erp)
    out["crp_us"] = safe("crp_us", lambda: get_crp("United States"))
    out["industry_beta"] = safe("industry_beta", lambda: get_industry_beta(sub_industry))
    out["spread_lookup_example"] = safe("spread", lambda: get_spread(8.0, "large"))

    # ── 4. Peers ────────────────────────────────────────────
    print("Peers...")
    suggested = safe("suggested_peers", lambda: get_suggested_peers(TICKER)) or []
    out["suggested_peers"] = suggested
    out["peer_data"] = to_jsonable(safe("peer_data", lambda: get_peer_data(suggested)))

    # ── 5. Historical multiples ─────────────────────────────
    print("Historical multiples...")
    hist = safe("historical_multiples", lambda: get_historical_multiples(TICKER))
    if hist and isinstance(hist, dict):
        out["historical_multiples_summary"] = {
            "source": hist.get("source"),
            "n_quarters": len(hist.get("quarterly", [])) if hist.get("quarterly") is not None else None,
            "summary_stats": to_jsonable(hist.get("summary")),
            "implied_values_keys": list(hist.get("implied_values", {}).keys()) if hist.get("implied_values") else [],
        }
    else:
        out["historical_multiples_summary"] = None

    # ── 6. DDM data ─────────────────────────────────────────
    print("DDM provider...")
    ddm = safe("ddm_data", lambda: get_ddm_data(TICKER))
    out["ddm_data"] = to_jsonable(ddm)

    # ── 7. Recommendations ──────────────────────────────────
    print("Recommendations...")
    recs = safe("recommendations", lambda: generate_recommendations(prepared_data, ddm))
    out["recommendations"] = to_jsonable(recs)

# ── Write ─────────────────────────────────────────────────────
out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "test_results", "msft_extraction.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(to_jsonable(out), f, indent=2, default=str)
print(f"\n✓ Written to {out_path}")
print(f"Errors: {len(out['errors'])}")
for k,v in out["errors"].items():
    print(f"  {k}: {v}")
