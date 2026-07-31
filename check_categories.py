import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from collector.rss_fetcher import fetch_all_sources
from collector.dedup import deduplicate
from curator.classifier import classify_and_rank

raw = fetch_all_sources()
print(f"Raw: {len(raw)}")
uniq = deduplicate(raw)
print(f"Unique: {len(uniq)}")
curated = classify_and_rank(uniq, top_n=8)
print(f"Curated: {len(curated)}")
print()
for n in curated:
    print(f"[{n['category']:6}] {n['title'][:50]}")
