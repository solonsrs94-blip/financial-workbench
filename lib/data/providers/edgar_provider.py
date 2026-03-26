"""SEC EDGAR provider — 10+ years of US financial statements via edgartools.

Free, no API key, no rate limit. Requires User-Agent identity (SEC policy).

Two modes:
1. fetch_statements() — returns raw DataFrames (labels as rows, years as cols)
   Used for Step 1a (raw as-reported display)
2. fetch_historical_financials() — returns standardized dicts
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

                    # Filter to consolidated (non-dimension) rows
                    if "dimension" in df.columns:
                        df = df[df["dimension"] == False]  # noqa: E712

                    # Find year columns
                    year_cols = [
                        c for c in df.columns
                        if isinstance(c, str) and len(c) == 10 and c[4] == "-"
                    ]

                    for col in year_cols:
                        year = col[:4]
                        if year not in statements[stmt_type]:
                            # Extract label -> value for this year
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

        # Convert to DataFrames (rows = labels, columns = years sorted)
        result = {}
        for stmt_type in ("income", "balance", "cashflow"):
            yearly = statements[stmt_type]
            if not yearly:
                continue
            # Collect all labels across all years
            all_labels = []
            for year_data in yearly.values():
                for label in year_data:
                    if label not in all_labels:
                        all_labels.append(label)

            # Build DataFrame
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


def fetch_xbrl_statements(
    ticker: str, n_filings: int = 10,
) -> Optional[dict]:
    """Fetch XBRL DataFrames with full metadata (standard_concept, label, etc).

    Returns dict with 'income', 'balance', 'cashflow' keys.
    Each is the full XBRL DataFrame with columns: concept, label,
    standard_concept, year columns, level, abstract, dimension, etc.

    Used by the standardizer for Layer 1 (XBRL concept mapping).
    """
    try:
        _ensure_identity()
        from edgar import Company

        company = Company(ticker)
        filings_obj = company.get_filings(form="10-K")
        filing_list = list(filings_obj)[:n_filings]

        if not filing_list:
            return None

        # We need the latest filing's XBRL (has 2-3 years) plus older filings
        result = {}
        seen_years = {"income": set(), "balance": set(), "cashflow": set()}

        for filing in filing_list:
            try:
                xbrl = filing.xbrl()
                if not xbrl or not xbrl.statements:
                    continue

                for stmt_type, fn_name in [
                    ("income", "income_statement"),
                    ("balance", "balance_sheet"),
                    ("cashflow", "cash_flow_statement"),
                ]:
                    stmt = getattr(xbrl.statements, fn_name, lambda: None)()
                    if stmt is None:
                        continue
                    df = stmt.to_dataframe()
                    if df is None or df.empty:
                        continue

                    # Find year columns
                    year_cols = [
                        c for c in df.columns
                        if isinstance(c, str) and len(c) >= 8 and c[:4].isdigit()
                    ]

                    # Check for new years we haven't seen
                    new_years = [
                        c for c in year_cols
                        if c[:4] not in seen_years[stmt_type]
                    ]
                    if not new_years:
                        continue  # All years already covered

                    for c in new_years:
                        seen_years[stmt_type].add(c[:4])

                    # If first DataFrame for this statement, use it as base
                    if stmt_type not in result:
                        result[stmt_type] = df
                    else:
                        # Merge new year columns into existing DataFrame
                        existing = result[stmt_type]
                        for col in new_years:
                            if col not in existing.columns:
                                # Match by standard_concept or label
                                new_vals = {}
                                for _, row in df.iterrows():
                                    sc = row.get("standard_concept", "")
                                    label = row.get("label", "")
                                    val = row.get(col)
                                    if pd.notna(val):
                                        new_vals[(str(sc), str(label))] = float(val)

                                # Map to existing rows
                                col_data = []
                                for _, erow in existing.iterrows():
                                    esc = str(erow.get("standard_concept", ""))
                                    elabel = str(erow.get("label", ""))
                                    v = new_vals.get((esc, elabel))
                                    if v is None:
                                        # Try label-only match
                                        v = next(
                                            (val for (sc, lb), val in new_vals.items()
                                             if lb == elabel),
                                            None,
                                        )
                                    col_data.append(v)
                                existing[col] = col_data

            except Exception as e:
                logger.warning("EDGAR XBRL parse failed: %s", e)
                continue

        if not result:
            return None

        result["source"] = "edgar"
        return result

    except ImportError:
        logger.warning("edgartools not installed")
        return None
    except Exception as e:
        logger.error("EDGAR XBRL fetch failed for %s: %s", ticker, e)
        return None
