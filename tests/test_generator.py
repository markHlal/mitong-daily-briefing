import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from generator.detail_card import generate_detail_image
from generator.highlights_card import generate_highlights_image


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
    assert img.mode == "RGB"
