"""US daily trending topics collector — Google Trends RSS (geo=US).

Google Trends' daily trending feed returns the ~10 hottest US searches of
the day, each with approximate traffic and a representative news article.
This is the standard free proxy for "what America is talking about today"
(X/Twitter trend APIs are paywalled).
"""

import re
from html import unescape

import feedparser
import requests

from utils.logger import get_logger

logger = get_logger(__name__)

TRENDS_URL = "https://trends.google.com/trending/rss?geo=US"
FETCH_TIMEOUT = 15
_UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) MitongDailyBrief/1.0"}

_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(raw: str) -> str:
    return unescape(_TAG_RE.sub("", raw or "")).strip()


def fetch_us_trends(limit: int = 10) -> list[dict]:
    """Fetch today's top US trending topics. Returns [] on any failure —
    trends are a bonus section and must never break the main pipeline."""
    try:
        resp = requests.get(TRENDS_URL, headers=_UA, timeout=FETCH_TIMEOUT)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)

        trends = []
        for rank, entry in enumerate(feed.entries[:limit], start=1):
            topic = _strip_html(entry.get("title", ""))
            news_title = _strip_html(entry.get("ht_news_item_title", ""))
            news_url = entry.get("ht_news_item_url", "") or entry.get("link", "")
            trends.append({
                "rank": rank,
                "topic": topic,
                "title": news_title or topic,
                "url": news_url,
                "source": _strip_html(entry.get("ht_news_item_source", "")),
                "traffic": entry.get("ht_approx_traffic", ""),
                "summary": _strip_html(entry.get("ht_news_item_snippet", ""))[:150],
                "image_url": entry.get("ht_picture", "") or entry.get("ht_news_item_picture", ""),
            })

        logger.info("Fetched %d US trending topics", len(trends))
        return trends
    except Exception as e:
        logger.warning("US trends fetch failed (non-fatal): %s", e)
        return []
