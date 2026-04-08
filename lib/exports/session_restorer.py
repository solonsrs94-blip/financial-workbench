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

    # Drop widget keys that Streamlit forbids pre-seeding (data_editor etc.).
    # Old saves may contain these; strip on load for backward compat.
    _FORBIDDEN_SUFFIXES = ("_editor", "_btn", "_reset")
    _FORBIDDEN_EXACT = {
        "comps_peer_editor", "comps_exclude_select",
        "wacc_peer_add_input", "ddm_peer_add_input", "comps_manual_add",
    }
    raw_state = {
        k: v for k, v in raw_state.items()
        if not (isinstance(k, str) and (
            k in _FORBIDDEN_EXACT or k.endswith(_FORBIDDEN_SUFFIXES)
        ))
    }

    # Restore Python types (sets, DataFrames)
    state = _restore_types(raw_state)

    # Backstop: seed per-scenario widget keys from stored aggregate dicts
    # for scenarios whose individual widget keys weren't saved (old saves
    # or scenarios that were never opened in the original session).
    _seed_scenario_widgets(state)

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


_SCENARIOS = ("base", "bull", "bear")

# DCF Step 2 driver lists stored as decimals → widget percent
_DCF_PCT_KEYS = (
    "growth_rates", "ebit_margins", "tax_rates",
    "capex_pcts", "da_pcts", "sbc_pcts", "nwc_pcts",
)
# DCF Step 2 driver lists stored as days (no scaling)
_DCF_DAYS_KEYS = ("dso", "dio", "dpo")

# DDM scalar fields: (assumption_key, widget_suffix, scale)
_DDM_SCALAR = [
    ("g", "gordon_g", 100.0),
    ("g1", "g1", 100.0),
    ("g2", "g2", 100.0),
    ("eps_growth", "gordon_eps_g", 100.0),
    ("payout", "gordon_payout", 100.0),
    ("eps_growth1", "eps_g1", 100.0),
    ("eps_growth2", "eps_g2", 100.0),
    ("payout1", "payout1", 100.0),
    ("payout2", "payout2", 100.0),
    ("n", "n_years", 1.0),
]


def _seed_scenario_widgets(state: dict) -> None:
    """Write per-scenario widget keys from stored aggregate dicts.

    Overwrites only when the existing state value is missing or None —
    we explicitly want to rescue saves where widget keys were persisted
    as None but the aggregate dict still has good values.
    """
    def _needs_seed(key: str) -> bool:
        return state.get(key) is None
    # ── DCF Step 2 driver grid ──────────────────────────────────────
    dcf_scen = state.get("dcf_scenarios") or {}
    for scenario in _SCENARIOS:
        assumptions = dcf_scen.get(scenario)
        if not isinstance(assumptions, dict):
            continue
        for akey in _DCF_PCT_KEYS:
            vals = assumptions.get(akey) or []
            for i, v in enumerate(vals):
                k = f"dcf_{scenario}_{akey}_{i}"
                if v is None or not _needs_seed(k):
                    continue
                state[k] = v * 100.0
        for akey in _DCF_DAYS_KEYS:
            vals = assumptions.get(akey) or []
            for i, v in enumerate(vals):
                k = f"dcf_{scenario}_{akey}_{i}"
                if v is None or not _needs_seed(k):
                    continue
                state[k] = float(v)

    # ── DCF Step 4 terminal value ───────────────────────────────────
    dcf_term = state.get("dcf_scenarios_terminal") or {}
    for scenario in _SCENARIOS:
        term = dcf_term.get(scenario)
        if not isinstance(term, dict):
            continue
        g = term.get("g") or term.get("terminal_growth")
        if g is not None:
            k = f"dcf_{scenario}_terminal_g"
            if _needs_seed(k):
                state[k] = g * 100.0
        m = term.get("multiple") or term.get("exit_multiple")
        if m is not None:
            k = f"dcf_{scenario}_exit_multiple"
            if _needs_seed(k):
                state[k] = float(m)

    # ── DDM Step 2 scenario inputs ──────────────────────────────────
    ddm_scen = state.get("ddm_scenarios") or {}
    for scenario in _SCENARIOS:
        assumptions = ddm_scen.get(scenario)
        if not isinstance(assumptions, dict):
            continue
        for akey, suffix, scale in _DDM_SCALAR:
            v = assumptions.get(akey)
            if v is None:
                continue
            k = f"ddm_{scenario}_{suffix}"
            if not _needs_seed(k):
                continue
            state[k] = v * scale if scale != 1.0 else v

    # ── Comps Step 3 scenario inputs ────────────────────────────────
    comps = state.get("comps_valuation") or {}
    for scenario in _SCENARIOS:
        sc = comps.get(scenario)
        if not isinstance(sc, dict):
            continue
        if sc.get("applied_mult") is not None:
            k = f"comps_{scenario}_applied_mult"
            if _needs_seed(k):
                state[k] = float(sc["applied_mult"])
        if sc.get("premium") is not None:
            k = f"comps_{scenario}_premium"
            if _needs_seed(k):
                state[k] = float(sc["premium"])

    # ── Historical Step 2 scenario inputs ───────────────────────────
    hist = state.get("historical_result") or {}
    for scenario in _SCENARIOS:
        sc = hist.get(scenario)
        if not isinstance(sc, dict):
            continue
        if sc.get("applied_mult") is not None:
            k = f"hist_{scenario}_applied_mult"
            if _needs_seed(k):
                state[k] = float(sc["applied_mult"])


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
