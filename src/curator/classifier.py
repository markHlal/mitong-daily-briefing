"""News classifier with LLM (Kimi) + rule-based fallback."""

import json
import os
import re
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
    "world": ["国际", "美国", "俄罗斯", "乌克兰", "欧洲", "英国", "法国", "德国", "日本", "韩国",
              "朝鲜", "印度", "中东", "以色列", "伊朗", "联合国", "北约", "关税", "选举", "总统",
              "外交", "地缘", "冲突", "停火", "制裁", "trump", "ukraine", "gaza"],
    "finance": ["股", "基金", "债券", "央行", "利率", "降息", "加息", "IPO", "上市", "涨停", "跌停",
                "沪指", "深成指", "创业板", "纳斯达克", "标普", "道琼斯", "港股", "A股", "美股",
                "期货", "黄金", "原油", "汇率", "人民币", "美元", "国债", "券商", "牛市", "熊市"],
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


def _title_bigrams(title: str) -> set:
    """Character bigrams of a normalized title — works for Chinese (no word segmentation needed)."""
    t = re.sub(r"[^\w一-鿿]+", "", title.lower())
    return {t[i:i + 2] for i in range(len(t) - 1)} if len(t) > 1 else set()


def _attach_attention(news_list: list[dict]) -> list[dict]:
    """Cluster items covering the same story across platforms (title bigram Jaccard),
    and attach `sources_count` = number of DISTINCT sources reporting the story.
    This is the cross-platform attention signal used for ranking.
    """
    n = len(news_list)
    if n == 0:
        return news_list
    tokens = [_title_bigrams(it.get("title", "")) for it in news_list]
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i in range(n):
        for j in range(i + 1, n):
            if not tokens[i] or not tokens[j]:
                continue
            inter = len(tokens[i] & tokens[j])
            if inter == 0:
                continue
            jaccard = inter / len(tokens[i] | tokens[j])
            containment = inter / min(len(tokens[i]), len(tokens[j]))
            # calibrated on real feeds: catches same-story headlines across
            # platforms (0.28+ containment) while excluding lookalike pairs
            if containment >= 0.28 or jaccard >= 0.14:
                union(i, j)

    clusters: dict[int, list[int]] = {}
    for i in range(n):
        clusters.setdefault(find(i), []).append(i)
    for cid, members in enumerate(clusters.values()):
        srcs = {news_list[m].get("source_name", "") for m in members}
        for m in members:
            news_list[m]["sources_count"] = len(srcs)
            news_list[m]["cluster_id"] = cid
    multi = sum(1 for ms in clusters.values() if len({news_list[m].get('source_name', '') for m in ms}) > 1)
    logger.info("Attention clustering: %d stories covered by multiple sources", multi)
    return news_list


def _best_per_story(items: list[dict]) -> list[dict]:
    """Collapse each story cluster to its single best representative
    (highest score, prefer items with an image, then newest)."""
    best: dict[int, dict] = {}
    for it in items:
        cid = it.get("cluster_id", id(it))
        cur = best.get(cid)
        key = (it["score"], bool(it.get("image_url")), it.get("published_at", ""))
        if cur is None or key > (cur["score"], bool(cur.get("image_url")), cur.get("published_at", "")):
            best[cid] = it
    return list(best.values())


def _score_item(item: dict) -> int:
    """Score an item: cross-platform attention dominates, recency breaks ties."""
    score = item.get("sources_count", 1) * 3  # 1 source → 3, 2 → 6, 3+ → 9+
    try:
        pub = datetime.fromisoformat(item.get("published_at", ""))
        hours_ago = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if hours_ago < 6:
            score += 2
        elif hours_ago < 24:
            score += 1
    except Exception:
        pass
    return min(score, 10)


def _generate_brief(item: dict) -> str:
    """One-sentence brief: prefer the first complete sentence of the summary."""
    summary = item.get("summary", "").strip()
    if summary and len(summary) > 10:
        sentences = [s.strip() for s in re.split(r"(?<=[。！？!?])", summary) if s.strip()]
        if sentences:
            first = sentences[0]
            if 12 <= len(first) <= 60:
                return first
            if len(first) > 60:
                return first[:57].rstrip("，,、；;：: ") + "..."
        return summary[:60].rstrip("，,、；;：: ") + ("..." if len(summary) > 60 else "")
    return item.get("title", "")[:50] + "..."


def _build_prompt(news_list: list[dict]) -> str:
    """Build the LLM prompt for batch classification."""
    lines = []
    for i, item in enumerate(news_list):
        title = item.get("title", "")
        summary = item.get("summary", "")[:200]
        lines.append(f"[{i}] {title}\n摘要：{summary}")

    cat_names = "、".join(c["name"] for c in load_categories())
    prompt = f"""你是一位资深新闻编辑。请将以下资讯进行分类并生成一句话解读。

分类选项（严格从以下选择）：{cat_names}

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

    Ranking is attention-driven: stories covered by more sources rank higher,
    recency breaks ties. Priority:
    1. Try LLM classification (if KIMI_API_KEY is set)
    2. Fallback to rule-based classification
    """
    # Cross-platform attention signal must be computed before scoring
    news_list = _attach_attention(news_list)

    # Try LLM first
    enriched = llm_classify(news_list)
    if enriched is None:
        logger.info("Using rule-based classification")
        enriched = _rule_classify_all(news_list)

    # Score desc, newest first among ties (stable two-stage sort)
    enriched.sort(key=lambda x: x.get("published_at", ""), reverse=True)
    enriched.sort(key=lambda x: x["score"], reverse=True)

    # One representative per story — the briefing shows distinct stories,
    # ranked by how many platforms covered them
    enriched = _best_per_story(enriched)

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
    # Final order: attention score desc, newest first among ties
    selected.sort(key=lambda x: x.get("published_at", ""), reverse=True)
    selected.sort(key=lambda x: x["score"], reverse=True)

    logger.info("Curated %d items into top %d", len(news_list), len(selected))
    return selected
