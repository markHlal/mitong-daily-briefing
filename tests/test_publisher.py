# tests/test_publisher.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from publisher.wechat import WechatPublisher


def test_publisher_not_configured():
    pub = WechatPublisher()
    assert not pub._is_configured()
    result = pub.publish_images(Path("/fake/detail.png"), Path("/fake/highlights.png"), "2026.07.31")
    assert result is False
