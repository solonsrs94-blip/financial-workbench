"""EDGAR XBRL statement fetcher — full metadata from ALL 10-K filings.

Strategy: process filings newest->oldest. For each year that appears
in a filing, use the FIRST (newest) filing as primary. But ALWAYS
check older filings for rows that are MISSING in newer filings
(concept names change between years -- old filings have old concepts).

Split from edgar_provider.py for file size compliance.
"""

import logging
from typing import Optional

import pandas as pd

from lib.data.providers.edgar_provider import _ensure_identity

logger = logging.getLogger(__name__)


def fetch_xbrl_statements(
    ticker: str, n_filings: int = 10,
) -> Optional[dict]:
    """Fetch XBRL DataFrames with full metadata from ALL 10-K filings.

    Returns dict with 'income', 'balance', 'cashflow' keys.
    Each is the full XBRL DataFrame with concept, label,
    standard_concept, and year columns.
    """
    try:
        _ensure_identity()
        from edgar import Company

        company = Company(ticker)
        filings_obj = company.get_filings(form="10-K")
        filing_list = list(filings_obj)[:n_filings]

        if not filing_list:
            return None

        # {stmt_type: {year_col: [(concept, sc, label, value, filing_idx)]}}
        all_data = {"income": {}, "balance": {}, "cashflow": {}}
        year_col_map = {"income": {}, "balance": {}, "cashflow": {}}
        meta_cols = {"income": None, "balance": None, "cashflow": None}

        for f_idx, filing in enumerate(filing_list):
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

                    if "dimension" in df.columns:
                        df = df[df["dimension"] == False].copy()  # noqa: E712

                    if meta_cols[stmt_type] is None:
                        meta_cols[stmt_type] = [
                            c for c in df.columns
                            if not (isinstance(c, str) and len(c) >= 8
                                    and c[:4].isdigit())
                        ]

                    year_cols = [
                        c for c in df.columns
                        if isinstance(c, str) and len(c) >= 8 and c[:4].isdigit()
                    ]

                    for col in year_cols:
                        yr = col[:4]
                        if yr not in year_col_map[stmt_type]:
                            year_col_map[stmt_type][yr] = col

                    for _, row in df.iterrows():
                        if row.get("abstract", False):
                            continue

                        raw_concept = str(row.get("concept", "") or "").strip()
                        sc = str(row.get("standard_concept", "") or "").strip()
                        if sc == "None":
                            sc = ""
                        label = str(row.get("label", "") or "").strip()

                        row_meta = {}
                        if meta_cols[stmt_type]:
                            for mc in meta_cols[stmt_type]:
                                if mc in df.columns:
                                    row_meta[mc] = row.get(mc)

                        for col in year_cols:
                            year = col[:4]
                            val = row.get(col)
                            if pd.isna(val):
                                continue

                            if year not in all_data[stmt_type]:
                                all_data[stmt_type][year] = []

                            all_data[stmt_type][year].append({
                                "concept": raw_concept,
                                "sc": sc,
                                "label": label,
                                "value": float(val),
                                "filing_idx": f_idx,
                                "meta": row_meta,
                            })

            except Exception as e:
                logger.warning("EDGAR XBRL parse failed: %s", e)
                continue

        # Phase 2: Merge rows per year (newest filing wins for same key)
        result = {}

        for stmt_type in ("income", "balance", "cashflow"):
            yearly = all_data[stmt_type]
            if not yearly:
                continue

            years_sorted = sorted(yearly.keys())
            col_map = year_col_map[stmt_type]

            all_rows = []
            seen_keys = set()

            for year in years_sorted:
                for row in yearly[year]:
                    key = (row["sc"], row["label"])
                    if key not in seen_keys:
                        seen_keys.add(key)
                        all_rows.append({
                            "sc": row["sc"],
                            "label": row["label"],
                            "concept": row["concept"],
                            "meta": row["meta"],
                        })

            records = []
            for rinfo in all_rows:
                rec = dict(rinfo["meta"])
                rec["concept"] = rinfo["concept"]
                rec["standard_concept"] = rinfo["sc"]
                rec["label"] = rinfo["label"]

                for year in years_sorted:
                    col_name = col_map.get(year, year)
                    best_val = None
                    best_idx = 999
                    for row_data in yearly.get(year, []):
                        if row_data["sc"] == rinfo["sc"] and row_data["label"] == rinfo["label"]:
                            if row_data["filing_idx"] < best_idx:
                                best_val = row_data["value"]
                                best_idx = row_data["filing_idx"]
                    rec[col_name] = best_val

                records.append(rec)

            if records:
                result[stmt_type] = pd.DataFrame(records)

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
