"""Financial statement flagging — rules 8-15.

All rules accept `category` from _get_company_category() to skip or
adjust thresholds for financials, REITs, etc.
No Streamlit imports (lib/ rule).
"""
import statistics
from lib.analysis.flags_helpers import _g, _flag
from lib.analysis.flags_config import should_skip

# ── Rule 8: fcf_ni_divergence ───────────────────────────────────────

def rule_fcf_ni_divergence(is_table, cf_table, flags,
                           category="default"):
    """FCF vs NI mismatch.  Skip via config (financials, REITs, utilities)."""
    if should_skip("fcf_ni_divergence", category):
        return
    causes_neg = ["Heavy capex cycle", "Working capital build",
                  "Aggressive revenue recognition"]
    causes_high = ["High non-cash charges (D&A, SBC)",
                   "Working capital release", "Aggressive capitalization"]
    for i in range(len(is_table)):
        if i >= len(cf_table):
            break
        ni = _g(is_table[i], "net_income")
        fcf = _g(cf_table[i], "free_cash_flow")
        if ni is None or fcf is None or ni == 0:
            continue
        year = is_table[i].get("year")
        ratio = fcf / ni

        if ni > 0 and fcf < 0:
            flags.append(_flag(
                "quality", "high", year,
                f"Net Income positive (${ni/1e9:.1f}B) but FCF negative "
                f"(${fcf/1e9:.1f}B)",
                causes_neg, abs(ni - fcf) / 1e6, "free_cash_flow",
            ))
        elif ratio > 2.0:
            flags.append(_flag(
                "quality", "medium", year,
                f"FCF (${fcf/1e9:.1f}B) is {ratio:.1f}x Net Income "
                f"(${ni/1e9:.1f}B)",
                causes_high, abs(fcf - ni) / 1e6, "free_cash_flow",
            ))

# ── Rule 9: working_capital_trend ───────────────────────────────────

def rule_working_capital_trend(ratios, flags, category="default"):
    """CCC lengthening.  Skip via config."""
    if should_skip("working_capital", category):
        return
    causes = ["Customer payment delays", "Inventory buildup",
              "Supplier leverage loss"]
    ccc_data = []
    for r in ratios:
        dso = _g(r, "dso")
        dio = _g(r, "dio")
        dpo = _g(r, "dpo")
        if dso is not None and dpo is not None:
            ccc = dso + (dio or 0) - dpo
            ccc_data.append((r["year"], ccc))

    if len(ccc_data) < 5:
        return

    for start in range(len(ccc_data) - 3):
        streak = 0
        for j in range(start + 1, len(ccc_data)):
            if ccc_data[j][1] > ccc_data[j - 1][1]:
                streak += 1
            else:
                break
        if streak >= 3:
            total_change = ccc_data[start + streak][1] - ccc_data[start][1]
            if total_change > 20:
                flags.append(_flag(
                    "quality", "medium", ccc_data[start + streak][0],
                    f"Cash Conversion Cycle lengthened {total_change:.0f} "
                    f"days over {streak + 1} years",
                    causes, None, "accounts_receivable",
                ))
                return

# ── Rule 10: interest_rate_spike ────────────────────────────────────

def rule_interest_rate_spike(is_table, bs_table, flags,
                             category="default"):
    """Implied interest rate rise.  Skip via config."""
    if should_skip("interest_rate_spike", category):
        return
    causes = ["Refinancing at higher rates", "New expensive debt",
              "Floating rate exposure"]
    prev_rate = None
    for i in range(len(is_table)):
        if i >= len(bs_table):
            break
        ie = _g(is_table[i], "interest_expense")
        td = _g(bs_table[i], "total_debt")
        if not ie or not td or td <= 0:
            prev_rate = None
            continue
        rate = abs(ie) / td
        if rate < 0.001 or rate > 0.20:
            prev_rate = None
            continue

        if prev_rate is not None:
            delta = rate - prev_rate
            if delta > 0.05:
                ie_mn = abs(ie) / 1e6
                flags.append(_flag(
                    "quality", "medium", is_table[i].get("year"),
                    f"Implied interest rate rose {delta*100:.1f}pp "
                    f"({prev_rate*100:.1f}% -> {rate*100:.1f}%)",
                    causes, ie_mn, "interest_expense",
                ))
        prev_rate = rate

# ── Rule 11: goodwill_impairment ────────────────────────────────────

def rule_goodwill_impairment(bs_table, flags):
    """Goodwill decline >20%.  Universal — noteworthy for all types."""
    for i in range(1, len(bs_table)):
        curr = _g(bs_table[i], "goodwill")
        prev = _g(bs_table[i - 1], "goodwill")
        if not curr or not prev or prev <= 0:
            continue
        decline = (curr - prev) / prev
        if decline < -0.20:
            impact = abs(curr - prev) / 1e6
            flags.append(_flag(
                "m_and_a", "high", bs_table[i].get("year"),
                f"Goodwill declined {abs(decline)*100:.0f}% "
                f"(${prev/1e9:.1f}B -> ${curr/1e9:.1f}B)",
                None, impact, "goodwill",
            ))

# ── Rule 12: margin_mean_reversion ──────────────────────────────────

def rule_margin_mean_reversion(ratios, flags, category="default"):
    """Margin at >95th pctl + >2σ.  Skip via config.  Needs 7+ years."""
    if should_skip("margin_mean_reversion", category):
        return
    causes = ["Cyclical peak", "Unsustainable pricing",
              "Temporary cost advantage", "New business model"]
    if len(ratios) < 7:
        return
    for metric, label, line in [
        ("ebit_margin", "EBIT Margin", "ebit_margin"),
        ("net_margin", "Net Margin", "net_margin"),
    ]:
        values = [_g(r, metric) for r in ratios if _g(r, metric) is not None]
        if len(values) < 7:
            continue
        curr = values[-1]
        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0

        if stdev < 0.01:
            continue

        sorted_vals = sorted(values)
        rank = sorted_vals.index(curr)
        pctl = rank / (len(sorted_vals) - 1)

        if pctl >= 0.95 and curr > mean + 2 * stdev:
            flags.append(_flag(
                "quality", "medium", ratios[-1]["year"],
                f"{label} at {pctl*100:.0f}th percentile of own history "
                f"({curr*100:.1f}% vs avg {mean*100:.1f}%, "
                f"+{(curr-mean)/stdev:.1f}σ)",
                causes, None, line,
            ))

# ── Rule 13: long_trend_reversal ────────────────────────────────────

def rule_long_trend_reversal(ratios, flags, category="default"):
    """4-year trend breaks.  Skip via config.  Needs 6+ years."""
    if should_skip("long_trend_reversal", category):
        return
    causes = ["Structural change", "Cyclical turning point",
              "Competitive pressure"]
    if len(ratios) < 6:
        return

    for metric, label, line in [
        ("ebit_margin", "EBIT Margin", "ebit"),
        ("net_margin", "Net Margin", "net_income"),
    ]:
        values = []
        for r in ratios:
            v = _g(r, metric)
            if v is not None:
                values.append((r["year"], v))

        if len(values) < 6:
            continue

        for end in range(5, len(values)):
            trend_vals = [values[j][1] for j in range(end - 4, end)]
            diffs = [trend_vals[j+1] - trend_vals[j] for j in range(3)]

            all_up = all(d > 0.005 for d in diffs)
            all_down = all(d < -0.005 for d in diffs)
            if not all_up and not all_down:
                continue

            reversal = values[end][1] - values[end - 1][1]
            if all_up and reversal < -0.03:
                flags.append(_flag(
                    "quality", "medium", values[end][0],
                    f"{label} reversed after 4yr improvement "
                    f"({reversal*100:+.1f}pp)",
                    causes, None, line,
                ))
            elif all_down and reversal > 0.03:
                flags.append(_flag(
                    "quality", "medium", values[end][0],
                    f"{label} reversed after 4yr decline "
                    f"({reversal*100:+.1f}pp)",
                    causes, None, line,
                ))

# ── Rule 14: major_dilution ─────────────────────────────────────────

def rule_major_dilution(is_table, flags, category="default"):
    """Shares ±10% (±15% for REITs).  Skip via config."""
    if should_skip("major_dilution", category):
        return
    threshold = 0.15 if category == "reit" else 0.10
    for i in range(1, len(is_table)):
        curr = _g(is_table[i], "diluted_shares")
        prev = _g(is_table[i - 1], "diluted_shares")
        if not curr or not prev or prev <= 0:
            continue
        pct = (curr - prev) / prev

        if abs(pct) > 0.80:
            continue

        year = is_table[i].get("year")
        if pct > threshold:
            flags.append(_flag(
                "dilution", "medium", year,
                f"Diluted shares increased {pct*100:.1f}%",
                ["Equity offering", "M&A stock consideration",
                 "Convertible exercise", "Heavy SBC"],
                None, "diluted_shares",
            ))
        elif pct < -threshold:
            flags.append(_flag(
                "dilution", "medium", year,
                f"Diluted shares decreased {abs(pct)*100:.1f}%",
                ["Major buyback program", "Reverse split"],
                None, "diluted_shares",
            ))

# ── Rule 15: earnings_quality ───────────────────────────────────────

def rule_earnings_quality(ratios, is_table, cf_table, flags,
                          category="default"):
    """FCF/NI + SBC score.  Skip via config (financials, REITs, utilities)."""
    if should_skip("earnings_quality", category):
        return
    if len(ratios) < 3:
        return
    _score_buckets = [(0.9, 100), (0.7, 80), (0.5, 60), (0.3, 40)]
    _sbc_buckets = [(0.02, 100), (0.05, 80), (0.10, 60), (0.15, 40)]

    scores = []
    for i in range(max(len(ratios) - 3, 0), len(ratios)):
        is_r = is_table[i] if i < len(is_table) else {}
        cf_r = cf_table[i] if i < len(cf_table) else {}
        ni = _g(is_r, "net_income")
        fcf, rev = _g(cf_r, "free_cash_flow"), _g(is_r, "revenue")
        sbc = _g(cf_r, "stock_based_compensation")
        subs = []
        if ni and ni > 0 and fcf is not None:
            r = fcf / ni
            subs.append(next((s for t, s in _score_buckets if r >= t), 20))
        if sbc and rev and rev > 0:
            p = abs(sbc) / rev
            subs.append(next((s for t, s in _sbc_buckets if p < t), 20))
        if subs:
            scores.append(statistics.mean(subs))
    if not scores:
        return
    avg = statistics.mean(scores)
    if avg < 40:
        sev = "high" if avg < 25 else "medium"
        flags.append(_flag(
            "quality", sev, ratios[-1]["year"],
            f"Earnings quality score {avg:.0f}/100 (3yr avg)",
            ["High accruals", "Revenue recognition concerns",
             "SBC dilution", "Working capital manipulation"],
            None, "net_income",
        ))
