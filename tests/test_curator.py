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
