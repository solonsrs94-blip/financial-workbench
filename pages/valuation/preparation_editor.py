"""Editable financial table — data_editor for override values.

Shows values in $M (millions) for readability. Converts back to raw
dollars when storing overrides. Non-dollar fields (shares, EPS, days)
are shown in their native units.

Split from preparation_display.py for file size compliance.
"""

import streamlit as st
import pandas as pd

# Fields that should NOT be divided by 1M (they are counts, not dollars)
_NO_SCALE_FIELDS = {
    "diluted_shares", "basic_shares", "shares_outstanding",
    "ordinary_shares", "diluted_eps", "basic_eps",
}


def render_editable_table(
    rows: list[dict], fields: list[tuple],
    stmt_key: str, ticker: str,
    overrides: dict, data: dict,
) -> None:
    """Render st.data_editor with values in $M for dollar fields."""
    if not rows:
        return

    ovr_key = f"financial_overrides_{ticker}"
    original_std = data.get("original_standardized", {})
    orig_stmt = original_std.get(stmt_key, {})
    years = [r["year"] for r in rows]

    # Filter to non-empty fields
    active_fields = [
        fd for fd in fields
        if any(r.get(fd[0]) is not None for r in rows)
    ]

    # Build DataFrame in $M for dollar fields, native for others
    df_data = {
        "Line Item": [fd[1].lstrip("= >") for fd in active_fields],
        "_key": [fd[0] for fd in active_fields],
    }
    for i, yr in enumerate(years):
        col = []
        for fd in active_fields:
            val = rows[i].get(fd[0])
            if val is not None and fd[0] not in _NO_SCALE_FIELDS:
                val = val / 1e6  # raw → $M
            col.append(val)
        df_data[f"{yr} ($M)"] = col

    df = pd.DataFrame(df_data)

    # Column config
    col_config = {
        "Line Item": st.column_config.TextColumn(
            "Line Item", disabled=True, width="medium",
        ),
        "_key": None,  # hidden
    }
    for yr in years:
        col_config[f"{yr} ($M)"] = st.column_config.NumberColumn(
            f"{yr} ($M)", format="%.0f",
        )

    edited = st.data_editor(
        df, column_config=col_config, use_container_width=True,
        hide_index=True, key=f"prep_editor_{stmt_key}_{ticker}",
        num_rows="fixed",
    )

    # Detect changes — convert $M back to raw dollars for storage
    _detect_changes(
        edited, df, active_fields, years, stmt_key, ovr_key, orig_stmt,
    )


def _detect_changes(
    edited: pd.DataFrame, original: pd.DataFrame,
    fields: list[tuple], years: list[str],
    stmt_key: str, ovr_key: str, orig_stmt: dict,
) -> None:
    """Compare edited vs original and store overrides in raw dollars."""
    overrides = st.session_state.get(ovr_key, {
        "income": {}, "balance": {}, "cashflow": {},
    })
    stmt_ovr = overrides.setdefault(stmt_key, {})
    changed = False

    for row_idx, fd in enumerate(fields):
        key = fd[0]
        is_dollar = key not in _NO_SCALE_FIELDS

        for yr in years:
            col_name = f"{yr} ($M)"
            new_val = edited.at[row_idx, col_name]
            orig_val = original.at[row_idx, col_name]

            new_nan = new_val is None or (isinstance(new_val, float)
                                          and pd.isna(new_val))
            orig_nan = orig_val is None or (isinstance(orig_val, float)
                                             and pd.isna(orig_val))
            if new_nan and orig_nan:
                continue

            if new_val != orig_val:
                # Convert $M input back to raw dollars for storage
                raw_new = (new_val * 1e6 if is_dollar else new_val
                           ) if not new_nan else None
                source_val = orig_stmt.get(yr, {}).get(key)

                if raw_new is not None:
                    threshold = 500_000 if is_dollar else 0.5
                    if source_val is None or abs(raw_new - source_val) > threshold:
                        stmt_ovr.setdefault(yr, {})[key] = float(raw_new)
                        changed = True
                    elif yr in stmt_ovr and key in stmt_ovr[yr]:
                        del stmt_ovr[yr][key]
                        if not stmt_ovr[yr]:
                            del stmt_ovr[yr]
                        changed = True

    if changed:
        st.session_state[ovr_key] = overrides
        st.rerun()
