"""RSS collector: fetch and normalize news items from configured sources."""

import re
from datetime import datetime, timedelta, timezone

import feedparser
import requests

from utils.config_loader import load_sources
from utils.logger import get_logger

logger = get_logger(__name__)

FETCH_TIMEOUT = 15  # seconds; feedparser itself has no timeout
_UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) MitongDailyBrief/1.0"}

# Regex to find the first image in HTML content (last-resort fallback)
_IMG_RE = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)


def _is_usable_image(url: str) -> bool:
    """Skip tracking pixels and tiny/beacon images."""
    if not url:
        return False
    low = url.lower()
    return not (low.endswith(".gif") or "tracking" in low or "pixel" in low or "feedburner" in low)


def _extract_media_image(entry) -> str | None:
    """Extract an image from RSS media fields (media:thumbnail / media:content / enclosure)."""
    # media:thumbnail — most common for Chinese feeds
    for thumb in entry.get("media_thumbnail", []) or []:
        url = thumb.get("url", "")
        if _is_usable_image(url):
            return url
    # media:content
    for media in entry.get("media_content", []) or []:
        url = media.get("url", "")
        mtype = media.get("type", "") or ""
        if _is_usable_image(url) and (mtype.startswith("image") or media.get("medium") == "image" or not mtype):
            return url
    # enclosures with image mime type
    for enc in entry.get("enclosures", []) or []:
        url = enc.get("href", "") or enc.get("url", "")
        if _is_usable_image(url) and enc.get("type", "").startswith("image"):
            return url
    return None


def _extract_image_from_html(html_content: str) -> str | None:
    """Extract the first usable <img> from HTML content."""
    if not html_content:
        return None
    match = _IMG_RE.search(html_content)
    if match:
        url = match.group(1).strip()
        if _is_usable_image(url):
            return url
    return None


def _entry_image(entry) -> str | None:
    """Best-effort image for an entry: media fields first, HTML content as fallback."""
    img = _extract_media_image(entry)
    if img:
        return img
    content_html = ""
    if entry.get("content"):
        content_html = entry.content[0].get("value", "")
    elif entry.get("summary"):
        content_html = entry.summary
    return _extract_image_from_html(content_html)


def parse_rss(url: str) -> list[dict]:
    """Parse an RSS feed and return a list of normalized news items."""
    try:
        # fetch with an explicit timeout first — feedparser.parse(url) can hang forever
        resp = requests.get(url, headers=_UA, timeout=FETCH_TIMEOUT)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
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
                "image_url": _entry_image(entry) or "",
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
