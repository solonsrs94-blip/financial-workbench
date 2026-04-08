"""Step 2 output rendering — projected revenue + calculated FCF table.

Split from dcf_step2_assumptions.py to stay under 300 lines.
Uses Streamlit columns to render the calculated output section.
"""

import streamlit as st
from typing import Optional

from pages.valuation.dcf_step2_table import (
    compute_projections,
    _fmt_proj_money,
)


# ── Projected revenue display ───────────────────────────────────────


def render_projected_revenue(
    rev_cols,
    assumptions: dict,
    hist: dict,
    n_years: int,
    sep_idx: int,
) -> None:
    """Show projected revenue in the revenue row if growth rates are filled."""
    growth = assumptions.get("growth_rates", [])
    raw_revs = hist.get("revenue_raw", [])
    base_rev = raw_revs[-1] if raw_revs else None

    if base_rev is None:
        return

    prev = base_rev / 1e6  # raw dollars → millions
    for i in range(n_years):
        col_idx = sep_idx + 1 + i
        g = growth[i] if i < len(growth) else None
        if g is not None:
            rev = prev * (1 + g)
            rev_cols[col_idx].markdown(
                f'<div style="font-size:13px;text-align:right;'
                f'padding-top:6px;color:#1c83e1">'
                f'{_fmt_proj_money(rev)}</div>',
                unsafe_allow_html=True,
            )
            prev = rev
        else:
            rev_cols[col_idx].markdown(
                '<div style="font-size:13px;text-align:right;'
                'padding-top:6px;opacity:0.3">—</div>',
                unsafe_allow_html=True,
            )
            break


# ── Calculated output ───────────────────────────────────────────────


def render_calculated_output(
    assumptions: dict,
    hist: dict,
    proj_years: list[int],
) -> None:
    """Render the calculated FCF table if all assumptions are filled."""
    raw_revs = hist.get("revenue_raw", [])
    base_revenue = raw_revs[-1] if raw_revs else None

    if base_revenue is None:
        st.warning("No base revenue available.")
        return

    # COGS % from historical data (for DIO/DPO projections). No silent
    # 60% fallback — surface a warning and skip when data is missing.
    base_cogs_pct = hist.get("base_cogs_pct")
    from components.fetch_warnings import record_fetch
    record_fetch(
        "cogs_pct",
        base_cogs_pct is not None,
        source="standardized income statement",
        message="COGS % could not be computed — enter a baseline manually",
    )
    if base_cogs_pct is None:
        st.warning(
            "COGS % could not be computed from historical data — "
            "projections that depend on COGS cannot be generated.",
            icon="⚠️",
        )
        return

    proj = compute_projections(assumptions, base_revenue, base_cogs_pct)

    if proj is None:
        st.info(
            "Complete all assumptions above to calculate "
            "projected financials."
        )
        return

    st.markdown("#### Projected Financials")
    n = len(proj_years)

    # Line items: (label, values, negate_for_display)
    line_items = [
        ("Revenue", proj["revenue"], False),
        ("EBIT", proj["ebit"], False),
        ("NOPAT", proj["nopat"], False),
        ("+ D&A", proj["da"], False),
        ("− CapEx", proj["capex"], True),
        ("− SBC", proj["sbc"], True),
        ("± NWC Change", proj["nwc_change"], True),
        ("= Free Cash Flow", proj["fcf"], False),
    ]

    # Header row
    hdr = st.columns([1.5] + [1] * n)
    hdr[0].markdown("**Line Item**")
    for i, yr in enumerate(proj_years):
        hdr[1 + i].markdown(
            f'<div style="text-align:right;font-weight:600;'
            f'font-size:13px;color:#1c83e1">{yr}E</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<hr style="margin:4px 0;border-color:rgba(28,131,225,0.2)">',
        unsafe_allow_html=True,
    )

    for label, values, negate in line_items:
        _render_line_item(label, values, negate, n)


def _render_line_item(
    label: str,
    values: list[float],
    negate: bool,
    n: int,
) -> None:
    """Render one line item row in the calculated output."""
    is_total = label.startswith("=")
    row_cols = st.columns([1.5] + [1] * n)

    weight = "700" if is_total else "400"
    color = "#1c83e1" if is_total else "inherit"

    row_cols[0].markdown(
        f'<div style="font-size:13px;font-weight:{weight};'
        f'padding-top:4px">{label}</div>',
        unsafe_allow_html=True,
    )

    for i, val in enumerate(values):
        display = -val if negate else val
        val_color = "#ff6b6b" if display < 0 else color
        row_cols[1 + i].markdown(
            f'<div style="font-size:13px;text-align:right;'
            f'padding-top:4px;font-weight:{weight};'
            f'color:{val_color}">{_fmt_proj_money(display)}</div>',
            unsafe_allow_html=True,
        )

    if is_total:
        st.markdown(
            '<hr style="margin:2px 0;'
            'border-color:rgba(28,131,225,0.3)">',
            unsafe_allow_html=True,
        )
