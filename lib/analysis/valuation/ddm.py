"""DDM calculation engine — Gordon Growth + 2-Stage models.

Pure Python — NO Streamlit imports.
All rates as decimals (0.10 = 10%).
"""

import numpy as np
import pandas as pd


def gordon_growth(d0: float, ke: float, g: float) -> dict:
    """Single-stage Gordon Growth Model: P₀ = D₁ / (Ke − g).

    Args:
        d0: Current annual DPS.
        ke: Cost of equity (decimal).
        g: Perpetual dividend growth rate (decimal).

    Returns dict with implied_price, d1, ke, g.
    """
    d1 = d0 * (1 + g)
    if ke <= g:
        return {"implied_price": 0.0, "d1": d1, "error": "g >= Ke"}
    return {
        "implied_price": d1 / (ke - g),
        "d1": d1,
        "d0": d0,
        "ke": ke,
        "g": g,
    }


def two_stage_ddm(
    d0: float,
    ke: float,
    g1: float,
    g2: float,
    n: int,
    eps0: float | None = None,
    eps_growth1: float | None = None,
    payout1: float | None = None,
    eps_growth2: float | None = None,
    payout2: float | None = None,
    use_eps_method: bool = False,
) -> dict:
    """2-Stage DDM.

    Two projection methods:
      A) Direct DPS growth: DPS grows at g1 for N years, then g2.
      B) EPS × Payout: EPS grows, DPS = EPS × payout ratio.

    Args:
        d0: Current DPS.
        ke: Cost of equity.
        g1: Stage 1 DPS growth (method A) or ignored if use_eps_method.
        g2: Terminal growth rate.
        n: High-growth period years.
        eps0: Current EPS (method B).
        eps_growth1: Stage 1 EPS growth (method B).
        payout1: Stage 1 payout ratio (method B).
        eps_growth2: Terminal EPS growth (method B).
        payout2: Terminal payout ratio (method B).
        use_eps_method: True for method B.

    Returns dict with implied_price, pv_stage1, pv_terminal,
        terminal_value, projection_table.
    """
    rows = []
    pv_dividends = 0.0

    if use_eps_method and eps0 and eps_growth1 is not None and payout1 is not None:
        # Method B: EPS × Payout
        eps = eps0
        for t in range(1, n + 1):
            eps = eps * (1 + eps_growth1)
            po = payout1
            dps = eps * po
            pv_factor = 1 / (1 + ke) ** t
            pv = dps * pv_factor
            pv_dividends += pv
            rows.append({
                "Year": t,
                "EPS": eps,
                "Payout": po,
                "DPS": dps,
                "PV Factor": pv_factor,
                "PV of Dividend": pv,
            })
        # Terminal DPS
        term_eps = eps * (1 + (eps_growth2 or g2))
        term_dps = term_eps * (payout2 or payout1)
    else:
        # Method A: Direct DPS Growth
        dps = d0
        for t in range(1, n + 1):
            dps = dps * (1 + g1)
            pv_factor = 1 / (1 + ke) ** t
            pv = dps * pv_factor
            pv_dividends += pv
            rows.append({
                "Year": t,
                "DPS": dps,
                "PV Factor": pv_factor,
                "PV of Dividend": pv,
            })
        # Terminal DPS
        term_dps = dps * (1 + g2)

    # Terminal value (Gordon Growth at year N)
    if ke <= g2:
        return {
            "implied_price": 0.0,
            "error": "Terminal growth >= Ke",
        }

    terminal_value = term_dps / (ke - g2)
    pv_terminal = terminal_value / (1 + ke) ** n

    implied_price = pv_dividends + pv_terminal

    return {
        "implied_price": implied_price,
        "pv_stage1": pv_dividends,
        "pv_terminal": pv_terminal,
        "terminal_value": terminal_value,
        "terminal_dps": term_dps,
        "projection": pd.DataFrame(rows),
        "n": n,
        "ke": ke,
        "g1": g1,
        "g2": g2,
    }


def ddm_sensitivity(
    d0: float,
    ke_base: float,
    g_base: float,
    model: str = "gordon",
    n: int = 5,
    g1: float | None = None,
    eps0: float | None = None,
    eps_growth1: float | None = None,
    payout1: float | None = None,
    eps_growth2: float | None = None,
    payout2: float | None = None,
    use_eps_method: bool = False,
    ke_steps: int = 9,
    g_steps: int = 9,
) -> pd.DataFrame:
    """2D sensitivity table: Ke (rows) vs growth (cols) → implied price.

    For Gordon: varies Ke and g directly.
    For 2-Stage: varies Ke and terminal growth (g2).
    """
    ke_range = np.linspace(
        max(0.01, ke_base - 0.02), ke_base + 0.02, ke_steps,
    )
    g_range = np.linspace(
        max(0.001, g_base - 0.02), g_base + 0.02, g_steps,
    )

    data = {}
    for g in g_range:
        col = []
        for ke in ke_range:
            if model == "gordon":
                r = gordon_growth(d0, ke, g)
            else:
                r = two_stage_ddm(
                    d0, ke,
                    g1=g1 or 0.05,
                    g2=g,
                    n=n,
                    eps0=eps0,
                    eps_growth1=eps_growth1,
                    payout1=payout1,
                    eps_growth2=g if use_eps_method else None,
                    payout2=payout2,
                    use_eps_method=use_eps_method,
                )
            price = r.get("implied_price", 0.0)
            col.append(max(price, 0.0))
        data[f"g={g:.1%}"] = col

    return pd.DataFrame(data, index=[f"{ke:.1%}" for ke in ke_range])
