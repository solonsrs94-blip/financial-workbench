"""Restore a saved valuation dict into session state keys.

Pure Python — NO streamlit imports.
"""

from models.company import Company, CompanyInfo, CompanyPrice, CompanyRatios


def restore_valuation_state(saved: dict) -> tuple[dict, str]:
    """Convert a saved valuation dict into flat session state keys.

    Returns (state_dict, ticker) where state_dict is ready to inject
    into st.session_state.
    """
    meta = saved.get("_meta", {})
    ticker = meta.get("ticker", "")
    raw_state = saved.get("state", {})

    # Restore Python types (sets, DataFrames)
    state = _restore_types(raw_state)

    # Reconstruct Company dataclass from serialized dict
    company_key = f"company_{ticker}"
    if company_key in state:
        state[company_key] = _restore_company(state[company_key])

    # Set cache-guard keys so the valuation page doesn't wipe loaded data
    state["_val_cached_ticker"] = ticker
    state["_loaded_from_save"] = True
    state["_loaded_ticker"] = ticker

    # Ensure preparation cache key is set (preparation.py caches here)
    prepared = state.get("prepared_data")
    if prepared:
        state[f"prepared_data_{ticker}"] = prepared

    return state, ticker


def _restore_company(data) -> Company:
    """Reconstruct a Company dataclass from a serialized dict."""
    if not isinstance(data, dict):
        return data

    info_data = data.get("info", {}) or {}
    price_data = data.get("price", {}) or {}
    ratios_data = data.get("ratios", {}) or {}

    # Remove __dataclass__ markers
    for d in [info_data, price_data, ratios_data]:
        d.pop("__dataclass__", None)

    # Build sub-dataclasses, filtering unknown fields
    info = _build_dataclass(CompanyInfo, info_data)
    price = _build_dataclass(CompanyPrice, price_data)
    ratios = _build_dataclass(CompanyRatios, ratios_data)

    return Company(info=info, price=price, ratios=ratios)


def _build_dataclass(cls, data: dict):
    """Build a dataclass instance, ignoring unknown fields."""
    import dataclasses
    valid_fields = {f.name for f in dataclasses.fields(cls)}
    filtered = {k: v for k, v in data.items() if k in valid_fields}
    return cls(**filtered)


def _restore_types(obj):
    """Recursively restore Python types from JSON-safe format."""
    if obj is None:
        return None

    if isinstance(obj, dict):
        # Set marker
        if obj.get("__set__") is True and "values" in obj:
            return set(_restore_types(v) for v in obj["values"])

        # DataFrame marker
        if obj.get("__df__") is True:
            return _restore_dataframe(obj)

        # Regular dict — recurse values
        return {k: _restore_types(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [_restore_types(item) for item in obj]

    # Primitives pass through
    return obj


def _restore_dataframe(data: dict):
    """Reconstruct a pandas DataFrame from serialized format."""
    try:
        import pandas as pd
        df = pd.DataFrame(data["__data__"])
        index_col = data.get("__index_col__", "index")
        if index_col in df.columns:
            df = df.set_index(index_col)
            df.index.name = None
        return df
    except (ImportError, Exception):
        return data
