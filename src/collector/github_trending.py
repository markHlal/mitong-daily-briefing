"""GitHub fastest-growing repositories collector — GitHub Search API.

Uses the Search API with `created:>N days` + sort=stars as the proxy for
"fastest star growth": among repos created in the recent window, the ones
with the most stars are the ones growing fastest. This mirrors how GitHub
Trending ranks "new and hot" projects, using only the official API.
"""

import os
from datetime import datetime, timedelta, timezone

import requests

from utils.logger import get_logger

logger = get_logger(__name__)

SEARCH_URL = "https://api.github.com/search/repositories"
FETCH_TIMEOUT = 20
WINDOW_DAYS = 30


def fetch_github_trending(limit: int = 10, topic: str = "") -> list[dict]:
    """Fetch the fastest-growing repos (newest + most starred), optionally filtered
    to a topic (e.g. 'ai'). Returns [] on any failure — this is a bonus section and
    must never break the main pipeline."""
    try:
        since = (datetime.now(timezone.utc) - timedelta(days=WINDOW_DAYS)).strftime("%Y-%m-%d")
        q = f"created:>{since}" + (f" topic:{topic}" if topic else "")
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "MitongDailyBrief/1.0"}
        token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
        if token:
            headers["Authorization"] = f"token {token}"
        resp = requests.get(
            SEARCH_URL,
            params={"q": q, "sort": "stars", "order": "desc", "per_page": limit},
            headers=headers,
            timeout=FETCH_TIMEOUT,
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])
        repos = []
        for rank, r in enumerate(items[:limit], start=1):
            repos.append({
                "rank": rank,
                "name": r.get("full_name", ""),
                "url": r.get("html_url", ""),
                "description": (r.get("description") or "").strip(),
                "language": r.get("language") or "",
                "stars": r.get("stargazers_count", 0),
                "created_at": (r.get("created_at") or "")[:10],
            })
        logger.info("Fetched %d fastest-growing GitHub repos%s", len(repos), f" (topic={topic})" if topic else "")
        return repos
    except Exception as e:
        logger.warning("GitHub trending fetch failed (non-fatal): %s", e)
        return []
