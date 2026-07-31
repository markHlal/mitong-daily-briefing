import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from collector.dedup import deduplicate


def test_deduplicate_by_url():
    items = [
        {"title": "News A", "url": "http://a.com/1", "summary": "", "published_at": "2026-07-31T00:00:00+00:00", "source_name": "A"},
        {"title": "News A dup", "url": "http://a.com/1", "summary": "", "published_at": "2026-07-31T00:00:00+00:00", "source_name": "B"},
        {"title": "News B", "url": "http://a.com/2", "summary": "", "published_at": "2026-07-31T00:00:00+00:00", "source_name": "A"},
    ]
    result = deduplicate(items)
    assert len(result) == 2
    urls = {r["url"] for r in result}
    assert "http://a.com/1" in urls
    assert "http://a.com/2" in urls


def test_deduplicate_by_similar_title():
    items = [
        {"title": "Apple releases iOS 18", "url": "http://a.com/1", "summary": "", "published_at": "2026-07-31T00:00:00+00:00", "source_name": "A"},
        {"title": "Apple releases iOS 18 today", "url": "http://a.com/2", "summary": "", "published_at": "2026-07-31T00:00:00+00:00", "source_name": "B"},
        {"title": "完全不同的新闻", "url": "http://a.com/3", "summary": "", "published_at": "2026-07-31T00:00:00+00:00", "source_name": "C"},
    ]
    result = deduplicate(items)
    assert len(result) == 2


def test_clean_summary():
    from collector.rss_fetcher import _clean_summary
    raw = "<p>This is <b>bold</b> text</p>"
    assert _clean_summary(raw) == "This is bold text"
