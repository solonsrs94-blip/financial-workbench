"""Summary tab — combined valuation overview from all models."""

import streamlit as st
import numpy as np

from pages.valuation.summary_table import render_valuation_table
from pages.valuation.summary_football import render_combined_football


def render(prepared: dict, ticker: str) -> None:
    """Render Summary tab."""
    st.subheader("Valuation Summary")
    st.caption(
        "Executive summary combining results from all completed "
        "valuation models. Uncheck a model to exclude it from the "
        "consensus."
    )

    current_price = _get_current_price(ticker)
    all_rows = _collect_rows(current_price)
    all_bars = _collect_bars()

    if not all_rows:
        st.info(
            "No valuation models have been completed yet. "
            "Complete at least one model (DCF, Comps, Historical, or DDM) "
            "to see the summary."
        )
        return

    # ── Model selector ─────────────────────────────────────
    available = _available_groups(all_rows)
    included = _render_model_selector(available)
    rows = [r for r in all_rows if _row_group(r) in included]
    bars = [b for b in all_bars if _bar_group(b) in included]
    excluded = [r for r in all_rows if _row_group(r) not in included]

    # ── Section 1: Current price reference ─────────────────
    if current_price > 0:
        st.markdown(
            f'<div style="font-size:13px;opacity:0.6">'
            f'Current Market Price: <b>${current_price:,.2f}</b>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Section 2: Valuation overview table ────────────────
    if rows:
        render_valuation_table(rows, current_price)
    else:
        st.info("All models excluded. Check at least one above.")

    # ── Section 3: Combined football field ─────────────────
    st.markdown("---")
    if bars:
        render_combined_football(bars, current_price)

    # ── Section 4: Summary statistics ──────────────────────
    if len(rows) > 1:
        st.markdown("---")
        _render_summary_stats(rows, current_price)

    # ── Section 5: Excluded models (grayed out) ────────────
    if excluded:
        st.markdown("---")
        _render_excluded(excluded, current_price)


_GROUP_ORDER = ["DCF", "Comps", "Historical", "DDM"]


def _row_group(row: dict) -> str:
    """Map a row's method name to its model group."""
    m = row["method"]
    if m.startswith("DCF"):
        return "DCF"
    if m.startswith("Comps"):
        return "Comps"
    if m.startswith("Historical"):
        return "Historical"
    if m.startswith("DDM"):
        return "DDM"
    return m


def _bar_group(bar: dict) -> str:
    """Map a bar's label to its model group."""
    return _row_group({"method": bar["label"]})


def _available_groups(rows: list[dict]) -> list[str]:
    """Return ordered list of model groups present in rows."""
    present = {_row_group(r) for r in rows}
    return [g for g in _GROUP_ORDER if g in present]


def _render_model_selector(available: list[str]) -> set[str]:
    """Render checkboxes and return set of included model groups."""
    cols = st.columns(len(available))
    included = set()
    for i, group in enumerate(available):
        key = f"summary_include_{group}"
        default = st.session_state.get(key, True)
        checked = cols[i].checkbox(
            group, value=default, key=key,
        )
        if checked:
            included.add(group)
    return included


def _render_excluded(rows: list[dict], current_price: float):
    """Show excluded models in a muted style."""
    parts = ["#### Excluded from Consensus"]
    for r in rows:
        imp = r["implied"]
        up = (imp / current_price - 1) * 100 if current_price > 0 else 0
        parts.append(f"- ~~{r['method']}~~: ${imp:,.2f} ({up:+.1f}%)")
    st.markdown(
        f'<div style="opacity:0.45">\n\n' + "\n".join(parts) + "\n</div>",
        unsafe_allow_html=True,
    )


def _collect_rows(current_price: float) -> list[dict]:
    """Collect implied price rows from all completed models."""
    rows = []
    dcf = st.session_state.get("dcf_output")
    if dcf and dcf.get("implied_price"):
        w, tg = dcf.get("wacc", 0), dcf.get("terminal_growth", 0)
        rows.append({"method": "DCF", "implied": dcf["implied_price"],
                      "notes": f"WACC: {w*100:.1f}%, g: {tg*100:.1f}%"})
    comps = st.session_state.get("comps_valuation")
    if comps and comps.get("implied_prices"):
        for key, data in comps["implied_prices"].items():
            if data is None:
                continue
            med = data.get("median")
            if med is None or med <= 0:
                continue
            label = data.get("label", key)
            rows.append({
                "method": f"Comps ({label})",
                "implied": med,
                "notes": f"Peer median {label}",
            })

    hist = st.session_state.get("historical_result")
    if hist and hist.get("implied_values"):
        per = hist.get("period", "?")
        for key, iv in hist["implied_values"].items():
            if not iv:
                continue
            med = iv.get("at_median")
            if not med or med <= 0:
                continue
            lbl = _HIST_LABELS.get(key, key)
            rows.append({"method": f"Historical ({lbl})", "implied": med,
                          "notes": f"{per}Y median {lbl}"})
    # DDM — primary model + alt model (if available)
    for ddm_key in ["ddm_output", "ddm_output_alt"]:
        ddm = st.session_state.get(ddm_key)
        if ddm and ddm.get("implied_price") and ddm["implied_price"] > 0:
            ml = "Gordon Growth" if ddm.get("model") == "gordon" else "2-Stage"
            ke, g = ddm.get("ke", 0), ddm.get("g", 0)
            rows.append({"method": f"DDM ({ml})", "implied": ddm["implied_price"],
                          "notes": f"Ke: {ke*100:.1f}%, g: {g*100:.1f}%"})
    return rows


def _collect_bars() -> list[dict]:
    """Collect football field bar data from all completed models."""
    bars = []

    # DCF — sensitivity range
    dcf = st.session_state.get("dcf_output")
    if dcf and dcf.get("implied_price"):
        lo = dcf.get("sensitivity_min", dcf["implied_price"])
        hi = dcf.get("sensitivity_max", dcf["implied_price"])
        bars.append({
            "label": "DCF",
            "low": lo, "high": hi,
            "mid": dcf["implied_price"],
            "color": "rgba(28, 131, 225, 0.5)",
            "marker_color": "#1c83e1",
        })

    # Comps — one bar per multiple (low → high)
    comps = st.session_state.get("comps_valuation")
    if comps and comps.get("implied_prices"):
        for key, data in comps["implied_prices"].items():
            if data is None:
                continue
            lo = data.get("low")
            hi = data.get("high")
            med = data.get("median")
            if lo is None or hi is None or med is None:
                continue
            label = data.get("label", key)
            bars.append({
                "label": f"Comps ({label})",
                "low": lo, "high": hi, "mid": med,
                "color": "rgba(63, 185, 80, 0.5)",
                "marker_color": "#3fb950",
            })

    # Historical — one bar per multiple (p10 → p90)
    hist = st.session_state.get("historical_result")
    if hist and hist.get("implied_values"):
        for key, iv in hist["implied_values"].items():
            if iv is None:
                continue
            lo = iv.get("at_p10")
            hi = iv.get("at_p90")
            med = iv.get("at_median")
            if lo is None or hi is None or med is None:
                continue
            if lo <= 0 or hi <= 0:
                continue
            label = _HIST_LABELS.get(key, key)
            bars.append({
                "label": f"Historical ({label})",
                "low": lo, "high": hi, "mid": med,
                "color": "rgba(210, 153, 34, 0.5)",
                "marker_color": "#d29922",
            })

    # DDM — primary + alt model
    for ddm_key in ["ddm_output", "ddm_output_alt"]:
        ddm = st.session_state.get(ddm_key)
        if ddm and ddm.get("implied_price") and ddm["implied_price"] > 0:
            lo = ddm.get("sensitivity_min", ddm["implied_price"])
            hi = ddm.get("sensitivity_max", ddm["implied_price"])
            ml = "Gordon" if ddm.get("model") == "gordon" else "2-Stage"
            bars.append({
                "label": f"DDM ({ml})",
                "low": lo, "high": hi, "mid": ddm["implied_price"],
                "color": "rgba(163, 113, 247, 0.5)",
                "marker_color": "#a371f7",
            })

    return bars


def _render_summary_stats(rows: list[dict], current_price: float) -> None:
    """Cross-method summary statistics (included models only)."""
    st.markdown("#### Summary Statistics")
    prices = [r["implied"] for r in rows]
    mean_p, median_p = float(np.mean(prices)), float(np.median(prices))
    lo, hi = min(prices), max(prices)
    spread = (hi - lo) / mean_p * 100 if mean_p > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Mean", f"${mean_p:,.2f}")
    c2.metric("Median", f"${median_p:,.2f}")
    c3.metric("Range", f"${lo:,.0f} – ${hi:,.0f}")
    c4.metric("Spread", f"{spread:.0f}%")

    if current_price > 0:
        up_mean = (mean_p / current_price - 1) * 100
        up_med = (median_p / current_price - 1) * 100
        cm = "#2ea043" if up_mean > 0 else "#f85149"
        cd = "#2ea043" if up_med > 0 else "#f85149"
        st.markdown(
            f'<div style="font-size:13px;opacity:0.7;margin-top:4px">'
            f'Consensus — Mean: <span style="color:{cm}">{up_mean:+.1f}%</span>'
            f' · Median: <span style="color:{cd}">{up_med:+.1f}%</span></div>',
            unsafe_allow_html=True,
        )


_HIST_LABELS = {
    "pe": "P/E",
    "ev_ebitda": "EV/EBITDA",
    "ev_revenue": "EV/Revenue",
    "p_book": "P/Book",
    "p_tbv": "P/TBV",
}


def _get_current_price(ticker: str) -> float:
    """Get current share price from session state."""
    company = st.session_state.get(f"company_{ticker}")
    if company:
        price_obj = getattr(company, "price", None)
        return getattr(price_obj, "price", 0) or 0
    return 0.0
