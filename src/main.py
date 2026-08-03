#!/usr/bin/env python3
# src/main.py
"""Daily news briefing pipeline entry point."""

import json
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

    # Step 4: Save structured data as JSON (website generator reads this)
    logger.info("Step 4: Saving structured data...")
    date_part = date_str.split()[0].replace(".", "-")
    data_dir = Path("output") / date_part
    data_dir.mkdir(parents=True, exist_ok=True)
    data_path = data_dir / "data.json"
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump({
            "date": date_str,
            "date_key": date_part,
            "items": curated,
            "highlights": curated[:3],
        }, f, ensure_ascii=False, indent=2)
    logger.info("Saved data to %s", data_path)

    # Step 5: Generate images
    logger.info("Step 5: Generating images...")
    detail_path = save_detail_image(curated, date_str)
    highlights_path = save_highlights_image(curated[:3], date_str)

    # Step 6: Publish
    logger.info("Step 6: Publishing...")
    publisher = WechatPublisher()
    published = publisher.publish_images(detail_path, highlights_path, date_str)

    result = {
        "status": "success",
        "collected": len(raw_news),
        "unique": len(unique_news),
        "curated": len(curated),
        "data_path": str(data_path),
        "detail_image": str(detail_path),
        "highlights_image": str(highlights_path),
        "published": published,
    }
    logger.info("Pipeline complete: %s", result)
    return result


if __name__ == "__main__":
    result = run()
    if result["status"] == "success":
        print("✅ Success! Images saved.")
        print(f"   Data: {result['data_path']}")
        print(f"   Detail: {result['detail_image']}")
        print(f"   Highlights: {result['highlights_image']}")
        if result["published"]:
            print("   📤 Published to WeChat.")
        else:
            print("   ⚠️  WeChat not configured. Images saved locally only.")
    else:
        print("❌ No news available today.")
        sys.exit(1)
