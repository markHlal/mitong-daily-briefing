import os
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def load_config(rel_path: str) -> dict:
    path = PROJECT_ROOT / "config" / rel_path
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_sources() -> list[dict]:
    cfg = load_config("sources.yaml")
    return cfg.get("sources", [])


def load_categories() -> list[dict]:
    cfg = load_config("categories.yaml")
    return cfg.get("categories", [])


def load_wechat_config() -> dict:
    cfg = load_config("wechat.yaml")
    wechat = cfg.get("wechat", {})
    wechat["app_id"] = os.getenv("WECHAT_APPID", wechat.get("app_id", ""))
    wechat["app_secret"] = os.getenv("WECHAT_APPSECRET", wechat.get("app_secret", ""))
    return wechat
