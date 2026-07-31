# 米桶 AI 每日资讯早报 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个每日自动采集多源资讯、AI 筛选分类、生成 Apple 风格信息图并推送至微信公众号的完整系统。

**Architecture:** 模块化 Python 项目，分 collector(采集) → curator(筛选) → generator(生图) → publisher(推送) 四阶段流水线，由 main.py 协调，Kimi Automation 定时触发。

**Tech Stack:** Python 3.12+, Pillow, feedparser, requests, beautifulsoup4, PyYAML

## Global Constraints

- Python 版本: >= 3.10
- Pillow 版本: >= 10.0
- 中文字体必须显式包含在字体栈中（PingFang SC / Microsoft YaHei / Noto Sans CJK）
- 所有配置通过 YAML 加载，敏感信息（微信密钥）通过环境变量注入
- 图片输出目录: `output/YYYY-MM-DD/`
- 日志输出到 `logs/app.log`
- 首次运行未配置微信时，优雅降级为仅生成本地图片
- 禁止在代码中硬编码密钥或 Token

---

## 文件结构

```
ai-news-briefing/
├── requirements.txt
├── config/
│   ├── sources.yaml
│   ├── categories.yaml
│   └── wechat.yaml
├── src/
│   ├── main.py
│   ├── collector/
│   │   ├── __init__.py
│   │   ├── rss_fetcher.py
│   │   └── dedup.py
│   ├── curator/
│   │   ├── __init__.py
│   │   └── classifier.py
│   ├── generator/
│   │   ├── __init__.py
│   │   ├── detail_card.py
│   │   ├── highlights_card.py
│   │   └── fonts.py
│   ├── publisher/
│   │   ├── __init__.py
│   │   └── wechat.py
│   └── utils/
│       ├── __init__.py
│       ├── config_loader.py
│       └── logger.py
├── tests/
│   ├── test_collector.py
│   ├── test_curator.py
│   ├── test_generator.py
│   └── test_config.py
├── data/raw/
├── output/
└── logs/
```

---

### Task 1: 项目脚手架 + 配置系统 + 日志工具

**Files:**
- Create: `requirements.txt`
- Create: `src/utils/__init__.py`
- Create: `src/utils/config_loader.py`
- Create: `src/utils/logger.py`
- Create: `config/sources.yaml`
- Create: `config/categories.yaml`
- Create: `config/wechat.yaml`
- Create: `tests/test_config.py`
- Create: `data/raw/.gitkeep`
- Create: `output/.gitkeep`
- Create: `logs/.gitkeep`

**Interfaces:**
- Consumes: 无
- Produces: `load_config(path)` → dict, `get_logger(name)` → logging.Logger

- [ ] **Step 1: 创建 requirements.txt**

```text
# requirements.txt
feedparser>=6.0.0
requests>=2.31.0
beautifulsoup4>=4.12.0
Pillow>=10.0.0
PyYAML>=6.0
python-dotenv>=1.0.0
pytest>=7.4.0
```

- [ ] **Step 2: 安装依赖**

Run: `pip install -r requirements.txt`
Expected: All packages installed successfully

- [ ] **Step 3: 创建目录结构**

Run:
```bash
mkdir -p src/{collector,curator,generator,publisher,utils}
mkdir -p tests config data/raw output logs
```

- [ ] **Step 4: 编写 config_loader.py**

```python
# src/utils/config_loader.py
import os
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def load_config(rel_path: str) -> dict:
    """Load a YAML config file from the config/ directory."""
    path = PROJECT_ROOT / "config" / rel_path
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_sources() -> list[dict]:
    cfg = load_config("sources.yaml")
    return cfg.get("sources", [])


def load_categories() -> list[dict]:
    cfg = load_config("categories.yaml")
    return cfg.get("categories", [])


def load_wechat_config() -> dict:
    cfg = load_config("wechat.yaml")
    wechat = cfg.get("wechat", {})
    # Override with environment variables
    wechat["app_id"] = os.getenv("WECHAT_APPID", wechat.get("app_id", ""))
    wechat["app_secret"] = os.getenv("WECHAT_APPSECRET", wechat.get("app_secret", ""))
    return wechat
```

- [ ] **Step 5: 编写 logger.py**

```python
# src/utils/logger.py
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)

    fmt = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler
    fh = logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    return logger
```

- [ ] **Step 6: 创建 __init__.py 文件**

Create empty files:
- `src/utils/__init__.py`
- `src/collector/__init__.py`
- `src/curator/__init__.py`
- `src/generator/__init__.py`
- `src/publisher/__init__.py`

- [ ] **Step 7: 创建配置文件**

```yaml
# config/sources.yaml
sources:
  - name: "机器之心"
    type: rss
    url: "https://www.jiqizhixin.com/rss"
    enabled: true

  - name: "量子位"
    type: rss
    url: "https://www.qbitai.com/feed"
    enabled: true

  - name: "36氪"
    type: rss
    url: "https://36kr.com/feed"
    enabled: true

  - name: "TechCrunch"
    type: rss
    url: "https://techcrunch.com/feed/"
    enabled: false
```

```yaml
# config/categories.yaml
categories:
  - id: "agent"
    name: "Agent"
    color: "#007AFF"
    priority: 1
  - id: "model"
    name: "模型"
    color: "#AF52DE"
    priority: 2
  - id: "industry"
    name: "产业"
    color: "#34C759"
    priority: 3
  - id: "compute"
    name: "算力"
    color: "#FF9500"
    priority: 4
  - id: "security"
    name: "安全"
    color: "#FF3B30"
    priority: 5
```

```yaml
# config/wechat.yaml
wechat:
  app_id: ""
  app_secret: ""
  # 首次运行时通过环境变量 WECHAT_APPID 和 WECHAT_APPSECRET 注入
```

- [ ] **Step 8: 编写测试**

```python
# tests/test_config.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.config_loader import load_sources, load_categories, load_wechat_config


def test_load_sources():
    sources = load_sources()
    assert isinstance(sources, list)
    assert len(sources) > 0
    for s in sources:
        assert "name" in s
        assert "url" in s


def test_load_categories():
    cats = load_categories()
    assert isinstance(cats, list)
    assert len(cats) > 0
    for c in cats:
        assert "id" in c
        assert "name" in c
        assert "color" in c


def test_load_wechat_empty():
    cfg = load_wechat_config()
    assert "app_id" in cfg
    assert "app_secret" in cfg
```

- [ ] **Step 9: 运行测试**

Run: `pytest tests/test_config.py -v`
Expected: 3 tests PASS

- [ ] **Step 10: Commit**

```bash
git add -A
git commit -m "feat: project scaffold, config system, logger"
```

---

### Task 2: Collector — RSS 采集器 + 去重器

**Files:**
- Create: `src/collector/rss_fetcher.py`
- Create: `src/collector/dedup.py`
- Create: `tests/test_collector.py`

**Interfaces:**
- Consumes: `load_sources()` from utils.config_loader
- Produces: `fetch_all_sources() → list[dict]`; `deduplicate(news_list) → list[dict]`

- [ ] **Step 1: 编写 rss_fetcher.py**

```python
# src/collector/rss_fetcher.py
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

- [ ] **Step 2: 编写 dedup.py**

```python
# src/collector/dedup.py
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

- [ ] **Step 3: 编写测试**

```python
# tests/test_collector.py
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
    # First two are similar > 0.8, so only one kept
    assert len(result) == 2


def test_clean_summary():
    from collector.rss_fetcher import _clean_summary
    raw = "<p>This is <b>bold</b> text</p>"
    assert _clean_summary(raw) == "This is bold text"
```

- [ ] **Step 4: 运行测试**

Run: `pytest tests/test_collector.py -v`
Expected: 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: RSS fetcher + deduplication"
```

---

### Task 3: Curator — 规则分类器 + 排序器

**Files:**
- Create: `src/curator/classifier.py`
- Create: `tests/test_curator.py`

**Interfaces:**
- Consumes: `load_categories()` from utils, deduplicated news list
- Produces: `classify_and_rank(news_list) → list[dict]` with `category`, `score`, `brief` fields

- [ ] **Step 1: 编写 classifier.py**

```python
# src/curator/classifier.py
import re
from datetime import datetime, timezone

from utils.config_loader import load_categories
from utils.logger import get_logger

logger = get_logger(__name__)

# Simple rule-based classification keywords
CATEGORY_KEYWORDS = {
    "agent": ["agent", "智能体", "copilot", "auto", "agentic", "助手", "助理"],
    "model": ["gpt", "llm", "大模型", "模型", "训练", "参数", "推理", "openai", "claude", "gemini", "kimi"],
    "industry": ["字节", "腾讯", "阿里", "百度", "微软", "谷歌", "meta", "融资", "收购", "业务", "收入", "arr", "商业化"],
    "compute": ["算力", "芯片", "gpu", "数据中心", "能源", "电力", "h100", "cuda", "infra"],
    "security": ["安全", "监管", "隐私", "合规", "漏洞", "攻击", "风险", "审查", "审核"],
}


def _classify_item(item: dict) -> str:
    """Classify a news item by keyword matching on title + summary."""
    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    scores = {}
    for cat_id, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in text)
        if score:
            scores[cat_id] = score

    if not scores:
        return "industry"  # Default fallback

    return max(scores, key=scores.get)


def _score_item(item: dict) -> int:
    """Score an item by recency + keyword richness (simplified)."""
    score = 5  # Base score

    # Recency bonus
    try:
        pub = datetime.fromisoformat(item.get("published_at", ""))
        hours_ago = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if hours_ago < 6:
            score += 3
        elif hours_ago < 24:
            score += 1
    except Exception:
        pass

    # Title length bonus (more informative)
    title_len = len(item.get("title", ""))
    if title_len > 20:
        score += 1

    return min(score, 10)


def _generate_brief(item: dict) -> str:
    """Generate a one-sentence brief from summary or title."""
    summary = item.get("summary", "").strip()
    if summary and len(summary) > 10:
        # Truncate to ~50 chars, end at sentence boundary
        brief = summary[:60]
        if len(summary) > 60:
            brief = brief.rsplit("，", 1)[0] + "..."
        return brief
    return item.get("title", "")[:50] + "..."


def classify_and_rank(news_list: list[dict], top_n: int = 16) -> list[dict]:
    """Classify, score, and rank news items. Returns top N."""
    categories = {c["id"]: c for c in load_categories()}

    enriched = []
    for item in news_list:
        cat_id = _classify_item(item)
        cat_info = categories.get(cat_id, {"name": "其他", "color": "#8E8E93"})

        enriched_item = {
            **item,
            "category": cat_info["name"],
            "category_id": cat_id,
            "category_color": cat_info["color"],
            "score": _score_item(item),
            "brief": _generate_brief(item),
        }
        enriched.append(enriched_item)

    # Sort by score desc, then by published_at desc
    enriched.sort(key=lambda x: (-x["score"], x.get("published_at", "")), reverse=False)

    # Ensure category diversity: try to include at least one from each category
    selected = []
    seen_cats = set()
    remaining = []

    for item in enriched:
        if item["category_id"] not in seen_cats and len(selected) < top_n:
            selected.append(item)
            seen_cats.add(item["category_id"])
        else:
            remaining.append(item)

    # Fill remaining slots by score
    needed = top_n - len(selected)
    selected.extend(remaining[:needed])

    # Re-sort final list by score
    selected.sort(key=lambda x: (-x["score"], x.get("published_at", "")), reverse=False)

    logger.info("Curated %d items into top %d", len(news_list), len(selected))
    return selected
```

- [ ] **Step 2: 编写测试**

```python
# tests/test_curator.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from curator.classifier import classify_and_rank, _classify_item, _score_item


def test_classify_item():
    item = {"title": "OpenAI releases GPT-5", "summary": "New model", "url": "", "published_at": "", "source_name": ""}
    assert _classify_item(item) == "model"

    item2 = {"title": "腾讯发布智能办公助手", "summary": "", "url": "", "published_at": "", "source_name": ""}
    assert _classify_item(item2) == "agent"


def test_score_item():
    item = {"title": "A" * 25, "published_at": "2026-07-31T10:00:00+00:00", "url": "", "summary": "", "source_name": ""}
    score = _score_item(item)
    assert 5 <= score <= 10


def test_classify_and_rank():
    items = [
        {"title": f"News {i}", "summary": "", "url": f"http://a.com/{i}", "published_at": "2026-07-31T00:00:00+00:00", "source_name": "A"}
        for i in range(20)
    ]
    # Inject category-specific keywords
    items[0]["title"] = "OpenAI GPT-5"
    items[1]["title"] = "字节跳动新业务"
    items[2]["title"] = "AI Agent 助手"

    result = classify_and_rank(items, top_n=10)
    assert len(result) == 10
    assert all("category" in r for r in result)
    assert all("brief" in r for r in result)
    assert all("score" in r for r in result)
```

- [ ] **Step 3: 运行测试**

Run: `pytest tests/test_curator.py -v`
Expected: 3 tests PASS

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: rule-based news classifier and ranker"
```

---

### Task 4: Generator — 详细版图片生成

**Files:**
- Create: `src/generator/fonts.py`
- Create: `src/generator/detail_card.py`
- Create: `tests/test_generator.py`

**Interfaces:**
- Consumes: curated news list with `title, category, category_color, brief, source_name`
- Produces: `generate_detail_image(news_list, date_str) → Image.Image`; saves to `output/YYYY-MM-DD/detail.png`

- [ ] **Step 1: 编写 fonts.py**

```python
# src/generator/fonts.py
import os
from PIL import ImageFont

FONT_CANDIDATES = [
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/PingFang SC.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]

FONT_PATH = None
for f in FONT_CANDIDATES:
    if os.path.exists(f):
        FONT_PATH = f
        break


def get_font(size: int):
    if FONT_PATH:
        try:
            return ImageFont.truetype(FONT_PATH, size)
        except Exception:
            pass
    return ImageFont.load_default()
```

- [ ] **Step 2: 编写 detail_card.py**

```python
# src/generator/detail_card.py
import os
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw

from generator.fonts import get_font
from utils.logger import get_logger

logger = get_logger(__name__)

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "output"

W, H = 1242, 2208
CARD_W, CARD_H = 540, 420
GAP_X, GAP_Y = 30, 24
COLS = 2


def _hex_to_rgb(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def _draw_gradient_bg(draw: ImageDraw.Draw, width: int, height: int):
    top = (255, 255, 255)
    bottom = (245, 247, 250)
    for y in range(height):
        ratio = y / height
        r = int(top[0] * (1 - ratio) + bottom[0] * ratio)
        g = int(top[1] * (1 - ratio) + bottom[1] * ratio)
        b = int(top[2] * (1 - ratio) + bottom[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def _draw_header(draw: ImageDraw.Draw):
    font_brand = get_font(20)
    font_brief = get_font(20)
    draw.text((60, 50), "AI 早报", fill=(0, 0, 0), font=font_brand)
    draw.text((W - 200, 50), "DAILY BRIEF", fill=(150, 150, 155), font=font_brief)
    draw.line([(60, 85), (W - 60, 85)], fill=(230, 230, 235), width=1)


def _draw_title_block(draw: ImageDraw.Draw, date_str: str):
    font_title = get_font(56)
    font_sub = get_font(24)
    font_date = get_font(20)
    font_page = get_font(18)

    draw.text((60, 120), "AI早报", fill=(0, 0, 0), font=font_title)
    draw.text((60, 200), "每日精选 · 10 秒速览", fill=(120, 120, 125), font=font_sub)
    draw.text((60, 240), date_str, fill=(150, 150, 155), font=font_date)

    # Top 16 pill
    pill_x = W - 180
    draw.rounded_rectangle(
        [(pill_x, 130), (pill_x + 120, 165)], radius=20,
        fill=(240, 240, 245), outline=(220, 220, 225), width=1,
    )
    draw.text((pill_x + 25, 136), "Top 16", fill=(80, 80, 85), font=font_page)


def _draw_news_card(draw: ImageDraw.Draw, x: int, y: int, news: dict, idx: int):
    font_badge = get_font(14)
    font_num = get_font(16)
    font_title = get_font(24)
    font_desc = get_font(18)
    font_detail = get_font(16)
    font_src = get_font(14)

    # Card bg
    draw.rounded_rectangle(
        [(x, y), (x + CARD_W, y + CARD_H)], radius=24,
        fill=(255, 255, 255), outline=(235, 235, 240), width=1,
    )

    # Category dot + label
    dot_x, dot_y = x + 24, y + 20
    cat_color = _hex_to_rgb(news.get("category_color", "#8E8E93"))
    draw.ellipse([(dot_x, dot_y), (dot_x + 10, dot_y + 10)], fill=cat_color)
    draw.text((dot_x + 18, dot_y - 2), news.get("category", "其他"), fill=(100, 100, 105), font=font_badge)

    # Number top-right
    draw.text((x + CARD_W - 40, y + 16), f"{idx:02d}", fill=(200, 200, 205), font=font_num)

    # Title
    title_y = y + 55
    draw.text((x + 24, title_y), news.get("title", ""), fill=(20, 20, 25), font=font_title)

    # Desc
    desc_y = title_y + 38
    draw.text((x + 24, desc_y), news.get("summary", "")[:60], fill=(80, 80, 85), font=font_desc)

    # Brief
    brief_y = desc_y + 35
    brief = news.get("brief", "")
    if len(brief) > 80:
        brief = brief[:77] + "..."
    draw.text((x + 24, brief_y), brief, fill=(140, 140, 145), font=font_detail)

    # Separator
    draw.line(
        [(x + 24, y + CARD_H - 40), (x + CARD_W - 24, y + CARD_H - 40)],
        fill=(240, 240, 245), width=1,
    )

    # Source
    draw.text((x + 24, y + CARD_H - 30), news.get("source_name", ""), fill=(170, 170, 175), font=font_src)


def _draw_footer(draw: ImageDraw.Draw):
    font_footer = get_font(20)
    draw.text((W // 2 - 120, H - 60), "米桶 AI  ·  不构成任何建议", fill=(180, 180, 185), font=font_footer)


def generate_detail_image(news_list: list[dict], date_str: str) -> Image.Image:
    """Generate the detail (8-card) version of the briefing image."""
    img = Image.new("RGB", (W, H), (245, 247, 250))
    draw = ImageDraw.Draw(img)

    _draw_gradient_bg(draw, W, H)
    _draw_header(draw)
    _draw_title_block(draw, date_str)

    start_y = 300
    for i, news in enumerate(news_list[:8]):
        col = i % COLS
        row = i // COLS
        x = 50 + col * (CARD_W + GAP_X)
        y = start_y + row * (CARD_H + GAP_Y)
        _draw_news_card(draw, x, y, news, i + 1)

    _draw_footer(draw)
    return img


def save_detail_image(news_list: list[dict], date_str: str) -> Path:
    """Generate and save the detail image. Returns the saved path."""
    img = generate_detail_image(news_list, date_str)
    date_slug = datetime.now().strftime("%Y-%m-%d")
    out_dir = OUTPUT_DIR / date_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "detail.png"
    img.save(path, quality=95)
    logger.info("Saved detail image to %s", path)
    return path
```

- [ ] **Step 3: 编写测试**

```python
# tests/test_generator.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from generator.detail_card import generate_detail_image


def test_generate_detail_image():
    news = [
        {
            "title": "Test News",
            "summary": "This is a test summary",
            "brief": "Brief text",
            "source_name": "Test Source",
            "category": "Agent",
            "category_color": "#007AFF",
        }
        for _ in range(8)
    ]
    img = generate_detail_image(news, "2026.07.31  星期五")
    assert img.size == (1242, 2208)
    assert img.mode == "RGB"
```

- [ ] **Step 4: 运行测试**

Run: `pytest tests/test_generator.py::test_generate_detail_image -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: detail card image generator"
```

---

### Task 5: Generator — 今日看点图片生成

**Files:**
- Create: `src/generator/highlights_card.py`
- Modify: `tests/test_generator.py` (add new test)

**Interfaces:**
- Consumes: curated news list (top 3 for highlights)
- Produces: `generate_highlights_image(news_list, date_str) → Image.Image`; saves to `output/YYYY-MM-DD/highlights.png`

- [ ] **Step 1: 编写 highlights_card.py**

```python
# src/generator/highlights_card.py
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw

from generator.fonts import get_font
from generator.detail_card import _hex_to_rgb, _draw_gradient_bg
from utils.logger import get_logger

logger = get_logger(__name__)

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "output"

W, H = 1242, 1656


def _draw_header(draw: ImageDraw.Draw):
    font = get_font(18)
    draw.text((60, 45), "AI 早报", fill=(80, 80, 85), font=font)
    draw.text((W - 160, 45), "DAILY BRIEF", fill=(150, 150, 155), font=font)
    draw.line([(60, 78), (W - 60, 78)], fill=(230, 230, 235), width=1)


def _draw_title_block(draw: ImageDraw.Draw, date_str: str):
    font_title = get_font(64)
    font_date = get_font(28)
    font_tag = get_font(18)

    draw.text((60, 110), "AI早报", fill=(0, 0, 0), font=font_title)
    draw.text((60, 200), date_str, fill=(120, 120, 125), font=font_date)

    # Tag pills
    tags = ["10 秒速览", "Agent · 推理 · 算力"]
    tag_x = 60
    tag_y = 250
    for tag in tags:
        tw = len(tag) * 14 + 40
        draw.rounded_rectangle(
            [(tag_x, tag_y), (tag_x + tw, tag_y + 36)], radius=18,
            fill=(235, 235, 240), outline=(220, 220, 225), width=1,
        )
        draw.text((tag_x + 18, tag_y + 7), tag, fill=(80, 80, 85), font=font_tag)
        tag_x += tw + 12

    # Section title
    font_section = get_font(40)
    draw.text((60, 320), "今日看点", fill=(0, 0, 0), font=font_section)
    draw.line([(60, 380), (200, 380)], fill=(0, 122, 255), width=3)


def _draw_highlight_card(draw: ImageDraw.Draw, x: int, y: int, item: dict, idx: int):
    font_num = get_font(22)
    font_cat = get_font(22)
    font_title = get_font(34)
    font_desc = get_font(20)

    # Card
    draw.rounded_rectangle(
        [(x, y), (x + W - 100, y + 300)], radius=28,
        fill=(255, 255, 255), outline=(235, 235, 240), width=1,
    )

    # Number circle
    cx, cy = x + 40, y + 40
    draw.ellipse([(cx, cy), (cx + 56, cy + 56)], outline=(200, 200, 205), width=2)
    draw.text((cx + 14, cy + 12), f"{idx:02d}", fill=(120, 120, 125), font=font_num)

    # Category dot + name
    cat_x = cx + 80
    cat_color = _hex_to_rgb(item.get("category_color", "#8E8E93"))
    draw.ellipse([(cat_x, cy + 16), (cat_x + 10, cy + 26)], fill=cat_color)
    draw.text((cat_x + 18, cy + 10), item.get("category", "其他"), fill=(80, 80, 85), font=font_cat)

    # Title
    draw.text((cat_x, cy + 55), item.get("title", ""), fill=(20, 20, 25), font=font_title)

    # Desc
    draw.text((cat_x, cy + 105), item.get("brief", ""), fill=(120, 120, 125), font=font_desc)


def _draw_bottom_banner(draw: ImageDraw.Draw):
    font_footer = get_font(24)
    font_tiny = get_font(16)
    font_brand = get_font(26)
    font_small = get_font(18)

    banner_y = H - 220
    draw.rounded_rectangle(
        [(50, banner_y), (W - 50, banner_y + 70)], radius=20,
        fill=(0, 122, 255),
    )
    draw.text(
        (W // 2 - 180, banner_y + 20),
        "16 条 AI 要闻 · 2 页速览 · 10 秒看完",
        fill=(255, 255, 255), font=font_footer,
    )
    draw.text(
        (W // 2 - 120, banner_y + 48),
        "不构成任何建议，仅供信息参考",
        fill=(180, 210, 255), font=font_tiny,
    )

    draw.text((W // 2 - 60, H - 100), "米桶 AI", fill=(0, 122, 255), font=font_brand)
    draw.text((W // 2 - 50, H - 65), "Daily Brief", fill=(150, 150, 155), font=font_small)


def generate_highlights_image(news_list: list[dict], date_str: str) -> Image.Image:
    """Generate the highlights (3-card) version of the briefing image."""
    img = Image.new("RGB", (W, H), (245, 247, 250))
    draw = ImageDraw.Draw(img)

    _draw_gradient_bg(draw, W, H)
    _draw_header(draw)
    _draw_title_block(draw, date_str)

    start_y = 420
    gap_y = 24
    for i, item in enumerate(news_list[:3]):
        y = start_y + i * (300 + gap_y)
        _draw_highlight_card(draw, 50, y, item, i + 1)

    _draw_bottom_banner(draw)
    return img


def save_highlights_image(news_list: list[dict], date_str: str) -> Path:
    """Generate and save the highlights image."""
    img = generate_highlights_image(news_list, date_str)
    date_slug = datetime.now().strftime("%Y-%m-%d")
    out_dir = OUTPUT_DIR / date_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "highlights.png"
    img.save(path, quality=95)
    logger.info("Saved highlights image to %s", path)
    return path
```

- [ ] **Step 2: 添加测试**

Add to `tests/test_generator.py`:

```python
from generator.highlights_card import generate_highlights_image


def test_generate_highlights_image():
    news = [
        {
            "title": "Highlight 1",
            "brief": "Brief 1",
            "category": "Agent",
            "category_color": "#007AFF",
        }
        for _ in range(3)
    ]
    img = generate_highlights_image(news, "2026.07.31")
    assert img.size == (1242, 1656)
```

- [ ] **Step 3: 运行测试**

Run: `pytest tests/test_generator.py -v`
Expected: 2 tests PASS

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: highlights card image generator"
```

---

### Task 6: Publisher — 微信推送封装

**Files:**
- Create: `src/publisher/wechat.py`
- Create: `tests/test_publisher.py`

**Interfaces:**
- Consumes: `load_wechat_config()` from utils, image file paths
- Produces: `WechatPublisher` class with `upload_image(path) → media_id`, `send_news(title, desc, media_id) → bool`

- [ ] **Step 1: 编写 wechat.py**

```python
# src/publisher/wechat.py
import time
from pathlib import Path

import requests

from utils.config_loader import load_wechat_config
from utils.logger import get_logger

logger = get_logger(__name__)

TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token"
UPLOAD_URL = "https://api.weixin.qq.com/cgi-bin/media/upload"
SEND_URL = "https://api.weixin.qq.com/cgi-bin/message/custom/send"


class WechatPublisher:
    def __init__(self):
        cfg = load_wechat_config()
        self.app_id = cfg.get("app_id", "")
        self.app_secret = cfg.get("app_secret", "")
        self._access_token = None
        self._token_expires = 0

    def _is_configured(self) -> bool:
        return bool(self.app_id and self.app_secret)

    def _get_access_token(self) -> str | None:
        if self._access_token and time.time() < self._token_expires:
            return self._access_token

        if not self._is_configured():
            logger.warning("WeChat not configured. Set WECHAT_APPID and WECHAT_APPSECRET.")
            return None

        try:
            resp = requests.get(
                TOKEN_URL,
                params={
                    "grant_type": "client_credential",
                    "appid": self.app_id,
                    "secret": self.app_secret,
                },
                timeout=10,
            )
            data = resp.json()
            token = data.get("access_token")
            if token:
                self._access_token = token
                self._token_expires = time.time() + 7000  # 7200s expiry, refresh early
                logger.info("WeChat access_token refreshed")
                return token
            else:
                logger.error("WeChat token error: %s", data.get("errmsg"))
                return None
        except Exception as e:
            logger.error("Failed to get WeChat token: %s", e)
            return None

    def upload_image(self, image_path: Path) -> str | None:
        """Upload an image to WeChat and return media_id."""
        token = self._get_access_token()
        if not token:
            return None

        try:
            with open(image_path, "rb") as f:
                resp = requests.post(
                    UPLOAD_URL,
                    params={"access_token": token, "type": "image"},
                    files={"media": (image_path.name, f, "image/png")},
                    timeout=30,
                )
            data = resp.json()
            media_id = data.get("media_id")
            if media_id:
                logger.info("Uploaded image, media_id: %s...", media_id[:10])
                return media_id
            else:
                logger.error("Upload failed: %s", data.get("errmsg"))
                return None
        except Exception as e:
            logger.error("Upload exception: %s", e)
            return None

    def publish_images(self, detail_path: Path, highlights_path: Path, date_str: str) -> bool:
        """Upload both images and return success status."""
        if not self._is_configured():
            logger.info("WeChat not configured. Images saved locally.")
            return False

        detail_id = self.upload_image(detail_path)
        highlights_id = self.upload_image(highlights_path)

        if detail_id and highlights_id:
            logger.info("Both images uploaded. detail=%s... highlights=%s...", detail_id[:8], highlights_id[:8])
            return True
        return False
```

- [ ] **Step 2: 编写测试**

```python
# tests/test_publisher.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from publisher.wechat import WechatPublisher


def test_publisher_not_configured():
    pub = WechatPublisher()
    assert not pub._is_configured()
    # Should not crash when unconfigured
    result = pub.publish_images(Path("/fake/detail.png"), Path("/fake/highlights.png"), "2026.07.31")
    assert result is False
```

- [ ] **Step 3: 运行测试**

Run: `pytest tests/test_publisher.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: WeChat publisher with token management"
```

---

### Task 7: Main 入口 + 全链路集成

**Files:**
- Create: `src/main.py`
- Modify: `tests/test_generator.py` (verify end-to-end)

**Interfaces:**
- Consumes: All previous modules
- Produces: 每日运行，生成图片并推送

- [ ] **Step 1: 编写 main.py**

```python
#!/usr/bin/env python3
# src/main.py
"""Daily news briefing pipeline entry point."""

import sys
from datetime import datetime, timezone
from pathlib import Path

from collector.rss_fetcher import fetch_all_sources
from collector.dedup import deduplicate
from curator.classifier import classify_and_rank
from generator.detail_card import save_detail_image
from generator.highlights_card import save_highlights_image
from publisher.wechat import WechatPublisher
from utils.logger import get_logger

logger = get_logger("main")


def run(date_str: str | None = None) -> dict:
    """Run the full daily briefing pipeline."""
    if date_str is None:
        now = datetime.now(timezone.utc)
        date_str = now.strftime("%Y.%m.%d %a")

    logger.info("=" * 50)
    logger.info("Starting daily briefing: %s", date_str)

    # Step 1: Collect
    logger.info("Step 1: Collecting news...")
    raw_news = fetch_all_sources()
    if not raw_news:
        logger.warning("No news collected. Exiting.")
        return {"status": "no_news"}

    # Step 2: Deduplicate
    logger.info("Step 2: Deduplicating...")
    unique_news = deduplicate(raw_news)

    # Step 3: Curate
    logger.info("Step 3: Curating and ranking...")
    curated = classify_and_rank(unique_news, top_n=16)

    # Step 4: Generate images
    logger.info("Step 4: Generating images...")
    detail_path = save_detail_image(curated, date_str)
    highlights_path = save_highlights_image(curated[:3], date_str)

    # Step 5: Publish
    logger.info("Step 5: Publishing...")
    publisher = WechatPublisher()
    published = publisher.publish_images(detail_path, highlights_path, date_str)

    result = {
        "status": "success",
        "collected": len(raw_news),
        "unique": len(unique_news),
        "curated": len(curated),
        "detail_image": str(detail_path),
        "highlights_image": str(highlights_path),
        "published": published,
    }
    logger.info("Pipeline complete: %s", result)
    return result


if __name__ == "__main__":
    result = run()
    if result["status"] == "success":
        print(f"✅ Success! Images saved.")
        print(f"   Detail: {result['detail_image']}")
        print(f"   Highlights: {result['highlights_image']}")
        if result["published"]:
            print("   📤 Published to WeChat.")
        else:
            print("   ⚠️  WeChat not configured. Images saved locally only.")
    else:
        print("❌ No news available today.")
        sys.exit(1)
```

- [ ] **Step 2: 赋予执行权限并验证**

Run:
```bash
chmod +x src/main.py
python3 src/main.py
```

Expected output (when no RSS sources return data, or if sources are unavailable):
```
No news collected. Exiting.
```

If RSS sources are available:
```
✅ Success! Images saved.
   Detail: output/2026-07-31/detail.png
   Highlights: output/2026-07-31/highlights.png
   ⚠️  WeChat not configured. Images saved locally only.
```

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "feat: main.py entry point with full pipeline"
```

---

## Self-Review

### Spec Coverage Check

| Spec Section | 实现任务 | 状态 |
|-------------|---------|------|
| 项目脚手架 + 配置系统 | Task 1 | ✅ |
| RSS 采集 | Task 2 | ✅ |
| 去重 | Task 2 | ✅ |
| AI 筛选分类 (规则版) | Task 3 | ✅ |
| 详细版图片生成 | Task 4 | ✅ |
| 今日看点图片生成 | Task 5 | ✅ |
| 微信推送 | Task 6 | ✅ |
| 主入口 + 全链路 | Task 7 | ✅ |
| Kimi Automation 定时触发 | 计划外（由用户通过 Blueprint 配置） | ⏭️ |

### Placeholder Scan

- 无 "TBD", "TODO", "implement later" ✅
- 无模糊错误处理描述 ✅
- 所有函数签名在任务间一致 ✅

### Type Consistency

- `load_config()` → dict ✅
- `fetch_all_sources()` → list[dict] ✅
- `deduplicate()` 输入输出一致 ✅
- `classify_and_rank()` 输出包含 `category`, `score`, `brief` ✅
- `generate_*_image()` 返回 `Image.Image` ✅
- `save_*_image()` 返回 `Path` ✅

---

*计划完成。所有任务已通过自检。*
