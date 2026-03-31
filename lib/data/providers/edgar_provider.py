"""SEC EDGAR provider — 10+ years of US financial statements via edgartools.

Free, no API key, no rate limit. Requires User-Agent identity (SEC policy).

Two modes:
1. fetch_statements() — returns raw DataFrames (labels as rows, years as cols)
   Used for Step 1a (raw as-reported display)
2. fetch_xbrl_statements() — in edgar_xbrl.py, returns standardized dicts
   Used for ratios, flags, and DCF calculations
"""

import logging
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


def _ensure_identity():
    """Set SEC-required identity (User-Agent)."""
    try:
        from edgar import set_identity
        set_identity("Financial Workbench App contact@example.com")
    except Exception:
        pass


def fetch_statements(
    ticker: str, n_filings: int = 10,
) -> Optional[dict]:
    """Fetch raw financial statement DataFrames from EDGAR 10-K filings.

    Returns dict with 'income', 'balance', 'cashflow' keys.
    Each is a DataFrame: rows = line items (labels), columns = years.
    This preserves the company's own reporting format.
    """
    try:
        _ensure_identity()
        from edgar import Company

        company = Company(ticker)
        filings_obj = company.get_filings(form="10-K")
        filing_list = list(filings_obj)[:n_filings]

        if not filing_list:
            logger.info("EDGAR: no 10-K filings for %s", ticker)
            return None

        statements = {"income": {}, "balance": {}, "cashflow": {}}

        for filing in filing_list:
            try:
                xbrl = filing.xbrl()
                if not xbrl or not xbrl.statements:
                    continue

                for stmt_type, fn_name in [
                    ("income", "income_statement"),
                    ("balance", "balance_sheet"),
                    ("cashflow", "cashflow_statement"),
                ]:
                    stmt = getattr(xbrl.statements, fn_name, lambda: None)()
                    if stmt is None:
                        continue
                    df = stmt.to_dataframe()
                    if df is None or df.empty:
                        continue

                    if "dimension" in df.columns:
                        df = df[df["dimension"] == False]  # noqa: E712

                    year_cols = [
                        c for c in df.columns
                        if isinstance(c, str) and len(c) == 10 and c[4] == "-"
                    ]

                    for col in year_cols:
                        year = col[:4]
                        if year not in statements[stmt_type]:
                            for _, row in df.iterrows():
                                label = row.get("label")
                                if not label or pd.isna(label):
                                    continue
                                val = row.get(col)
                                if pd.notna(val):
                                    if year not in statements[stmt_type]:
                                        statements[stmt_type][year] = {}
                                    statements[stmt_type][year][label] = float(val)

            except Exception as e:
                logger.warning("EDGAR filing parse failed: %s", e)
                continue

        result = {}
        for stmt_type in ("income", "balance", "cashflow"):
            yearly = statements[stmt_type]
            if not yearly:
                continue
            all_labels = []
            for year_data in yearly.values():
                for label in year_data:
                    if label not in all_labels:
                        all_labels.append(label)

            years_sorted = sorted(yearly.keys())
            data = {}
            for yr in years_sorted:
                data[yr] = [yearly[yr].get(label) for label in all_labels]

            result[stmt_type] = pd.DataFrame(
                data, index=all_labels, columns=years_sorted,
            )

        if not result:
            return None

        result["source"] = "edgar"
        result["n_years"] = len(
            set().union(*(statements[k].keys() for k in statements))
        )
        return result

    except ImportError:
        logger.warning("edgartools not installed")
        return None
    except Exception as e:
        logger.error("EDGAR fetch failed for %s: %s", ticker, e)
        return None
