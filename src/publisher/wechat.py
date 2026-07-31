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
