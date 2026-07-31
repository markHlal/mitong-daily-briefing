import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from curator.classifier import (
    classify_and_rank,
    _classify_item,
    _score_item,
    llm_classify,
    _rule_classify_all,
)


def test_classify_item():
    item = {"title": "OpenAI releases GPT-5", "summary": "New model", "url": "", "published_at": "", "source_name": ""}
    assert _classify_item(item) == "model"

    item2 = {"title": "腾讯发布智能办公助手", "summary": "", "url": "", "published_at": "", "source_name": ""}
    assert _classify_item(item2) == "agent"


def test_score_item():
    item = {"title": "A" * 25, "published_at": "2026-07-31T10:00:00+00:00", "url": "", "summary": "", "source_name": ""}
    score = _score_item(item)
    assert 5 <= score <= 10


def test_classify_and_rank_fallback():
    """When KIMI_API_KEY is not set, fallback to rule-based classification."""
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


def test_llm_classify_no_key():
    """llm_classify returns None when KIMI_API_KEY is not set."""
    items = [
        {"title": "Test", "summary": "", "url": "", "published_at": "", "source_name": "A"}
    ]
    result = llm_classify(items)
    assert result is None


def test_llm_classify_success():
    """llm_classify parses LLM response correctly."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": '[\n  {"index": 0, "category": "模型", "brief": "OpenAI发布GPT-5"}\n]'
                }
            }
        ]
    }
    mock_response.raise_for_status = Mock()

    items = [
        {"title": "OpenAI releases GPT-5", "summary": "New model", "url": "", "published_at": "2026-07-31T00:00:00+00:00", "source_name": "A"}
    ]

    with patch("curator.classifier.requests.post", return_value=mock_response):
        with patch.dict("os.environ", {"KIMI_API_KEY": "fake_key"}):
            result = llm_classify(items)

    assert result is not None
    assert len(result) == 1
    assert result[0]["category"] == "模型"
    assert result[0]["brief"] == "OpenAI发布GPT-5"


def test_llm_classify_markdown_code_block():
    """llm_classify handles markdown-wrapped JSON."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": '```json\n[\n  {"index": 0, "category": "Agent", "brief": "智能助手上线"}\n]\n```'
                }
            }
        ]
    }
    mock_response.raise_for_status = Mock()

    items = [
        {"title": "智能助手", "summary": "", "url": "", "published_at": "2026-07-31T00:00:00+00:00", "source_name": "A"}
    ]

    with patch("curator.classifier.requests.post", return_value=mock_response):
        with patch.dict("os.environ", {"KIMI_API_KEY": "fake_key"}):
            result = llm_classify(items)

    assert result is not None
    assert result[0]["category"] == "Agent"


def test_rule_classify_all():
    """_rule_classify_all processes all items with keyword matching."""
    items = [
        {"title": "OpenAI GPT-5", "summary": "", "url": "", "published_at": "", "source_name": ""},
        {"title": "腾讯收购", "summary": "", "url": "", "published_at": "", "source_name": ""},
    ]
    result = _rule_classify_all(items)
    assert len(result) == 2
    assert result[0]["category_id"] == "model"
    assert result[1]["category_id"] == "industry"
