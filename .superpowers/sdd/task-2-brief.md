# Task 2: RSS 采集器 + 去重器

**项目**: 米桶 AI 每日资讯早报系统  
**工作目录**: `/Users/huang/Documents/Kimi/Workspaces/ai新闻收集`

这是数据采集层的第一步。从配置的 RSS 信源抓取资讯，去重后供后续模块使用。

## 前置依赖

Task 1 已完成，以下接口可用：
- `from utils.config_loader import load_sources` → 返回 `list[dict]`，每个 dict 有 `name`, `type`, `url`, `enabled`
- `from utils.logger import get_logger` → 返回 `logging.Logger`

## 需要创建的文件

1. `src/collector/rss_fetcher.py`
2. `src/collector/dedup.py`
3. `tests/test_collector.py`

## 代码要求

### rss_fetcher.py

```python
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
```

### dedup.py

```python
import hashlib
from difflib import SequenceMatcher

from utils.logger import get_logger

logger = get_logger(__name__)


def _url_hash(url: str) -> str:
    return hashlib.md5(url.encode("utf-8")).hexdigest()


def _title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def deduplicate(news_list: list[dict]) -> list[dict]:
    """Remove duplicate news items by URL hash and title similarity."""
    seen_hashes = set()
    unique = []

    for item in news_list:
        url = item.get("url", "")
        title = item.get("title", "")
        h = _url_hash(url)

        if h in seen_hashes:
            continue

        # Check title similarity against already-kept items
        is_dup = False
        for kept in unique:
            if _title_similarity(title, kept["title"]) > 0.8:
                is_dup = True
                break

        if not is_dup:
            seen_hashes.add(h)
            unique.append(item)

    logger.info("Deduplicated: %d → %d items", len(news_list), len(unique))
    return unique
```

### tests/test_collector.py

```python
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
```

## 执行步骤

1. 创建 `src/collector/rss_fetcher.py`
2. 创建 `src/collector/dedup.py`
3. 创建 `tests/test_collector.py`
4. 运行测试: `pytest tests/test_collector.py -v`，确保 3 个测试全部通过
5. 提交: `git add -A && git commit -m "feat: RSS fetcher + deduplication"`

## 全局约束

- Python >= 3.10
- 禁止硬编码密钥
- 日志输出到 `logs/app.log`
- 采集失败时应记录错误并返回空列表（不中断整个流程）

---
**注意**: 请严格按照上述代码实现。测试必须全部通过后才能提交。`fetch_all_sources()` 会调用外部 RSS，但测试不应依赖网络（只测 `_clean_summary` 和 `deduplicate`）。
