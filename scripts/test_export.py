"""Generate a realistic test export JSON for AAPL.

Fetches real company data via project modules, then constructs
realistic mock analyst assumptions, scenarios, and commentary.
"""

import sys
import json
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.data.fundamentals import get_company
from lib.data.valuation_data import get_valuation_data, get_risk_free_rate
from lib.data.yfinance_standardizer import standardize_yfinance
from lib.exports.analysis_export import build_export_json

import yfinance as yf


def main():
    ticker = "AAPL"
    print(f"Fetching real data for {ticker}...")

    # ── Real data from project modules ────────────────────────
    company, _ = get_company(ticker)
    val_data, _ = get_valuation_data(ticker)
    rf = get_risk_free_rate()

    # Standardize financials
    yt = yf.Ticker(ticker)
    std = standardize_yfinance(yt.income_stmt, yt.balance_sheet, yt.cashflow)

    print(f"  Company: {company.info.name}")
    print(f"  Price: ${company.price.price:,.2f}")
    print(f"  PE: {company.ratios.pe_trailing}")
    print(f"  Years: {std['years'] if std else 'N/A'}")

    # ── Build mock session state ──────────────────────────────
    state = _build_mock_state(ticker, company, val_data, rf, std)

    # ── Run export ────────────────────────────────────────────
    included = {"DCF": True, "DDM": False, "Comps": True, "Historical": True}
    result = build_export_json(state, ticker, included, default_templates={})

    # ── Save ──────────────────────────────────────────────────
    out_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "AAPL_analysis_test.json",
    )
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)

    print(f"\nExport saved to: {out_path}")
    print(f"JSON size: {os.path.getsize(out_path):,} bytes")
    print(f"Top-level sections: {list(result.keys())}")
    if result.get("dcf"):
        print(f"DCF scenarios: {list(result['dcf']['scenarios'].keys())}")
    if result.get("historical_financials"):
        print(f"Financial years: {result['historical_financials']['years']}")


def _build_mock_state(ticker, company, val_data, rf, std):
    """Construct realistic session_state dict."""
    state = {}

    # ── Company + valuation data (REAL) ───────────────────────
    state[f"company_{ticker}"] = company
    state[f"val_data_{ticker}"] = val_data
    state["val_risk_free_rate"] = rf

    # ── Prepared data (REAL standardized + mock ratios/averages)
    prepared = {
        "company_type": {"type": "normal"},
        "years": std["years"] if std else ["2021", "2022", "2023", "2024"],
        "standardized": std if std else {},
        "ratios": _mock_ratios(std),
        "averages": {
            "revenue_growth_3y": 0.06,
            "ebit_margin_3y": 0.30,
            "capex_pct_3y": 0.038,
            "da_pct_3y": 0.034,
            "tax_rate_3y": 0.16,
        },
    }
    state["prepared_data"] = prepared

    # ── DCF ───────────────────────────────────────────────────
    state["dcf_sector_template"] = "Technology / Growth"
    state["dcf_wacc"] = {
        "wacc": 0.095, "ke": 0.105, "rf": rf, "beta": 1.24,
        "beta_method": "blume", "erp": 0.055, "size_premium": 0.0,
        "crp": 0.0, "kd_pre_tax": 0.035, "kd_after_tax": 0.029,
        "kd_method": "actual", "tax_rate": 0.16,
        "weight_equity": 0.93, "weight_debt": 0.07,
        "cap_structure_method": "market",
    }
    state["dcf_scenarios"] = {
        "base": _dcf_assumptions(
            [0.08, 0.07, 0.06, 0.05, 0.04],
            [0.30, 0.30, 0.30, 0.30, 0.30], 0.16,
        ),
        "bull": _dcf_assumptions(
            [0.12, 0.10, 0.09, 0.07, 0.06],
            [0.31, 0.31, 0.32, 0.32, 0.32], 0.16,
        ),
        "bear": _dcf_assumptions(
            [0.03, 0.03, 0.02, 0.02, 0.02],
            [0.28, 0.27, 0.27, 0.26, 0.26], 0.16,
        ),
    }
    state["dcf_scenarios_terminal"] = {
        "base": _dcf_terminal(0.025, 20.0),
        "bull": _dcf_terminal(0.030, 23.0),
        "bear": _dcf_terminal(0.020, 16.0),
    }
    base_price = company.price.price or 200
    state["dcf_output"] = {
        "base": _dcf_output(base_price * 1.05, base_price, 0.095, 0.025),
        "bull": _dcf_output(base_price * 1.30, base_price, 0.095, 0.030),
        "bear": _dcf_output(base_price * 0.75, base_price, 0.095, 0.020),
    }

    # ── Comps ─────────────────────────────────────────────────
    state["comps_table"] = {
        "target": {"ticker": "AAPL", "name": "Apple Inc.",
                   "price": base_price, "market_cap": 3.76e12,
                   "enterprise_value": 3.78e12, "revenue": 391e9,
                   "ebitda": 134e9, "ebit": 123e9, "net_income": 100e9,
                   "eps": 6.75, "ev_revenue": 9.7, "ev_ebitda": 28.2,
                   "trailing_pe": 32.4, "shares_outstanding": 14.7e9,
                   "total_debt": 104e9, "cash": 62e9},
        "peers": [
            _comps_peer("MSFT", "Microsoft", 420, 3.1e12, 3.2e12, 33.5, 25.2, 35.0),
            _comps_peer("GOOGL", "Alphabet", 170, 2.1e12, 2.0e12, 6.8, 18.5, 25.0),
            _comps_peer("META", "Meta Platforms", 580, 1.5e12, 1.4e12, 9.5, 20.0, 27.0),
            _comps_peer("AMZN", "Amazon", 195, 2.0e12, 2.1e12, 3.8, 22.0, 55.0),
            _comps_peer("NVDA", "NVIDIA", 130, 3.2e12, 3.2e12, 28.0, 55.0, 60.0),
        ],
        "excluded": set(),
        "summary": {
            "median": {"ev_revenue": 9.5, "ev_ebitda": 22.0, "trailing_pe": 30.0},
            "mean": {"ev_revenue": 12.1, "ev_ebitda": 28.1, "trailing_pe": 36.5},
            "high": {"ev_revenue": 28.0, "ev_ebitda": 55.0, "trailing_pe": 60.0},
            "low": {"ev_revenue": 3.8, "ev_ebitda": 18.5, "trailing_pe": 25.0},
        },
        "is_financial": False,
        "fetched": True,
    }
    state["comps_valuation"] = {
        "base": {"implied_price": base_price * 1.02, "applied_mult": 22.0,
                 "premium": 0.0, "final_mult": 22.0},
        "bull": {"implied_price": base_price * 1.20, "applied_mult": 28.0,
                 "premium": 0.0, "final_mult": 28.0},
        "bear": {"implied_price": base_price * 0.80, "applied_mult": 18.5,
                 "premium": 0.0, "final_mult": 18.5},
        "current_price": base_price,
    }

    # ── Historical Multiples ──────────────────────────────────
    state["historical_result"] = {
        "base": {"implied_price": base_price * 0.98, "applied_mult": 25.5,
                 "mult_key": "pe"},
        "bull": {"implied_price": base_price * 1.15, "applied_mult": 30.0,
                 "mult_key": "pe"},
        "bear": {"implied_price": base_price * 0.82, "applied_mult": 21.0,
                 "mult_key": "pe"},
        "summary": {
            "pe": {"current": 32.4, "mean": 25.5, "median": 25.0,
                   "min": 12.0, "max": 40.0, "minus_1std": 21.0,
                   "plus_1std": 30.0, "percentile": 78},
            "ev_ebitda": {"current": 28.2, "mean": 20.5, "median": 20.0,
                          "min": 10.0, "max": 32.0, "minus_1std": 16.0,
                          "plus_1std": 25.0, "percentile": 82},
        },
        "implied_values": {
            "pe": {"at_mean": base_price * 0.79, "at_median": base_price * 0.77,
                   "at_minus_1std": base_price * 0.65, "at_p10": base_price * 0.55,
                   "at_p90": base_price * 1.10, "upside_mean": -0.21},
        },
        "current_price": base_price,
    }

    # ── Financial overrides ───────────────────────────────────
    state[f"financial_overrides_{ticker}"] = {
        "income": {}, "balance": {}, "cashflow": {},
    }

    # ── Commentary ────────────────────────────────────────────
    _add_commentary(state)

    return state


# ── Helper builders ───────────────────────────────────────────────


def _dcf_assumptions(growth, margins, tax):
    n = len(growth)
    return {
        "n_years": n, "nwc_method": "simplified",
        "growth_rates": growth, "ebit_margins": margins,
        "tax_rates": [tax] * n, "capex_pcts": [0.04] * n,
        "da_pcts": [0.034] * n, "sbc_pcts": [0.02] * n,
        "dso": [None] * n, "dio": [None] * n, "dpo": [None] * n,
        "nwc_pcts": [-0.15] * n,
    }


def _dcf_terminal(g, mult):
    return {
        "method": "gordon", "terminal_value": 5000000,
        "terminal_growth": g, "exit_multiple": mult,
        "gordon_tv": 5000000, "exit_tv": 4500000,
        "fcf_final": 110000, "ebitda_final": 160000, "n_years": 5,
    }


def _dcf_output(implied, current, wacc, tg):
    return {
        "enterprise_value": 3500000, "equity_value": 3400000,
        "implied_price": round(implied, 2),
        "current_price": current,
        "tv_pct_of_ev": 0.72,
        "sensitivity_min": round(implied * 0.80, 2),
        "sensitivity_max": round(implied * 1.25, 2),
        "wacc": wacc, "terminal_growth": tg,
        "terminal_method": "Gordon Growth",
    }


def _comps_peer(tick, name, price, mcap, ev, ev_rev, ev_ebitda, pe):
    return {
        "ticker": tick, "name": name, "price": price,
        "market_cap": mcap, "enterprise_value": ev,
        "ev_revenue": ev_rev, "ev_ebitda": ev_ebitda,
        "trailing_pe": pe,
    }


def _mock_ratios(std):
    if not std:
        return []
    return [
        {"year": yr, "revenue_growth": 0.06, "ebit_margin": 0.30,
         "tax_rate": 0.16, "capex_pct": 0.038, "da_pct": 0.034,
         "sbc_pct": 0.02, "nwc_pct": -0.15}
        for yr in std.get("years", [])
    ]


def _add_commentary(state):
    """Add realistic analyst commentary for every field."""

    # DCF Step 2 — per scenario
    state["commentary_dcf_step2_base"] = (
        "AAPL's base case assumes revenue growth decelerating from 8% to 4% "
        "as the smartphone market matures and Services growth normalizes. "
        "EBIT margins held at ~30%, consistent with the 3-year average. "
        "This reflects steady execution without major new product categories."
    )
    state["commentary_dcf_step2_bull"] = (
        "Bull case assumes Apple Vision Pro drives a new product cycle, "
        "Services accelerates to 15%+ growth, and India/emerging markets "
        "expand the iPhone TAM. Revenue growth stays elevated at 10%+ "
        "through 2027 with modest margin expansion from Services mix shift."
    )
    state["commentary_dcf_step2_bear"] = (
        "Bear case models smartphone saturation and regulatory headwinds "
        "(EU DMA, app store fees) compressing Services margins. Revenue "
        "growth slows to low single digits with EBIT margins declining "
        "to 26-27% as competition intensifies in wearables and services."
    )

    # DCF Step 3 — WACC
    state["commentary_dcf_step3"] = (
        "WACC of 9.5% reflects AAPL's low debt-to-equity (7% weight) "
        "and Ke of 10.5% using Blume-adjusted beta of 1.24. The minimal "
        "debt means WACC is essentially driven by cost of equity. The "
        "spread to risk-free seems appropriate for a mega-cap tech company."
    )

    # DCF Step 4 — per scenario
    state["commentary_dcf_step4_base"] = (
        "Terminal growth of 2.5% is slightly above long-term US GDP growth, "
        "justified by Apple's ecosystem lock-in and recurring Services revenue. "
        "TV represents 72% of EV, which is typical for a mature tech company."
    )
    state["commentary_dcf_step4_bull"] = (
        "Terminal growth of 3.0% assumes Apple maintains its premium brand "
        "and grows Services at a structural premium to GDP. Higher exit "
        "multiple of 23x reflects sustained quality of earnings."
    )
    state["commentary_dcf_step4_bear"] = (
        "Terminal growth of 2.0% assumes AAPL reverts to a hardware company "
        "growing at inflation. Lower exit multiple of 16x reflects margin "
        "compression and increased competition from Android ecosystem."
    )

    # DCF Step 5 — shared comparison
    state["commentary_dcf_step5"] = (
        "Probability weighting: Bull 25% / Base 55% / Bear 20%. The weighted "
        "fair value is approximately $245, suggesting modest upside from "
        "current levels. The spread is relatively narrow for a mega-cap, "
        "reflecting AAPL's predictable business model. Key risk is Services "
        "growth deceleration; key catalyst is Vision Pro adoption."
    )

    # Comps Step 3 — per scenario
    state["commentary_comps_step3_base"] = (
        "Base case uses median EV/EBITDA of 22x from the mega-cap tech "
        "peer group. AAPL's premium to peers is warranted by its ecosystem "
        "but offset by lower growth vs NVDA/META."
    )
    state["commentary_comps_step3_bull"] = (
        "Bull case uses 75th percentile (28x), justified if Services "
        "re-rating drives a valuation closer to pure software peers. "
        "MSFT trades at 25x on similar margin profile."
    )
    state["commentary_comps_step3_bear"] = (
        "Bear case uses 25th percentile (18.5x), reflecting a scenario "
        "where AAPL is valued as a mature hardware company. GOOGL at 18.5x "
        "provides the comp — lower multiple, higher growth."
    )
    state["commentary_comps_comparison"] = (
        "The comps range ($205-$307) is consistent with the DCF range, "
        "providing cross-validation. The peer group is imperfect — NVDA's "
        "AI premium inflates the high end, while AMZN's low margins "
        "depress EV/Revenue comps. EV/EBITDA is the most reliable multiple."
    )

    # Historical — per scenario
    state["commentary_historical_base"] = (
        "Base case anchors on the 5-year mean P/E of 25.5x. AAPL currently "
        "trades at 32x, well above the historical average, suggesting "
        "the market is pricing in stronger growth than history supports."
    )
    state["commentary_historical_bull"] = (
        "Bull case uses +1 sigma (30x P/E), which was reached during "
        "the 2020-2021 re-rating when Services growth accelerated. "
        "Sustainable only if Services mix continues to shift higher."
    )
    state["commentary_historical_bear"] = (
        "Bear case uses -1 sigma (21x P/E), last seen in 2018-2019 "
        "during the China trade war and iPhone demand concerns. "
        "A return to these levels would require a significant earnings miss."
    )
    state["commentary_historical_comparison"] = (
        "Historical multiples confirm AAPL is trading near the top of "
        "its historical range. Mean reversion would imply 15-20% downside. "
        "The key question is whether the Services-driven re-rating is "
        "permanent or cyclical."
    )

    # Summary
    state["commentary_summary"] = (
        "THESIS: Apple appears fairly valued to slightly overvalued at "
        "current levels. DCF base case implies ~5% upside, while comps "
        "and historical multiples suggest the stock is near the top of "
        "its fair value range. The bull case requires Vision Pro success "
        "and sustained Services acceleration. Conviction: moderate — the "
        "business quality is exceptional but largely priced in."
    )


if __name__ == "__main__":
    main()
