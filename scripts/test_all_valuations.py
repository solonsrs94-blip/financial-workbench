"""
Comprehensive valuation test — DCF, DDM, Comps, Historical Multiples, Summary.

Tests 12 companies across US, Europe, and Asia using real market data.
Outputs results to test_results/valuation_test_report.md.

Usage:
    cd Vision
    python scripts/test_all_valuations.py
"""

import sys
import os
import time
import traceback
import warnings
from datetime import datetime

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np

# --- Lib imports ---
from lib.data.valuation_data import (
    get_risk_free_rate,
    get_valuation_data,
    get_erp,
    get_industry_beta,
    get_comps_row,
    get_ddm_data,
    get_historical_multiples,
    get_suggested_peers,
    get_peer_data,
    get_comps_candidate_info,
    get_peer_universe,
    filter_peer_universe,
)
from lib.data.providers import yahoo
from lib.analysis.valuation.wacc import (
    auto_wacc,
    adjusted_beta,
    calc_capm,
    size_premium_bracket,
    cost_of_debt_from_interest,
)
from lib.analysis.valuation.dcf import build_fcf_table, run_dcf, calc_terminal_value
from lib.analysis.valuation.sensitivity import sensitivity_table, exit_sensitivity_table
from lib.analysis.valuation.ddm import gordon_growth, two_stage_ddm, ddm_sensitivity
from models.valuation import WACCResult

# ══════════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════════

DCF_COMPANIES = [
    # US
    {"ticker": "AAPL", "name": "Apple Inc.", "region": "US"},
    {"ticker": "JPM", "name": "JPMorgan Chase", "region": "US", "is_financial": True},
    {"ticker": "XOM", "name": "ExxonMobil", "region": "US"},
    # Europe
    {"ticker": "NESN.SW", "name": "Nestlé", "region": "Europe"},
    {"ticker": "SHEL.L", "name": "Shell plc", "region": "Europe"},
    {"ticker": "SAP.DE", "name": "SAP SE", "region": "Europe"},
    # Asia
    {"ticker": "7203.T", "name": "Toyota Motor", "region": "Asia"},
    {"ticker": "005930.KS", "name": "Samsung Electronics", "region": "Asia"},
    {"ticker": "0700.HK", "name": "Tencent Holdings", "region": "Asia"},
]

DDM_COMPANIES = [
    {"ticker": "JNJ", "name": "Johnson & Johnson", "region": "US"},
    {"ticker": "KO", "name": "Coca-Cola Co", "region": "US"},
    {"ticker": "PG", "name": "Procter & Gamble", "region": "US"},
]

PROJECTION_YEARS = 5
TERMINAL_GROWTH = 0.025
EXIT_MULTIPLE_DEFAULT = 12.0


# ══════════════════════════════════════════════════════════════════════
# Helper functions
# ══════════════════════════════════════════════════════════════════════

def safe_pct(val, digits=1):
    """Format decimal as percentage string."""
    if val is None:
        return "N/A"
    return f"{val*100:.{digits}f}%"


def safe_dollar(val, digits=2):
    """Format as dollar string."""
    if val is None:
        return "N/A"
    return f"${val:,.{digits}f}"


def safe_num(val, digits=2):
    """Format a number."""
    if val is None:
        return "N/A"
    return f"{val:,.{digits}f}"


def safe_large(val):
    """Format large number (billions/millions)."""
    if val is None:
        return "N/A"
    if abs(val) >= 1e12:
        return f"${val/1e12:.2f}T"
    if abs(val) >= 1e9:
        return f"${val/1e9:.2f}B"
    if abs(val) >= 1e6:
        return f"${val/1e6:.1f}M"
    return f"${val:,.0f}"


def upside_str(implied, current):
    """Calculate and format upside/downside."""
    if not implied or not current or current <= 0:
        return "N/A"
    pct = (implied / current - 1) * 100
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.1f}%"


def sanity_check_price(implied, current, label=""):
    """Check if implied price is in a reasonable range."""
    issues = []
    if implied is None or implied <= 0:
        issues.append(f"Implied price is non-positive ({implied})")
        return False, issues
    if current and current > 0:
        ratio = implied / current
        if ratio > 5:
            issues.append(f"Implied price is {ratio:.1f}x current — very high")
        elif ratio < 0.1:
            issues.append(f"Implied price is {ratio:.2f}x current — very low")
    return len(issues) == 0, issues


def avg_historical(margins, key, default=None):
    """Average a historical margin field."""
    vals = [m[key] for m in margins if m.get(key) is not None]
    if not vals:
        return default
    return sum(vals) / len(vals)


# ══════════════════════════════════════════════════════════════════════
# Test modules
# ══════════════════════════════════════════════════════════════════════

class CompanyTestResult:
    """Accumulates test results for one company."""

    def __init__(self, ticker, name, region):
        self.ticker = ticker
        self.name = name
        self.region = region
        self.current_price = None
        self.market_cap = None
        self.currency = "USD"
        self.price_factor = 1.0  # listing→financial currency conversion
        self.data_status = {}
        self.dcf = None
        self.ddm = None
        self.comps = None
        self.historical = None
        self.errors = []
        self.timings = {}

    def add_error(self, module, msg, severity="Warning"):
        self.errors.append({"module": module, "msg": msg, "severity": severity})


def test_data_fetch(company, result: CompanyTestResult):
    """Test 1: Fetch financial data and validate."""
    t0 = time.time()
    ticker = company["ticker"]

    # Market data
    try:
        info = yahoo.fetch_all_info(ticker)
        if info:
            result.current_price = info.get("price", {}).get("price")
            result.market_cap = info.get("price", {}).get("market_cap")
            result.currency = info.get("info", {}).get("currency", "USD")
            result.data_status["market_data"] = "OK"
        else:
            result.data_status["market_data"] = "FAIL"
            result.add_error("Data", f"No market data for {ticker}", "Critical")
    except Exception as e:
        result.data_status["market_data"] = f"ERROR: {e}"
        result.add_error("Data", f"Market data error: {e}", "Critical")

    # Valuation data (IS/BS/CF details)
    try:
        val_data, status = get_valuation_data(ticker)
        if val_data:
            result.data_status["valuation_data"] = f"OK ({status})"
            # Check for NaN/None in key fields
            inc = val_data.get("income_detail", {})
            missing = [k for k in ["revenue", "ebit", "net_income"] if not inc.get(k)]
            if missing:
                result.data_status["valuation_data"] += f" (missing: {', '.join(missing)})"
            # Historical margin years
            hist = val_data.get("historical_margins", [])
            result.data_status["historical_years"] = len(hist)
        else:
            result.data_status["valuation_data"] = f"FAIL ({status})"
            result.add_error("Data", f"No valuation data for {ticker}", "Critical")
    except Exception as e:
        result.data_status["valuation_data"] = f"ERROR: {e}"
        result.add_error("Data", f"Valuation data error: {e}", "Critical")

    result.timings["data_fetch"] = time.time() - t0
    return val_data


def test_dcf(company, result: CompanyTestResult, val_data, rf, erp_val):
    """Test 2: DCF valuation."""
    t0 = time.time()
    ticker = company["ticker"]

    if not val_data:
        result.dcf = {"status": "SKIP", "reason": "No valuation data"}
        result.timings["dcf"] = time.time() - t0
        return

    try:
        inc = val_data.get("income_detail", {})
        bs = val_data.get("balance_sheet", {})
        cf = val_data.get("cash_flow", {})
        wc = val_data.get("working_capital", {})
        hist = val_data.get("historical_margins", [])

        base_revenue = inc.get("revenue")
        if not base_revenue or base_revenue <= 0:
            result.dcf = {"status": "FAIL", "reason": "No revenue data"}
            result.add_error("DCF", "No revenue data", "Critical")
            return

        # Build assumptions from historical data
        avg_ebit_m = avg_historical(hist, "ebit_margin", 0.15)
        avg_capex = avg_historical(hist, "capex_pct", 0.05)
        avg_da = avg_historical(hist, "da_pct", 0.04)
        avg_sbc = avg_historical(hist, "sbc_pct", 0.01)
        avg_cogs = avg_historical(hist, "cogs_pct", 0.60)
        tax_rate = inc.get("effective_tax_rate") or 0.21

        # Revenue growth: start at 5-8%, fade to terminal
        # Use a simple fade from estimated growth to terminal
        start_growth = 0.06  # default moderate growth
        growth_rates = [start_growth - i * (start_growth - TERMINAL_GROWTH) / PROJECTION_YEARS
                        for i in range(PROJECTION_YEARS)]

        ebit_margins = [avg_ebit_m] * PROJECTION_YEARS
        capex_pcts = [avg_capex] * PROJECTION_YEARS
        da_pcts = [avg_da] * PROJECTION_YEARS
        sbc_pcts = [avg_sbc] * PROJECTION_YEARS

        dso = [wc.get("dso") or 45] * PROJECTION_YEARS
        dio = [wc.get("dio") or 30] * PROJECTION_YEARS
        dpo = [wc.get("dpo") or 40] * PROJECTION_YEARS

        # Build FCF table
        fcf_table = build_fcf_table(
            base_revenue=base_revenue,
            n_years=PROJECTION_YEARS,
            growth_rates=growth_rates,
            ebit_margins=ebit_margins,
            tax_rate=tax_rate,
            capex_pcts=capex_pcts,
            da_pcts=da_pcts,
            sbc_pcts=sbc_pcts,
            dso=dso, dio=dio, dpo=dpo,
            base_cogs_pct=avg_cogs if avg_cogs else 0.60,
        )

        # WACC
        beta = val_data.get("beta") or 1.0
        market_cap = val_data.get("market_cap") or result.market_cap or 100e9
        total_debt = bs.get("total_debt", 0)
        interest = inc.get("interest_expense", 0)

        wacc_result = auto_wacc(
            rf=rf,
            raw_beta=beta,
            market_cap=market_cap,
            total_debt=total_debt,
            interest_expense=interest,
            tax_rate=tax_rate,
            erp=erp_val or 0.055,
        )

        # Run DCF
        net_debt = bs.get("net_debt", 0)
        shares = val_data.get("shares") or 1e9
        minority = bs.get("minority_interest", 0)
        preferred = bs.get("preferred_equity", 0)

        dcf_result = run_dcf(
            fcf_table=fcf_table,
            wacc_result=wacc_result,
            terminal_growth=TERMINAL_GROWTH,
            terminal_method="gordon",
            exit_multiple=EXIT_MULTIPLE_DEFAULT,
            net_debt=net_debt,
            shares=shares,
            current_price=result.current_price or 0,
            minority_interest=minority,
            preferred_equity=preferred,
        )

        # Currency: convert implied price to listing currency
        pf = result.price_factor

        # Sensitivity
        try:
            sens_g = sensitivity_table(
                fcf_table, wacc_result, TERMINAL_GROWTH, "gordon", None,
                net_debt, shares, result.current_price or 0, minority, preferred,
            )
            if pf != 1.0:
                sens_g = sens_g / pf
            valid_s = sens_g.values.flatten()
            valid_s = [float(v) for v in valid_s if not np.isnan(v) and v > 0]
            sens_min = min(valid_s) if valid_s else None
            sens_max = max(valid_s) if valid_s else None
        except Exception:
            sens_min, sens_max = None, None
        implied_listing = dcf_result.implied_price / pf if pf != 1.0 else dcf_result.implied_price

        # Sanity checks
        ok, issues = sanity_check_price(implied_listing, result.current_price, "DCF")
        wacc_ok = 0.03 <= wacc_result.wacc <= 0.20
        if not wacc_ok:
            issues.append(f"WACC {safe_pct(wacc_result.wacc)} outside 3-20% range")

        result.dcf = {
            "status": "OK",
            "implied_price": implied_listing,
            "ev": dcf_result.enterprise_value,
            "wacc": wacc_result.wacc,
            "ke": wacc_result.cost_of_equity,
            "beta": wacc_result.beta,
            "terminal_growth": TERMINAL_GROWTH,
            "tv_pct": dcf_result.tv_pct_of_ev,
            "warnings": dcf_result.warnings,
            "sanity_ok": ok and wacc_ok,
            "sanity_issues": issues,
            "assumptions": {
                "growth_rates": growth_rates,
                "ebit_margin": avg_ebit_m,
                "tax_rate": tax_rate,
                "capex_pct": avg_capex,
                "da_pct": avg_da,
            },
            "sensitivity_min": sens_min,
            "sensitivity_max": sens_max,
        }

    except Exception as e:
        result.dcf = {"status": "ERROR", "reason": str(e)}
        result.add_error("DCF", f"Exception: {e}", "Critical")
        traceback.print_exc()

    result.timings["dcf"] = time.time() - t0


def test_ddm(company, result: CompanyTestResult, rf, erp_val):
    """Test 3: DDM valuation."""
    t0 = time.time()
    ticker = company["ticker"]

    try:
        ddm_data = get_ddm_data(ticker)
        if not ddm_data or not ddm_data.get("has_dividend"):
            result.ddm = {"status": "SKIP", "reason": "No dividend data"}
            result.timings["ddm"] = time.time() - t0
            return

        d0 = ddm_data.get("current_dps", 0)
        if not d0 or d0 <= 0:
            result.ddm = {"status": "SKIP", "reason": f"DPS is {d0}"}
            result.timings["ddm"] = time.time() - t0
            return

        # Ke via CAPM
        info = yahoo.fetch_all_info(ticker)
        beta_raw = info.get("price", {}).get("beta", 1.0) if info else 1.0
        beta = adjusted_beta(beta_raw) if beta_raw and beta_raw > 0 else 1.0
        market_cap = info.get("price", {}).get("market_cap", 50e9) if info else 50e9
        sp, _ = size_premium_bracket(market_cap)
        ke = calc_capm(rf, beta, erp_val or 0.055, sp)

        # Growth assumptions from historical CAGR
        cagr = ddm_data.get("dps_cagr", {})
        g_hist = cagr.get("5y") or cagr.get("3y") or cagr.get("10y") or 0.04
        # Cap growth at ke - 1% for Gordon to work
        g_gordon = min(g_hist, ke - 0.01, 0.06)
        g_gordon = max(g_gordon, 0.01)

        # Gordon Growth
        gg = gordon_growth(d0, ke, g_gordon)

        # 2-Stage DDM
        g1 = min(g_hist, 0.08)  # stage 1: historical but capped
        g2 = min(g_gordon, 0.03)  # terminal: lower
        ts = two_stage_ddm(d0, ke, g1, g2, n=5)

        # Sensitivity (Gordon) — computed before ddm_pf is known,
        # so we convert after the fact below.
        try:
            sens = ddm_sensitivity(d0, ke, g_gordon, model="gordon")
        except Exception:
            sens = None
        try:
            sens2 = ddm_sensitivity(d0, ke, g2, model="two_stage", n=5, g1=g1)
        except Exception:
            sens2 = None

        # Currency: convert DDM implied prices to listing currency
        ddm_pf = result.price_factor

        gg_price_raw = gg.get("implied_price", 0)
        ts_price_raw = ts.get("implied_price", 0)
        gg_price = gg_price_raw / ddm_pf if ddm_pf != 1.0 else gg_price_raw
        ts_price = ts_price_raw / ddm_pf if ddm_pf != 1.0 else ts_price_raw

        # Extract sensitivity ranges (converted to listing currency, capped at 100x)
        ddm_sens_min = ddm_sens_max = ts_sens_min = ts_sens_max = None
        cap = (result.current_price or 1) * 100
        for s_df, prefix in [(sens, "gordon"), (sens2, "two_stage")]:
            if s_df is not None:
                if ddm_pf != 1.0:
                    s_df = s_df / ddm_pf
                sv = s_df.values.flatten()
                sv = [float(v) for v in sv if not np.isnan(v) and 0 < v < cap]
                if sv:
                    if prefix == "gordon":
                        ddm_sens_min, ddm_sens_max = min(sv), max(sv)
                    else:
                        ts_sens_min, ts_sens_max = min(sv), max(sv)

        # Sanity
        ok_g, issues_g = sanity_check_price(gg_price, result.current_price, "Gordon")
        ok_t, issues_t = sanity_check_price(ts_price, result.current_price, "2-Stage")

        result.ddm = {
            "status": "OK",
            "d0": d0,
            "ke": ke,
            "g_gordon": g_gordon,
            "g1": g1,
            "g2": g2,
            "gordon_price": gg_price,
            "two_stage_price": ts_price,
            "years_paying": ddm_data.get("years_paying"),
            "years_increasing": ddm_data.get("years_increasing"),
            "dps_cagr": cagr,
            "sanity_ok": ok_g and ok_t,
            "sanity_issues": issues_g + issues_t,
            "sensitivity_min": ddm_sens_min,
            "sensitivity_max": ddm_sens_max,
            "ts_sensitivity_min": ts_sens_min,
            "ts_sensitivity_max": ts_sens_max,
            "ddm_data": ddm_data,
        }

    except Exception as e:
        result.ddm = {"status": "ERROR", "reason": str(e)}
        result.add_error("DDM", f"Exception: {e}", "Critical")
        traceback.print_exc()

    result.timings["ddm"] = time.time() - t0


def test_comps(company, result: CompanyTestResult):
    """Test 4: Comparable companies analysis."""
    t0 = time.time()
    ticker = company["ticker"]
    is_financial = company.get("is_financial", False)

    try:
        # Get target data
        target_row = get_comps_row(ticker)
        if not target_row:
            result.comps = {"status": "FAIL", "reason": "No comps data for target"}
            result.add_error("Comps", "No comps row for target", "Warning")
            result.timings["comps"] = time.time() - t0
            return

        # Get peers — prefer GICS-filtered universe, fallback to Yahoo recs
        target_info = get_comps_candidate_info(ticker)
        peers = []
        peer_source = "yahoo"
        if target_info:
            industry = target_info.get("industry", "")
            mcap = target_info.get("market_cap", 0)
            universe = get_peer_universe()
            if universe and industry:
                peers = filter_peer_universe(universe, ticker, industry, mcap)
                peer_source = "GICS"
        if not peers:
            peers = get_suggested_peers(ticker, max_peers=6)
            peer_source = "yahoo"
        if not peers:
            result.comps = {"status": "FAIL", "reason": "No peers found"}
            result.add_error("Comps", "No peers found", "Warning")
            result.timings["comps"] = time.time() - t0
            return

        # Fetch comps data for each peer
        peer_rows = []
        for p in peers[:6]:
            try:
                row = get_comps_row(p)
                if row:
                    peer_rows.append(row)
            except Exception:
                pass

        if not peer_rows:
            result.comps = {"status": "FAIL", "reason": "No peer data fetched"}
            result.add_error("Comps", "No peer data fetched", "Warning")
            result.timings["comps"] = time.time() - t0
            return

        # Calculate median multiples
        if is_financial:
            mult_keys = ["trailing_pe", "price_to_book", "dividend_yield"]
        else:
            mult_keys = ["trailing_pe", "ev_ebitda", "ev_revenue"]

        medians = {}
        implied_prices = {}
        for key in mult_keys:
            vals = [r.get(key) for r in peer_rows
                   if r.get(key) is not None and isinstance(r[key], (int, float)) and r[key] > 0]
            if vals:
                med = float(np.median(vals))
                medians[key] = med

                # Implied value
                if key == "trailing_pe":
                    target_eps = target_row.get("eps")
                    if target_eps and target_eps > 0:
                        implied_prices[key] = med * target_eps
                elif key == "ev_ebitda":
                    target_ebitda = target_row.get("ebitda")
                    net_debt = (target_row.get("total_debt", 0) or 0) - (target_row.get("cash", 0) or 0)
                    shares = target_row.get("shares_outstanding", 1)
                    if target_ebitda and target_ebitda > 0 and shares:
                        impl_ev = med * target_ebitda
                        impl_eq = impl_ev - net_debt
                        implied_prices[key] = impl_eq / shares
                elif key == "ev_revenue":
                    target_rev = target_row.get("revenue")
                    net_debt = (target_row.get("total_debt", 0) or 0) - (target_row.get("cash", 0) or 0)
                    shares = target_row.get("shares_outstanding", 1)
                    if target_rev and target_rev > 0 and shares:
                        impl_ev = med * target_rev
                        impl_eq = impl_ev - net_debt
                        implied_prices[key] = impl_eq / shares
                elif key == "price_to_book":
                    bvps = target_row.get("book_value_ps")
                    if bvps and bvps > 0:
                        implied_prices[key] = med * bvps

        # Currency: convert comps implied prices to listing currency
        comps_pf = result.price_factor
        if comps_pf != 1.0:
            implied_prices = {k: v / comps_pf for k, v in implied_prices.items()}

        # Sanity
        all_ok = True
        all_issues = []
        for k, v in implied_prices.items():
            ok, iss = sanity_check_price(v, result.current_price, f"Comps {k}")
            if not ok:
                all_ok = False
            all_issues.extend(iss)

        result.comps = {
            "status": "OK",
            "peers": [r.get("ticker", "?") for r in peer_rows],
            "peer_source": peer_source,
            "medians": medians,
            "implied_prices": implied_prices,
            "n_peers": len(peer_rows),
            "is_financial": is_financial,
            "sanity_ok": all_ok,
            "sanity_issues": all_issues,
        }

    except Exception as e:
        result.comps = {"status": "ERROR", "reason": str(e)}
        result.add_error("Comps", f"Exception: {e}", "Critical")
        traceback.print_exc()

    result.timings["comps"] = time.time() - t0


def test_historical_multiples(company, result: CompanyTestResult):
    """Test 5: Historical multiples analysis."""
    t0 = time.time()
    ticker = company["ticker"]
    is_financial = company.get("is_financial", False)

    try:
        data = get_historical_multiples(ticker, period_years=3, is_financial=is_financial)

        if not data or not data.get("summary"):
            result.historical = {"status": "FAIL", "reason": "No historical multiples data"}
            result.add_error("Historical", "No data returned", "Warning")
            result.timings["historical"] = time.time() - t0
            return

        summary = data["summary"]
        implied = data.get("implied_values", {})
        daily = data.get("daily_multiples")

        if is_financial:
            mult_keys = ["pe", "pb", "ptbv"]
        else:
            mult_keys = ["pe", "ev_ebitda", "ev_revenue"]

        hist_results = {}
        for key in mult_keys:
            s = summary.get(key, {})
            iv = implied.get(key, {})
            if s:
                hist_results[key] = {
                    "current": s.get("current"),
                    "mean": s.get("mean"),
                    "median": s.get("median"),
                    "std": s.get("std"),
                    "p10": s.get("p10"),
                    "p90": s.get("p90"),
                    "percentile": s.get("percentile"),
                    "implied_median": iv.get("at_median"),
                    "implied_mean": iv.get("at_mean"),
                }

        # Sanity
        all_ok = True
        all_issues = []
        for k, v in hist_results.items():
            imp = v.get("implied_median")
            if imp:
                ok, iss = sanity_check_price(imp, result.current_price, f"Hist {k}")
                if not ok:
                    all_ok = False
                all_issues.extend(iss)

        result.historical = {
            "status": "OK",
            "data_source": data.get("data_source", "unknown"),
            "data_start": str(data.get("data_start", "?")),
            "data_end": str(data.get("data_end", "?")),
            "n_days": len(daily) if daily is not None else 0,
            "multiples": hist_results,
            "sanity_ok": all_ok,
            "sanity_issues": all_issues,
        }

    except Exception as e:
        result.historical = {"status": "ERROR", "reason": str(e)}
        result.add_error("Historical", f"Exception: {e}", "Critical")
        traceback.print_exc()

    result.timings["historical"] = time.time() - t0


def build_summary(result: CompanyTestResult):
    """Test 6: Build summary football field from all models."""
    models = []

    if result.dcf and result.dcf.get("status") == "OK":
        models.append({
            "model": "DCF",
            "base": result.dcf["implied_price"],
            "low": result.dcf.get("sensitivity_min"),
            "high": result.dcf.get("sensitivity_max"),
        })

    if result.ddm and result.ddm.get("status") == "OK":
        gg = result.ddm.get("gordon_price", 0)
        ts = result.ddm.get("two_stage_price", 0)
        models.append({
            "model": "DDM (Gordon)",
            "base": gg,
            "low": result.ddm.get("sensitivity_min"),
            "high": result.ddm.get("sensitivity_max"),
        })
        if ts > 0:
            models.append({
                "model": "DDM (2-Stage)",
                "base": ts,
                "low": result.ddm.get("ts_sensitivity_min"),
                "high": result.ddm.get("ts_sensitivity_max"),
            })

    if result.comps and result.comps.get("status") == "OK":
        prices = list(result.comps.get("implied_prices", {}).values())
        if prices:
            models.append({
                "model": "Comps",
                "base": float(np.median(prices)),
                "low": min(prices),
                "high": max(prices),
            })

    if result.historical and result.historical.get("status") == "OK":
        hist_prices = []
        for k, v in result.historical.get("multiples", {}).items():
            if v.get("implied_median"):
                hist_prices.append(v["implied_median"])
        if hist_prices:
            models.append({
                "model": "Historical",
                "base": float(np.median(hist_prices)),
                "low": min(hist_prices),
                "high": max(hist_prices),
            })

    if not models:
        return {"status": "SKIP", "reason": "No models completed"}

    all_bases = [m["base"] for m in models if m["base"]]
    all_lows = [m["low"] for m in models if m.get("low")]
    all_highs = [m["high"] for m in models if m.get("high")]

    return {
        "status": "OK",
        "models": models,
        "consensus_base": float(np.median(all_bases)) if all_bases else None,
        "range_low": min(all_lows) if all_lows else (min(all_bases) if all_bases else None),
        "range_high": max(all_highs) if all_highs else (max(all_bases) if all_bases else None),
    }


# ══════════════════════════════════════════════════════════════════════
# Report generation
# ══════════════════════════════════════════════════════════════════════

def generate_report(results: list[CompanyTestResult], rf, erp_val, total_time):
    """Generate markdown report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    n_companies = len(results)
    n_errors = sum(len(r.errors) for r in results)
    n_critical = sum(1 for r in results for e in r.errors if e["severity"] == "Critical")

    # Count modules tested
    modules_tested = set()
    for r in results:
        if r.dcf and r.dcf.get("status") == "OK":
            modules_tested.add("DCF")
        if r.ddm and r.ddm.get("status") == "OK":
            modules_tested.add("DDM")
        if r.comps and r.comps.get("status") == "OK":
            modules_tested.add("Comps")
        if r.historical and r.historical.get("status") == "OK":
            modules_tested.add("Historical")

    overall = "PASS" if n_critical == 0 else "FAIL" if n_critical > 3 else "PARTIAL"

    lines = []
    lines.append("# Financial Workbench — Valuation Test Report")
    lines.append(f"**Date:** {now}")
    lines.append(f"**Run by:** Claude Code automated test")
    lines.append(f"**Rf:** {safe_pct(rf)} (US 10Y) | **ERP:** {safe_pct(erp_val)}")
    lines.append(f"**Total runtime:** {total_time:.0f}s")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Companies tested: **{n_companies}**")
    lines.append(f"- Modules with successful results: **{', '.join(sorted(modules_tested)) or 'None'}**")
    lines.append(f"- Total errors/warnings: **{n_errors}** ({n_critical} critical)")
    lines.append(f"- Overall status: **{overall}**")
    lines.append("")

    # Quick overview table
    lines.append("## Quick Overview")
    lines.append("")
    lines.append("| Ticker | Price | DCF | DDM | Comps | Historical |")
    lines.append("|--------|-------|-----|-----|-------|------------|")
    for r in results:
        dcf_s = _status_emoji(r.dcf)
        ddm_s = _status_emoji(r.ddm)
        comp_s = _status_emoji(r.comps)
        hist_s = _status_emoji(r.historical)
        price = safe_dollar(r.current_price) if r.currency == "USD" else f"{r.current_price:,.2f} {r.currency}" if r.current_price else "N/A"
        lines.append(f"| {r.ticker} | {price} | {dcf_s} | {ddm_s} | {comp_s} | {hist_s} |")
    lines.append("")

    # Detailed results per company
    lines.append("---")
    lines.append("")
    lines.append("## Detailed Results")
    lines.append("")

    for r in results:
        lines.append(f"### {r.ticker} — {r.name}")
        price_str = safe_dollar(r.current_price) if r.currency == "USD" else f"{r.current_price:,.2f} {r.currency}" if r.current_price else "N/A"
        lines.append(f"**Market Price:** {price_str} | **Market Cap:** {safe_large(r.market_cap)} | **Currency:** {r.currency}")
        lines.append("")

        # Data fetch
        lines.append("#### Data Fetch")
        for k, v in r.data_status.items():
            emoji = "OK" if "OK" in str(v) else "FAIL"
            lines.append(f"- {k}: {emoji} — {v}")
        rf_info = r.data_status.get("rf", "N/A")
        lines.append(f"- Rf: {rf_info}")
        lines.append(f"- *Fetch time: {r.timings.get('data_fetch', 0):.1f}s*")
        lines.append("")

        # DCF
        if r.dcf:
            lines.append("#### DCF")
            if r.dcf.get("status") == "OK":
                d = r.dcf
                a = d.get("assumptions", {})
                gr = a.get("growth_rates", [])
                gr_str = f"{safe_pct(gr[0])} -> {safe_pct(gr[-1])}" if gr else "N/A"
                lines.append(f"- **Assumptions:** Rev growth: {gr_str}, EBIT margin: {safe_pct(a.get('ebit_margin'))}, Tax: {safe_pct(a.get('tax_rate'))}")
                lines.append(f"- **WACC:** {safe_pct(d['wacc'])} (Ke: {safe_pct(d['ke'])}, Beta: {safe_num(d['beta'])})")
                lines.append(f"- **Terminal growth:** {safe_pct(d['terminal_growth'])} | TV as % of EV: {safe_pct(d['tv_pct'])}")
                lines.append(f"- **Enterprise Value:** {safe_large(d['ev'])}")
                lines.append(f"- **Implied share price:** {safe_dollar(d['implied_price'])}")
                lines.append(f"- **Upside/Downside:** {upside_str(d['implied_price'], r.current_price)}")
                if d.get("sensitivity_min") is not None:
                    lines.append(f"- **Sensitivity range:** {safe_dollar(d['sensitivity_min'])} — {safe_dollar(d['sensitivity_max'])}")
                if d.get("warnings"):
                    for w in d["warnings"]:
                        lines.append(f"- Warning: {w}")
                sanity = "PASS" if d.get("sanity_ok") else "ISSUES"
                lines.append(f"- **Sanity check:** {sanity}")
                for iss in d.get("sanity_issues", []):
                    lines.append(f"  - {iss}")
            elif r.dcf.get("status") == "SKIP":
                lines.append(f"- *Skipped: {r.dcf.get('reason')}*")
            else:
                lines.append(f"- **ERROR:** {r.dcf.get('reason')}")
            lines.append(f"- *Time: {r.timings.get('dcf', 0):.1f}s*")
            lines.append("")

        # DDM
        if r.ddm:
            lines.append("#### DDM")
            if r.ddm.get("status") == "OK":
                d = r.ddm
                lines.append(f"- **Current DPS:** {safe_dollar(d['d0'])} | Ke: {safe_pct(d['ke'])}")
                lines.append(f"- **Dividend history:** {d.get('years_paying', '?')} years paying, {d.get('years_increasing', '?')} years increasing")
                cagr = d.get("dps_cagr", {})
                lines.append(f"- **DPS CAGR:** 3Y={safe_pct(cagr.get('3y'))}, 5Y={safe_pct(cagr.get('5y'))}, 10Y={safe_pct(cagr.get('10y'))}")
                lines.append(f"- **Gordon Growth:** g={safe_pct(d['g_gordon'])} → **{safe_dollar(d['gordon_price'])}** ({upside_str(d['gordon_price'], r.current_price)})")
                lines.append(f"- **2-Stage DDM:** g1={safe_pct(d['g1'])}, g2={safe_pct(d['g2'])} → **{safe_dollar(d['two_stage_price'])}** ({upside_str(d['two_stage_price'], r.current_price)})")
                if d.get("sensitivity_min") is not None:
                    lines.append(f"- **Gordon sensitivity:** {safe_dollar(d['sensitivity_min'])} — {safe_dollar(d['sensitivity_max'])}")
                if d.get("ts_sensitivity_min") is not None:
                    lines.append(f"- **2-Stage sensitivity:** {safe_dollar(d['ts_sensitivity_min'])} — {safe_dollar(d['ts_sensitivity_max'])}")
                sanity = "PASS" if d.get("sanity_ok") else "ISSUES"
                lines.append(f"- **Sanity check:** {sanity}")
                for iss in d.get("sanity_issues", []):
                    lines.append(f"  - {iss}")
            elif r.ddm.get("status") == "SKIP":
                lines.append(f"- *Skipped: {r.ddm.get('reason')}*")
            else:
                lines.append(f"- **ERROR:** {r.ddm.get('reason')}")
            lines.append(f"- *Time: {r.timings.get('ddm', 0):.1f}s*")
            lines.append("")

        # Comps
        if r.comps:
            lines.append("#### Comps")
            if r.comps.get("status") == "OK":
                d = r.comps
                src = d.get("peer_source", "yahoo")
                lines.append(f"- **Peers ({d['n_peers']}, {src}):** {', '.join(d['peers'])}")
                for k, v in d.get("medians", {}).items():
                    impl = d.get("implied_prices", {}).get(k)
                    impl_str = safe_dollar(impl) if impl else "N/A"
                    up_str = upside_str(impl, r.current_price) if impl else ""
                    lines.append(f"- **Median {k}:** {safe_num(v)}x → Implied: {impl_str} ({up_str})")
                sanity = "PASS" if d.get("sanity_ok") else "ISSUES"
                lines.append(f"- **Sanity check:** {sanity}")
                for iss in d.get("sanity_issues", []):
                    lines.append(f"  - {iss}")
            elif r.comps.get("status") == "FAIL":
                lines.append(f"- *Failed: {r.comps.get('reason')}*")
            else:
                lines.append(f"- **ERROR:** {r.comps.get('reason')}")
            lines.append(f"- *Time: {r.timings.get('comps', 0):.1f}s*")
            lines.append("")

        # Historical
        if r.historical:
            lines.append("#### Historical Multiples")
            if r.historical.get("status") == "OK":
                d = r.historical
                lines.append(f"- **Data source:** {d['data_source']} | Period: {d['data_start']} to {d['data_end']} ({d['n_days']} trading days)")
                for k, v in d.get("multiples", {}).items():
                    cur = safe_num(v.get("current"))
                    med = safe_num(v.get("median"))
                    pctl = safe_num(v.get("percentile"), 0) if v.get("percentile") is not None else "N/A"
                    impl = safe_dollar(v.get("implied_median"))
                    lines.append(f"- **{k}:** Current={cur}, Median={med}, Percentile={pctl}th → Implied: {impl}")
                sanity = "PASS" if d.get("sanity_ok") else "ISSUES"
                lines.append(f"- **Sanity check:** {sanity}")
                for iss in d.get("sanity_issues", []):
                    lines.append(f"  - {iss}")
            elif r.historical.get("status") == "FAIL":
                lines.append(f"- *Failed: {r.historical.get('reason')}*")
            else:
                lines.append(f"- **ERROR:** {r.historical.get('reason')}")
            lines.append(f"- *Time: {r.timings.get('historical', 0):.1f}s*")
            lines.append("")

        # Summary / Football Field
        summary = build_summary(r)
        lines.append("#### Summary / Football Field")
        if summary.get("status") == "OK":
            for m in summary["models"]:
                low_str = safe_dollar(m.get("low"))
                high_str = safe_dollar(m.get("high"))
                lines.append(f"- **{m['model']}:** {safe_dollar(m['base'])} (range: {low_str} — {high_str})")
            lines.append(f"- **Consensus (median):** {safe_dollar(summary.get('consensus_base'))}")
            lines.append(f"- **Full range:** {safe_dollar(summary.get('range_low'))} — {safe_dollar(summary.get('range_high'))}")
            if summary.get("consensus_base") and r.current_price:
                lines.append(f"- **Overall upside:** {upside_str(summary['consensus_base'], r.current_price)}")
        else:
            lines.append(f"- *{summary.get('reason', 'No data')}*")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Error table
    lines.append("## Errors and Issues")
    lines.append("")
    all_errors = []
    for r in results:
        for e in r.errors:
            all_errors.append((r.ticker, e["module"], e["msg"], e["severity"]))

    if all_errors:
        lines.append("| # | Ticker | Module | Issue | Severity |")
        lines.append("|---|--------|--------|-------|----------|")
        for i, (tick, mod, msg, sev) in enumerate(all_errors, 1):
            lines.append(f"| {i} | {tick} | {mod} | {msg} | {sev} |")
    else:
        lines.append("No errors detected.")
    lines.append("")

    # Timing summary
    lines.append("## Performance")
    lines.append("")
    lines.append("| Ticker | Data | DCF | DDM | Comps | Historical | Total |")
    lines.append("|--------|------|-----|-----|-------|------------|-------|")
    for r in results:
        t_data = r.timings.get("data_fetch", 0)
        t_dcf = r.timings.get("dcf", 0)
        t_ddm = r.timings.get("ddm", 0)
        t_comps = r.timings.get("comps", 0)
        t_hist = r.timings.get("historical", 0)
        t_total = t_data + t_dcf + t_ddm + t_comps + t_hist
        lines.append(f"| {r.ticker} | {t_data:.1f}s | {t_dcf:.1f}s | {t_ddm:.1f}s | {t_comps:.1f}s | {t_hist:.1f}s | {t_total:.1f}s |")
    lines.append("")

    # Conclusions
    lines.append("## Conclusions")
    lines.append("")

    # Auto-generate conclusions
    working = []
    broken = []
    for r in results:
        crits = [e for e in r.errors if e["severity"] == "Critical"]
        if crits:
            broken.append(f"{r.ticker}: {crits[0]['msg']}")
        else:
            working.append(r.ticker)

    if working:
        lines.append(f"**Working well:** {', '.join(working)}")
    if broken:
        lines.append(f"**Issues found:**")
        for b in broken:
            lines.append(f"- {b}")

    # Changes since v1
    lines.append("")
    lines.append("## Changes Since v2")
    lines.append("")
    lines.append("1. **Rf reverted to ^TNX:** All companies use US 10Y Treasury. Country risk via CRP (Damodaran).")
    lines.append("2. **DCF/DDM/Comps currency conversion:** Implied prices now converted to listing currency via price_factor (fixes SHEL.L showing USD)")
    lines.append("3. **100x sensitivity cap:** Gordon/2-Stage sensitivity values >100x current price excluded as asymptotic")
    lines.append("")

    lines.append("---")
    lines.append(f"*Report generated {now} by test_all_valuations.py (v3)*")

    return "\n".join(lines)


def _status_emoji(module_result):
    """Status indicator for overview table."""
    if not module_result:
        return "—"
    s = module_result.get("status", "?")
    if s == "OK":
        sanity = module_result.get("sanity_ok", True)
        return "PASS" if sanity else "WARN"
    if s == "SKIP":
        return "SKIP"
    if s == "FAIL":
        return "FAIL"
    return "ERR"


# ══════════════════════════════════════════════════════════════════════
# Main runner
# ══════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("Financial Workbench — Comprehensive Valuation Test")
    print("=" * 60)
    total_start = time.time()

    # Global market data
    print("\n[1/2] Fetching global market data (Rf, ERP)...")
    rf = get_risk_free_rate()
    erp_val = get_erp()
    print(f"  Risk-free rate: {safe_pct(rf)} (US 10Y Treasury)")
    print(f"  ERP (Damodaran): {safe_pct(erp_val)}")

    all_companies = DCF_COMPANIES + DDM_COMPANIES
    results = []

    print(f"\n[2/2] Testing {len(all_companies)} companies...\n")

    for idx, company in enumerate(all_companies, 1):
        ticker = company["ticker"]
        name = company["name"]
        is_dcf = company in DCF_COMPANIES
        is_ddm = company in DDM_COMPANIES
        is_financial = company.get("is_financial", False)

        print(f"  [{idx}/{len(all_companies)}] {ticker} ({name})...")
        result = CompanyTestResult(ticker, name, company["region"])

        # Always: data fetch
        val_data = test_data_fetch(company, result)
        print(f"    Data: {result.data_status.get('valuation_data', '?')}")

        # Rf is always ^TNX (US 10Y). CRP adds country risk.
        result.data_status["rf"] = f"{safe_pct(rf)} (US 10Y)"

        # Compute price_factor for currency conversion
        if val_data:
            val_cur = val_data.get("currency", "USD")
            fin_cur = val_data.get("financial_currency", val_cur)
            if val_cur != fin_cur and result.current_price and result.market_cap:
                shares_pf = val_data.get("shares")
                if shares_pf and shares_pf > 0:
                    result.price_factor = result.market_cap / (result.current_price * shares_pf)

        # DCF (for DCF companies)
        if is_dcf and not is_financial:
            test_dcf(company, result, val_data, rf, erp_val)
            if result.dcf and result.dcf.get("status") == "OK":
                print(f"    DCF: implied={safe_dollar(result.dcf['implied_price'])}, WACC={safe_pct(result.dcf['wacc'])}")
            else:
                print(f"    DCF: {result.dcf.get('status', '?')} — {result.dcf.get('reason', '')}")
        elif is_financial:
            result.dcf = {"status": "SKIP", "reason": "Financial company — DCF not standard"}
            print(f"    DCF: skipped (financial)")

        # DDM (for DDM companies + any dividend payer)
        if is_ddm:
            test_ddm(company, result, rf, erp_val)
            if result.ddm and result.ddm.get("status") == "OK":
                print(f"    DDM: Gordon={safe_dollar(result.ddm['gordon_price'])}, 2-Stage={safe_dollar(result.ddm['two_stage_price'])}")
            else:
                print(f"    DDM: {result.ddm.get('status', '?')} — {result.ddm.get('reason', '')}")
        else:
            # Try DDM anyway if company pays dividends
            test_ddm(company, result, rf, erp_val)
            if result.ddm and result.ddm.get("status") == "OK":
                print(f"    DDM: Gordon={safe_dollar(result.ddm['gordon_price'])} (bonus)")
            elif result.ddm:
                s = result.ddm.get("status", "?")
                if s != "SKIP":
                    print(f"    DDM: {s}")

        # Comps (all companies)
        test_comps(company, result)
        if result.comps and result.comps.get("status") == "OK":
            print(f"    Comps: {result.comps['n_peers']} peers, medians={result.comps.get('medians', {})}")
        else:
            print(f"    Comps: {result.comps.get('status', '?')} — {result.comps.get('reason', '')}")

        # Historical (all companies)
        test_historical_multiples(company, result)
        if result.historical and result.historical.get("status") == "OK":
            print(f"    Historical: {result.historical['data_source']}, {result.historical['n_days']} days")
        else:
            print(f"    Historical: {result.historical.get('status', '?')} — {result.historical.get('reason', '')}")

        results.append(result)
        print()

    total_time = time.time() - total_start

    # Generate report
    print("Generating report...")
    report = generate_report(results, rf, erp_val, total_time)

    report_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "test_results", "valuation_test_report_v3.md",
    )
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nReport written to: {report_path}")
    print(f"Total time: {total_time:.0f}s")
    print("Done!")


if __name__ == "__main__":
    main()
