"""Search middleware — company search with cache."""

import logging
from typing import Optional
from lib import cache
from lib.data.providers import yahoo

logger = logging.getLogger(__name__)


def search_companies(query: str, max_results: int = 8) -> list[dict]:
    """Search for companies by name or ticker, with cache."""
    query = query.strip()
    if not query:
        return []

    cache_key = f"yahoo:search:{query.lower()}"

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    results = yahoo.search_companies(query, max_results=max_results)
    if results:
        cache.store(cache_key, results, provider="yahoo", ttl_key="news")

    return results
