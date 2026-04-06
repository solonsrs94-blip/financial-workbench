"""Summary tab — model weighting, weighted fair value, and stats.

Extracted from summary_helpers.py to keep files under 300 lines.
"""

import numpy as np
import streamlit as st


_GROUP_MAP = {"DCF": "dcf", "Comps": "comps", "Historical": "historical", "DDM": "ddm"}


def _row_group(row: dict) -> str:
    """Map a row's method name to its model group key."""
    m = row["method"]
    if m.startswith("DCF"):
        return "dcf"
    if m.startswith("Comps"):
        return "comps"
    if m.startswith("Historical"):
        return "historical"
    if m.startswith("DDM"):
        return "ddm"
    return m.lower()


def render_weight_inputs(included: set[str]) -> dict:
    """Render model weight inputs. Returns weights dict {group_key: decimal}.

    Only shows when 2+ models are included.
    """
    groups = [g for g in ["DCF", "Comps", "Historical", "DDM"] if g in included]
    if len(groups) < 2:
        return {}

    default_w = 100 // len(groups)
    remainder = 100 - default_w * len(groups)

    with st.expander("Model Weights", expanded=False):
        cols = st.columns(len(groups) + 1)
        raw = {}
        for i, group in enumerate(groups):
            key = _GROUP_MAP[group]
            default = default_w + (1 if i < remainder else 0)
            stored = st.session_state.get(f"summary_weight_{key}")
            val = stored if stored is not None else default
            raw[key] = cols[i].number_input(
                f"{group} %", min_value=0, max_value=100,
                value=val, step=5,
                key=f"summary_weight_{key}",
            )
        total = sum(raw.values())
        if total != 100:
            cols[-1].warning(f"Total: {total}%")
        else:
            cols[-1].success(f"Total: {total}%")

    # Normalize to decimals
    total = sum(raw.values())
    if total > 0:
        weights = {k: v / total for k, v in raw.items()}
    else:
        weights = {_GROUP_MAP[g]: 1 / len(groups) for g in groups}

    # Store for export
    st.session_state["summary_weights"] = weights
    return weights


def compute_weighted_fair_value(
    rows: list[dict], weights: dict | None,
) -> float | None:
    """Compute weighted fair value from base-case prices.

    Uses one representative price per model group (base case preferred).
    Returns None if weights are empty or no valid prices.
    """
    if not weights or not rows:
        return None

    # Get base-case price per group (prefer "Base" scenario row)
    group_prices = {}
    for row in rows:
        grp = _row_group(row)
        if grp not in weights:
            continue
        m = row["method"]
        # Prefer base case scenario
        if "(Base)" in m or "(Base Case)" in m:
            group_prices[grp] = row["implied"]
        elif grp not in group_prices:
            group_prices[grp] = row["implied"]

    if not group_prices:
        return None

    # Renormalize weights to only groups with prices
    active_w = {k: weights[k] for k in group_prices if k in weights}
    w_total = sum(active_w.values())
    if w_total <= 0:
        return None

    weighted = sum(
        group_prices[k] * (active_w[k] / w_total)
        for k in active_w
    )
    return weighted


def render_summary_stats(
    rows: list[dict], current_price: float, weights: dict | None = None,
) -> None:
    """Cross-method summary statistics (included models only)."""
    st.markdown("#### Summary Statistics")
    prices = [r["implied"] for r in rows]
    mean_p, median_p = float(np.mean(prices)), float(np.median(prices))
    lo, hi = min(prices), max(prices)
    spread = (hi - lo) / mean_p * 100 if mean_p > 0 else 0

    weighted_p = compute_weighted_fair_value(rows, weights)
    cols = st.columns(5) if weighted_p else st.columns(4)
    i = 0
    if weighted_p:
        cols[i].metric("Weighted", f"${weighted_p:,.2f}"); i += 1
    cols[i].metric("Mean", f"${mean_p:,.2f}"); i += 1
    cols[i].metric("Median", f"${median_p:,.2f}"); i += 1
    cols[i].metric("Range", f"${lo:,.0f} – ${hi:,.0f}"); i += 1
    cols[i].metric("Spread", f"{spread:.0f}%")

    if current_price > 0:
        ref = weighted_p or mean_p
        up = (ref / current_price - 1) * 100
        up_med = (median_p / current_price - 1) * 100
        cr = "#2ea043" if up > 0 else "#f85149"
        cd = "#2ea043" if up_med > 0 else "#f85149"
        lbl = "Weighted" if weighted_p else "Mean"
        st.markdown(
            f'<div style="font-size:13px;opacity:0.7;margin-top:4px">'
            f'Consensus — {lbl}: <span style="color:{cr}">{up:+.1f}%</span>'
            f' · Median: <span style="color:{cd}">{up_med:+.1f}%</span></div>',
            unsafe_allow_html=True,
        )
