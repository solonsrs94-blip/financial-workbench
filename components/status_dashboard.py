"""Feature status dashboard — single source of truth for what's built vs pending.

When a feature's status changes, update FEATURE_STATUS below. This is the
authoritative roadmap — the Guide page renders this dashboard, and individual
placeholder pages should mirror their entry here.

Status values:
    done        — fully implemented and tested
    partial     — partially built (in progress)
    placeholder — not yet started (stub UI only)
"""

import streamlit as st


# ── Feature registry ──────────────────────────────────────────────
# Organized by user-facing category. Update this dict when features advance.

FEATURE_STATUS: dict[str, dict[str, dict]] = {
    "Research": {
        "Company Overview": {
            "status": "done",
            "progress": 100,
            "tier": "personal",
            "page": "1_company.py",
        },
        "Financial Preparation": {
            "status": "done",
            "progress": 100,
            "tier": "personal",
            "page": "3_valuation.py",
        },
        "DCF Valuation": {
            "status": "partial",
            "progress": 60,
            "tier": "personal",
            "page": "3_valuation.py",
            "note": "Core math works; needs mid-year, iterative WACC, Reverse DCF, Monte Carlo",
        },
        "Comps Analysis": {
            "status": "done",
            "progress": 95,
            "tier": "personal",
            "page": "3_valuation.py",
        },
        "DDM": {
            "status": "done",
            "progress": 95,
            "tier": "personal",
            "page": "3_valuation.py",
        },
        "Historical Multiples": {
            "status": "done",
            "progress": 90,
            "tier": "personal",
            "page": "3_valuation.py",
        },
        "Valuation Summary": {
            "status": "partial",
            "progress": 70,
            "tier": "personal",
            "page": "3_valuation.py",
            "note": "Football field works; needs Monte Carlo distribution, audit trail",
        },
        "Technical Charts": {
            "status": "placeholder",
            "progress": 0,
            "tier": "personal",
            "page": "4_charts.py",
        },
        "Stock Screener": {
            "status": "placeholder",
            "progress": 0,
            "tier": "personal",
            "page": "5_screener.py",
        },
    },
    "Portfolio": {
        "Watchlist": {
            "status": "placeholder",
            "progress": 0,
            "tier": "personal",
            "page": "6_watchlist.py",
        },
        "Portfolio Tracker": {
            "status": "placeholder",
            "progress": 0,
            "tier": "personal",
            "page": "7_portfolio.py",
        },
        "Saved Valuations": {
            "status": "done",
            "progress": 100,
            "tier": "personal",
            "page": "2_saved.py",
        },
    },
    "Context": {
        "Macro Overview": {
            "status": "placeholder",
            "progress": 0,
            "tier": "personal",
            "page": "8_macro.py",
        },
        "Calendars": {
            "status": "placeholder",
            "progress": 0,
            "tier": "personal",
            "page": "13_calendars.py",
        },
        "News Feed": {
            "status": "placeholder",
            "progress": 0,
            "tier": "personal",
            "page": "14_news.py",
        },
    },
    "Tools": {
        "Investment Journal": {
            "status": "placeholder",
            "progress": 0,
            "tier": "personal",
            "page": "11_journal.py",
        },
        "AI Assistant": {
            "status": "placeholder",
            "progress": 0,
            "tier": "personal",
            "page": "9_ai.py",
        },
        "Academy": {
            "status": "placeholder",
            "progress": 0,
            "tier": "personal",
            "page": "10_academy.py",
        },
        "Settings": {
            "status": "placeholder",
            "progress": 0,
            "tier": "personal",
            "page": "12_settings.py",
        },
    },
    "Professional": {
        "LBO Modeling": {
            "status": "placeholder",
            "progress": 0,
            "tier": "professional",
            "page": "20_lbo.py",
        },
        "M&A Analysis": {
            "status": "placeholder",
            "progress": 0,
            "tier": "professional",
            "page": "21_ma.py",
        },
        "M&A Precedents": {
            "status": "placeholder",
            "progress": 0,
            "tier": "professional",
            "page": "22_precedents.py",
        },
    },
}


# ── Aggregation helpers ───────────────────────────────────────────

STATUS_ICON = {
    "done": "✅",
    "partial": "🟡",
    "placeholder": "🚧",
}


def _flatten() -> list[dict]:
    """Flatten FEATURE_STATUS into a list of feature dicts for iteration."""
    flat = []
    for category, features in FEATURE_STATUS.items():
        for name, info in features.items():
            flat.append({"category": category, "name": name, **info})
    return flat


def compute_overall() -> dict:
    """Return aggregate stats: total features, by-status counts, weighted progress."""
    flat = _flatten()
    total = len(flat)
    done = sum(1 for f in flat if f["status"] == "done")
    partial = sum(1 for f in flat if f["status"] == "partial")
    placeholder = sum(1 for f in flat if f["status"] == "placeholder")
    weighted = sum(f.get("progress", 0) for f in flat) / total if total else 0

    return {
        "total": total,
        "done": done,
        "partial": partial,
        "placeholder": placeholder,
        "weighted_progress": weighted,
    }


# ── Rendering ─────────────────────────────────────────────────────


def render_status_dashboard(show_professional: bool = True) -> None:
    """Render the feature status dashboard.

    Parameters
    ----------
    show_professional : if False, hides the Professional category.
        Useful if you want to show only the user's current tier.
    """
    stats = compute_overall()

    st.markdown("## Feature Status")
    st.caption("Live view of what's built, in progress, and planned.")

    # Overall metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Overall", f"{stats['weighted_progress']:.0f}%")
    col2.metric("Complete", f"{stats['done']}/{stats['total']}")
    col3.metric("In progress", stats["partial"])
    col4.metric("Planned", stats["placeholder"])

    st.progress(stats["weighted_progress"] / 100)

    # Per-category breakdown
    for category, features in FEATURE_STATUS.items():
        if category == "Professional" and not show_professional:
            continue

        # Category header with its own completion %
        cat_progress = sum(f.get("progress", 0) for f in features.values()) / len(features)
        with st.expander(
            f"**{category}** ({len(features)} features, {cat_progress:.0f}% complete)",
            expanded=(category in ("Research", "Portfolio")),
        ):
            for name, info in features.items():
                cols = st.columns([4, 1, 2])
                icon = STATUS_ICON.get(info["status"], "❓")
                cols[0].markdown(f"{icon} **{name}**")
                cols[1].markdown(f"`{info.get('progress', 0)}%`")
                cols[2].progress(info.get("progress", 0) / 100)
                if info.get("note"):
                    st.caption(f"   ↳ {info['note']}")


def get_feature_status(category: str, name: str) -> dict | None:
    """Look up a specific feature's status entry."""
    return FEATURE_STATUS.get(category, {}).get(name)
