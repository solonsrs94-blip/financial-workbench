"""Test script for Summary tab logic.

Tests _collect_rows, _collect_bars, and rendering without full Streamlit.
Mocks st.session_state with realistic data from each valuation model.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock streamlit before importing summary modules
import types
st_mock = types.ModuleType("streamlit")
st_mock.session_state = {}
st_mock.markdown = lambda *a, **kw: None
st_mock.caption = lambda *a, **kw: None
st_mock.subheader = lambda *a, **kw: None
st_mock.info = lambda *a, **kw: None
st_mock.warning = lambda *a, **kw: None
st_mock.columns = lambda n: [types.SimpleNamespace(metric=lambda *a, **kw: None) for _ in range(n)]
st_mock.dataframe = lambda *a, **kw: None
st_mock.plotly_chart = lambda *a, **kw: None
sys.modules["streamlit"] = st_mock

# Also mock components and config used by summary files
config_mod = types.ModuleType("config")
config_constants = types.ModuleType("config.constants")
config_constants.CHART_TEMPLATE = "plotly_dark"
sys.modules["config"] = config_mod
sys.modules["config.constants"] = config_constants

# Mock components.layout
comp_mod = types.ModuleType("components")
comp_layout = types.ModuleType("components.layout")
comp_layout.format_large_number = lambda x: f"${x:,.0f}"
comp_layout.page_header = lambda *a, **kw: None
comp_layout.data_status_banner = lambda *a, **kw: None
comp_layout.load_css = lambda: None
sys.modules["components"] = comp_mod
sys.modules["components.layout"] = comp_layout

from pages.valuation.summary_tab import _collect_rows, _collect_bars, _HIST_LABELS

import numpy as np


# ── Test data fixtures ─────────────────────────────────────────

DCF_OUTPUT = {
    "enterprise_value": 2800000,
    "equity_value": 2750000,
    "implied_price": 185.50,
    "current_price": 165.00,
    "tv_pct_of_ev": 0.72,
    "sensitivity_min": 142.00,
    "sensitivity_max": 248.00,
    "wacc": 0.095,
    "terminal_growth": 0.025,
    "terminal_method": "Gordon Growth",
}

COMPS_VALUATION = {
    "method": "median",
    "implied_prices": {
        "trailing_pe": {
            "low": 140.0, "median": 172.0, "mean": 175.0, "high": 210.0,
            "target_metric": 6.5, "label": "P / E", "basis": "equity",
            "net_debt": 50000,
        },
        "ev_ebitda": {
            "low": 135.0, "median": 168.0, "mean": 170.0, "high": 195.0,
            "target_metric": 120000, "label": "EV / EBITDA", "basis": "ev",
            "net_debt": 50000,
        },
        "ev_revenue": {
            "low": 110.0, "median": 148.0, "mean": 150.0, "high": 180.0,
            "target_metric": 400000, "label": "EV / Revenue", "basis": "ev",
            "net_debt": 50000,
        },
    },
    "current_price": 165.00,
}

HISTORICAL_RESULT = {
    "summary": {
        "pe": {"current": 22.5, "mean": 20.1, "median": 19.8},
        "ev_ebitda": {"current": 14.2, "mean": 13.0, "median": 12.5},
        "ev_revenue": {"current": 6.8, "mean": 6.2, "median": 6.0},
    },
    "implied_values": {
        "pe": {
            "at_mean": 147.0, "at_median": 155.0,
            "at_p10": 120.0, "at_p90": 195.0,
            "at_minus_1std": 130.0, "upside_mean": -10.9,
        },
        "ev_ebitda": {
            "at_mean": 151.0, "at_median": 160.0,
            "at_p10": 125.0, "at_p90": 190.0,
            "at_minus_1std": 135.0, "upside_mean": -8.5,
        },
        "ev_revenue": {
            "at_mean": 145.0, "at_median": 150.0,
            "at_p10": 115.0, "at_p90": 185.0,
            "at_minus_1std": 128.0, "upside_mean": -12.1,
        },
    },
    "current_price": 165.00,
    "currency": "USD",
    "period": 5,
    "is_financial": False,
}

DDM_OUTPUT = {
    "implied_price": 142.00,
    "current_price": 165.00,
    "model": "gordon",
    "ke": 0.095,
    "g": 0.03,
    "sensitivity_min": 95.00,
    "sensitivity_max": 210.00,
}

# Financial company comps (P/Book, P/TBV instead of EV-based)
COMPS_FINANCIAL = {
    "method": "median",
    "implied_prices": {
        "trailing_pe": {
            "low": 38.0, "median": 52.0, "mean": 54.0, "high": 68.0,
            "target_metric": 4.2, "label": "P / E", "basis": "equity",
            "net_debt": 0,
        },
        "price_to_book": {
            "low": 35.0, "median": 48.0, "mean": 50.0, "high": 62.0,
            "target_metric": 95.5, "label": "P / Book", "basis": "equity",
            "net_debt": 0,
        },
        "price_to_tbv": {
            "low": 30.0, "median": 44.0, "mean": 46.0, "high": 58.0,
            "target_metric": 85.0, "label": "P / TBV", "basis": "equity",
            "net_debt": 0,
        },
        "dividend_yield": {
            "low": 42.0, "median": 55.0, "mean": 56.0, "high": 70.0,
            "target_metric": 0.028, "label": "Div Yield", "basis": "equity",
            "net_debt": 0,
        },
    },
    "current_price": 50.00,
}


# ── Tests ──────────────────────────────────────────────────────

def clear_state():
    st_mock.session_state.clear()


def test_no_models():
    """Test 1: No models run → empty rows."""
    clear_state()
    rows = _collect_rows(165.0)
    bars = _collect_bars()
    assert len(rows) == 0, f"Expected 0 rows, got {len(rows)}"
    assert len(bars) == 0, f"Expected 0 bars, got {len(bars)}"
    print("PASS  Test 1: No models → 0 rows, 0 bars")


def test_dcf_only():
    """Test 2: DCF only → 1 row, 1 bar."""
    clear_state()
    st_mock.session_state["dcf_output"] = DCF_OUTPUT
    rows = _collect_rows(165.0)
    bars = _collect_bars()
    assert len(rows) == 1, f"Expected 1 row, got {len(rows)}"
    assert rows[0]["method"] == "DCF"
    assert rows[0]["implied"] == 185.50
    assert "WACC: 9.5%" in rows[0]["notes"]
    assert "g: 2.5%" in rows[0]["notes"]
    assert len(bars) == 1
    assert bars[0]["label"] == "DCF"
    assert bars[0]["low"] == 142.0
    assert bars[0]["high"] == 248.0
    assert bars[0]["mid"] == 185.50
    print("PASS  Test 2: DCF only → 1 row, 1 bar, correct range")


def test_dcf_plus_comps():
    """Test 3: DCF + Comps → 4 rows (1 DCF + 3 comps multiples), 4 bars."""
    clear_state()
    st_mock.session_state["dcf_output"] = DCF_OUTPUT
    st_mock.session_state["comps_valuation"] = COMPS_VALUATION
    rows = _collect_rows(165.0)
    bars = _collect_bars()
    assert len(rows) == 4, f"Expected 4 rows, got {len(rows)}: {[r['method'] for r in rows]}"
    assert rows[0]["method"] == "DCF"
    assert rows[1]["method"] == "Comps (P / E)"
    assert rows[2]["method"] == "Comps (EV / EBITDA)"
    assert rows[3]["method"] == "Comps (EV / Revenue)"
    assert len(bars) == 4
    # Check comps bar range
    pe_bar = bars[1]
    assert pe_bar["low"] == 140.0
    assert pe_bar["high"] == 210.0
    assert pe_bar["mid"] == 172.0
    print("PASS  Test 3: DCF + Comps → 4 rows, 4 bars")


def test_ddm_plus_historical():
    """Test 4: DDM + Historical → 4 rows (1 DDM + 3 hist multiples)."""
    clear_state()
    st_mock.session_state["ddm_output"] = DDM_OUTPUT
    st_mock.session_state["historical_result"] = HISTORICAL_RESULT
    rows = _collect_rows(165.0)
    bars = _collect_bars()
    assert len(rows) == 4, f"Expected 4 rows, got {len(rows)}: {[r['method'] for r in rows]}"
    # DDM should be last
    ddm_row = [r for r in rows if r["method"].startswith("DDM")][0]
    assert ddm_row["implied"] == 142.0
    assert "Ke: 9.5%" in ddm_row["notes"]
    assert "g: 3.0%" in ddm_row["notes"]
    # Historical rows
    hist_rows = [r for r in rows if r["method"].startswith("Historical")]
    assert len(hist_rows) == 3
    assert any("P/E" in r["method"] for r in hist_rows)
    assert any("EV/EBITDA" in r["method"] for r in hist_rows)
    assert any("EV/Revenue" in r["method"] for r in hist_rows)
    # Bars
    assert len(bars) == 4
    hist_bars = [b for b in bars if b["label"].startswith("Historical")]
    assert len(hist_bars) == 3
    pe_hist = [b for b in hist_bars if "P/E" in b["label"]][0]
    assert pe_hist["low"] == 120.0  # at_p10
    assert pe_hist["high"] == 195.0  # at_p90
    assert pe_hist["mid"] == 155.0  # at_median
    print("PASS  Test 4: DDM + Historical → 4 rows, 4 bars")


def test_all_models():
    """Test 5: All 4 models → 8 rows (1 DCF + 3 comps + 3 hist + 1 DDM)."""
    clear_state()
    st_mock.session_state["dcf_output"] = DCF_OUTPUT
    st_mock.session_state["comps_valuation"] = COMPS_VALUATION
    st_mock.session_state["historical_result"] = HISTORICAL_RESULT
    st_mock.session_state["ddm_output"] = DDM_OUTPUT
    rows = _collect_rows(165.0)
    bars = _collect_bars()
    assert len(rows) == 8, f"Expected 8 rows, got {len(rows)}: {[r['method'] for r in rows]}"
    assert len(bars) == 8, f"Expected 8 bars, got {len(bars)}"
    # Check ordering: DCF first, then Comps, then Historical, then DDM
    assert rows[0]["method"] == "DCF"
    assert rows[1]["method"].startswith("Comps")
    assert rows[4]["method"].startswith("Historical")
    assert rows[7]["method"].startswith("DDM")
    print("PASS  Test 5: All models → 8 rows, 8 bars")


def test_financial_comps():
    """Test 6: Financial company Comps → P/Book, P/TBV labels."""
    clear_state()
    st_mock.session_state["comps_valuation"] = COMPS_FINANCIAL
    rows = _collect_rows(50.0)
    bars = _collect_bars()
    methods = [r["method"] for r in rows]
    assert "Comps (P / Book)" in methods, f"Missing P/Book: {methods}"
    assert "Comps (P / TBV)" in methods, f"Missing P/TBV: {methods}"
    assert "Comps (Div Yield)" in methods, f"Missing Div Yield: {methods}"
    assert len(rows) == 4  # P/E, P/Book, P/TBV, Div Yield
    print("PASS  Test 6: Financial Comps → P/Book, P/TBV, Div Yield labels")


def test_summary_stats():
    """Test 7: Summary statistics calculation."""
    clear_state()
    st_mock.session_state["dcf_output"] = DCF_OUTPUT
    st_mock.session_state["ddm_output"] = DDM_OUTPUT
    rows = _collect_rows(165.0)
    prices = [r["implied"] for r in rows]
    assert len(prices) == 2
    mean_p = float(np.mean(prices))
    median_p = float(np.median(prices))
    lo = min(prices)
    hi = max(prices)
    spread = (hi - lo) / mean_p * 100
    assert abs(mean_p - 163.75) < 0.01, f"Mean: {mean_p}"
    assert abs(median_p - 163.75) < 0.01, f"Median: {median_p}"
    assert lo == 142.0, f"Low: {lo}"
    assert hi == 185.50, f"High: {hi}"
    assert spread > 0, f"Spread: {spread}"
    print(f"PASS  Test 7: Summary stats — mean=${mean_p:.2f}, "
          f"spread={spread:.0f}%")


def test_upside_downside():
    """Test 8: Upside/downside calculation."""
    clear_state()
    st_mock.session_state["dcf_output"] = DCF_OUTPUT
    rows = _collect_rows(165.0)
    implied = rows[0]["implied"]
    upside = (implied / 165.0 - 1) * 100
    assert abs(upside - 12.42) < 0.1, f"Upside: {upside}"
    print(f"PASS  Test 8: DCF upside = {upside:+.1f}%")


def test_none_in_comps():
    """Test 9: None values in comps implied_prices are skipped."""
    clear_state()
    comps_with_none = {
        "method": "median",
        "implied_prices": {
            "trailing_pe": COMPS_VALUATION["implied_prices"]["trailing_pe"],
            "ev_ebitda": None,
            "ev_revenue": {
                "low": None, "median": None, "mean": None, "high": None,
                "target_metric": 0, "label": "EV / Revenue", "basis": "ev",
                "net_debt": 0,
            },
        },
        "current_price": 165.0,
    }
    st_mock.session_state["comps_valuation"] = comps_with_none
    rows = _collect_rows(165.0)
    bars = _collect_bars()
    assert len(rows) == 1, f"Expected 1 row, got {len(rows)}"
    assert len(bars) == 1, f"Expected 1 bar, got {len(bars)}"
    print("PASS  Test 9: None values in Comps → correctly skipped")


def test_negative_implied_skipped():
    """Test 10: Negative/zero implied values are skipped."""
    clear_state()
    hist_neg = {
        "implied_values": {
            "pe": {
                "at_mean": -5.0, "at_median": -3.0,
                "at_p10": -10.0, "at_p90": -1.0,
            },
            "ev_ebitda": {
                "at_mean": 0.0, "at_median": 0.0,
                "at_p10": 0.0, "at_p90": 0.0,
            },
        },
        "current_price": 50.0, "currency": "USD",
        "period": 5, "is_financial": False,
    }
    st_mock.session_state["historical_result"] = hist_neg
    rows = _collect_rows(50.0)
    bars = _collect_bars()
    assert len(rows) == 0, f"Expected 0 rows, got {len(rows)}"
    assert len(bars) == 0, f"Expected 0 bars, got {len(bars)}"
    print("PASS  Test 10: Negative/zero implied → skipped")


def test_wide_price_spread():
    """Test 11: Very different implied prices → spread calculation."""
    clear_state()
    st_mock.session_state["dcf_output"] = {
        **DCF_OUTPUT, "implied_price": 200.0,
        "sensitivity_min": 150.0, "sensitivity_max": 250.0,
    }
    st_mock.session_state["ddm_output"] = {
        **DDM_OUTPUT, "implied_price": 50.0,
        "sensitivity_min": 30.0, "sensitivity_max": 80.0,
    }
    rows = _collect_rows(100.0)
    prices = [r["implied"] for r in rows]
    mean_p = float(np.mean(prices))
    spread = (max(prices) - min(prices)) / mean_p * 100
    assert spread == 120.0, f"Spread: {spread}"
    # Bars should also work
    bars = _collect_bars()
    assert bars[0]["low"] == 150.0
    assert bars[1]["low"] == 30.0
    print(f"PASS  Test 11: Wide spread ({spread:.0f}%) — bars scale correctly")


def test_ddm_two_stage():
    """Test 12: DDM 2-stage model label."""
    clear_state()
    st_mock.session_state["ddm_output"] = {
        **DDM_OUTPUT, "model": "two_stage",
    }
    rows = _collect_rows(165.0)
    bars = _collect_bars()
    assert rows[0]["method"] == "DDM (2-Stage)"
    assert bars[0]["label"] == "DDM (2-Stage)"
    print("PASS  Test 12: DDM 2-Stage label correct")


# ── Run all tests ──────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_no_models,
        test_dcf_only,
        test_dcf_plus_comps,
        test_ddm_plus_historical,
        test_all_models,
        test_financial_comps,
        test_summary_stats,
        test_upside_downside,
        test_none_in_comps,
        test_negative_implied_skipped,
        test_wide_price_spread,
        test_ddm_two_stage,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"FAIL  {test.__name__}: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")
    if failed == 0:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
