"""Comps Step 2 — HTML table renderer.

Renders the comps table as a single HTML table with:
- Target row highlighted
- Peer rows (grayed if excluded)
- Summary rows (Mean, Median, High, Low)

Supports both normal and financial company column sets.
Split from comps_step2_table.py for file size compliance.
"""

import streamlit as st

# ── Column definitions ─────────────────────────────────────────

# Normal companies: (key, header, format_type)
RAW_COLS_NORMAL = [
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

MULT_COLS_NORMAL = [
    ("ev_revenue", "EV/Rev", "mult"),
    ("ev_ebitda", "EV/EBITDA", "mult"),
    ("ev_ebit", "EV/EBIT", "mult"),
    ("trailing_pe", "P/E", "mult"),
    ("forward_pe", "Fwd P/E", "mult"),
    ("fwd_ev_revenue", "Fwd EV/Rev", "mult"),
    ("fwd_ev_ebitda", "Fwd EV/EBITDA*", "mult"),
]

# Financial companies (banks, insurance)
RAW_COLS_FINANCIAL = [
    ("ticker", "Ticker", "text"),
    ("name", "Company", "text"),
    ("price", "Price", "price"),
    ("market_cap", "Mkt Cap", "money"),
    ("book_value_ps", "Book/Share", "price"),
    ("tangible_book_ps", "TBV/Share", "price"),
    ("net_income", "Net Inc", "money"),
    ("eps", "EPS", "price"),
    ("dividend_yield", "Div Yield", "pct"),
]

MULT_COLS_FINANCIAL = [
    ("trailing_pe", "P/E", "mult"),
    ("forward_pe", "Fwd P/E", "mult"),
    ("price_to_book", "P/Book", "mult"),
    ("price_to_tbv", "P/TBV", "mult"),
    ("dividend_yield", "Div Yield", "pct"),
]


# ── Formatters ─────────────────────────────────────────────────


def _fmt(val, fmt_type: str) -> str:
    """Format a value based on type."""
    if val is None:
        return "N/A"
    if fmt_type == "text":
        return str(val)
    if fmt_type == "price":
        return f"${val:,.2f}"
    if fmt_type == "pct":
        return f"{val * 100:.1f}%" if val else "N/A"
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
    is_financial: bool = False,
) -> None:
    """Render full comps HTML table."""
    raw_cols = RAW_COLS_FINANCIAL if is_financial else RAW_COLS_NORMAL
    mult_cols = MULT_COLS_FINANCIAL if is_financial else MULT_COLS_NORMAL

    html = _TABLE_CSS + '<table class="comps-tbl">'
    html += _build_header(raw_cols, mult_cols)
    html += "<tbody>"
    html += _build_data_row(target, raw_cols, mult_cols, "target-row")
    for p in peers:
        cls = "excluded-row" if p["ticker"] in excluded else ""
        html += _build_data_row(p, raw_cols, mult_cols, cls)
    for label in ["Median", "Mean", "High", "Low"]:
        stats = summary.get(label.lower(), {})
        html += _build_summary_row(label, stats, raw_cols, mult_cols)
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)


# ── HTML builders ──────────────────────────────────────────────


def _build_header(raw_cols, mult_cols) -> str:
    """Build two-tier header: block labels + column names."""
    n_raw = len(raw_cols)
    n_mult = len(mult_cols)
    tier1 = (
        "<thead>"
        f'<tr class="block-header">'
        f'<th colspan="{n_raw}">Financials</th>'
        f'<th colspan="{n_mult}" class="mult-block">'
        f"Trading Multiples</th></tr>"
    )
    tier2 = "<tr>"
    for _, header, fmt_type in raw_cols:
        align = "left" if fmt_type == "text" else "right"
        tier2 += f'<th class="{align}">{header}</th>'
    for _, header, _ in mult_cols:
        tier2 += f'<th class="right mult-col">{header}</th>'
    tier2 += "</tr></thead>"
    return tier1 + tier2


def _build_data_row(
    row: dict, raw_cols, mult_cols, row_class: str = "",
) -> str:
    """Build a single <tr> for a company."""
    cls = f' class="{row_class}"' if row_class else ""
    tr = f"<tr{cls}>"
    for key, _, fmt_type in raw_cols:
        align = "left" if fmt_type == "text" else "right"
        tr += f'<td class="{align}">{_fmt(row.get(key), fmt_type)}</td>'
    for key, _, fmt_type in mult_cols:
        tr += f'<td class="right mult-col">{_fmt(row.get(key), fmt_type)}</td>'
    tr += "</tr>"
    return tr


def _build_summary_row(
    label: str, stats: dict, raw_cols, mult_cols,
) -> str:
    """Build a summary row (Mean/Median/High/Low)."""
    is_primary = label in ("Median", "Mean")
    cls = "summary-row primary" if is_primary else "summary-row"
    tr = f'<tr class="{cls}">'
    tr += f'<td class="left summary-label">{label}</td>'
    for _ in raw_cols[1:]:
        tr += "<td></td>"
    for key, _, fmt_type in mult_cols:
        val = stats.get(key)
        tr += f'<td class="right mult-col">{_fmt(val, fmt_type)}</td>'
    tr += "</tr>"
    return tr


# ── CSS ────────────────────────────────────────────────────────

_TABLE_CSS = """
<style>
.comps-tbl {
    width: 100%; border-collapse: collapse; font-size: 12px; margin: 8px 0;
}
.comps-tbl th, .comps-tbl td { padding: 5px 8px; white-space: nowrap; }
.comps-tbl th {
    font-weight: 600; border-bottom: 2px solid rgba(128,128,128,0.4);
}
.comps-tbl th.left, .comps-tbl td.left { text-align: left; }
.comps-tbl th.right, .comps-tbl td.right { text-align: right; }
.comps-tbl .block-header th {
    font-size: 11px; text-transform: uppercase;
    letter-spacing: 0.5px; padding: 4px 8px;
    border-bottom: 1px solid rgba(128,128,128,0.2);
}
.comps-tbl .mult-block { border-left: 2px solid rgba(28,131,225,0.3); }
.comps-tbl .mult-col { border-left: 1px solid rgba(128,128,128,0.1); }
.comps-tbl td { border-bottom: 1px solid rgba(128,128,128,0.1); }
.comps-tbl .target-row { background: rgba(28,131,225,0.08); font-weight: 600; }
.comps-tbl .excluded-row { opacity: 0.4; text-decoration: line-through; }
.comps-tbl .summary-row td {
    border-top: 2px solid rgba(128,128,128,0.3); font-weight: 500;
}
.comps-tbl .summary-row.primary td {
    font-weight: 700; background: rgba(28,131,225,0.04);
}
.comps-tbl .summary-label { font-weight: 700; font-style: italic; }
</style>
"""
