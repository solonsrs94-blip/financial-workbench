"""Historical ratio calculations — margins, growth, efficiency, returns.

Split from historical.py to keep under 200 lines.
No Streamlit imports allowed (lib/ rule).
"""

from typing import Optional


def _safe_div(a: Optional[float], b: Optional[float]) -> Optional[float]:
    if a is None or b is None or b == 0:
        return None
    return a / b


def _pct_change(new: Optional[float], old: Optional[float]) -> Optional[float]:
    if new is None or old is None or old == 0:
        return None
    return (new - old) / abs(old)


def build_ratios_table(
    is_table: list[dict], bs_table: list[dict], cf_table: list[dict],
) -> list[dict]:
    """Calculate key ratios per year from IS, BS, CF tables."""
    rows = []
    for i, is_row in enumerate(is_table):
        yr = is_row["year"]
        rev = is_row.get("revenue")
        cogs = is_row.get("cogs")
        gp = is_row.get("gross_profit")
        ebit = is_row.get("ebit")
        ebitda = is_row.get("ebitda")
        ni = is_row.get("net_income")
        da = is_row.get("da")
        tax = is_row.get("tax_provision")
        pretax = is_row.get("pretax_income")

        bs = bs_table[i] if i < len(bs_table) else {}
        cf = cf_table[i] if i < len(cf_table) else {}

        ar = bs.get("accounts_receivable")
        inv = bs.get("inventories")
        ap = bs.get("accounts_payable")
        total_assets = bs.get("total_assets")
        total_equity = bs.get("total_equity")
        total_debt = bs.get("total_debt")
        capex = cf.get("capital_expenditure")
        fcf = cf.get("free_cash_flow")
        sbc = cf.get("stock_based_compensation") or cf.get("sbc")
        cf_da = cf.get("da")

        if da is None:
            da = cf_da

        # Margins
        gross_margin = _safe_div(gp, rev)
        ebit_margin = _safe_div(ebit, rev)
        ebitda_margin = _safe_div(ebitda, rev)
        net_margin = _safe_div(ni, rev)
        fcf_margin = _safe_div(fcf, rev)

        # Growth
        prev_rev = is_table[i - 1].get("revenue") if i > 0 else None
        prev_ni = is_table[i - 1].get("net_income") if i > 0 else None
        rev_growth = _pct_change(rev, prev_rev)
        ni_growth = _pct_change(ni, prev_ni)

        # Efficiency (working capital days)
        abs_cogs = abs(cogs) if cogs is not None else None
        dso = _safe_div(ar, rev) * 365 if ar and rev else None
        dio = _safe_div(inv, abs_cogs) * 365 if inv and abs_cogs else None
        dpo = _safe_div(ap, abs_cogs) * 365 if ap and abs_cogs else None

        # Investment
        capex_pct = _safe_div(abs(capex) if capex else None, rev)
        da_pct = _safe_div(abs(da) if da else None, rev)
        capex_da = _safe_div(
            abs(capex) if capex else None, abs(da) if da else None,
        )
        sbc_pct = _safe_div(sbc, rev)

        # Returns
        eff_tax = None
        if pretax and pretax > 0 and tax is not None:
            eff_tax = _safe_div(abs(tax), pretax)
        nopat = ebit * (1 - (eff_tax or 0.21)) if ebit else None
        invested_cap = None
        if total_equity is not None and total_debt is not None:
            cash = bs.get("cash") or 0
            invested_cap = total_equity + total_debt - cash
        roic = _safe_div(nopat, invested_cap)
        roe = _safe_div(ni, total_equity)
        roa = _safe_div(ni, total_assets)

        # Leverage & coverage
        interest = is_row.get("interest_expense")
        interest_coverage = _safe_div(ebit, interest) if interest and interest > 0 else None
        debt_ebitda = _safe_div(total_debt, ebitda) if ebitda and ebitda > 0 else None
        debt_equity = _safe_div(total_debt, total_equity) if total_equity and total_equity > 0 else None
        current_ratio = _safe_div(
            bs.get("total_current_assets"), bs.get("total_current_liabilities"),
        )

        # FCF quality
        fcf_conversion = _safe_div(fcf, ni) if ni and ni > 0 else None
        fcf_yield = None  # Needs market cap — calculated at page level

        # NWC / Revenue — try explicit, then derive from CA - CL
        wc = bs.get("working_capital")
        if wc is None:
            ca = bs.get("total_current_assets")
            cl = bs.get("total_current_liabilities")
            if ca is not None and cl is not None:
                wc = ca - cl
        nwc_pct_rev = _safe_div(wc, rev)

        # EPS growth
        prev_eps = is_table[i - 1].get("diluted_eps") if i > 0 else None
        curr_eps = is_row.get("diluted_eps")
        eps_growth = _pct_change(curr_eps, prev_eps)

        # EBITDA growth
        prev_ebitda = is_table[i - 1].get("ebitda") if i > 0 else None
        ebitda_growth = _pct_change(ebitda, prev_ebitda)

        # Payout ratio
        divs = cf.get("dividends_paid")
        payout_ratio = _safe_div(abs(divs) if divs else None, ni) if ni and ni > 0 else None

        # Asset turnover
        asset_turnover = _safe_div(rev, total_assets)

        rows.append({
            "year": yr,
            # Margins
            "gross_margin": gross_margin,
            "ebit_margin": ebit_margin,
            "ebitda_margin": ebitda_margin,
            "net_margin": net_margin,
            "fcf_margin": fcf_margin,
            # Growth
            "revenue_growth": rev_growth,
            "net_income_growth": ni_growth,
            "ebitda_growth": ebitda_growth,
            "eps_growth": eps_growth,
            # Efficiency
            "dso": dso,
            "dio": dio,
            "dpo": dpo,
            "nwc_pct_revenue": nwc_pct_rev,
            "asset_turnover": asset_turnover,
            # Investment
            "capex_pct": capex_pct,
            "da_pct": da_pct,
            "capex_da_ratio": capex_da,
            "sbc_pct": sbc_pct,
            # Leverage & Coverage
            "interest_coverage": interest_coverage,
            "debt_ebitda": debt_ebitda,
            "debt_equity": debt_equity,
            "current_ratio": current_ratio,
            # Returns
            "effective_tax_rate": eff_tax,
            "roic": roic,
            "roe": roe,
            "roa": roa,
            # Quality
            "fcf_conversion": fcf_conversion,
            "payout_ratio": payout_ratio,
        })
    return rows
