"""Financial statement standardizer — 4-layer mapping system.

Layer 1: XBRL concept mapping (US-GAAP taxonomy → standardized keys)
Layer 2: Keyword matching on labels
Layer 3: Hierarchy inference from XBRL parent-child
Layer 4: "Other" catch-all buckets

No Streamlit imports (lib/ rule).
"""

import pandas as pd
from typing import Optional

from lib.data.xbrl_concept_map import (
    IS_CONCEPT_MAP, BS_CONCEPT_MAP, CF_CONCEPT_MAP,
    KEYWORD_FALLBACKS, CF_SUBTOTAL_CONCEPTS,
)


def standardize_statement(
    df: pd.DataFrame,
    statement_type: str,
) -> dict:
    """Standardize a raw EDGAR DataFrame into {year: {key: {value, raw_label, source, layer}}}.

    Args:
        df: Raw DataFrame from EDGAR (rows=line items, cols=years)
            Must have columns: concept, label, standard_concept, and year columns.
            If it's a simple DataFrame (rows=labels, cols=dates), falls back to label matching.
        statement_type: "income", "balance", or "cashflow"

    Returns:
        {year: {standardized_key: {"value": float, "raw_label": str, "layer": int}}}
    """
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return {}

    concept_map = {
        "income": IS_CONCEPT_MAP,
        "balance": BS_CONCEPT_MAP,
        "cashflow": CF_CONCEPT_MAP,
    }[statement_type]

    # Detect format: EDGAR XBRL (has standard_concept) vs simple (Yahoo-like)
    has_xbrl = "standard_concept" in df.columns and "label" in df.columns

    if has_xbrl:
        return _standardize_xbrl(df, concept_map, statement_type)
    else:
        return _standardize_simple(df, statement_type)


def _standardize_xbrl(
    df: pd.DataFrame, concept_map: dict, statement_type: str,
) -> dict:
    """Standardize EDGAR XBRL DataFrame using 4-layer system."""
    # Filter to consolidated only (no dimensions/segments)
    if "dimension" in df.columns:
        df = df[df["dimension"] == False].copy()

    # Find year columns (dates like 2024-09-28)
    year_cols = [c for c in df.columns if len(str(c)) >= 8 and str(c)[:4].isdigit()]
    if not year_cols:
        return {}

    result = {}

    for _, row in df.iterrows():
        sc = str(row.get("standard_concept", "") or "").strip()
        label = str(row.get("label", "") or "").strip()
        parent = str(row.get("parent_concept", "") or "").strip()
        is_abstract = row.get("abstract", False)

        if is_abstract:
            continue

        # Handle CF subtotal concepts (appear multiple times — always last wins)
        if statement_type == "cashflow" and sc in CF_SUBTOTAL_CONCEPTS:
            subtotal_key = CF_SUBTOTAL_CONCEPTS[sc]
            for col in year_cols:
                year = str(col)[:4]
                val = row.get(col)
                if pd.isna(val):
                    continue
                if year not in result:
                    result[year] = {}
                # Always overwrite — last occurrence is sub-total
                result[year][subtotal_key] = {
                    "value": float(val),
                    "raw_label": label,
                    "layer": 1,
                }
            continue  # Don't process this row again below

        # Layer 1: XBRL concept mapping
        std_key = concept_map.get(sc)
        layer = 1

        # Layer 2: Keyword fallback
        if not std_key:
            label_lower = label.lower()
            for kw, key, stmt in KEYWORD_FALLBACKS:
                if stmt == statement_type and kw in label_lower:
                    std_key = key
                    layer = 2
                    break

        # Layer 3: Hierarchy inference from parent concept
        if not std_key and parent:
            parent_key = concept_map.get(
                parent.replace("us-gaap_", "").replace("us-gaap:", "")
            )
            if parent_key:
                std_key = f"{parent_key}_detail"
                layer = 3

        # Layer 4: "Other" catch-all
        if not std_key:
            std_key = _classify_other(label, statement_type)
            layer = 4

        if not std_key:
            continue

        # Extract values per year
        for col in year_cols:
            year = str(col)[:4]
            val = row.get(col)
            if pd.isna(val):
                continue

            if year not in result:
                result[year] = {}

            # Overwrite rules:
            # - Higher layer never overwrites lower layer
            # - Same layer: LAST value wins (important for CF sub-totals
            #   where NetCashFromOperatingActivities appears multiple
            #   times — individual items first, sub-total last)
            existing = result[year].get(std_key)
            if existing and existing["layer"] < layer:
                continue

            result[year][std_key] = {
                "value": float(val),
                "raw_label": label,
                "layer": layer,
            }

    return result


def _standardize_simple(df: pd.DataFrame, statement_type: str) -> dict:
    """Standardize simple DataFrame (Yahoo-like: rows=labels, cols=dates)."""
    result = {}

    for col in df.columns:
        year = str(col)[:4]
        if not year.isdigit():
            continue

        if year not in result:
            result[year] = {}

        for label in df.index:
            val = df.loc[label, col]
            if pd.isna(val):
                continue

            label_lower = str(label).lower().strip()

            # Layer 2: Keyword matching
            std_key = None
            for kw, key, stmt in KEYWORD_FALLBACKS:
                if stmt == statement_type and kw in label_lower:
                    std_key = key
                    break

            if not std_key:
                std_key = _classify_other(str(label), statement_type)

            if not std_key:
                continue

            existing = result[year].get(std_key)
            if existing:
                continue  # Keep first match

            result[year][std_key] = {
                "value": float(val),
                "raw_label": str(label),
                "layer": 2,
            }

    return result


def _classify_other(label: str, statement_type: str) -> Optional[str]:
    """Layer 4: Classify unknown items into 'Other' buckets."""
    ll = label.lower()

    if statement_type == "income":
        if any(w in ll for w in ["expense", "cost", "charge", "loss"]):
            return "other_operating_expense"
        if any(w in ll for w in ["income", "gain", "revenue"]):
            return "other_operating_income"
        return "other_is_item"

    elif statement_type == "balance":
        if any(w in ll for w in ["receivable", "prepaid", "inventory", "current asset"]):
            return "other_current_assets"
        if any(w in ll for w in ["payable", "accrued", "current liab", "deferred rev"]):
            return "other_current_liabilities"
        if any(w in ll for w in ["asset", "investment", "intangible", "property"]):
            return "other_non_current_assets"
        if any(w in ll for w in ["debt", "liabilit", "obligation", "lease"]):
            return "other_non_current_liabilities"
        if any(w in ll for w in ["equity", "stock", "capital", "retained", "treasury"]):
            return "other_equity"
        return "other_bs_item"

    elif statement_type == "cashflow":
        if any(w in ll for w in ["operating", "working capital", "receivable", "payable"]):
            return "other_operating_cf"
        if any(w in ll for w in ["investing", "purchase", "acquisition", "proceeds"]):
            return "other_investing_cf"
        if any(w in ll for w in ["financing", "debt", "dividend", "repurchase", "stock"]):
            return "other_financing_cf"
        return "other_cf_item"

    return None
