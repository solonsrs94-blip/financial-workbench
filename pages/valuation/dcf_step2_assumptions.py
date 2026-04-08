"""Step 2: Assumptions + Projected Financials.

IB-style table: historical (left, read-only) | projected (right, editable).
Analyst fills in all assumptions manually — no pre-populated defaults.
Calculated FCF output appears below when all assumptions are complete.

Split into 4 files:
  - dcf_step2_assumptions.py (this) — controls + input rows + driver table
  - dcf_step2_scenarios.py — Bull/Base/Bear tab orchestration
  - dcf_step2_table.py — data extraction + projection math
  - dcf_step2_output.py — calculated output rendering
"""

import streamlit as st

from pages.valuation.dcf_step2_table import build_historical_data
from pages.valuation.dcf_step2_output import render_projected_revenue
from pages.valuation.dcf_step2_scenarios import (
    migrate_legacy,
    render_scenario_tabs,
)


# ── NWC method auto-detection ───────────────────────────────────────


def _detect_nwc_method(ratios: list[dict]) -> str:
    """Detect whether detailed NWC (DSO/DIO/DPO) is possible."""
    if not ratios:
        return "simplified"
    last = ratios[-1]
    has_detail = (
        last.get("dso") is not None
        and last.get("dio") is not None
        and last.get("dpo") is not None
    )
    return "detailed" if has_detail else "simplified"


# ── Input row renderer ──────────────────────────────────────────────


def _render_input_row(
    label: str,
    hist_values: list[str],
    assumption_key: str,
    assumptions: dict,
    n_years: int,
    proj_years: list[int],
    scenario: str = "base",
    suffix: str = "%",
    divisor: float = 100.0,
    is_days: bool = False,
) -> None:
    """Render one driver row: historical (read-only) + projected (inputs)."""
    n_hist = len(hist_values)
    cols = st.columns([1.5] + [1] * n_hist + [0.2] + [1] * n_years)

    _HIST_STYLE = ('font-size:13px;text-align:right;padding-top:6px;'
                   'opacity:0.6')
    cols[0].markdown(
        f'<div style="font-size:13px;font-weight:500;padding-top:6px">'
        f'{label}</div>', unsafe_allow_html=True)
    for i, val in enumerate(hist_values):
        cols[1 + i].markdown(
            f'<div style="{_HIST_STYLE}">{val}</div>',
            unsafe_allow_html=True)
    sep_idx = 1 + n_hist
    cols[sep_idx].markdown(
        '<div style="border-left:2px solid rgba(28,131,225,0.3);'
        'height:38px"></div>', unsafe_allow_html=True)

    # Projected inputs — scenario-prefixed widget keys
    vals = assumptions.get(assumption_key, [None] * n_years)
    for i in range(n_years):
        col_idx = sep_idx + 1 + i
        k = f"dcf_{scenario}_{assumption_key}_{i}"
        cur = vals[i]
        if is_days:
            new_val = cols[col_idx].number_input(
                f"{proj_years[i]}E", min_value=0.0, max_value=365.0,
                value=cur, step=1.0, format="%.0f",
                key=k, label_visibility="collapsed", placeholder="days")
        else:
            disp = cur * divisor if cur is not None else None
            raw = cols[col_idx].number_input(
                f"{proj_years[i]}E", min_value=-100.0, max_value=200.0,
                value=disp, step=0.5, format="%.1f",
                key=k, label_visibility="collapsed", placeholder=suffix)
            new_val = raw / divisor if raw is not None else None
        assumptions[assumption_key][i] = new_val


# ── Main render ─────────────────────────────────────────────────────


def render(prepared: dict, ticker: str) -> None:
    """Render Step 2: Assumptions + Projected Financials."""
    migrate_legacy()

    st.markdown("### Step 2: Assumptions & Projected Financials")
    st.caption(
        "Enter your assumptions for each projected year. "
        "Historical data is shown for reference. All projected fields "
        "start empty — fill them to see calculated FCF below."
    )

    ratios = prepared.get("ratios", [])
    standardized = prepared.get("standardized", {})
    years = prepared.get("years", [])

    if not years or not ratios:
        st.warning(
            "No historical data available. Run Financial Preparation first.",
        )
        return

    # ── Shared controls ─────────────────────────────────────────
    ctrl_cols = st.columns([1, 1, 3])

    with ctrl_cols[0]:
        n_years = st.selectbox(
            "Projection Period",
            options=[3, 4, 5, 6, 7, 8, 9, 10],
            index=2,  # default 5
            key="dcf_proj_period",
            help="Number of years to project. Most companies: 5-7.",
        )

    default_method = _detect_nwc_method(ratios)
    method_options = [
        "Detailed (DSO/DIO/DPO)",
        "Simplified (NWC/Revenue %)",
    ]
    default_idx = 0 if default_method == "detailed" else 1

    with ctrl_cols[1]:
        method_label = st.selectbox(
            "Working Capital Method",
            options=method_options,
            index=default_idx,
            key="dcf_nwc_method",
            help="Detailed uses days metrics. "
                 "Simplified uses NWC as % of revenue.",
        )

    nwc_method = (
        "detailed" if "Detailed" in method_label else "simplified"
    )

    # ── Historical data (shared across all scenarios) ────────────
    n_display = min(5, len(years))
    hist = build_historical_data(ratios, standardized, years, n_display)

    last_year = int(years[-1])
    proj_years = [last_year + i + 1 for i in range(n_years)]

    # ── Scenario tabs ────────────────────────────────────────────
    render_scenario_tabs(
        hist, n_years, proj_years, nwc_method,
        render_driver_table_fn=_render_driver_table,
    )



# ── Driver table ────────────────────────────────────────────────────


@st.fragment
def _render_driver_table(
    hist: dict,
    assumptions: dict,
    n_years: int,
    proj_years: list[int],
    nwc_method: str,
    scenario: str = "base",
) -> None:
    """Render the full driver input table with headers."""
    n_hist = len(hist["years"])
    sep_idx = 1 + n_hist

    # Column headers
    _HDR = 'text-align:right;font-weight:600;font-size:13px'
    hdr = st.columns([1.5] + [1] * n_hist + [0.2] + [1] * n_years)
    hdr[0].markdown("**Driver**")
    for i, yr in enumerate(hist["years"]):
        hdr[1 + i].markdown(
            f'<div style="{_HDR}">{yr}</div>', unsafe_allow_html=True)
    for i, yr in enumerate(proj_years):
        hdr[sep_idx + 1 + i].markdown(
            f'<div style="{_HDR};color:#1c83e1">{yr}E</div>',
            unsafe_allow_html=True)

    st.markdown(
        '<hr style="margin:4px 0;border-color:rgba(28,131,225,0.2)">',
        unsafe_allow_html=True,
    )

    # Revenue row (read-only historical + projected filled dynamically)
    _CELL = ('font-size:13px;text-align:right;padding-top:6px;'
             'opacity:0.6')
    col_spec = [1.5] + [1] * n_hist + [0.2] + [1] * n_years
    rev_cols = st.columns(col_spec)
    rev_cols[0].markdown(
        '<div style="font-size:13px;font-weight:600;padding-top:6px">'
        'Revenue ($M)</div>', unsafe_allow_html=True)
    for i, val in enumerate(hist["revenue"]):
        rev_cols[1 + i].markdown(
            f'<div style="{_CELL}">{val}</div>', unsafe_allow_html=True)
    rev_cols[sep_idx].markdown(
        '<div style="border-left:2px solid rgba(28,131,225,0.3);'
        'height:38px"></div>', unsafe_allow_html=True)

    # ── Assumption input rows ────────────────────────────────
    drivers = [
        ("Revenue Growth %", "revenue_growth", "growth_rates", False),
        ("EBIT Margin %", "ebit_margin", "ebit_margins", False),
        ("Tax Rate %", "tax_rate", "tax_rates", False),
        ("CapEx / Revenue %", "capex_pct", "capex_pcts", False),
        ("D&A / Revenue %", "da_pct", "da_pcts", False),
        ("SBC / Revenue %", "sbc_pct", "sbc_pcts", False),
    ]

    for label, hist_key, assumption_key, is_days in drivers:
        _render_input_row(
            label, hist[hist_key],
            assumption_key, assumptions, n_years, proj_years,
            scenario=scenario, is_days=is_days,
        )

    # Working capital separator
    st.markdown(
        '<hr style="margin:8px 0;border-color:rgba(128,128,128,0.2)">',
        unsafe_allow_html=True,
    )

    if nwc_method == "detailed":
        for label, hist_key, key in [
            ("DSO (days)", "dso", "dso"),
            ("DIO (days)", "dio", "dio"),
            ("DPO (days)", "dpo", "dpo"),
        ]:
            _render_input_row(
                label, hist[hist_key],
                key, assumptions, n_years, proj_years,
                scenario=scenario, is_days=True,
            )
    else:
        _render_input_row(
            "NWC / Revenue %", hist["nwc_pct"],
            "nwc_pcts", assumptions, n_years, proj_years,
            scenario=scenario,
        )

    # Show projected revenue
    render_projected_revenue(
        rev_cols, assumptions, hist, n_years, sep_idx,
    )
