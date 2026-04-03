"""Historical Multiples — summary statistics + implied value tables."""

import streamlit as st

# ── Labels ────────────────────────────────────────────────────

_LABELS = {
    "pe": "P/E",
    "ev_ebitda": "EV/EBITDA",
    "ev_revenue": "EV/Revenue",
    "p_book": "P/Book",
    "p_tbv": "P/TBV",
}

_ORDINALS = {1: "st", 2: "nd", 3: "rd"}


def _ordinal(n: int) -> str:
    """Return integer with ordinal suffix (1st, 2nd, 3rd, 4th...)."""
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    return f"{n}{_ORDINALS.get(n % 10, 'th')}"


# ── Public ────────────────────────────────────────────────────


def render_historical_summary(
    summary: dict,
    implied: dict,
    current_price: float,
    currency: str,
) -> None:
    """Render summary stats table + implied value table."""
    _render_stats_table(summary)
    st.markdown("")  # spacer
    _render_implied_table(implied, current_price, currency)


# ── Summary statistics table ──────────────────────────────────


def _render_stats_table(summary: dict) -> None:
    """Render summary statistics as HTML table."""
    st.markdown("#### Summary Statistics")

    if not summary:
        st.info("No summary data available.")
        return

    header = (
        "<tr><th>Multiple</th><th>Current</th><th>Mean</th>"
        "<th>Median</th><th>Min</th><th>Max</th>"
        "<th>-1&sigma;</th><th>+1&sigma;</th><th>Percentile</th></tr>"
    )
    rows = []
    for key in ["pe", "ev_ebitda", "ev_revenue", "p_book", "p_tbv"]:
        s = summary.get(key)
        if not s:
            continue
        label = _LABELS.get(key, key)
        pct = _ordinal(s["percentile"])

        # Color-code percentile
        p = s["percentile"]
        if p >= 75:
            pct_color = "#f85149"  # expensive
        elif p <= 25:
            pct_color = "#3fb950"  # cheap
        else:
            pct_color = "#d29922"  # fair

        rows.append(
            f"<tr>"
            f"<td><b>{label}</b></td>"
            f"<td>{s['current']:.1f}x</td>"
            f"<td>{s['mean']:.1f}x</td>"
            f"<td>{s['median']:.1f}x</td>"
            f"<td>{s['min']:.1f}x</td>"
            f"<td>{s['max']:.1f}x</td>"
            f"<td>{s['minus_1std']:.1f}x</td>"
            f"<td>{s['plus_1std']:.1f}x</td>"
            f'<td style="color:{pct_color};font-weight:600">{pct}</td>'
            f"</tr>"
        )

    if not rows:
        st.info("No valid multiples to display.")
        return

    html = (
        '<table style="width:100%;border-collapse:collapse;'
        'font-size:0.88em;text-align:right">'
        f"<thead>{header}</thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )
    st.markdown(html, unsafe_allow_html=True)


# ── Implied value table ───────────────────────────────────────


def _render_implied_table(
    implied: dict, current_price: float, currency: str,
) -> None:
    """Render implied fair value table."""
    st.markdown("#### Implied Value (Historical Averages)")

    if not implied or not current_price:
        st.info("Insufficient data for implied value calculation.")
        return

    sym = "$" if currency == "USD" else currency + " "

    header = (
        "<tr><th>Multiple</th><th>Current</th><th>At Mean</th>"
        "<th>At Median</th><th>At -1&sigma;</th>"
        "<th>Upside/Downside</th></tr>"
    )
    rows = []
    for key in ["pe", "ev_ebitda", "ev_revenue", "p_book", "p_tbv"]:
        iv = implied.get(key)
        if not iv:
            continue
        label = _LABELS.get(key, key)
        upside = iv["upside_mean"]
        color = "#3fb950" if upside > 0 else "#f85149"
        sign = "+" if upside > 0 else ""

        rows.append(
            f"<tr>"
            f"<td><b>{label}</b></td>"
            f"<td>{sym}{current_price:,.0f}</td>"
            f"<td>{sym}{iv['at_mean']:,.0f}</td>"
            f"<td>{sym}{iv['at_median']:,.0f}</td>"
            f"<td>{sym}{iv['at_minus_1std']:,.0f}</td>"
            f'<td style="color:{color};font-weight:600">'
            f"{sign}{upside:.0%} (mean)</td>"
            f"</tr>"
        )

    if not rows:
        st.info("No implied values available.")
        return

    html = (
        '<table style="width:100%;border-collapse:collapse;'
        'font-size:0.88em;text-align:right">'
        f"<thead>{header}</thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )
    st.markdown(html, unsafe_allow_html=True)
