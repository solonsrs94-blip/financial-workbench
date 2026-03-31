"""Standardizer utilities — derived fields calculator and cross-checks.

Split from standardizer.py for file size compliance.
No Streamlit imports (lib/ rule).
"""


# ============================================================
# DERIVED FIELDS
# ============================================================

def compute_derived_fields(std_data: dict) -> None:
    """Compute fields that can be derived from others.

    Modifies std_data in place, adding derived fields where missing.
    """
    for year, fields in std_data.items():
        _v = lambda k: fields.get(k, {}).get("value") if isinstance(fields.get(k), dict) else fields.get(k)

        rev = _v("revenue")
        cogs = _v("cogs")
        gp = _v("gross_profit")
        ebit = _v("ebit")
        da = _v("da") or _v("depreciation_amortization")
        pretax = _v("pretax_income")
        tax = _v("tax_provision")
        ni = _v("net_income")
        ocf = _v("operating_cash_flow")
        capex = _v("capital_expenditure")

        sga = _v("sga")
        s_and_m = _v("selling_and_marketing")
        rd = _v("rd")
        interest_exp = _v("interest_expense")
        total_costs = _v("total_costs")

        # SGA combination: merge S&M + G&A into sga if split
        g_and_a = _v("general_and_administrative")
        if s_and_m and g_and_a:
            combined = abs(s_and_m) + abs(g_and_a)
            fields["sga"] = {
                "value": combined,
                "raw_label": "Derived: S&M + G&A",
                "layer": 0,
            }
            sga = combined
        elif s_and_m and sga:
            # S&M exists alongside something already called sga — add
            combined = abs(s_and_m) + abs(sga)
            fields["sga"] = {
                "value": combined,
                "raw_label": "Derived: S&M + SGA",
                "layer": 0,
            }
            sga = combined
        elif s_and_m and not sga:
            fields["sga"] = {
                "value": abs(s_and_m),
                "raw_label": "Derived: from S&M only",
                "layer": 0,
            }
            sga = abs(s_and_m)

        # D&A combination: merge depreciation + amortization if split
        dep_only = _v("depreciation")
        amort_only = _v("amortization") or _v("amortization_intangibles")
        if not da and (dep_only or amort_only):
            da_val = abs(dep_only or 0) + abs(amort_only or 0)
            fields["depreciation_amortization"] = {
                "value": da_val,
                "raw_label": "Derived: Depreciation + Amortization",
                "layer": 0,
            }
            da = da_val

        # Gross Profit = Revenue - COGS
        if not gp and rev and cogs:
            gp_val = rev - abs(cogs)
            fields["gross_profit"] = {
                "value": gp_val, "raw_label": "Derived: Revenue - COGS",
                "layer": 0,
            }
            gp = gp_val

        # EBIT = GP - SGA - R&D (if no explicit EBIT, e.g. JNJ)
        if not ebit and gp:
            ebit_val = gp
            components = "GP"
            if sga:
                ebit_val -= abs(sga)
                components += " - SGA"
            if rd:
                ebit_val -= abs(rd)
                components += " - R&D"
            if da:
                ebit_val -= abs(da)
                components += " - D&A"
            fields["ebit"] = {
                "value": ebit_val,
                "raw_label": f"Derived: {components}",
                "layer": 0,
            }
            ebit = ebit_val

        # EBIT from Pretax + Interest (energy companies like XOM)
        if not ebit and pretax and interest_exp:
            ebit_val = pretax + abs(interest_exp)
            fields["ebit"] = {
                "value": ebit_val,
                "raw_label": "Derived: Pretax + Interest Expense",
                "layer": 0,
            }
            ebit = ebit_val

        # GP from Revenue - Total Costs + EBIT (energy: Rev - TotalCosts = Pretax)
        if not gp and rev and total_costs and ebit:
            # For energy: COGS is not separate, but GP ≈ EBIT + SGA + R&D + D&A
            gp_val = ebit
            if sga:
                gp_val += abs(sga)
            if rd:
                gp_val += abs(rd)
            if da:
                gp_val += abs(da)
            fields["gross_profit"] = {
                "value": gp_val,
                "raw_label": "Derived: EBIT + OpEx (no separate COGS)",
                "layer": 0,
            }

        # EBITDA = EBIT + D&A (within same statement — if IS has its own D&A)
        if not _v("ebitda") and ebit and da:
            fields["ebitda"] = {
                "value": ebit + abs(da),
                "raw_label": "Derived: EBIT + D&A", "layer": 0,
            }

        # Net Income = Pretax - Tax (if missing)
        if not ni and pretax and tax:
            fields["net_income"] = {
                "value": pretax - abs(tax),
                "raw_label": "Derived: Pretax - Tax", "layer": 0,
            }

        # Total Equity: fallback to incl_minority if specific is missing
        if not _v("total_equity") and _v("total_equity_incl_minority"):
            minority = _v("minority_interest") or 0
            eq_val = _v("total_equity_incl_minority") - minority
            fields["total_equity"] = {
                "value": eq_val,
                "raw_label": "Derived: Total Equity Incl. Minority - Minority",
                "layer": 0,
            }

        # Total Liabilities = Total Assets - Total Equity
        ta = _v("total_assets")
        tl = _v("total_liabilities")
        te = _v("total_equity")
        tei = _v("total_equity_incl_minority")
        if not tl and ta:
            eq_for_calc = tei or te  # prefer incl_minority
            if eq_for_calc:
                fields["total_liabilities"] = {
                    "value": ta - eq_for_calc,
                    "raw_label": "Derived: Total Assets - Total Equity",
                    "layer": 0,
                }

        # FCF = OCF - CapEx
        if not _v("free_cash_flow") and ocf and capex:
            fields["free_cash_flow"] = {
                "value": ocf - abs(capex),
                "raw_label": "Derived: OCF - CapEx", "layer": 0,
            }

        # Net Debt — computed in cross-statement step (historical.py)
        # to include short_term_investments in the subtraction.


# ============================================================
# CROSS-CHECKS
# ============================================================

def run_cross_checks(std_data: dict, statement_type: str) -> list[dict]:
    """Validate internal consistency. Returns list of check results."""
    checks = []

    for year, fields in std_data.items():
        _v = lambda k: fields.get(k, {}).get("value") if isinstance(fields.get(k), dict) else fields.get(k)

        if statement_type == "income":
            rev = _v("revenue")
            cogs = _v("cogs")
            gp = _v("gross_profit")
            if rev and cogs and gp:
                expected_gp = rev - abs(cogs)
                diff = abs(gp - expected_gp)
                ok = diff < abs(rev) * 0.01  # Within 1%
                checks.append({
                    "year": year, "check": "Revenue - COGS = GP",
                    "ok": ok, "diff": diff,
                })

        elif statement_type == "balance":
            assets = _v("total_assets")
            liab = _v("total_liabilities")
            eq = _v("total_equity_incl_minority") or _v("total_equity")
            if assets and liab and eq:
                expected = liab + eq
                diff = abs(assets - expected)
                ok = diff < abs(assets) * 0.01
                checks.append({
                    "year": year, "check": "Assets = L + E",
                    "ok": ok, "diff": diff,
                })

    return checks
