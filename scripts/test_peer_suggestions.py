"""Test peer candidate generation on 10 diverse companies.

Runs the same logic as Comps Step 1 (Finnhub + S&P 500 filter)
but outside Streamlit, directly using providers/middleware.
"""

import sys
import time

sys.path.insert(0, ".")

from lib.data.providers.comps_peers import (
    fetch_candidate_info,
    fetch_finnhub_peers,
    fetch_sp500_constituents,
    filter_universe,
)

test_targets = [
    "AAPL",   # Consumer Electronics, mega cap
    "CRWD",   # Cybersecurity, mid-large cap
    "JNJ",    # Pharma, mega cap
    "JPM",    # Banking, mega cap
    "XOM",    # Oil & Gas, mega cap
    "COST",   # Retail, large cap
    "ETSY",   # E-commerce, small-mid cap
    "NEE",    # Utilities, large cap
    "SWK",    # Industrials, mid cap
    "DIS",    # Entertainment, large cap
]


def fmt_num(val):
    if val is None:
        return "N/A"
    av = abs(val)
    if av >= 1e12:
        return f"${val/1e12:.2f}T"
    if av >= 1e9:
        return f"${val/1e9:.1f}B"
    if av >= 1e6:
        return f"${val/1e6:.0f}M"
    return f"${val:,.0f}"


def fmt_pct(val):
    if val is None:
        return "N/A"
    return f"{val*100:.1f}%"


def main():
    total_start = time.time()
    output_lines = []

    def log(msg=""):
        print(msg)
        output_lines.append(msg)

    # Fetch S&P 500 universe once
    log("Fetching S&P 500 universe from Wikipedia...")
    t0 = time.time()
    universe = fetch_sp500_constituents()
    log(f"  Got {len(universe)} constituents in {time.time()-t0:.1f}s\n")

    for ticker in test_targets:
        t_start = time.time()
        log("=" * 70)

        # Target info
        target_info = fetch_candidate_info(ticker)
        if not target_info:
            log(f"TARGET: {ticker} -- FAILED to fetch info")
            log("=" * 70)
            continue

        t_ind = target_info.get("industry", "?")
        t_mcap = target_info.get("market_cap", 0)
        t_rev = target_info.get("revenue")
        t_margin = target_info.get("ebitda_margin")

        log(
            f"TARGET: {ticker} -- {target_info.get('name', '?')}"
        )
        log(
            f"  Industry: {t_ind} | "
            f"Market Cap: {fmt_num(t_mcap)} | "
            f"Revenue: {fmt_num(t_rev)} | "
            f"EBITDA Margin: {fmt_pct(t_margin)}"
        )
        log("=" * 70)

        # Layer 1: Finnhub peers
        finnhub_tickers = fetch_finnhub_peers(ticker)
        finnhub_set = set(finnhub_tickers)

        # Layer 2: Universe filter
        universe_tickers = []
        if universe and t_mcap:
            universe_tickers = filter_universe(
                universe, ticker, t_ind, t_mcap,
            )

        # Merge + deduplicate
        seen = {ticker.upper()}
        ordered = []
        sources = {}
        for t in finnhub_tickers:
            t_up = t.upper()
            if t_up not in seen:
                seen.add(t_up)
                ordered.append(t)
                sources[t_up] = "Finnhub"
        for t in universe_tickers:
            t_up = t.upper()
            if t_up not in seen:
                seen.add(t_up)
                ordered.append(t)
                sources[t_up] = "Universe"

        ordered = ordered[:30]

        # Fetch info for each candidate
        candidates = []
        failed = []
        for t in ordered:
            info = fetch_candidate_info(t)
            if info:
                info["_source"] = sources.get(t.upper(), "?")
                candidates.append(info)
            else:
                failed.append(t)

        # Sort: same industry first, then market cap proximity
        def sort_key(c):
            same = 0 if c.get("industry") == t_ind else 1
            mcap = c.get("market_cap") or 0
            dist = abs(mcap - t_mcap) / max(t_mcap, 1)
            return (same, dist)

        candidates.sort(key=sort_key)

        # Count stats
        n_finnhub = sum(
            1 for c in candidates if c["_source"] == "Finnhub"
        )
        n_universe = sum(
            1 for c in candidates if c["_source"] == "Universe"
        )
        n_same_ind = sum(
            1 for c in candidates if c.get("industry") == t_ind
        )

        # Print table
        log("")
        log(
            f"{'#':<4} {'Source':<10} {'Ticker':<8} "
            f"{'Company':<30} {'Country':<10} "
            f"{'Industry':<30} {'Mkt Cap':>10} "
            f"{'Revenue':>10} {'EBITDA Mgn':>10}"
        )
        log("-" * 152)

        for i, c in enumerate(candidates, 1):
            name = (c.get("name") or "")[:28]
            ind = (c.get("industry") or "")[:28]
            log(
                f"{i:<4} {c['_source']:<10} {c['ticker']:<8} "
                f"{name:<30} {c.get('country',''):<10} "
                f"{ind:<30} {fmt_num(c.get('market_cap')):>10} "
                f"{fmt_num(c.get('revenue')):>10} "
                f"{fmt_pct(c.get('ebitda_margin')):>10}"
            )

        if failed:
            log(f"\n  Failed tickers: {', '.join(failed)}")

        elapsed = time.time() - t_start
        log(
            f"\nTotal candidates: {len(candidates)} "
            f"(Finnhub: {n_finnhub}, Universe: {n_universe})"
        )
        log(f"Same industry as target: {n_same_ind}")
        log(f"Time: {elapsed:.1f}s")
        log("")

    total_elapsed = time.time() - total_start
    log(f"\n{'='*70}")
    log(f"TOTAL TIME: {total_elapsed:.1f}s for {len(test_targets)} targets")
    log(f"Average: {total_elapsed/len(test_targets):.1f}s per target")

    # Save to file
    out_path = "scripts/peer_suggestions_test.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
