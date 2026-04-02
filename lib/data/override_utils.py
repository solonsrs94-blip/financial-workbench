"""Override utilities — apply user overrides to standardized financial data.

Merges user-provided overrides into a copy of standardized data.
Original data is never modified.

No Streamlit imports allowed (lib/ rule).
"""

import copy
from typing import Optional


def apply_overrides(standardized: dict, overrides: dict) -> dict:
    """Apply overrides to a deep copy of standardized data.

    Args:
        standardized: Original standardized dict with income/balance/cashflow
        overrides: Dict of {statement: {year: {field: value}}}

    Returns:
        New dict with overrides merged in. Original is untouched.
    """
    if not overrides:
        return standardized

    result = copy.deepcopy(standardized)

    for stmt in ("income", "balance", "cashflow"):
        stmt_overrides = overrides.get(stmt, {})
        if not stmt_overrides:
            continue

        stmt_data = result.get(stmt, {})
        for year, fields in stmt_overrides.items():
            if year not in stmt_data:
                stmt_data[year] = {}
            for field, value in fields.items():
                stmt_data[year][field] = value

    return result


def count_overrides(overrides: dict) -> int:
    """Count total number of active override values."""
    total = 0
    for stmt in ("income", "balance", "cashflow"):
        for year_data in overrides.get(stmt, {}).values():
            total += len(year_data)
    return total


def get_override_set(overrides: dict) -> set:
    """Get set of (statement, year, field) tuples for all active overrides."""
    result = set()
    for stmt in ("income", "balance", "cashflow"):
        for year, fields in overrides.get(stmt, {}).items():
            for field in fields:
                result.add((stmt, year, field))
    return result
