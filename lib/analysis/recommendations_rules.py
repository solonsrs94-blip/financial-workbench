"""Recommendation building blocks — model assessment rules.

Each rule checks a condition and returns a recommendation dict.
Model assessment rules always return a result (never None).
Rules consume a `ctx` dict built by the orchestrator with derived signals.

Attention items and risk rules are in recommendations_risks.py.

No Streamlit imports (lib/ rule).
"""


# ── Helpers ─────────────────────────────────────────────────────────

def _fmt_pct(v: float) -> str:
    return f"{v * 100:.1f}%"


def _fmt_m(v: float) -> str:
    if abs(v) >= 1000:
        return f"${v / 1000:.1f}B"
    return f"${v:.0f}M"


def _model(name, fit, headline, reasons, caveats=None):
    return {"model": name, "fit": fit, "headline": headline,
            "reasons": reasons, "caveats": caveats or []}


# ═══════════════════════════════════════════════════════════════════
# MODEL ASSESSMENT RULES — always return a result
# ═══════════════════════════════════════════════════════════════════

def assess_dcf(ctx: dict) -> dict:
    """Assess DCF suitability."""
    if ctx["is_financial"]:
        return _model("dcf", "weak",
            "DCF has limited value — bank/insurance revenue from interest/premiums",
            ["Free cash flow concept does not apply to financial institutions",
             "Balance sheet IS the business — NIM and ROE are the key metrics"],
            ["Use P/B and P/TBV for relative valuation instead of EV-based metrics"])

    reasons, caveats = [], []
    avg = ctx["averages"]
    ebit_m = avg.get("ebit_margin_3yr")
    fcf_yrs = ctx.get("fcf_positive_years", 0)
    total_yrs = ctx.get("n_years", 0)

    if ctx["is_dividend_stable"]:
        reasons.append("Provides fundamental cross-check alongside DDM")
        if ebit_m is not None:
            reasons.append(f"Stable margins ({_fmt_pct(ebit_m)} 3yr avg EBIT) support projections")
        if ctx.get("has_positive_fcf"):
            reasons.append(f"Positive FCF in {fcf_yrs} of {total_yrs} years")
        return _model("dcf", "moderate",
            "DCF provides fundamental cross-check — DDM is primary for this company",
            reasons, caveats)

    # Normal company
    if ctx.get("has_positive_fcf") and ctx.get("margin_stable"):
        fit = "strong"
        headline = "DCF is the primary model"
        if ebit_m is not None:
            headline += f" — stable {_fmt_pct(ebit_m)} EBIT margin"
        reasons.append(f"Positive FCF in {fcf_yrs} of {total_yrs} years")
        if ctx.get("margin_stable") and ebit_m:
            reasons.append("Stable margin profile supports reliable projection")
    elif ctx.get("has_positive_fcf"):
        fit = "strong"
        headline = "DCF is the primary model — positive FCF base"
        reasons.append(f"Positive FCF in {fcf_yrs} of {total_yrs} years")
        if ctx.get("fcf_volatile"):
            caveats.append("FCF volatility suggests wider scenario ranges")
    else:
        fit = "moderate"
        headline = "DCF applicable but requires careful FCF projection"
        reasons.append("Standard operating company — DCF is the natural framework")
        if fcf_yrs < total_yrs:
            caveats.append(
                f"Negative FCF in {total_yrs - fcf_yrs} of {total_yrs} years"
                " — model path to positive FCF explicitly")

    # Common caveats
    sbc = avg.get("sbc_pct_3yr")
    if sbc and sbc > 0.03:
        caveats.append(f"High SBC ({_fmt_pct(sbc)} of revenue) — adjust FCF for dilution")
    if "m_and_a" in ctx["flag_categories"]:
        caveats.append("Recent M&A — strip acquisition effects or use pro-forma base")
    rev_g = avg.get("revenue_growth_3yr")
    if rev_g is not None and rev_g < -0.02:
        caveats.append(f"Revenue declining ({_fmt_pct(rev_g)} 3yr avg) — model turnaround explicitly")

    return _model("dcf", fit, headline, reasons, caveats)


def assess_ddm(ctx: dict) -> dict:
    """Assess DDM suitability."""
    div = ctx.get("dividend_data") or {}
    has_div = div.get("has_dividend", False)
    yrs_pay = div.get("years_paying", 0)
    yrs_inc = div.get("years_increasing_clean", div.get("years_increasing", 0))
    cuts = div.get("dividend_cuts_clean", div.get("dividend_cuts", []))
    payout = div.get("payout_ratio")
    dps_cagr = div.get("dps_cagr_clean", div.get("dps_cagr", {}))

    if ctx["is_financial"]:
        reasons = ["Financial institution — capital return capacity drives valuation",
                   "Dividend policy reflects regulatory capital constraints"]
        if has_div and yrs_pay > 0:
            reasons.append(f"{yrs_pay} years of consecutive dividend payments")
        return _model("ddm", "strong",
            "DDM is the primary model — bank/insurance valuation driven by capital return",
            reasons)

    if not has_div:
        reasons = ["Company does not pay dividends"]
        cf = ctx.get("latest_cf", {})
        bb = abs(cf.get("buybacks_and_issuance", 0) or 0)
        if bb > 0:
            reasons.append(f"Buyback-focused capital return ({_fmt_m(bb / 1e6)} in latest year)")
        return _model("ddm", "weak",
            "DDM not applicable — no dividend history", reasons)

    reasons, caveats = [], []

    if ctx["is_dividend_stable"] or ctx.get("category") == "reit":
        fit = "strong"
        headline = "DDM is the primary model"
        if yrs_pay >= 10:
            reasons.append(f"{yrs_pay} years of consecutive dividend payments")
        if yrs_inc >= 5:
            reasons.append(f"{yrs_inc} consecutive years of dividend increases")
        if ctx.get("category") == "reit":
            reasons.append("REIT must distribute 90%+ of taxable income")
            headline += " — REIT distribution requirement"
        elif payout and payout > 0.5:
            reasons.append(f"High payout ratio ({_fmt_pct(payout)}) — mature distribution policy")
        cagr_5 = dps_cagr.get("5y")
        if cagr_5 is not None:
            reasons.append(f"5yr DPS CAGR: {_fmt_pct(cagr_5)}")
    elif yrs_pay >= 5 and not cuts:
        fit = "moderate"
        headline = f"DDM viable — {yrs_pay} years of payments, no cuts"
        reasons.append(f"{yrs_pay} consecutive years of dividend payments")
        if yrs_inc >= 3:
            reasons.append(f"{yrs_inc} consecutive increases")
        caveats.append("DDM is secondary to DCF for this company type")
    else:
        fit = "weak"
        headline = "DDM has limited value"
        if yrs_pay < 3:
            reasons.append(f"Only {yrs_pay} years of payments — insufficient track record")
        if cuts:
            cut_yrs = ", ".join(str(y) for y in cuts[-3:])
            reasons.append(f"Dividend cuts in {cut_yrs} — unstable policy")

    if payout and payout > 0.85 and fit != "weak":
        caveats.append(f"Payout ratio {_fmt_pct(payout)} approaching ceiling — DPS growth limited to EPS growth")

    return _model("ddm", fit, headline, reasons, caveats)


def assess_comps(ctx: dict) -> dict:
    """Assess Comparable Companies suitability."""
    ind = ctx.get("industry_averages")
    reasons, caveats = [], []

    if ctx["is_financial"]:
        sub = ctx.get("subtype", "bank")
        reasons.append(f"Large peer group of {sub}s with comparable metrics")
        reasons.append("Key multiples: P/B, P/TBV, P/E (not EV/EBITDA)")
        caveats.append("Ensure peers have similar business mix and geography")
        return _model("comps", "moderate",
            f"Comps useful — established {sub} peer group",
            reasons, caveats)

    if ind:
        name = ind.get("industry_name", "")
        n = ind.get("n_firms")
        reasons.append(f"Industry data available: {name}")
        if n:
            reasons.append(f"Damodaran sample: {n} firms in industry")

        ebit_m = ctx["averages"].get("ebit_margin_3yr")
        ind_m = ind.get("operating_margin")
        if ebit_m and ind_m and ind_m > 0:
            ratio = ebit_m / ind_m
            if ratio > 2.0:
                caveats.append(
                    f"Company margin ({_fmt_pct(ebit_m)}) is {ratio:.1f}x industry "
                    f"({_fmt_pct(ind_m)}) — peers may not be comparable")
                return _model("comps", "moderate",
                    "Comps useful but company is a margin outlier",
                    reasons, caveats)
            elif ratio < 0.5:
                caveats.append(
                    f"Company margin ({_fmt_pct(ebit_m)}) well below industry "
                    f"({_fmt_pct(ind_m)}) — select peers carefully")

        fit = "strong"
        headline = "Comps provide strong relative valuation anchor"
        if ctx.get("category") == "reit":
            reasons.append("P/FFO and P/AFFO are key REIT multiples (not P/E)")
        caveats.append("Accounting differences across peers can distort multiples")
    else:
        fit = "moderate"
        headline = "Comps applicable — limited industry benchmark data"
        reasons.append("Standard relative valuation framework applies")
        caveats.append("No Damodaran industry data found — select peers manually")

    return _model("comps", fit, headline, reasons, caveats)


def assess_historical(ctx: dict) -> dict:
    """Assess Historical Multiples suitability."""
    reasons, caveats = [], []
    n_yrs = ctx.get("n_years", 0)

    if ctx["is_financial"]:
        reasons.append("P/B and P/TBV time series useful for cycle analysis")
        caveats.append("P/E multiples can be distorted by provision cycles")
        return _model("historical", "moderate",
            "Historical multiples useful for cycle positioning",
            reasons, caveats)

    has_ma = "m_and_a" in ctx["flag_categories"]
    has_goodwill = any(f.get("what", "").startswith("Goodwill")
                       for f in ctx.get("flags", []))

    if ctx.get("margin_stable") and not has_ma and n_yrs >= 4:
        fit = "strong"
        headline = "Historical multiples reliable — stable margin profile"
        reasons.append(f"{n_yrs} years of data with consistent margins")
        reasons.append("Mean-reversion analysis well-supported")
    elif n_yrs >= 3:
        fit = "moderate"
        headline = "Historical multiples provide context — interpret with care"
        if has_ma:
            caveats.append("M&A activity changed the business — pre-acquisition multiples may not apply")
        if ctx.get("margin_volatile"):
            caveats.append("Volatile margins make P/E mean-reversion less reliable — prefer EV/EBITDA")
        reasons.append(f"{n_yrs} years of historical data available")
    else:
        fit = "weak"
        headline = f"Historical multiples limited — only {n_yrs} years of data"
        reasons.append("Insufficient history for meaningful mean-reversion analysis")

    if has_goodwill:
        caveats.append("Goodwill changes affect book value — P/B may be distorted")
    if ctx.get("revenue_declining"):
        caveats.append("Declining revenue base — historical multiples may anchor too high")

    return _model("historical", fit, headline, reasons, caveats)
