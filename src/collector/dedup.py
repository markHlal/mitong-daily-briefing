import hashlib
from difflib import SequenceMatcher

from utils.logger import get_logger

logger = get_logger(__name__)


def _url_hash(url: str) -> str:
    return hashlib.md5(url.encode("utf-8")).hexdigest()


def _title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.split(), b.split()).ratio()
    return SequenceMatcher(None, a.split(), b.split()).ratio()

    return SequenceMatcher(None, a.split(), b.split()).ratio()


def deduplicate(news_list: list[dict]) -> list[dict]:
    """Remove duplicate news items by URL hash and title similarity."""
    seen_hashes = set()
    unique = []

    for item in news_list:
        url = item.get("url", "")
        title = item.get("title", "")
        h = _url_hash(url)

        if h in seen_hashes:
            continue

        # Check title similarity against already-kept items
        is_dup = False
        for kept in unique:
            if _title_similarity(title, kept["title"]) > 0.8:
                is_dup = True
                break

        if not is_dup:
            seen_hashes.add(h)
            unique.append(item)

    logger.info("Deduplicated: %d → %d items", len(news_list), len(unique))
    return unique
