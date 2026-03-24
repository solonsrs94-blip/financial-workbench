"""
Cache layer — SQLite-based caching for API responses.

How it works:
1. Before any API call, check cache first
2. If cached data exists and is not expired, return it
3. If expired or missing, fetch from API, store in cache, return
4. If API fails, return stale cached data with a warning
"""

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Optional

from config.settings import CACHE_DB, CACHE_DIR
from config.constants import CACHE_TTL, CACHE_MAX_AGE


def _ensure_db() -> sqlite3.Connection:
    """Create cache database and table if they don't exist."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(CACHE_DB))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cache_store (
            key TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            fetched REAL NOT NULL,
            expires REAL NOT NULL,
            provider TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def get(key: str) -> Optional[dict]:
    """Get fresh cached data. Returns None if missing or expired."""
    conn = _ensure_db()
    try:
        row = conn.execute(
            "SELECT data, expires FROM cache_store WHERE key = ?",
            (key,)
        ).fetchone()

        if row is None:
            return None

        data_json, expires = row
        if time.time() > expires:
            return None

        return json.loads(data_json)
    finally:
        conn.close()


def get_stale(key: str) -> Optional[dict]:
    """Get cached data even if expired. Used as fallback when API fails."""
    conn = _ensure_db()
    try:
        row = conn.execute(
            "SELECT data, fetched FROM cache_store WHERE key = ?",
            (key,)
        ).fetchone()

        if row is None:
            return None

        data_json, fetched = row

        # Don't return extremely old data
        if time.time() - fetched > CACHE_MAX_AGE:
            return None

        return json.loads(data_json)
    finally:
        conn.close()


def store(key: str, data: dict, provider: str, ttl_key: str = "price_daily") -> None:
    """Store data in cache with appropriate TTL."""
    ttl = CACHE_TTL.get(ttl_key, CACHE_TTL["price_daily"])
    now = time.time()

    conn = _ensure_db()
    try:
        conn.execute(
            """INSERT OR REPLACE INTO cache_store (key, data, fetched, expires, provider)
               VALUES (?, ?, ?, ?, ?)""",
            (key, json.dumps(data, default=str), now, now + ttl, provider)
        )
        conn.commit()
    finally:
        conn.close()


def delete(key: str) -> None:
    """Delete a specific cache entry."""
    conn = _ensure_db()
    try:
        conn.execute("DELETE FROM cache_store WHERE key = ?", (key,))
        conn.commit()
    finally:
        conn.close()


def clear_provider(provider: str) -> int:
    """Clear all cache entries from a specific provider. Returns count deleted."""
    conn = _ensure_db()
    try:
        cursor = conn.execute(
            "DELETE FROM cache_store WHERE provider = ?", (provider,)
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def clear_expired() -> int:
    """Remove all expired entries. Returns count deleted."""
    conn = _ensure_db()
    try:
        cursor = conn.execute(
            "DELETE FROM cache_store WHERE expires < ?", (time.time(),)
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def clear_all() -> int:
    """Clear entire cache. Returns count deleted."""
    conn = _ensure_db()
    try:
        cursor = conn.execute("DELETE FROM cache_store")
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()
