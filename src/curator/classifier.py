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
