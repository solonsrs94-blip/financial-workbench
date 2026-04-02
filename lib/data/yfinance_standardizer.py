"""yfinance standardizer — map yfinance DataFrames to prepared_data format.

Takes income_stmt, balance_sheet, cashflow from yfinance and produces
the same structure as the EDGAR standardizer pipeline:
  - standardized: {income/balance/cashflow: {year: {field: value}}}
  - years: sorted list of year strings

yfinance already provides consistent key names across companies,
so this is a simple 1:1 mapping with no XBRL concept resolution.

No Streamlit imports allowed (lib/ rule).
"""

from typing import Optional

import pandas as pd

from lib.data.yfinance_maps import IS_MAP, BS_MAP, CF_MAP


def standardize_yfinance(
    income_stmt: Optional[pd.DataFrame],
    balance_sheet: Optional[pd.DataFrame],
    cashflow: Optional[pd.DataFrame],
) -> Optional[dict]:
    """Convert yfinance DataFrames to prepared_data standardized format.

    Returns same structure as EDGAR standardizer:
        {
            "income": {year_str: {field: value, ...}},
            "balance": {year_str: {field: value, ...}},
            "cashflow": {year_str: {field: value, ...}},
            "years": [sorted year strings],
            "source": "yfinance",
        }
    """
    income = _map_dataframe(income_stmt, IS_MAP)
    balance = _map_dataframe(balance_sheet, BS_MAP)
    cashflow_d = _map_dataframe(cashflow, CF_MAP)

    if not income and not balance and not cashflow_d:
        return None

    # Collect all years from all statements
    all_years = set()
    for stmt in [income, balance, cashflow_d]:
        all_years.update(stmt.keys())

    years = sorted(all_years)

    # Derive fields that yfinance doesn't always provide
    _derive_fields(income, balance, cashflow_d, years)

    return {
        "income": income,
        "balance": balance,
        "cashflow": cashflow_d,
        "years": years,
        "source": "yfinance",
    }


def _map_dataframe(df: Optional[pd.DataFrame], mapping: dict) -> dict:
    """Map a yfinance DataFrame to {year_str: {field: value}}.

    yfinance format: rows = line items, columns = dates (newest first).
    """
    if df is None or df.empty:
        return {}

    result = {}
    for col in df.columns:
        year_str = str(col.year) if hasattr(col, "year") else str(col)[:4]
        yr_data = {}

        for idx_name in df.index:
            val = df.loc[idx_name, col]

            # Skip NaN values
            if pd.isna(val):
                continue

            our_key = mapping.get(idx_name)
            if our_key and our_key not in yr_data:
                yr_data[our_key] = float(val)

        if yr_data:
            result[year_str] = yr_data

    return result


def _derive_fields(
    income: dict, balance: dict, cashflow: dict, years: list[str],
) -> None:
    """Compute derived fields not directly in yfinance."""
    for yr in years:
        inc = income.get(yr, {})
        bal = balance.get(yr, {})
        cf = cashflow.get(yr, {})

        rev = inc.get("total_revenue")

        # D&A: try IS reconciled first, then CF
        if "da" not in inc and "depreciation_amortization" in cf:
            inc["da"] = abs(cf["depreciation_amortization"])

        # EBITDA: derive if missing
        ebit = inc.get("ebit")
        da = inc.get("da") or abs(cf.get("depreciation_amortization", 0))
        if "ebitda" not in inc and ebit is not None and da:
            inc["ebitda"] = ebit + abs(da)

        # Gross profit: derive if missing
        cogs = inc.get("cost_of_revenue")
        if "gross_profit" not in inc and rev and cogs:
            inc["gross_profit"] = rev - abs(cogs)

        # Working capital: derive if missing on BS
        ca = bal.get("total_current_assets")
        cl = bal.get("total_current_liabilities")
        if "working_capital" not in bal and ca is not None and cl is not None:
            bal["working_capital"] = ca - cl

        # Total debt: derive if missing
        if "total_debt" not in bal:
            ltd = bal.get("long_term_debt") or 0
            cd = bal.get("current_debt") or 0
            if ltd or cd:
                bal["total_debt"] = ltd + cd

        # Net debt: derive if missing
        td = bal.get("total_debt")
        cash = bal.get("cash") or 0
        if "net_debt" not in bal and td is not None:
            bal["net_debt"] = td - cash

        # Free cash flow: derive if missing
        ocf = cf.get("operating_cash_flow")
        capex = cf.get("capital_expenditure")
        if "free_cash_flow" not in cf and ocf is not None and capex is not None:
            cf["free_cash_flow"] = ocf + capex  # capex is negative

        # Ensure cost_of_revenue is positive for ratio calculations
        if "cost_of_revenue" in inc:
            inc["cost_of_revenue"] = abs(inc["cost_of_revenue"])

        # Map cogs alias for downstream compatibility
        if "cost_of_revenue" in inc and "cogs" not in inc:
            inc["cogs"] = inc["cost_of_revenue"]

        # Map revenue alias
        if "total_revenue" in inc and "revenue" not in inc:
            inc["revenue"] = inc["total_revenue"]

        # Shares outstanding: prefer ordinary shares on BS
        if "shares_outstanding" not in bal:
            bal["shares_outstanding"] = bal.get("ordinary_shares")
