"""Step 5: DCF Output — EV, equity bridge, implied price, sensitivity."""

import streamlit as st
import pandas as pd

from pages.valuation.dcf_step2_table import compute_projections, build_historical_data
from pages.valuation.dcf_step5_bridge import render_bridge
from pages.valuation.dcf_step5_sensitivity import render_sensitivity
from lib.analysis.valuation.dcf import run_dcf
from models.valuation import WACCResult
from components.layout import format_large_number


def render(prepared: dict, ticker: str) -> None:
    """Render DCF output step."""
    st.markdown("### Step 5: DCF Output")
    st.caption(
        "Enterprise value, equity bridge, implied share price, "
        "and sensitivity analysis."
    )

    wacc_data = st.session_state.get("dcf_wacc")
    terminal = st.session_state.get("dcf_terminal")
    assumptions = st.session_state.get("dcf_assumptions")

    if not all([wacc_data, terminal, assumptions]):
        st.warning("Complete Steps 2, 3, and 4 first.")
        return

    proj = _get_projections(prepared, assumptions)
    if proj is None:
        st.info("Complete all Step 2 assumptions to see DCF output.")
        return

    # ── Build inputs ───────────────────────────────────────────
    fcf_table = _build_fcf_df(proj, assumptions)
    wacc_result = _to_wacc_result(wacc_data)
    bridge_inputs = _get_bridge_inputs(prepared, ticker)
    current_price = bridge_inputs["current_price"]

    # ── Run DCF engine ─────────────────────────────────────────
    result = run_dcf(
        fcf_table=fcf_table,
        wacc_result=wacc_result,
        terminal_growth=terminal["terminal_growth"],
        terminal_method=terminal["method"],
        exit_multiple=terminal["exit_multiple"],
        net_debt=bridge_inputs["net_debt"],
        shares=bridge_inputs["shares"],
        current_price=current_price,
        minority_interest=bridge_inputs["minority"],
        preferred_equity=bridge_inputs["preferred"],
    )

    # Currency: DCF output is in financialCurrency. Convert to
    # listing currency for display when they differ.
    pf = bridge_inputs.get("price_factor", 1.0)
    currency = bridge_inputs.get("currency", "USD")

    # ── 1. Summary metrics ─────────────────────────────────────
    _render_summary(result, wacc_data, terminal, pf, currency)

    # ── 2. EV breakdown (PV FCFs vs PV TV) ─────────────────────
    _render_ev_breakdown(result)

    # ── 3. Equity bridge with overrides ────────────────────────
    st.markdown("---")
    bridge_result = render_bridge(result, bridge_inputs, ticker)

    # ── 4. Implied price vs market ─────────────────────────────
    st.markdown("---")
    _render_implied_price(bridge_result, current_price, pf, currency)

    # ── 5. Sensitivity tables ──────────────────────────────────
    st.markdown("---")
    sens_range = render_sensitivity(
        fcf_table, wacc_result, terminal,
        bridge_inputs, current_price,
    )

    # ── 6. Warnings ────────────────────────────────────────────
    for w in result.warnings:
        st.warning(w)

    # ── Store output (implied_price in listing currency) ─────────
    method_label = ("Gordon Growth" if terminal["method"] == "gordon"
                    else "Exit Multiple")
    implied_listing = bridge_result["implied_price"]
    if pf != 1.0:
        implied_listing = implied_listing / pf
    st.session_state["dcf_output"] = {
        "enterprise_value": result.enterprise_value,
        "equity_value": bridge_result["equity_value"],
        "implied_price": implied_listing,
        "current_price": current_price,
        "tv_pct_of_ev": result.tv_pct_of_ev,
        "sensitivity_min": sens_range["min"] / pf if pf != 1.0 else sens_range["min"],
        "sensitivity_max": sens_range["max"] / pf if pf != 1.0 else sens_range["max"],
        "wacc": wacc_data["wacc"],
        "terminal_growth": terminal["terminal_growth"],
        "terminal_method": method_label,
    }



def _render_summary(result, wacc_data, terminal, pf=1.0, cur="USD"):
    """Top-line metrics row."""
    ev = result.enterprise_value
    eq = result.bridge.equity_value
    # Convert implied price to listing currency
    implied = result.implied_price / pf if pf != 1.0 else result.implied_price
    current = result.current_price
    upside = (implied / current - 1) * 100 if current > 0 else 0
    sym = "$" if cur == "USD" else ""

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Enterprise Value", format_large_number(ev * 1e6))
    c2.metric("Equity Value", format_large_number(eq * 1e6))
    c3.metric("Implied Price", f"{sym}{implied:,.2f} {cur}")
    c4.metric("Current Price", f"{sym}{current:,.2f} {cur}")
    color = "#2ea043" if upside > 0 else "#f85149"
    c5.markdown(
        f'<div style="font-size:13px;opacity:0.6">Upside / Downside</div>'
        f'<div style="font-size:24px;font-weight:700;color:{color}">'
        f'{upside:+.1f}%</div>',
        unsafe_allow_html=True,
    )

    # Key assumptions line
    method_label = ("Gordon Growth" if terminal["method"] == "gordon"
                    else "Exit Multiple")
    st.markdown(
        f'<div style="font-size:13px;opacity:0.6;margin-top:4px">'
        f'WACC: {wacc_data["wacc"]*100:.2f}% &nbsp;|&nbsp; '
        f'Terminal: {method_label} '
        f'(g={terminal["terminal_growth"]*100:.2f}%, '
        f'multiple={terminal["exit_multiple"]:.1f}x) &nbsp;|&nbsp; '
        f'{terminal["n_years"]}yr projection</div>',
        unsafe_allow_html=True,
    )



def _render_ev_breakdown(result) -> None:
    """Show PV of FCFs + PV of TV = EV."""
    pv_fcfs_total = sum(result.pv_fcfs)
    pv_tv = result.pv_terminal
    ev = result.enterprise_value
    tv_pct = result.tv_pct_of_ev

    st.markdown("#### Enterprise Value Breakdown")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("PV of FCFs", format_large_number(pv_fcfs_total * 1e6))
    c2.metric("PV of Terminal Value", format_large_number(pv_tv * 1e6))
    c3.metric("Enterprise Value", format_large_number(ev * 1e6))
    c4.metric("TV as % of EV", f"{tv_pct:.0%}")



def _render_implied_price(bridge_result, current_price, pf=1.0, cur="USD"):
    """Large implied price display with upside/downside."""
    implied = bridge_result["implied_price"]
    if pf != 1.0:
        implied = implied / pf
    upside = (implied / current_price - 1) * 100 if current_price > 0 else 0
    color = "#2ea043" if upside > 0 else "#f85149"
    verdict = "UNDERVALUED" if upside > 0 else "OVERVALUED"
    sym = "$" if cur == "USD" else ""

    st.markdown(
        f'<div style="text-align:center;padding:16px 0">'
        f'<div style="font-size:14px;opacity:0.6">Implied Share Price</div>'
        f'<div style="font-size:36px;font-weight:700;color:#1c83e1">'
        f'{sym}{implied:,.2f} {cur}</div>'
        f'<div style="font-size:14px;margin-top:4px">'
        f'vs {sym}{current_price:,.2f} {cur} current → '
        f'<span style="color:{color};font-weight:700">'
        f'{upside:+.1f}% ({verdict})</span></div></div>',
        unsafe_allow_html=True,
    )



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

    # Net debt (raw dollars → millions)
    net_debt_raw = bs.get("net_debt", 0)
    if not net_debt_raw:
        # Fallback: prepared standardized balance sheet
        years = prepared.get("years", [])
        if years:
            bal = prepared.get("standardized", {}).get("balance", {})
            last_bs = bal.get(years[-1], {})
            net_debt_raw = last_bs.get("net_debt", 0) or 0

    minority_raw = bs.get("minority_interest", 0) or 0
    preferred_raw = bs.get("preferred_equity", 0) or 0

    # Shares (raw count → millions, for consistent units)
    shares_raw = (
        val_data.get("shares")
        or (getattr(getattr(company, "ratios", None),
                    "shares_outstanding", None) if company else None)
        or 1
    )

    # Current price (dollars)
    current_price = 0
    if company:
        current_price = getattr(
            getattr(company, "price", None), "price", 0,
        ) or 0

    # Currency alignment: DCF runs in financialCurrency, but
    # current_price is in listing currency. Compute factor.
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
