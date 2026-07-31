# Task 3: 规则分类器 + 排序器

**项目**: 米桶 AI 每日资讯早报系统  
**工作目录**: `/Users/huang/Documents/Kimi/Workspaces/ai新闻收集`

对去重后的资讯进行分类、打分、排序，选出 Top 16，并为每条生成一句话摘要。

## 前置依赖

Task 1-2 已完成，以下接口可用：
- `from utils.config_loader import load_categories` → 返回 `list[dict]`，每个有 `id`, `name`, `color`, `priority`
- `from utils.logger import get_logger` → 返回 `logging.Logger`
- `from collector.dedup import deduplicate` → 输入 `list[dict]`，输出去重后的 `list[dict]`

输入数据格式（来自 collector）：
```python
{
    "title": str,
    "url": str,
    "summary": str,
    "published_at": str (ISO 8601),
    "source_name": str,
}
```

## 需要创建的文件

1. `src/curator/classifier.py`
2. `tests/test_curator.py`

## 输出数据格式

每条资讯需扩展以下字段：
```python
{
    # 原有字段...
    "category": str,       # 分类名称（如 "Agent"）
    "category_id": str,    # 分类 ID（如 "agent"）
    "category_color": str, # 分类颜色（如 "#007AFF"）
    "score": int,          # 1-10 重要性评分
    "brief": str,          # 一句话摘要（50字以内）
}
```

## 代码要求

### classifier.py

```python
# src/curator/classifier.py
import re
from datetime import datetime, timezone

from utils.config_loader import load_categories
from utils.logger import get_logger

logger = get_logger(__name__)

# 规则分类关键词映射
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
        return "industry"
    return max(scores, key=scores.get)


def _score_item(item: dict) -> int:
    """Score an item by recency + keyword richness."""
    score = 5
    try:
        pub = datetime.fromisoformat(item.get("published_at", ""))
        hours_ago = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if hours_ago < 6:
            score += 3
        elif hours_ago < 24:
            score += 1
    except Exception:
        pass
    if len(item.get("title", "")) > 20:
        score += 1
    return min(score, 10)


def _generate_brief(item: dict) -> str:
    """Generate a one-sentence brief from summary or title."""
    summary = item.get("summary", "").strip()
    if summary and len(summary) > 10:
        brief = summary[:60]
        if len(summary) > 60:
            brief = brief.rsplit("，", 1)[0] + "..."
        return brief
    return item.get("title", "")[:50] + "..."


def classify_and_rank(news_list: list[dict], top_n: int = 16) -> list[dict]:
    """Classify, score, and rank news items. Returns top N with category diversity."""
    categories = {c["id"]: c for c in load_categories()}

    enriched = []
    for item in news_list:
        cat_id = _classify_item(item)
        cat_info = categories.get(cat_id, {"name": "其他", "color": "#8E8E93"})
        enriched.append({
            **item,
            "category": cat_info["name"],
            "category_id": cat_id,
            "category_color": cat_info["color"],
            "score": _score_item(item),
            "brief": _generate_brief(item),
        })

    enriched.sort(key=lambda x: (-x["score"], x.get("published_at", "")), reverse=False)

    # Category diversity: ensure at least one from each category
    selected = []
    seen_cats = set()
    remaining = []
    for item in enriched:
        if item["category_id"] not in seen_cats and len(selected) < top_n:
            selected.append(item)
            seen_cats.add(item["category_id"])
        else:
            remaining.append(item)

    needed = top_n - len(selected)
    selected.extend(remaining[:needed])
    selected.sort(key=lambda x: (-x["score"], x.get("published_at", "")), reverse=False)

    logger.info("Curated %d items into top %d", len(news_list), len(selected))
    return selected
```

### tests/test_curator.py

```python
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
    items[0]["title"] = "OpenAI GPT-5"
    items[1]["title"] = "字节跳动新业务"
    items[2]["title"] = "AI Agent 助手"

    result = classify_and_rank(items, top_n=10)
    assert len(result) == 10
    assert all("category" in r for r in result)
    assert all("brief" in r for r in result)
    assert all("score" in r for r in result)
```

## 执行步骤

1. 创建 `src/curator/classifier.py`
2. 创建 `tests/test_curator.py`
3. 运行测试: `pytest tests/test_curator.py -v`，确保 3 个测试全部通过
4. 提交: `git add -A && git commit -m "feat: rule-based news classifier and ranker"`

## 全局约束

- Python >= 3.10
- 禁止硬编码密钥
- 日志输出到 `logs/app.log`

---
**注意**: 严格按照上述代码实现。测试必须全部通过后才能提交。
