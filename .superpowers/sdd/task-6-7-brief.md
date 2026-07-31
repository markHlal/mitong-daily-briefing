# Task 6+7: 微信推送 + Main 入口集成

**项目**: 米桶 AI 每日资讯早报系统  
**工作目录**: `/Users/huang/Documents/Kimi/Workspaces/ai新闻收集`

实现微信公众号推送封装和主入口，完成全链路集成。

## 前置依赖

Task 1-5 全部已完成。可用接口：
- `from utils.config_loader import load_wechat_config` → dict with app_id, app_secret
- `from utils.logger import get_logger` → logging.Logger
- `from collector.rss_fetcher import fetch_all_sources` → list[dict]
- `from collector.dedup import deduplicate` → list[dict]
- `from curator.classifier import classify_and_rank` → list[dict] with category, score, brief
- `from generator.detail_card import save_detail_image` → Path
- `from generator.highlights_card import save_highlights_image` → Path

## 需要创建的文件

1. `src/publisher/wechat.py` — 微信推送封装
2. `src/main.py` — 主入口

## 代码要求

### wechat.py

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
                params={"grant_type": "client_credential", "appid": self.app_id, "secret": self.app_secret},
                timeout=10,
            )
            data = resp.json()
            token = data.get("access_token")
            if token:
                self._access_token = token
                self._token_expires = time.time() + 7000
                logger.info("WeChat access_token refreshed")
                return token
            else:
                logger.error("WeChat token error: %s", data.get("errmsg"))
                return None
        except Exception as e:
            logger.error("Failed to get WeChat token: %s", e)
            return None

    def upload_image(self, image_path: Path) -> str | None:
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
        if not self._is_configured():
            logger.info("WeChat not configured. Images saved locally.")
            return False
        detail_id = self.upload_image(detail_path)
        highlights_id = self.upload_image(highlights_path)
        if detail_id and highlights_id:
            logger.info("Both images uploaded.")
            return True
        return False
```

### main.py

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

### 测试

```python
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
```

## 执行步骤

1. 创建 `src/publisher/wechat.py`
2. 创建 `src/main.py`
3. 创建 `tests/test_publisher.py`
4. 运行测试: `pytest tests/test_publisher.py -v`
5. 验证 main.py 可执行: `python src/main.py`（未配置微信时应显示"No news"或"WeChat not configured"）
6. 提交: `git add -A && git commit -m "feat: WeChat publisher + main entry point"`

## 全局约束

- Python >= 3.10
- 禁止硬编码密钥或 Token
- 微信配置通过环境变量 WECHAT_APPID / WECHAT_APPSECRET 注入
- 未配置微信时优雅降级为仅生成本地图片
- 日志输出到 `logs/app.log`

---
**注意**: 严格按照上述代码实现。测试必须全部通过。main.py 应能独立运行，未配置微信时不崩溃。
