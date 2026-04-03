"""Comps Step 2 — HTML table renderer.

Renders the comps table as a single HTML table with:
- Target row highlighted
- Peer rows (grayed if excluded)
- Summary rows (Mean, Median, High, Low)

Split from comps_step2_table.py for file size compliance.
"""

import streamlit as st

# ── Column definitions ─────────────────────────────────────────

# (key, header, format_fn)
_RAW_COLS = [
    ("ticker", "Ticker", "text"),
    ("name", "Company", "text"),
    ("price", "Price", "price"),
    ("market_cap", "Mkt Cap", "money"),
    ("enterprise_value", "EV", "money"),
    ("revenue", "Revenue", "money"),
    ("ebitda", "EBITDA", "money"),
    ("ebit", "EBIT", "money"),
    ("net_income", "Net Inc", "money"),
    ("eps", "EPS", "price"),
]

_MULT_COLS = [
    ("ev_revenue", "EV/Rev", "mult"),
    ("ev_ebitda", "EV/EBITDA", "mult"),
    ("ev_ebit", "EV/EBIT", "mult"),
    ("trailing_pe", "P/E", "mult"),
    ("forward_pe", "Fwd P/E", "mult"),
    ("fwd_ev_revenue", "Fwd EV/Rev", "mult"),
    ("fwd_ev_ebitda", "Fwd EV/EBITDA*", "mult"),
]

_SUMMARY_MULT_KEYS = [c[0] for c in _MULT_COLS]


# ── Formatters ─────────────────────────────────────────────────


def _fmt(val, fmt_type: str) -> str:
    """Format a value based on type."""
    if val is None:
        return "N/A"

    if fmt_type == "text":
        return str(val)

    if fmt_type == "price":
        return f"${val:,.2f}"

    if fmt_type == "money":
        av = abs(val)
        if av >= 1e12:
            return f"${val / 1e12:.2f}T"
        if av >= 1e9:
            return f"${val / 1e9:.1f}B"
        if av >= 1e6:
            return f"${val / 1e6:.0f}M"
        return f"${val:,.0f}"

    if fmt_type == "mult":
        if val <= 0:
            return "N/A"
        return f"{val:.1f}x"

    return str(val)


# ── Main renderer ──────────────────────────────────────────────


def render_comps_table(
    target: dict,
    peers: list[dict],
    summary: dict,
    excluded: set,
) -> None:
    """Render full comps HTML table."""
    html = _TABLE_CSS + '<table class="comps-tbl">'

    # Header rows (two-tier: block labels + column headers)
    html += _build_header()

    # Body
    html += "<tbody>"

    # Target row
    html += _build_data_row(target, row_class="target-row")

    # Peer rows
    for p in peers:
        cls = "excluded-row" if p["ticker"] in excluded else ""
        html += _build_data_row(p, row_class=cls)

    # Summary rows
    for label in ["Median", "Mean", "High", "Low"]:
        key = label.lower()
        stats = summary.get(key, {})
        html += _build_summary_row(label, stats)

    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)


# ── HTML builders ──────────────────────────────────────────────


def _build_header() -> str:
    """Build two-tier header: block labels + column names."""
    # Tier 1: block labels
    n_raw = len(_RAW_COLS)
    n_mult = len(_MULT_COLS)
    tier1 = (
        "<thead>"
        f'<tr class="block-header">'
        f'<th colspan="{n_raw}">Financials</th>'
        f'<th colspan="{n_mult}" class="mult-block">Trading Multiples</th>'
        f"</tr>"
    )

    # Tier 2: column headers
    tier2 = "<tr>"
    for _, header, fmt_type in _RAW_COLS:
        align = "left" if fmt_type == "text" else "right"
        tier2 += f'<th class="{align}">{header}</th>'
    for _, header, _ in _MULT_COLS:
        tier2 += f'<th class="right mult-col">{header}</th>'
    tier2 += "</tr></thead>"

    return tier1 + tier2


def _build_data_row(row: dict, row_class: str = "") -> str:
    """Build a single <tr> for a company."""
    cls = f' class="{row_class}"' if row_class else ""
    tr = f"<tr{cls}>"

    for key, _, fmt_type in _RAW_COLS:
        align = "left" if fmt_type == "text" else "right"
        val = row.get(key)
        tr += f'<td class="{align}">{_fmt(val, fmt_type)}</td>'

    for key, _, fmt_type in _MULT_COLS:
        val = row.get(key)
        tr += f'<td class="right mult-col">{_fmt(val, fmt_type)}</td>'

    tr += "</tr>"
    return tr


def _build_summary_row(label: str, stats: dict) -> str:
    """Build a summary row (Mean/Median/High/Low)."""
    is_primary = label in ("Median", "Mean")
    cls = "summary-row primary" if is_primary else "summary-row"

    tr = f'<tr class="{cls}">'

    # First col = label, rest of raw cols empty
    tr += f'<td class="left summary-label">{label}</td>'
    for _ in _RAW_COLS[1:]:
        tr += "<td></td>"

    # Multiple cols
    for key, _, fmt_type in _MULT_COLS:
        val = stats.get(key)
        tr += f'<td class="right mult-col">{_fmt(val, fmt_type)}</td>'

    tr += "</tr>"
    return tr


# ── CSS ────────────────────────────────────────────────────────

_TABLE_CSS = """
<style>
.comps-tbl {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
    margin: 8px 0;
}
.comps-tbl th, .comps-tbl td {
    padding: 5px 8px;
    white-space: nowrap;
}
.comps-tbl th {
    font-weight: 600;
    border-bottom: 2px solid rgba(128,128,128,0.4);
}
.comps-tbl th.left, .comps-tbl td.left { text-align: left; }
.comps-tbl th.right, .comps-tbl td.right { text-align: right; }
.comps-tbl .block-header th {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 4px 8px;
    border-bottom: 1px solid rgba(128,128,128,0.2);
}
.comps-tbl .mult-block {
    border-left: 2px solid rgba(28,131,225,0.3);
}
.comps-tbl .mult-col {
    border-left: 1px solid rgba(128,128,128,0.1);
}
.comps-tbl td {
    border-bottom: 1px solid rgba(128,128,128,0.1);
}
.comps-tbl .target-row {
    background: rgba(28,131,225,0.08);
    font-weight: 600;
}
.comps-tbl .excluded-row {
    opacity: 0.4;
    text-decoration: line-through;
}
.comps-tbl .summary-row td {
    border-top: 2px solid rgba(128,128,128,0.3);
    font-weight: 500;
}
.comps-tbl .summary-row.primary td {
    font-weight: 700;
    background: rgba(28,131,225,0.04);
}
.comps-tbl .summary-label {
    font-weight: 700;
    font-style: italic;
}
</style>
"""
