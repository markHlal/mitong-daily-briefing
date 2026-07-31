import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any

import feedparser
import requests

from utils.config_loader import load_sources
from utils.logger import get_logger

logger = get_logger(__name__)


def parse_rss(url: str) -> list[dict]:
    """Parse an RSS feed and return a list of normalized news items."""
    try:
        feed = feedparser.parse(url)
        results = []
        for entry in feed.entries:
            published = _parse_time(entry.get("published_parsed") or entry.get("updated_parsed"))
            if not published:
                continue
            # Only keep items from last 48 hours
            if datetime.now(timezone.utc) - published > timedelta(hours=48):
                continue

            item = {
                "title": entry.get("title", "").strip(),
                "url": entry.get("link", "").strip(),
                "summary": _clean_summary(entry.get("summary", "")),
                "published_at": published.isoformat(),
                "source_name": feed.feed.get("title", "未知来源"),
            }
            results.append(item)
        logger.info("Fetched %d items from %s", len(results), url)
        return results
    except Exception as e:
        logger.error("Failed to fetch RSS %s: %s", url, e)
        return []


def _parse_time(time_struct) -> datetime | None:
    if not time_struct:
        return None
    try:
        return datetime(*time_struct[:6], tzinfo=timezone.utc)
    except Exception:
        return None


def _clean_summary(raw: str) -> str:
    from html.parser import HTMLParser

    class MLStripper(HTMLParser):
        def __init__(self):
            super().__init__()
            self.reset()
            self.fed = []

        def handle_data(self, d):
            self.fed.append(d)

        def get_data(self):
            return "".join(self.fed)

    s = MLStripper()
    s.feed(raw)
    text = s.get_data().strip()
    return text[:300] if len(text) > 300 else text


def fetch_all_sources() -> list[dict]:
    """Fetch news from all enabled sources."""
    sources = load_sources()
    all_news = []
    for src in sources:
        if not src.get("enabled", True):
            continue
        if src.get("type") == "rss":
            items = parse_rss(src["url"])
            all_news.extend(items)
    return all_news
