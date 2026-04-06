"""Summary tab helpers — DCF/DDM scenario format handling + stats.

Extracted from summary_tab.py to keep files under 300 lines.
"""

import streamlit as st

from pages.valuation.summary_weights import (  # noqa: F401 — re-export
    render_weight_inputs,
    compute_weighted_fair_value,
    render_summary_stats,
)


def is_scenario_format(dcf: dict) -> bool:
    """Check if dcf_output uses scenario structure."""
    return "base" in dcf and isinstance(dcf.get("base"), dict)


def collect_dcf_rows(dcf: dict, rows: list) -> None:
    """Add DCF row(s) — handles both scenario and legacy formats."""
    if is_scenario_format(dcf):
        labels = {"bear": "Bear", "base": "Base", "bull": "Bull"}
        for scenario in ["bear", "base", "bull"]:
            s = dcf.get(scenario)
            if not s or not s.get("implied_price"):
                continue
            w = s.get("wacc", 0)
            tg = s.get("terminal_growth", 0)
            rows.append({
                "method": f"DCF ({labels[scenario]})",
                "implied": s["implied_price"],
                "notes": f"WACC: {w*100:.1f}%, g: {tg*100:.1f}%",
            })
    elif dcf.get("implied_price"):
        w, tg = dcf.get("wacc", 0), dcf.get("terminal_growth", 0)
        rows.append({"method": "DCF", "implied": dcf["implied_price"],
                      "notes": f"WACC: {w*100:.1f}%, g: {tg*100:.1f}%"})


def collect_dcf_bars(dcf: dict, bars: list) -> None:
    """Add DCF bar(s) — handles both scenario and legacy formats."""
    if is_scenario_format(dcf):
        base = dcf.get("base", {})
        if not base or not base.get("implied_price"):
            return
        # Spanning bar: bear low → bull high, base as mid
        lo = base.get("sensitivity_min", base["implied_price"])
        hi = base.get("sensitivity_max", base["implied_price"])
        mid = base["implied_price"]
        bear = dcf.get("bear", {})
        bull = dcf.get("bull", {})
        if bear and bear.get("sensitivity_min"):
            lo = min(lo, bear["sensitivity_min"])
        if bull and bull.get("sensitivity_max"):
            hi = max(hi, bull["sensitivity_max"])
        lo = max(lo, 0)
        bars.append({
            "label": "DCF",
            "low": lo, "high": hi, "mid": mid,
            "color": "rgba(28, 131, 225, 0.5)",
            "marker_color": "#1c83e1",
        })
    elif dcf.get("implied_price"):
        lo = dcf.get("sensitivity_min", dcf["implied_price"])
        hi = dcf.get("sensitivity_max", dcf["implied_price"])
        lo = max(lo, 0)
        bars.append({
            "label": "DCF",
            "low": lo, "high": hi,
            "mid": dcf["implied_price"],
            "color": "rgba(28, 131, 225, 0.5)",
            "marker_color": "#1c83e1",
        })


def collect_ddm_rows(ddm: dict, rows: list) -> None:
    """Add DDM row(s) — handles both scenario and legacy formats."""
    if is_scenario_format(ddm):
        labels = {"bear": "Bear", "base": "Base", "bull": "Bull"}
        for scenario in ["bear", "base", "bull"]:
            s = ddm.get(scenario)
            if not s or not s.get("implied_price") or s["implied_price"] <= 0:
                continue
            ml = "Gordon" if s.get("model") == "gordon" else "2-Stage"
            ke, g = s.get("ke", 0), s.get("g", 0)
            rows.append({
                "method": f"DDM {ml} ({labels[scenario]})",
                "implied": s["implied_price"],
                "notes": f"Ke: {ke*100:.1f}%, g: {g*100:.1f}%",
            })
    elif ddm.get("implied_price") and ddm["implied_price"] > 0:
        ml = "Gordon Growth" if ddm.get("model") == "gordon" else "2-Stage"
        ke, g = ddm.get("ke", 0), ddm.get("g", 0)
        rows.append({"method": f"DDM ({ml})", "implied": ddm["implied_price"],
                      "notes": f"Ke: {ke*100:.1f}%, g: {g*100:.1f}%"})


def collect_ddm_bars(ddm: dict, bars: list) -> None:
    """Add DDM bar(s) — handles both scenario and legacy formats."""
    if is_scenario_format(ddm):
        base = ddm.get("base", {})
        if not base or not base.get("implied_price"):
            return
        lo = base.get("sensitivity_min", base["implied_price"])
        hi = base.get("sensitivity_max", base["implied_price"])
        mid = base["implied_price"]
        bear = ddm.get("bear", {})
        bull = ddm.get("bull", {})
        if bear and bear.get("sensitivity_min"):
            lo = min(lo, bear["sensitivity_min"])
        if bull and bull.get("sensitivity_max"):
            hi = max(hi, bull["sensitivity_max"])
        lo = max(lo, 0)
        bars.append({
            "label": "DDM",
            "low": lo, "high": hi, "mid": mid,
            "color": "rgba(163, 113, 247, 0.5)",
            "marker_color": "#a371f7",
        })
    elif ddm.get("implied_price") and ddm["implied_price"] > 0:
        lo = ddm.get("sensitivity_min", ddm["implied_price"])
        hi = ddm.get("sensitivity_max", ddm["implied_price"])
        lo = max(lo, 0)
        bars.append({
            "label": "DDM",
            "low": lo, "high": hi,
            "mid": ddm["implied_price"],
            "color": "rgba(163, 113, 247, 0.5)",
            "marker_color": "#a371f7",
        })


def collect_comps_rows(comps: dict, rows: list) -> None:
    """Add Comps row(s) — handles both scenario and legacy formats."""
    if is_scenario_format(comps):
        labels = {"bear": "Bear", "base": "Base", "bull": "Bull"}
        for scenario in ["bear", "base", "bull"]:
            s = comps.get(scenario)
            if not s or not s.get("implied_price"):
                continue
            mult = s.get("final_mult", 0)
            rows.append({
                "method": f"Comps ({labels[scenario]})",
                "implied": s["implied_price"],
                "notes": f"Multiple: {mult:.1f}x",
            })
    elif comps.get("implied_prices"):
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


def collect_comps_bars(comps: dict, bars: list) -> None:
    """Add Comps bar(s) — handles both scenario and legacy formats."""
    if is_scenario_format(comps):
        base = comps.get("base", {})
        if not base or not base.get("implied_price"):
            return
        mid = base["implied_price"]
        lo = mid
        hi = mid
        bear = comps.get("bear", {})
        bull = comps.get("bull", {})
        if bear and bear.get("implied_price"):
            lo = min(lo, bear["implied_price"])
        if bull and bull.get("implied_price"):
            hi = max(hi, bull["implied_price"])
        lo = max(lo, 0)
        bars.append({
            "label": "Comps",
            "low": lo, "high": hi, "mid": mid,
            "color": "rgba(63, 185, 80, 0.5)",
            "marker_color": "#3fb950",
        })
    elif comps.get("implied_prices"):
        for key, data in comps["implied_prices"].items():
            if data is None:
                continue
            lo = data.get("low")
            hi = data.get("high")
            med = data.get("median")
            if lo is None or hi is None or med is None:
                continue
            lo = max(lo, 0)
            label = data.get("label", key)
            bars.append({
                "label": f"Comps ({label})",
                "low": lo, "high": hi, "mid": med,
                "color": "rgba(63, 185, 80, 0.5)",
                "marker_color": "#3fb950",
            })


def collect_historical_rows(hist: dict, rows: list) -> None:
    """Add Historical row(s) — handles both scenario and legacy formats."""
    if is_scenario_format(hist):
        labels = {"bear": "Bear", "base": "Base", "bull": "Bull"}
        for scenario in ["bear", "base", "bull"]:
            s = hist.get(scenario)
            if not s or not s.get("implied_price"):
                continue
            mult = s.get("applied_mult", 0)
            mk = _HIST_MULT_LABELS.get(s.get("mult_key", ""), "")
            rows.append({
                "method": f"Historical ({labels[scenario]})",
                "implied": s["implied_price"],
                "notes": f"{mk} {mult:.1f}x" if mk else f"{mult:.1f}x",
            })
    elif hist.get("implied_values"):
        per = hist.get("period", "?")
        for key, iv in hist["implied_values"].items():
            if not iv:
                continue
            med = iv.get("at_median")
            if not med or med <= 0:
                continue
            lbl = _HIST_MULT_LABELS.get(key, key)
            rows.append({
                "method": f"Historical ({lbl})",
                "implied": med,
                "notes": f"{per}Y median {lbl}",
            })


def collect_historical_bars(hist: dict, bars: list) -> None:
    """Add Historical bar(s) — handles both scenario and legacy formats."""
    if is_scenario_format(hist):
        base = hist.get("base", {})
        if not base or not base.get("implied_price"):
            return
        mid = base["implied_price"]
        lo, hi = mid, mid
        bear = hist.get("bear", {})
        bull = hist.get("bull", {})
        if bear and bear.get("implied_price"):
            lo = min(lo, bear["implied_price"])
        if bull and bull.get("implied_price"):
            hi = max(hi, bull["implied_price"])
        lo = max(lo, 0)
        bars.append({
            "label": "Historical",
            "low": lo, "high": hi, "mid": mid,
            "color": "rgba(210, 153, 34, 0.5)",
            "marker_color": "#d29922",
        })
    elif hist.get("implied_values"):
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
            label = _HIST_MULT_LABELS.get(key, key)
            bars.append({
                "label": f"Historical ({label})",
                "low": lo, "high": hi, "mid": med,
                "color": "rgba(210, 153, 34, 0.5)",
                "marker_color": "#d29922",
            })


_HIST_MULT_LABELS = {
    "pe": "P/E",
    "ev_ebitda": "EV/EBITDA",
    "ev_revenue": "EV/Revenue",
    "p_book": "P/Book",
    "p_tbv": "P/TBV",
}
