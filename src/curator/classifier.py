"""News classifier with LLM (Kimi) + rule-based fallback."""

import json
import os
from datetime import datetime, timezone

import requests

from utils.config_loader import load_categories
from utils.logger import get_logger

logger = get_logger(__name__)

KIMI_API_URL = "https://api.moonshot.cn/v1/chat/completions"
KIMI_MODEL = "moonshot-v1-8k"

# Rule-based fallback keywords
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


def _build_prompt(news_list: list[dict]) -> str:
    """Build the LLM prompt for batch classification."""
    lines = []
    for i, item in enumerate(news_list):
        title = item.get("title", "")
        summary = item.get("summary", "")[:200]
        lines.append(f"[{i}] {title}\n摘要：{summary}")

    prompt = f"""你是一位资深科技编辑。请将以下资讯进行分类并生成一句话解读。

分类选项（严格从以下选择）：Agent、模型、产业、算力、安全

要求：
1. 根据标题和摘要判断最相关的分类
2. 用一句话概括核心信息（50字以内）
3. 输出必须是纯 JSON 数组，不要有任何额外文字

输出格式（严格 JSON）：
[
  {{"index": 0, "category": "分类名", "brief": "一句话解读"}},
  ...
]

---

{"\n\n".join(lines)}
"""
    return prompt


def llm_classify(news_list: list[dict]) -> list[dict] | None:
    """Classify news items using Kimi LLM API. Returns enriched list or None on failure.

    This is the primary classification method. On API failure, callers should
    fall back to rule-based classification.
    """
    api_key = os.getenv("KIMI_API_KEY", "")
    if not api_key:
        logger.info("KIMI_API_KEY not set, skipping LLM classification")
        return None

    try:
        prompt = _build_prompt(news_list)
        resp = requests.post(
            KIMI_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": KIMI_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]

        # Extract JSON from possible markdown code block
        json_text = content.strip()
        if json_text.startswith("```"):
            json_text = json_text.split("\n", 1)[1].rsplit("\n", 1)[0]
        if json_text.startswith("```json"):
            json_text = json_text[7:].strip()

        results = json.loads(json_text)
        if not isinstance(results, list):
            logger.warning("LLM returned non-list JSON, fallback to rules")
            return None

        categories = {c["id"]: c for c in load_categories()}
        cat_name_to_id = {c["name"]: c["id"] for c in load_categories()}

        enriched = []
        for item, result in zip(news_list, results):
            cat_name = result.get("category", "产业")
            cat_id = cat_name_to_id.get(cat_name, "industry")
            cat_info = categories.get(cat_id, {"name": "产业", "color": "#34C759"})

            brief = result.get("brief", "")
            if not brief or len(brief) < 5:
                brief = _generate_brief(item)

            enriched.append({
                **item,
                "category": cat_info["name"],
                "category_id": cat_id,
                "category_color": cat_info["color"],
                "score": _score_item(item),
                "brief": brief,
            })

        logger.info("LLM classified %d items", len(enriched))
        return enriched

    except requests.exceptions.RequestException as e:
        logger.warning("LLM API request failed: %s", e)
    except json.JSONDecodeError as e:
        logger.warning("LLM response JSON parse failed: %s", e)
    except (KeyError, IndexError) as e:
        logger.warning("LLM response structure unexpected: %s", e)
    except Exception as e:
        logger.warning("LLM classification error: %s", e)

    return None


def _rule_classify_all(news_list: list[dict]) -> list[dict]:
    """Classify all items using rule-based method."""
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

    return enriched


def classify_and_rank(news_list: list[dict], top_n: int = 16) -> list[dict]:
    """Classify, score, and rank news items. Returns top N with category diversity.

    Priority:
    1. Try LLM classification (if KIMI_API_KEY is set)
    2. Fallback to rule-based classification
    """
    # Try LLM first
    enriched = llm_classify(news_list)
    if enriched is None:
        logger.info("Using rule-based classification")
        enriched = _rule_classify_all(news_list)

    # Sort by score desc, then published_at desc
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
