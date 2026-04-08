"""Step 3: WACC — Weighted Average Cost of Capital.

Orchestrator: extracts data from session state, calls three sub-renderers,
stores result in st.session_state["dcf_wacc"].

Sub-renderers:
  dcf_step3_ke.py        → Cost of Equity (Ke)
  dcf_step3_kd.py        → Cost of Debt (Kd)
  dcf_step3_structure.py → Capital Structure + WACC output
"""

import streamlit as st

from pages.valuation.dcf_step3_ke import render_cost_of_equity
from pages.valuation.dcf_step3_kd import render_cost_of_debt
from pages.valuation.dcf_step3_structure import render_structure_and_output
from components.commentary import render_commentary
from components.fetch_warnings import record_fetch


def render(prepared: dict, ticker: str) -> None:
    """Render WACC step — auto-calculated, all inputs editable."""
    st.markdown("### Step 3: WACC")
    st.caption(
        "Weighted Average Cost of Capital — discount rate for DCF. "
        "All values auto-fetched. Select methods and override as needed."
    )

    # ── Extract inputs from session state ─────────────────────
    inputs = _extract_inputs(prepared, ticker)
    if inputs is not None:
        record_fetch(
            "beta",
            inputs.get("raw_beta") is not None,
            source="Yahoo",
            message="Beta fetch failed — enter beta manually",
        )
        record_fetch(
            "total_debt",
            inputs.get("total_debt") is not None,
            source="Balance sheet",
            message="Total debt not available — balance sheet data missing",
        )
        record_fetch(
            "tax_rate",
            inputs.get("effective_tax_rate") is not None,
            source="Income statement",
            message="Effective tax rate not available — enter tax rate manually",
        )
    if inputs is None:
        st.warning(
            "Missing valuation data. Ensure Financial Preparation "
            "completed successfully."
        )
        return

    # ── A. Cost of Equity ─────────────────────────────────────
    ke_result = render_cost_of_equity(inputs)

    st.markdown(
        '<hr style="margin:16px 0;border-color:rgba(128,128,128,0.2)">',
        unsafe_allow_html=True,
    )

    # ── B. Cost of Debt ───────────────────────────────────────
    # Pass rf from Ke section (may have been overridden by analyst)
    inputs["rf"] = ke_result["rf"]
    kd_result = render_cost_of_debt(inputs)

    st.markdown(
        '<hr style="margin:16px 0;border-color:rgba(128,128,128,0.2)">',
        unsafe_allow_html=True,
    )

    # ── C + D. Capital Structure + WACC Output ────────────────
    wacc_result = render_structure_and_output(inputs, ke_result, kd_result)

    # ── Store in session state for Step 4 + 5 ─────────────────
    if wacc_result.get("wacc") is not None:
        st.session_state["dcf_wacc"] = wacc_result
    else:
        st.session_state.pop("dcf_wacc", None)

    # ── Analyst Commentary ────────────────────────────────────────
    render_commentary("commentary_dcf_step3")


# ── Data extraction ───────────────────────────────────────────────


def _extract_inputs(prepared: dict, ticker: str) -> dict | None:
    """Build consolidated inputs dict from session state + prepared."""

    # Company model (loaded by 3_valuation.py)
    company = st.session_state.get(f"company_{ticker}")
    if company is None:
        return None

    # Valuation data (loaded by 3_valuation.py)
    val_data = st.session_state.get(f"val_data_{ticker}") or {}
    inc = val_data.get("income_detail", {})
    bs = val_data.get("balance_sheet", {})

    # Risk-free rate (loaded by 3_valuation.py) — may be None if fetch
    # failed. Page layer records status and surfaces a warning.
    rf = st.session_state.get("val_risk_free_rate")

    raw_beta = (
        getattr(company.price, "beta", None)
        or val_data.get("beta")
    )
    market_cap = (
        getattr(company.price, "market_cap", None)
        or val_data.get("market_cap")
        or 0
    )
    total_debt = bs.get("total_debt")
    interest = inc.get("interest_expense") or 0
    ebit = inc.get("ebit") or 0
    eff_tax = inc.get("effective_tax_rate")

    # Fallback: use prepared_data standardized if val_data missing fields
    if not interest or not ebit:
        std = prepared.get("standardized", {})
        years = std.get("years", [])
        if years:
            for yr in reversed(years):
                yr_inc = std.get("income", {}).get(yr, {})
                if not interest:
                    ie = yr_inc.get("interest_expense")
                    if ie and ie > 0:
                        interest = ie
                if not ebit:
                    eb = yr_inc.get("ebit")
                    if eb and eb > 0:
                        ebit = eb
                if interest and ebit:
                    break

    # Company info
    info = getattr(company, "info", None)
    country = getattr(info, "country", "") or ""
    industry = getattr(info, "industry", "") or ""

    # Company type from prepared data
    ct = prepared.get("company_type", {})
    company_type = ct.get("type", "normal")

    return {
        "ticker": ticker,
        "rf": rf,
        "raw_beta": raw_beta,
        "market_cap": market_cap,
        "total_debt": total_debt,
        "interest_expense": interest,
        "ebit": ebit,
        "effective_tax_rate": eff_tax,
        "country": country,
        "industry": industry,
        "company_type": company_type,
    }
