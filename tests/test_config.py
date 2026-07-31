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
