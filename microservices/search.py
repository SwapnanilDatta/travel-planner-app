"""
Shared, cached DuckDuckGo search utility.
- Results are cached in-memory for CACHE_TTL seconds (default 10 min).
- Identical queries never hit the network twice within the TTL window.
- Callers that pass the same query string get the cached result instantly.
"""

import time
import threading
from ddgs import DDGS

CACHE_TTL = 600          # seconds to keep a result
MAX_RESULTS = 5          # per query – reduced to save LLM tokens

_cache: dict[str, tuple[str, float]] = {}   # query → (result, timestamp)
_lock = threading.Lock()


def cached_search(query: str) -> str:
    """
    Run a DuckDuckGo text search with in-memory caching.

    Returns a formatted string of results suitable for LLM consumption.
    Thread-safe; safe to call from multiple CrewAI agents simultaneously.
    """
    query = query.strip().lower()          # normalise so slight variants hit cache

    with _lock:
        if query in _cache:
            result, ts = _cache[query]
            if time.time() - ts < CACHE_TTL:
                return result              # cache hit – no network call

    # Cache miss – hit the network
    try:
        hits = DDGS().text(query, max_results=MAX_RESULTS)
        lines = []
        for h in hits:
            title = h.get("title", "")
            body  = h.get("body",  "")[:150] + "..." if len(h.get("body", "")) > 150 else h.get("body", "")
            href  = h.get("href",  "")
            lines.append(f"- {title}: {body}")
        result = "\n".join(lines) if lines else "No results found."
    except Exception as e:
        result = f"Search error: {e}"

    with _lock:
        _cache[query] = (result, time.time())

    return result
