"""Financial table component — clean, readable financial statement tables.

Renders IS/BS/CF data as HTML tables with:
- Formatted numbers ($B, $M, %)
- Negative values in accounting format: ($52.5B) instead of $-52.5B
- True negatives (losses, declines) in red
- Zero treated as dash for optional items
- Source tags per year
"""

import streamlit as st


def _fmt_number(val, scale: str = "auto", red_negative: bool = True) -> str:
    """Format a number for display.

    Args:
        val: Number to format
        scale: "auto", "pct", "days", "ratio"
        red_negative: If True, negative values get red color
    """
    if val is None:
        return "&mdash;"
    v = float(val)

    if scale == "pct":
        if v == 0:
            return "&mdash;"
        neg = ' class="neg"' if (v < 0 and red_negative) else ""
        return f'<span{neg}>{v*100:.1f}%</span>'
    elif scale == "days":
        if v == 0:
            return "&mdash;"
        return f'{v:.0f}'
    elif scale == "ratio":
        if v == 0:
            return "&mdash;"
        return f'{v:.2f}x'

    # Auto scale for dollar amounts
    av = abs(v)
    if av < 0.5:
        return "&mdash;"

    # Format the absolute value
    if av >= 1e12:
        s = f"${av/1e12:,.1f}T"
    elif av >= 1e9:
        s = f"${av/1e9:,.1f}B"
    elif av >= 1e6:
        s = f"${av/1e6:,.0f}M"
    elif av >= 1e3:
        s = f"${av/1e3:,.0f}K"
    else:
        s = f"${av:,.0f}"

    # Negative: accounting format ($X) with optional red
    if v < 0:
        neg_cls = ' class="neg"' if red_negative else ""
        return f'<span{neg_cls}>({s})</span>'

    return s


def render_financial_table(
    rows: list[dict],
    fields: list[tuple],
    title: str = "",
    show_source: bool = True,
) -> None:
    """Render a financial table.

    Args:
        rows: List of per-year dicts (from build_income_table etc.)
        fields: List of tuples defining rows to show:
            (key, label, scale) or (key, label, scale, red_negative)
            scale: "auto", "pct", "days", "ratio"
        title: Optional title above table
        show_source: Show source tag in header
    """
    if not rows:
        st.info("No data available.")
        return

    # Build HTML
    html = '<div class="fin-table-wrap"><table class="fin-table">'

    # Header
    html += "<thead><tr><th></th>"
    for r in rows:
        yr = r["year"]
        src = r.get("source", "")
        src_tag = (
            f'<span class="source-tag">{src}</span>'
            if show_source and src else ""
        )
        html += f"<th>{yr} {src_tag}</th>"
    html += "</tr></thead>"

    # Body
    html += "<tbody>"
    for field_def in fields:
        key = field_def[0]
        label = field_def[1]
        scale = field_def[2] if len(field_def) > 2 else "auto"
        red_neg = field_def[3] if len(field_def) > 3 else True

        # Detect total/summary rows from label prefix
        is_total = label.startswith("=") or label.startswith(">>")
        clean_label = label.lstrip("= >")
        row_cls = ' class="total-row"' if is_total else ""

        # Check if entire row is empty — skip it
        all_none = all(r.get(key) is None for r in rows)
        if all_none:
            continue

        html += f"<tr{row_cls}><td>{clean_label}</td>"
        for r in rows:
            val = r.get(key)
            html += f"<td>{_fmt_number(val, scale, red_neg)}</td>"
        html += "</tr>"
    html += "</tbody></table></div>"

    if title:
        st.markdown(f"**{title}**")
    st.markdown(html, unsafe_allow_html=True)
