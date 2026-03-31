"""Shared utility for concept map keyword sorting."""


def sort_by_length(d: dict) -> dict:
    """Return a new dict sorted by key length (longest first)."""
    return dict(sorted(d.items(), key=lambda x: -len(x[0])))
