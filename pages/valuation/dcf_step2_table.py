"""Step 2 table rendering — IB-style HTML table for assumptions + projections.

Builds the combined historical / projected table as HTML.
Split from dcf_step2_assumptions.py to stay under 300 lines.
"""
from typing import Optional


def _fmt_money(val: Optional[float]) -> str:
    """Format raw dollar value in millions (IB style: $391,035)."""
    if val is None:
        return "—"
    return f"${val / 1e6:,.0f}"


def _fmt_pct(val: Optional[float]) -> str:
    """Format decimal as percentage string."""
    if val is None:
        return "—"
    return f"{val * 100:.1f}%"


def _fmt_days(val: Optional[float]) -> str:
    """Format days value."""
    if val is None:
        return "—"
    return f"{val:.0f}"


def _fmt_proj_money(val: Optional[float]) -> str:
    """Format projected money (already in $M)."""
    return "—" if val is None else f"${val:,.0f}"


# ── Row builder ─────────────────────────────────────────────────────


def _build_header(hist_years: list[str], proj_years: list[int]) -> str:
    """Build table header row."""
    cols = ['<th style="text-align:left">Driver</th>']
    for yr in hist_years:
        cols.append(f"<th>{yr}</th>")
    # Separator
    cols.append('<th class="proj-sep"></th>')
    for yr in proj_years:
        cols.append(f'<th class="proj-col">{yr}E</th>')
    return "<tr>" + "".join(cols) + "</tr>"


def _build_input_row(
    label: str,
    hist_vals: list[str],
    n_proj: int,
    input_key: str,
    css_class: str = "",
) -> str:
    """Build a row with historical values + input placeholders.

    Input cells use data attributes for Streamlit to bind to.
    Returns HTML string. Actual inputs are rendered by Streamlit separately.
    """
    row_class = f' class="{css_class}"' if css_class else ""
    cells = [f'<td style="text-align:left">{label}</td>']
    for v in hist_vals:
        cells.append(f"<td>{v}</td>")
    cells.append('<td class="proj-sep"></td>')
    # Projected cells are empty — inputs rendered by Streamlit
    for i in range(n_proj):
        cells.append(f'<td class="proj-col input-cell" '
                     f'data-key="{input_key}_{i}">—</td>')
    return f"<tr{row_class}>{''.join(cells)}</tr>"


def _build_calc_row(
    label: str,
    hist_vals: list[str],
    proj_vals: list[str],
    css_class: str = "",
) -> str:
    """Build a row with historical + calculated projected values."""
    row_class = f' class="{css_class}"' if css_class else ""
    cells = [f'<td style="text-align:left">{label}</td>']
    for v in hist_vals:
        cells.append(f"<td>{v}</td>")
    cells.append('<td class="proj-sep"></td>')
    for v in proj_vals:
        cells.append(f'<td class="proj-col">{v}</td>')
    return f"<tr{row_class}>{''.join(cells)}</tr>"


# ── Main table builder ──────────────────────────────────────────────


def build_historical_data(
    ratios: list[dict],
    standardized: dict,
    years: list[str],
    n_display: int = 5,
) -> dict:
    """Extract historical driver values for display.

    Returns dict with lists of formatted values per driver.
    """
    # Use last n_display years
    display_years = years[-n_display:]
    display_ratios = ratios[-n_display:] if ratios else []

    # Revenue from standardized income statement (values in raw dollars).
    # Structure: standardized["income"][year][field] = plain value
    # (flattened from audit). Keys: "revenue" (primary) or "total_revenue".
    income_by_yr = standardized.get("income", {})
    revenues = []
    for yr in display_years:
        yr_inc = income_by_yr.get(yr, {})
        rev_val = yr_inc.get("total_revenue") or yr_inc.get("revenue")
        revenues.append(rev_val)

    # COGS % from last year (used for DIO/DPO projections)
    last_yr = years[-1]
    last_inc = income_by_yr.get(last_yr, {})
    last_rev = last_inc.get("total_revenue") or last_inc.get("revenue")
    last_cogs = last_inc.get("cost_of_revenue") or last_inc.get("cogs")
    if last_rev and last_cogs and last_rev != 0:
        base_cogs_pct = abs(last_cogs) / abs(last_rev)
    else:
        base_cogs_pct = 0.60  # fallback only when data is missing

    result = {
        "years": display_years,
        "revenue": [_fmt_money(r) for r in revenues],
        "revenue_raw": revenues,
        "base_cogs_pct": base_cogs_pct,
        "revenue_growth": [],
        "ebit_margin": [],
        "tax_rate": [],
        "capex_pct": [],
        "da_pct": [],
        "sbc_pct": [],
        "dso": [],
        "dio": [],
        "dpo": [],
        "nwc_pct": [],
    }

    for r in display_ratios:
        result["revenue_growth"].append(_fmt_pct(r.get("revenue_growth")))
        result["ebit_margin"].append(_fmt_pct(r.get("ebit_margin")))
        result["tax_rate"].append(_fmt_pct(r.get("effective_tax_rate")))
        result["capex_pct"].append(_fmt_pct(r.get("capex_pct")))
        result["da_pct"].append(_fmt_pct(r.get("da_pct")))
        result["sbc_pct"].append(_fmt_pct(r.get("sbc_pct")))
        result["dso"].append(_fmt_days(r.get("dso")))
        result["dio"].append(_fmt_days(r.get("dio")))
        result["dpo"].append(_fmt_days(r.get("dpo")))
        result["nwc_pct"].append(_fmt_pct(r.get("nwc_pct_revenue")))

    return result


def compute_projections(
    assumptions: dict,
    base_revenue: float,
    base_cogs_pct: float,
) -> Optional[dict]:
    """Compute projected financials from assumptions.

    Returns None if any assumption is missing.
    All monetary values returned in millions.
    """
    n = assumptions["n_years"]

    # Check all required assumptions are filled
    required = [
        "growth_rates", "ebit_margins", "tax_rates",
        "capex_pcts", "da_pcts", "sbc_pcts",
    ]
    for key in required:
        vals = assumptions.get(key, [])
        if not vals or any(v is None for v in vals[:n]):
            return None

    if assumptions["nwc_method"] == "detailed":
        for key in ["dso", "dio", "dpo"]:
            vals = assumptions.get(key, [])
            if not vals or any(v is None for v in vals[:n]):
                return None
    else:
        vals = assumptions.get("nwc_pcts", [])
        if not vals or any(v is None for v in vals[:n]):
            return None

    # Compute year by year
    proj = {
        "revenue": [], "ebit": [], "nopat": [], "da": [],
        "capex": [], "sbc": [], "nwc_change": [], "fcf": [],
    }
    prev_rev = base_revenue / 1e6  # raw dollars → millions
    prev_nwc = None

    for i in range(n):
        g = assumptions["growth_rates"][i]
        rev = prev_rev * (1 + g)
        ebit = rev * assumptions["ebit_margins"][i]
        nopat = ebit * (1 - assumptions["tax_rates"][i])
        da = rev * assumptions["da_pcts"][i]
        capex = rev * assumptions["capex_pcts"][i]
        sbc = rev * assumptions["sbc_pcts"][i]

        # NWC
        if assumptions["nwc_method"] == "detailed":
            cogs = rev * base_cogs_pct
            ar = rev * assumptions["dso"][i] / 365
            inv = cogs * assumptions["dio"][i] / 365
            ap = cogs * assumptions["dpo"][i] / 365
            nwc = ar + inv - ap
        else:
            nwc = rev * assumptions["nwc_pcts"][i]

        if prev_nwc is None:
            # Estimate base NWC from base year
            base_rev_m = base_revenue / 1e6
            if assumptions["nwc_method"] == "detailed":
                base_cogs = base_rev_m * base_cogs_pct
                prev_nwc = (
                    base_rev_m * assumptions["dso"][0] / 365
                    + base_cogs * assumptions["dio"][0] / 365
                    - base_cogs * assumptions["dpo"][0] / 365
                )
            else:
                prev_nwc = base_rev_m * assumptions["nwc_pcts"][0]

        d_nwc = nwc - prev_nwc
        fcf = nopat + da - capex - sbc - d_nwc

        proj["revenue"].append(rev)
        proj["ebit"].append(ebit)
        proj["nopat"].append(nopat)
        proj["da"].append(da)
        proj["capex"].append(capex)
        proj["sbc"].append(sbc)
        proj["nwc_change"].append(d_nwc)
        proj["fcf"].append(fcf)

        prev_rev = rev
        prev_nwc = nwc

    return proj


def render_calculated_table(
    hist: dict,
    proj: Optional[dict],
    proj_years: list[int],
) -> str:
    """Build HTML for the calculated output section."""
    n = len(proj_years)
    hist_years = hist["years"]

    rows = []
    # Section header
    rows.append(
        '<tr class="section-header">'
        '<td colspan="100" style="text-align:left;font-weight:700;'
        'padding-top:16px">Projected Financials</td></tr>'
    )
    rows.append(_build_header(hist_years, proj_years))

    # Revenue
    proj_rev = [_fmt_proj_money(v) for v in proj["revenue"]] if proj else ["—"] * n
    rows.append(_build_calc_row("Revenue", hist["revenue"], proj_rev))

    # EBIT
    proj_ebit = [_fmt_proj_money(v) for v in proj["ebit"]] if proj else ["—"] * n
    rows.append(_build_calc_row("EBIT", ["—"] * len(hist_years), proj_ebit, "sub-row"))

    # NOPAT
    proj_nopat = [_fmt_proj_money(v) for v in proj["nopat"]] if proj else ["—"] * n
    rows.append(_build_calc_row("NOPAT", ["—"] * len(hist_years), proj_nopat, "sub-row"))

    # + D&A
    proj_da = [_fmt_proj_money(v) for v in proj["da"]] if proj else ["—"] * n
    rows.append(_build_calc_row("+ D&A", ["—"] * len(hist_years), proj_da, "sub-row"))

    # - CapEx
    proj_capex = [_fmt_proj_money(-v) for v in proj["capex"]] if proj else ["—"] * n
    rows.append(_build_calc_row("− CapEx", ["—"] * len(hist_years), proj_capex, "sub-row"))

    # - SBC
    proj_sbc = [_fmt_proj_money(-v) for v in proj["sbc"]] if proj else ["—"] * n
    rows.append(_build_calc_row("− SBC", ["—"] * len(hist_years), proj_sbc, "sub-row"))

    # ± NWC Change
    proj_nwc = [_fmt_proj_money(-v) for v in proj["nwc_change"]] if proj else ["—"] * n
    rows.append(_build_calc_row("± NWC Change", ["—"] * len(hist_years), proj_nwc, "sub-row"))

    # = FCF
    proj_fcf = [_fmt_proj_money(v) for v in proj["fcf"]] if proj else ["—"] * n
    rows.append(_build_calc_row("= Free Cash Flow", ["—"] * len(hist_years), proj_fcf, "total-row"))

    return "\n".join(rows)
