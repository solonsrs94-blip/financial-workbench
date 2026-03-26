"""
Yahoo Finance provider — valuation-specific financial details.

Fetches balance sheet, cash flow, income statement details needed for DCF.
Returns raw dicts — no models, cache, or UI.
"""

import logging
import yfinance as yf
from typing import Optional

logger = logging.getLogger(__name__)


def _safe_val(df, row_name, col_idx=0):
    """Safely extract a value from a yfinance DataFrame."""
    if df is None or df.empty:
        return None
    if row_name not in df.index:
        return None
    try:
        val = df.iloc[df.index.get_loc(row_name), col_idx]
        if val is not None and str(val) != "nan":
            return float(val)
    except Exception:
        pass
    return None


def _safe_div(num, den):
    """Safe division, returns None on failure."""
    if num and den and den != 0:
        return num / den
    return None


def fetch_valuation_data(ticker: str) -> Optional[dict]:
    """Fetch detailed financials for DCF valuation.

    Returns dict with: balance_sheet, cash_flow, income_detail,
    working_capital, historical_margins, sbc_pct
    """
    try:
        stock = yf.Ticker(ticker)
        inc = stock.income_stmt
        bs = stock.balance_sheet
        cf = stock.cashflow
        info = stock.info or {}
    except Exception as e:
        logger.error("Valuation data failed for %s: %s", ticker, e)
        return None

    if inc is None or inc.empty:
        return None

    # --- Income Statement Details (most recent year) ---
    revenue = _safe_val(inc, "Total Revenue")
    cogs = _safe_val(inc, "Cost Of Revenue")
    gross_profit = _safe_val(inc, "Gross Profit")
    sga = _safe_val(inc, "Selling General And Administration")
    ebitda = _safe_val(inc, "EBITDA") or _safe_val(inc, "Normalized EBITDA")
    ebit = _safe_val(inc, "EBIT") or _safe_val(inc, "Operating Income")
    interest_expense = _safe_val(inc, "Interest Expense")
    pretax = _safe_val(inc, "Pretax Income")
    tax_provision = _safe_val(inc, "Tax Provision")
    net_income = _safe_val(inc, "Net Income")

    eff_tax = _safe_div(abs(tax_provision), pretax) if tax_provision and pretax and pretax > 0 else None

    income_detail = {
        "revenue": revenue, "cogs": cogs, "gross_profit": gross_profit,
        "sga": sga, "ebitda": ebitda, "ebit": ebit,
        "interest_expense": abs(interest_expense) if interest_expense else None,
        "pretax_income": pretax, "tax_provision": tax_provision,
        "net_income": net_income, "effective_tax_rate": eff_tax,
    }

    # --- Balance Sheet Details ---
    receivables = _safe_val(bs, "Accounts Receivable")
    inventory = _safe_val(bs, "Inventory")
    payables = _safe_val(bs, "Accounts Payable")
    total_debt = _safe_val(bs, "Total Debt") or (
        (_safe_val(bs, "Current Debt") or 0) + (_safe_val(bs, "Long Term Debt") or 0)
    )
    cash = _safe_val(bs, "Cash And Cash Equivalents") or _safe_val(bs, "Cash Cash Equivalents And Short Term Investments")
    minority = _safe_val(bs, "Minority Interest")
    preferred = _safe_val(bs, "Preferred Stock")
    total_equity = _safe_val(bs, "Stockholders Equity")

    balance_sheet = {
        "receivables": receivables, "inventory": inventory, "payables": payables,
        "total_debt": total_debt or 0, "cash": cash or 0,
        "net_debt": (total_debt or 0) - (cash or 0),
        "minority_interest": minority or 0, "preferred_equity": preferred or 0,
        "total_equity": total_equity,
    }

    # --- Cash Flow Details ---
    capex = _safe_val(cf, "Capital Expenditure") if cf is not None else None
    da = _safe_val(cf, "Depreciation And Amortization") if cf is not None else None
    sbc = _safe_val(cf, "Stock Based Compensation") if cf is not None else None
    ocf = _safe_val(cf, "Operating Cash Flow") if cf is not None else None
    fcf = _safe_val(cf, "Free Cash Flow") if cf is not None else None

    cash_flow = {
        "capex": abs(capex) if capex else None,
        "depreciation": abs(da) if da else None,
        "sbc": abs(sbc) if sbc else None,
        "operating_cash_flow": ocf, "free_cash_flow": fcf,
    }

    # --- Working Capital Days ---
    dso = (receivables / revenue * 365) if receivables and revenue and revenue > 0 else None
    dio = (inventory / cogs * 365) if inventory and cogs and cogs > 0 else None
    dpo = (payables / cogs * 365) if payables and cogs and cogs > 0 else None

    working_capital = {"dso": dso, "dio": dio, "dpo": dpo}

    # --- Historical Margins (last 3-4 years) ---
    historical = _build_historical(inc, cf)

    # --- SBC as % of revenue ---
    sbc_pct = abs(sbc) / revenue if sbc and revenue and revenue > 0 else None

    # --- Shares ---
    shares = info.get("sharesOutstanding") or info.get("impliedSharesOutstanding")

    return {
        "income_detail": income_detail,
        "balance_sheet": balance_sheet,
        "cash_flow": cash_flow,
        "working_capital": working_capital,
        "historical_margins": historical,
        "sbc_pct": sbc_pct,
        "shares": shares,
        "market_cap": info.get("marketCap"),
        "enterprise_value": info.get("enterpriseValue"),
        "beta": info.get("beta"),
        "dividend_yield": info.get("dividendYield"),
    }


def _build_historical(inc, cf) -> list:
    """Build per-year margin history from income statement and cash flow."""
    if inc is None or inc.empty:
        return []
    rows = []
    n_cols = min(len(inc.columns), 4)
    for i in range(n_cols):
        rev = _safe_val(inc, "Total Revenue", i)
        if not rev or rev <= 0:
            continue
        ebit = _safe_val(inc, "EBIT", i) or _safe_val(inc, "Operating Income", i)
        gross = _safe_val(inc, "Gross Profit", i)
        cogs = _safe_val(inc, "Cost Of Revenue", i)
        sga = _safe_val(inc, "Selling General And Administration", i)
        capex = abs(_safe_val(cf, "Capital Expenditure", i) or 0) if cf is not None and not cf.empty else 0
        da = abs(_safe_val(cf, "Depreciation And Amortization", i) or 0) if cf is not None and not cf.empty else 0
        sbc = abs(_safe_val(cf, "Stock Based Compensation", i) or 0) if cf is not None and not cf.empty else 0

        year = str(inc.columns[i])[:4]
        rows.append({
            "year": year,
            "revenue": rev,
            "gross_margin": gross / rev if gross else None,
            "ebit_margin": ebit / rev if ebit else None,
            "cogs_pct": cogs / rev if cogs else None,
            "sga_pct": sga / rev if sga else None,
            "capex_pct": capex / rev if capex else 0,
            "da_pct": da / rev if da else 0,
            "sbc_pct": sbc / rev if sbc else 0,
        })
    return rows


def fetch_analyst_estimates(ticker: str) -> Optional[dict]:
    """Fetch analyst consensus revenue/EPS estimates."""
    try:
        stock = yf.Ticker(ticker)
        result = {"revenue_growth": [], "eps_growth": []}

        rev_est = getattr(stock, "revenue_estimate", None)
        if rev_est is not None and not rev_est.empty and "avg" in rev_est.columns:
            for period in rev_est.index:
                result["revenue_growth"].append({
                    "period": str(period),
                    "avg": float(rev_est.loc[period, "avg"]) if "avg" in rev_est.columns else None,
                })

        growth_est = getattr(stock, "growth_estimates", None)
        if growth_est is not None and not growth_est.empty:
            for col in growth_est.columns:
                val = growth_est.iloc[0].get(col) if len(growth_est) > 0 else None
                if val is not None and str(val) != "nan":
                    result["eps_growth"].append({"period": str(col), "value": float(val)})

        return result if result["revenue_growth"] or result["eps_growth"] else None
    except Exception as e:
        logger.error("Analyst estimates failed for %s: %s", ticker, e)
        return None
