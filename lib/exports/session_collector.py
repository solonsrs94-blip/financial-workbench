"""Collect session state into a JSON-serializable dict for saving.

Pure Python — NO streamlit imports.
"""

import dataclasses
import math
from datetime import date, datetime

from lib.exports.company_data import compute_weighted_fair_value

# Keys to collect (no ticker interpolation)
_FIXED_KEYS = [
    "prepared_data", "recommendations", "val_risk_free_rate",
    # DCF
    "dcf_scenarios", "dcf_wacc", "dcf_scenarios_terminal", "dcf_output",
    "dcf_proj_period", "dcf_nwc_method", "dcf_sector_template",
    "dcf_scenarios_initialized", "dcf_scenarios_terminal_init",
    "wacc_beta", "wacc_tax_rate",
    # Comps
    "comps_peers", "comps_table", "comps_valuation",
    "comps_scenarios_initialized", "peer_universe",
    # DDM
    "ddm_ke", "ddm_scenarios", "ddm_output", "ddm_output_alt",
    "ddm_scenarios_initialized", "ddm_beta", "ddm_sector_template",
    # Historical
    "historical_result", "hist_eps_basis", "hist_eps_manual",
    # Summary
    "summary_weights",
]

# Keys that include the ticker (use {ticker} placeholder)
_TICKER_KEYS = [
    "company_{ticker}",
    "val_data_{ticker}",
    "prepared_data_overrides_{ticker}",
    "financial_overrides_{ticker}",
    "ddm_data_{ticker}",
]

# Prefix-matched keys
_PREFIX_KEYS = [
    "commentary_",
]


def collect_valuation_state(state: dict, ticker: str) -> dict:
    """Collect all relevant session state into a saveable dict.

    Returns {"_meta": {...}, "state": {...}}.
    """
    collected = {}

    # Fixed keys
    for key in _FIXED_KEYS:
        if key in state:
            collected[key] = state[key]

    # Ticker-interpolated keys
    for pattern in _TICKER_KEYS:
        key = pattern.format(ticker=ticker)
        if key in state:
            collected[key] = state[key]

    # Prefix-matched keys
    for prefix in _PREFIX_KEYS:
        for key in state:
            if isinstance(key, str) and key.startswith(prefix):
                collected[key] = state[key]

    # Make everything JSON-safe
    safe_state = _make_json_safe(collected)

    # Build metadata
    meta = _build_meta(state, ticker)

    return {"_meta": meta, "state": safe_state}


def _build_meta(state: dict, ticker: str) -> dict:
    """Build metadata envelope for the saved valuation."""
    company = state.get(f"company_{ticker}")
    name = ""
    price = 0.0
    currency = "USD"

    if company:
        info = getattr(company, "info", None)
        price_obj = getattr(company, "price", None)
        name = getattr(info, "name", "") or ""
        price = getattr(price_obj, "price", 0) or 0
        currency = getattr(price_obj, "currency", "USD") or "USD"
        if not currency:
            val_data = state.get(f"val_data_{ticker}") or {}
            currency = val_data.get("currency", "USD")

    # Determine which models were completed
    models = []
    if state.get("dcf_output"):
        models.append("DCF")
    if state.get("comps_valuation"):
        models.append("Comps")
    if state.get("historical_result"):
        models.append("Historical")
    if state.get("ddm_output"):
        models.append("DDM")

    # Weighted fair value
    weighted_fv = None
    weights = state.get("summary_weights")
    if weights:
        _KEY_MAP = {
            "dcf": "dcf_output", "comps": "comps_valuation",
            "historical_multiples": "historical_result", "ddm": "ddm_output",
        }
        football = {}
        for label, key in _KEY_MAP.items():
            data = state.get(key)
            if data and isinstance(data, dict):
                prices = _extract_scenario_prices(data)
                if prices:
                    football[label] = prices
        result = compute_weighted_fair_value(football, weights)
        if result:
            weighted_fv = result.get("weighted_fair_value")

    return {
        "version": 1,
        "ticker": ticker,
        "company_name": name,
        "save_date": datetime.now().isoformat(timespec="seconds"),
        "share_price": price,
        "currency": currency,
        "models_completed": models,
        "weighted_fair_value": weighted_fv,
    }


def _extract_scenario_prices(data: dict) -> dict | None:
    """Extract bear/base/bull implied prices from scenario data."""
    if "base" in data and isinstance(data.get("base"), dict):
        return {
            s: data[s].get("implied_price")
            for s in ["base", "bull", "bear"]
            if s in data and isinstance(data[s], dict)
        }
    if data.get("implied_price"):
        return {"base": data["implied_price"]}
    return None


def _make_json_safe(obj):
    """Recursively convert obj to JSON-serializable types."""
    if obj is None:
        return None

    # Primitives
    if isinstance(obj, (bool, int, str)):
        return obj
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj

    # Collections
    if isinstance(obj, dict):
        return {str(k): _make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_make_json_safe(item) for item in obj]
    if isinstance(obj, set):
        return {"__set__": True, "values": sorted(
            [_make_json_safe(v) for v in obj],
            key=lambda x: str(x),
        )}
    if isinstance(obj, frozenset):
        return {"__set__": True, "values": sorted(
            [_make_json_safe(v) for v in obj],
            key=lambda x: str(x),
        )}

    # NumPy types
    try:
        import numpy as np
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            val = float(obj)
            if math.isnan(val) or math.isinf(val):
                return None
            return val
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return _make_json_safe(obj.tolist())
    except ImportError:
        pass

    # Pandas
    try:
        import pandas as pd
        if isinstance(obj, pd.DataFrame):
            if obj.empty:
                return None
            df = obj.copy()
            df.columns = [str(c) for c in df.columns]
            index_name = df.index.name or "index"
            df = df.reset_index()
            return {
                "__df__": True,
                "__index_col__": index_name,
                "__data__": _make_json_safe(df.to_dict(orient="list")),
            }
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        if isinstance(obj, pd.Series):
            return _make_json_safe(obj.to_dict())
    except ImportError:
        pass

    # Dates
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, date):
        return obj.isoformat()

    # Dataclasses (Company, CompanyInfo, CompanyPrice, CompanyRatios)
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        d = {}
        for f in dataclasses.fields(obj):
            val = getattr(obj, f.name)
            # Skip DataFrame fields on Company (large, not needed)
            try:
                import pandas as pd
                if isinstance(val, pd.DataFrame):
                    d[f.name] = None
                    continue
            except ImportError:
                pass
            d[f.name] = _make_json_safe(val)
        d["__dataclass__"] = type(obj).__name__
        return d

    # Fallback
    return str(obj)
