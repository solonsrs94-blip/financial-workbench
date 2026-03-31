"""Search engine for top-down financial statement standardizer.

Contains the search/match logic extracted from standardizer.py:
- _search_direct: concept + keyword matching
- _try_combination: combining sub-fields
- _try_derived: formula evaluation
- _try_bs_delta: year-over-year BS changes
- Helper functions: _val, _eval_formula, _excluded, _prev_year, _check_quality
"""

import re
from typing import Optional

from lib.data.template import CRITICAL_LINES, IMPORTANT_LINES


def search_direct(key: str, rules: dict, year_rows: list, year: str):
    """Try concept and keyword searches on parsed rows.

    Returns: (value, raw_label, source_type) or (None, None, None)
    """
    if not year_rows:
        return None, None, None

    searches = rules.get("searches", [])

    excludes = set()
    for s in searches:
        if s["type"] == "keyword_exclude":
            excludes.update(w.lower() for w in s["values"])

    is_subtotal = rules.get("is_subtotal", False)
    subtotal_match = None

    for search in searches:
        stype = search["type"]

        if stype == "concept":
            concepts = set(search["values"])
            for row in year_rows:
                if row["concept"] in concepts:
                    if _excluded(row["label"], excludes):
                        continue
                    if is_subtotal:
                        subtotal_match = (row["value"], row["label"], "concept")
                    else:
                        return row["value"], row["label"], "concept"

        elif stype == "sc":
            scs = set(search["values"])
            for row in year_rows:
                if row["sc"] in scs:
                    if _excluded(row["label"], excludes):
                        continue
                    if is_subtotal:
                        subtotal_match = (row["value"], row["label"], "sc")
                    else:
                        return row["value"], row["label"], "sc"

        elif stype == "sc_subtotal":
            scs = set(search["values"])
            for row in year_rows:
                if row["sc"] in scs:
                    label_lower = row["label"].lower()
                    is_subtotal_label = any(
                        kw in label_lower for kw in [
                            "net cash", "total", "cash provided",
                            "cash used in", "cash generated",
                            "cash from", "increase/(decrease)",
                            "increase (decrease)",
                        ]
                    )
                    if is_subtotal_label:
                        subtotal_match = (row["value"], row["label"], "sc_subtotal")

        elif stype == "keyword":
            keywords = search["values"]
            for row in year_rows:
                label_lower = row["label"].lower()
                if _excluded(label_lower, excludes):
                    continue
                for kw in keywords:
                    if kw in label_lower:
                        if is_subtotal:
                            subtotal_match = (row["value"], row["label"], "keyword")
                        else:
                            return row["value"], row["label"], "keyword"
                        break

        elif stype == "value_filter":
            max_abs = search.get("max_abs", 1000)
            label_contains = search.get("label_contains", [])
            for row in year_rows:
                if abs(row["value"]) < max_abs:
                    label_lower = row["label"].lower()
                    if all(kw in label_lower for kw in label_contains):
                        return row["value"], row["label"], "keyword"

    if subtotal_match:
        return subtotal_match

    return None, None, None


def try_combination(key: str, rules: dict, year_data: dict):
    """Try combining sub-fields (e.g. S&M + G&A -> SGA)."""
    for search in rules.get("searches", []):
        if search["type"] != "combination":
            continue
        parts = search["parts"]
        total = 0
        found_any = False
        labels = []
        for part in parts:
            v = val(year_data, part)
            if v is not None:
                total += abs(v)
                found_any = True
                labels.append(part)
        if found_any:
            return total, f"Combined: {' + '.join(labels)}"
    return None, None


def try_derived(key: str, rules: dict, year_data: dict):
    """Try computing derived fields from formulas."""
    for search in rules.get("searches", []):
        if search["type"] != "derived":
            continue
        formula = search["formula"]
        try:
            result = _eval_formula(formula, year_data)
            if result is not None:
                return result, formula
        except Exception:
            continue
    return None, None


def try_bs_delta(key: str, rules: dict, year_data: dict, prev_year_data: dict):
    """Try computing CF items from BS year-over-year changes."""
    for search in rules.get("searches", []):
        if search["type"] != "bs_delta":
            continue
        bs_key = search["bs_key"]
        negate = search.get("negate", False)

        curr = val(year_data, bs_key)
        prev_info = prev_year_data.get(bs_key, {})
        prev = prev_info.get("value") if isinstance(prev_info, dict) else None

        if curr is not None and prev is not None:
            delta = curr - prev
            if negate:
                delta = -delta
            return delta, f"BS delta: {bs_key} ({prev:.0f} -> {curr:.0f})"
    return None, None


def val(data: dict, key: str):
    """Get value from year_data dict."""
    info = data.get(key)
    if info is None:
        return None
    if isinstance(info, dict):
        return info.get("value")
    return info


def _eval_formula(formula: str, year_data: dict):
    """Evaluate a simple formula like 'revenue - abs(cogs)'."""
    ns = {}
    for k, v in year_data.items():
        val_v = v.get("value") if isinstance(v, dict) else v
        ns[k] = val_v

    referenced = set(re.findall(r'[a-z_]+', formula))
    builtins = {"abs", "or", "and", "not"}
    for ref in referenced:
        if ref not in ns and ref not in builtins:
            ns[ref] = None

    try:
        result = eval(formula, {"__builtins__": {"abs": abs}}, ns)
        if result is not None and not isinstance(result, (int, float)):
            return None
        return result
    except (TypeError, NameError, ZeroDivisionError):
        return None


def _excluded(label: str, excludes: set) -> bool:
    """Check if label contains any exclude words."""
    if not excludes:
        return False
    label_lower = label.lower() if not label.islower() else label
    return any(ex in label_lower for ex in excludes)


def prev_year(year: str, years: list) -> Optional[str]:
    """Get previous year string."""
    try:
        idx = years.index(year)
        return years[idx - 1] if idx > 0 else None
    except ValueError:
        return None


def check_quality(results: dict, latest_year: str) -> dict:
    """Check which critical/important lines are missing."""
    if not latest_year:
        return {"critical_missing": CRITICAL_LINES, "important_missing": IMPORTANT_LINES}

    all_keys = set()
    for stmt_data in results.values():
        if latest_year in stmt_data:
            all_keys.update(stmt_data[latest_year].keys())

    return {
        "critical_missing": [k for k in CRITICAL_LINES if k not in all_keys],
        "important_missing": [k for k in IMPORTANT_LINES if k not in all_keys],
    }
