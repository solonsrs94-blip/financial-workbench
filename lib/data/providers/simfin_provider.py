"""SimFin provider — 10+ years of historical financial statements.

Free tier: data delayed ~12 months, unlimited API calls.
Returns standardized dicts matching Yahoo provider format for easy merging.
"""

import logging
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

# SimFin column name constants (imported at function level to avoid
# import errors if simfin is not installed).

# Mapping: SimFin column → our standardized key
_IS_MAP = {
    "Revenue": "total_revenue",
    "Cost of Revenue": "cost_of_revenue",
    "Gross Profit": "gross_profit",
    "Selling, General & Administrative": "selling_general_admin",
    "Research & Development": "research_development",
    "Depreciation & Amortization": "depreciation_amortization",
    "Operating Income (Loss)": "ebit",
    "Non-Operating Income (Loss)": "non_operating_income",
    "Interest Expense, Net": "interest_expense",
    "Pretax Income (Loss)": "pretax_income",
    "Income Tax (Expense) Benefit, Net": "tax_provision",
    "Net Income": "net_income",
    "EBITDA": "ebitda",
    "Operating Expenses": "operating_expenses",
}

_BS_MAP = {
    "Cash & Cash Equivalents": "cash_and_equivalents",
    "Accounts & Notes Receivable": "accounts_receivable",
    "Inventories": "inventories",
    "Total Current Assets": "total_current_assets",
    "Total Assets": "total_assets",
    "Accounts Payable": "accounts_payable",
    "Total Current Liabilities": "total_current_liabilities",
    "Total Debt": "total_debt",
    "Total Liabilities": "total_liabilities",
    "Total Equity": "total_equity",
    "Minority Interest": "minority_interest",
    "Common Stock": "common_stock",
}

_CF_MAP = {
    "Net Cash from Operating Activities": "operating_cash_flow",
    "Change in Fixed Assets & Intangibles": "capital_expenditure",
    "Net Cash from Investing Activities": "investing_cash_flow",
    "Net Cash from Financing Activities": "financing_cash_flow",
    "Depreciation & Amortization": "depreciation_amortization",
    "Stock-Based Compensation": "stock_based_compensation",
    "Shares (Diluted)": "diluted_shares",
}


def _load_simfin():
    """Lazy import simfin — avoids crash if not installed."""
    try:
        import simfin as sf
        from config.settings import SIMFIN_API_KEY, DATA_DIR
        if not SIMFIN_API_KEY:
            logger.warning("SIMFIN_API_KEY not set — SimFin unavailable")
            return None
        sf.set_api_key(SIMFIN_API_KEY)
        sf.set_data_dir(str(DATA_DIR / "simfin_cache"))
        return sf
    except ImportError:
        logger.warning("simfin not installed — pip install simfin")
        return None


def _df_to_yearly_dicts(
    df: pd.DataFrame, ticker: str, col_map: dict,
) -> Optional[dict[str, dict]]:
    """Convert SimFin DataFrame to {year: {field: value}} dict.

    Handles both MultiIndex (premium) and flat index (free tier) formats.
    """
    if df is None or df.empty:
        return None
    try:
        # Filter to ticker — free tier uses flat index with Ticker column
        if "Ticker" in df.columns:
            sub = df[df["Ticker"] == ticker]
        elif isinstance(df.index, pd.MultiIndex):
            if ticker in df.index.get_level_values(0):
                sub = df.loc[ticker]
            else:
                return None
        else:
            sub = df

        if sub.empty:
            return None

        result = {}
        for _, row in sub.iterrows():
            # Get year from Report Date or Fiscal Year
            if "Report Date" in row.index and pd.notna(row["Report Date"]):
                year = str(pd.Timestamp(row["Report Date"]).year)
            elif "Fiscal Year" in row.index and pd.notna(row["Fiscal Year"]):
                year = str(int(row["Fiscal Year"]))
            else:
                continue

            mapped = {}
            for sf_col, our_key in col_map.items():
                if sf_col in row.index:
                    val = row[sf_col]
                    mapped[our_key] = None if pd.isna(val) else float(val)
            result[year] = mapped
        return result if result else None
    except Exception as e:
        logger.error("SimFin parse error for %s: %s", ticker, e)
        return None


def fetch_historical_financials(
    ticker: str, market: str = "us",
) -> Optional[dict]:
    """Fetch 10+ years of IS, BS, CF from SimFin.

    Returns dict with keys: income_annual, balance_annual, cashflow_annual.
    Each is {year: {field: value}}.
    """
    sf = _load_simfin()
    if sf is None:
        return None

    try:
        income = sf.load(
            dataset="income", variant="annual", market=market,
        )
        balance = sf.load(
            dataset="balance", variant="annual", market=market,
        )
        cashflow = sf.load(
            dataset="cashflow", variant="annual", market=market,
        )

        result = {
            "income_annual": _df_to_yearly_dicts(income, ticker, _IS_MAP),
            "balance_annual": _df_to_yearly_dicts(balance, ticker, _BS_MAP),
            "cashflow_annual": _df_to_yearly_dicts(cashflow, ticker, _CF_MAP),
            "source": "simfin",
        }

        if all(v is None for k, v in result.items() if k != "source"):
            logger.info("SimFin: no data for %s in market=%s", ticker, market)
            return None

        return result
    except Exception as e:
        logger.error("SimFin fetch failed for %s: %s", ticker, e)
        return None


def get_available_years(ticker: str, market: str = "us") -> list[str]:
    """Return sorted list of years available for a ticker."""
    data = fetch_historical_financials(ticker, market)
    if data is None:
        return []
    years = set()
    for key in ("income_annual", "balance_annual", "cashflow_annual"):
        if data.get(key):
            years.update(data[key].keys())
    return sorted(years)
