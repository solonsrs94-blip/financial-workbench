"""Step 5: DCF Output — EV, equity bridge, implied price, sensitivity.

Split into:
  - dcf_step5_output.py (this) — orchestrator + data plumbing
  - dcf_step5_display.py — summary, EV breakdown, implied price renderers
  - dcf_step5_bridge.py — equity bridge with overrides
  - dcf_step5_sensitivity.py — 2D sensitivity tables
  - dcf_step5_scenarios.py — Bull/Base/Bear scenario orchestration
"""

import streamlit as st
import pandas as pd

from pages.valuation.dcf_step2_table import compute_projections, build_historical_data
from pages.valuation.dcf_step5_scenarios import render_scenario_output
from lib.analysis.valuation.dcf import run_dcf
from models.valuation import WACCResult
from components.commentary import render_dcf_step5_commentary


def render(prepared: dict, ticker: str) -> None:
    """Render DCF output step with scenario tabs."""
    st.markdown("### Step 5: DCF Output")
    st.caption(
        "Enterprise value, equity bridge, implied share price, "
        "and sensitivity analysis across all scenarios."
    )

    wacc_data = st.session_state.get("dcf_wacc")
    scenarios = st.session_state.get("dcf_scenarios")
    terminals = st.session_state.get("dcf_scenarios_terminal")

    if not all([wacc_data, scenarios, terminals]):
        st.warning("Complete Steps 2, 3, and 4 first.")
        return

    base_assumptions = scenarios.get("base")
    base_terminal = terminals.get("base")
    if not base_assumptions or not base_terminal:
        st.warning("Complete Steps 2 and 4 for the Base Case first.")
        return

    # Verify base case projections are complete
    proj = _get_projections(prepared, base_assumptions)
    if proj is None:
        st.info("Complete all Step 2 Base Case assumptions to see output.")
        return

    # ── Delegate to scenario orchestrator ──────────────────────
    render_scenario_output(
        prepared, ticker,
        build_fcf_fn=_build_fcf_df,
        to_wacc_fn=_to_wacc_result,
        get_bridge_fn=_get_bridge_inputs,
        get_proj_fn=_get_projections,
    )

    # ── Analyst Commentary ────────────────────────────────────────
    render_dcf_step5_commentary()


# ── Data plumbing (used by scenario orchestrator) ──────────────────


def _get_projections(prepared: dict, assumptions: dict) -> dict | None:
    """Recompute Step 2 projections."""
    standardized = prepared.get("standardized", {})
    years = prepared.get("years", [])
    ratios = prepared.get("ratios", [])
    if not years:
        return None
    hist = build_historical_data(ratios, standardized, years)
    raw_revs = hist.get("revenue_raw", [])
    base_revenue = raw_revs[-1] if raw_revs else None
    if base_revenue is None:
        return None
    return compute_projections(
        assumptions, base_revenue, hist.get("base_cogs_pct", 0.60),
    )


def _build_fcf_df(proj: dict, assumptions: dict) -> pd.DataFrame:
    """Convert Step 2 projection dict to DataFrame for run_dcf."""
    rows = []
    for i in range(len(proj["fcf"])):
        ebit = proj["ebit"][i]
        da = proj["da"][i]
        rows.append({
            "Year": i + 1,
            "Revenue": proj["revenue"][i],
            "Growth": assumptions["growth_rates"][i],
            "EBIT": ebit,
            "EBIT_Margin": assumptions["ebit_margins"][i],
            "NOPAT": proj["nopat"][i],
            "D&A": da,
            "CapEx": proj["capex"][i],
            "dNWC": proj["nwc_change"][i],
            "SBC": proj["sbc"][i],
            "FCF": proj["fcf"][i],
            "EBITDA": ebit + da,
        })
    return pd.DataFrame(rows)


def _to_wacc_result(d: dict) -> WACCResult:
    """Convert Step 3 dict to WACCResult for lib/ engine."""
    return WACCResult(
        rf=d.get("rf", 0.04),
        beta=d.get("beta", 1.0),
        erp=d.get("erp", 0.055),
        size_premium=d.get("size_premium", 0.0),
        crp=d.get("crp", 0.0),
        cost_of_equity=d.get("ke", 0.10),
        beta_method=d.get("beta_method", "blume"),
        cost_of_debt_pretax=d.get("kd_pre_tax", 0.05),
        tax_rate=d.get("tax_rate", 0.21),
        cost_of_debt_aftertax=d.get("kd_after_tax", 0.04),
        rd_method=d.get("kd_method", "interest_debt"),
        equity_weight=d.get("weight_equity", 1.0),
        debt_weight=d.get("weight_debt", 0.0),
        cap_structure_method=d.get("cap_structure_method", "market"),
        wacc=d.get("wacc", 0.10),
    )


def _get_bridge_inputs(prepared: dict, ticker: str) -> dict:
    """Extract bridge inputs. Monetary values in millions."""
    val_data = st.session_state.get(f"val_data_{ticker}") or {}
    company = st.session_state.get(f"company_{ticker}")
    bs = val_data.get("balance_sheet", {})

    net_debt_raw = bs.get("net_debt", 0)
    if not net_debt_raw:
        years = prepared.get("years", [])
        if years:
            bal = prepared.get("standardized", {}).get("balance", {})
            last_bs = bal.get(years[-1], {})
            net_debt_raw = last_bs.get("net_debt", 0) or 0

    minority_raw = bs.get("minority_interest", 0) or 0
    preferred_raw = bs.get("preferred_equity", 0) or 0

    shares_raw = (
        val_data.get("shares")
        or (getattr(getattr(company, "ratios", None),
                    "shares_outstanding", None) if company else None)
        or 1
    )

    current_price = 0
    if company:
        current_price = getattr(
            getattr(company, "price", None), "price", 0,
        ) or 0

    currency = val_data.get("currency", "USD")
    fin_currency = val_data.get("financial_currency", currency)
    mcap = val_data.get("market_cap")
    price_factor = 1.0
    if currency != fin_currency and current_price and mcap and shares_raw:
        price_factor = mcap / (current_price * shares_raw)

    return {
        "net_debt": net_debt_raw / 1e6,
        "minority": minority_raw / 1e6,
        "preferred": preferred_raw / 1e6,
        "shares": shares_raw / 1e6,
        "current_price": current_price,
        "price_factor": price_factor,
        "currency": currency,
        "financial_currency": fin_currency,
    }
