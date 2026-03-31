"""SimFin helper functions — data extraction, audit format, derived fields.

Split from simfin_provider.py for file size compliance.
"""

from typing import Optional

import pandas as pd


def extract_ticker_data(
    df: pd.DataFrame, ticker: str, col_map: dict,
) -> Optional[dict]:
    """Extract {year: {key: value}} for a specific ticker from SimFin DF.

    Handles sign normalization: SimFin uses negative numbers for expenses.
    We normalize to positive for consistency with EDGAR output.
    """
    if df is None or df.empty:
        return None

    try:
        if isinstance(df.index, pd.MultiIndex):
            if ticker in df.index.get_level_values("Ticker"):
                sub = df.loc[ticker]
            else:
                return None
        else:
            return None
    except Exception:
        return None

    if sub.empty:
        return None

    result = {}
    for idx, row in sub.iterrows():
        fy = row.get("Fiscal Year")
        if pd.isna(fy):
            continue
        year = str(int(fy))

        mapped = {}
        for sf_col, our_key in col_map.items():
            if sf_col in row.index:
                val = row[sf_col]
                if pd.notna(val):
                    mapped[our_key] = float(val)

        if mapped:
            result[year] = mapped

    return result if result else None


def to_audit_format(yearly_data: dict) -> dict:
    """Convert {year: {key: value}} to audit format."""
    audit = {}
    for year, fields in yearly_data.items():
        audit[year] = {}
        for key, value in fields.items():
            if value is not None:
                audit[year][key] = {
                    "value": value,
                    "raw_label": f"SimFin: {key}",
                    "layer": 1,
                }
    return audit


def compute_derived(yearly_data: dict) -> None:
    """Add derived fields to yearly data (modifies in place)."""
    for year, d in yearly_data.items():
        ebit = d.get("ebit")
        da = d.get("da_is") or d.get("depreciation_amortization")
        if ebit and da and "ebitda" not in d:
            d["ebitda"] = ebit + abs(da)

        rev = d.get("revenue")
        cogs = d.get("cogs")
        if rev and cogs and "gross_profit" not in d:
            d["gross_profit"] = rev - abs(cogs)

        ocf = d.get("operating_cash_flow")
        capex = d.get("capital_expenditure")
        if ocf and capex and "free_cash_flow" not in d:
            d["free_cash_flow"] = ocf - abs(capex)

        st = d.get("short_term_debt", 0)
        lt = d.get("long_term_debt", 0)
        if (st or lt) and "total_debt" not in d:
            d["total_debt"] = abs(st) + abs(lt)

        td = d.get("total_debt")
        cash = d.get("cash")
        if td and cash and "net_debt" not in d:
            d["net_debt"] = td - abs(cash)
