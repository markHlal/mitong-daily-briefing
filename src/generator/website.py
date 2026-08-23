"""Generate the 米桶 AI 早报 website — modern Apple-style edition.

Design language: clean, light, glassy — the Apple software aesthetic.
  · Light system-gray canvas, white cards, hairline dividers.
  · SF/PingFang system type, no serif.
  · Rounded cards (20px), one blue→violet gradient accent used with restraint.
  · Segmented control filters the news list by 资讯类型.
  · List layout (not card grid), source shown inline on each row.
  · Sticky frosted-glass top bar.
  · No external JS/CSS dependencies — everything works offline.
"""

import json
import re
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
WEB_DIR = PROJECT_ROOT / "website" / "cn"

WEEKDAYS_CN = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

# ── News sections (资讯类型栏目) ──
try:
    from utils.config_loader import load_sections, section_of_category
    SECTIONS = [(s["id"], s["name"]) for s in load_sections()]
    if not SECTIONS:
        raise ValueError("no sections configured")
except Exception:  # fallback when utils is not importable
    SECTIONS = [("ai", "AI 资讯"), ("world", "国际时事"), ("finance", "证券资讯")]

    def section_of_category(cat_id: str) -> str:
        return {"world": "world", "finance": "finance"}.get(cat_id, "ai")


# ───────────────────────── helpers ─────────────────────────

def _slug(date: str) -> str:
    """Filesystem-safe slug for a briefing date."""
    return date.replace(" ", "_").replace(".", "-")


def _esc(text) -> str:
    s = str(text or "")
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def _fmt_date(date: str) -> str:
    """'2026-07-31' -> '2026年7月31日 星期五' (falls back to raw string)."""
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", date)
    if not m:
        return date
    try:
        dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        return f"{dt.year}年{dt.month}月{dt.day}日 {WEEKDAYS_CN[dt.weekday()]}"
    except ValueError:
        return date


def _issue_no(date: str) -> str:
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", date)
    return f"NO.{m.group(1)}{m.group(2)}{m.group(3)}" if m else ""


def _valid_url(url: str) -> bool:
    return bool(url) and url != "#" and url.startswith(("http://", "https://"))


def get_all_briefings() -> list[dict]:
    """Scan output directory and return all briefings sorted by date (newest first)."""
    briefings = []
    if not OUTPUT_DIR.exists():
        return briefings
    for date_dir in sorted(OUTPUT_DIR.iterdir()):
        if not date_dir.is_dir():
            continue
        data_file = date_dir / "data.json"
        if not data_file.exists():
            continue
        data = {}
        try:
            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass
        briefings.append({
            "date": date_dir.name,
            "slug": _slug(date_dir.name),
            "date_cn": _fmt_date(date_dir.name),
            "issue_no": _issue_no(date_dir.name),
            "items": data.get("items", []),
            "highlights": data.get("highlights", []),
        })
    return list(reversed(briefings))


# ───────────────────────── shared CSS ─────────────────────────
CSS = '''<style>
:root {
    --bg: #F5F5F7;
    --card: #FFFFFF;
    --text: #1D1D1F;
    --text-2: #6E6E73;
    --text-3: #86868B;
    --accent: #0071E3;
    --accent-2: #5E5CE6;
    --hairline: rgba(0, 0, 0, 0.08);
    --hairline-soft: rgba(0, 0, 0, 0.05);
    --seg: #E8E8ED;
    --radius: 20px;
    --sans: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display",
            "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
    font-family: var(--sans);
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}
a { color: inherit; }
::selection { background: rgba(0, 113, 227, 0.18); }
:focus-visible { outline: 3px solid rgba(0, 113, 227, 0.5); outline-offset: 2px; border-radius: 6px; }

/* ── Top bar (frosted glass) ── */
.topbar {
    position: sticky; top: 0; z-index: 100;
    background: rgba(245, 245, 247, 0.72);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    border-bottom: 1px solid var(--hairline-soft);
}
.topbar-inner {
    max-width: 960px; margin: 0 auto;
    padding: 14px 28px;
    display: flex; align-items: center; justify-content: space-between; gap: 16px;
}
.brand { display: flex; align-items: center; gap: 10px; text-decoration: none; }
.brand img { width: 30px; height: 30px; border-radius: 8px; object-fit: cover; }
.brand-name { font-size: 17px; font-weight: 700; letter-spacing: 0.01em; }
.brand-sub { font-size: 12px; color: var(--text-3); }
.topbar-right { font-size: 13px; color: var(--text-2); display: flex; align-items: center; gap: 14px; }
.topbar-right a { text-decoration: none; color: var(--accent); }
.topbar-right a:hover { text-decoration: underline; }

/* ── Page frame ── */
.page { max-width: 960px; margin: 0 auto; padding: 0 28px 80px; }

/* ── Hero ── */
.hero { padding: 48px 0 12px; }
.eyebrow {
    font-size: 12px; font-weight: 600; letter-spacing: 0.22em;
    text-transform: uppercase; color: var(--text-3);
}
.hero-date {
    font-size: 44px; font-weight: 800; line-height: 1.1; letter-spacing: -0.02em;
    margin-top: 10px;
    background: linear-gradient(120deg, var(--accent), var(--accent-2));
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-meta { margin-top: 12px; font-size: 14px; color: var(--text-2); display: flex; gap: 18px; flex-wrap: wrap; }
.hero-meta .motto { color: var(--text-3); }

/* ── Section heading ── */
.section { padding: 32px 0 4px; }
.section-head {
    display: flex; align-items: baseline; justify-content: space-between; gap: 16px;
    margin-bottom: 18px;
}
.section-title { font-size: 22px; font-weight: 700; letter-spacing: -0.01em; }
.section-note { font-size: 13px; color: var(--text-3); }

/* ── Card (shared) ── */
.card {
    background: var(--card);
    border-radius: var(--radius);
    border: 1px solid var(--hairline-soft);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03), 0 8px 24px rgba(0, 0, 0, 0.04);
}

/* ── Highlights ── */
.lead {
    display: block; text-decoration: none; color: inherit;
    padding: 30px 30px 26px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.lead:hover { transform: translateY(-2px); box-shadow: 0 12px 32px rgba(0, 0, 0, 0.08); }
.lead .kicker {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 12px; font-weight: 600; letter-spacing: 0.06em;
}
.kicker .dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.lead h3 {
    font-size: 27px; font-weight: 800; line-height: 1.3; letter-spacing: -0.01em;
    margin: 14px 0 12px;
}
.lead p { font-size: 15px; color: var(--text-2); line-height: 1.75; max-width: 42em; }
.byline { margin-top: 18px; font-size: 13px; color: var(--text-3); display: flex; gap: 16px; flex-wrap: wrap; }
.heat { color: var(--accent); font-weight: 600; }

/* ── Briefs (sub-highlights) ── */
.briefs { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px; }
.brief {
    display: block; text-decoration: none; color: inherit;
    padding: 24px 24px 22px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.brief:hover { transform: translateY(-2px); box-shadow: 0 12px 32px rgba(0, 0, 0, 0.08); }
.brief .num {
    font-size: 13px; font-weight: 700; color: var(--accent);
    letter-spacing: 0.04em;
}
.brief h4 { font-size: 17px; font-weight: 700; line-height: 1.45; margin: 10px 0 8px; }
.brief p { font-size: 13.5px; color: var(--text-2); line-height: 1.7; }
.brief .byline { margin-top: 14px; font-size: 12px; }

/* ── Segmented control ── */
.seg {
    display: flex; gap: 2px; padding: 3px;
    background: var(--seg); border-radius: 11px;
    margin-bottom: 16px;
    overflow-x: auto;
}
.seg button {
    flex: 1 0 auto; white-space: nowrap;
    font-family: var(--sans); font-size: 13.5px; font-weight: 500;
    padding: 8px 16px; border: none; border-radius: 8px;
    background: transparent; color: var(--text-2); cursor: pointer;
    transition: background 0.15s, color 0.15s, box-shadow 0.15s;
}
.seg button:hover { color: var(--text); }
.seg button.active {
    background: var(--card); color: var(--text); font-weight: 600;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.12);
}

/* ── News list ── */
.news-list { padding: 8px 0; }
.news-item {
    display: block; text-decoration: none; color: inherit;
    padding: 18px 26px;
    border-bottom: 1px solid var(--hairline-soft);
    transition: background 0.15s;
}
.news-item:last-child { border-bottom: none; }
.news-item:hover { background: rgba(0, 0, 0, 0.02); }
.news-item .row { display: flex; align-items: center; gap: 10px; margin-bottom: 7px; }
.news-item .idx { font-size: 12px; font-weight: 700; color: var(--text-3); min-width: 2ch; }
.tag {
    font-size: 11px; font-weight: 600; letter-spacing: 0.04em;
    padding: 2px 10px 3px; border-radius: 999px;
}
.news-item h4 { font-size: 16.5px; font-weight: 600; line-height: 1.5; }
.news-item p { font-size: 13.5px; color: var(--text-2); line-height: 1.7; margin-top: 4px; }
.news-item .meta {
    margin-top: 8px; font-size: 12px; color: var(--text-3);
    display: flex; align-items: center; justify-content: space-between; gap: 12px;
}
.news-item .meta .src { display: inline-flex; align-items: center; gap: 6px; }
.news-item .more { color: var(--accent); opacity: 0; transition: opacity 0.15s; }
.news-item:hover .more { opacity: 1; }
.tab-empty { padding: 40px 20px; text-align: center; color: var(--text-3); font-size: 14px; }

/* ── Archive ── */
.archive-list { padding: 8px 0; }
.archive-row {
    display: flex; align-items: center; justify-content: space-between; gap: 16px;
    padding: 16px 26px; text-decoration: none; color: inherit;
    border-bottom: 1px solid var(--hairline-soft);
    transition: background 0.15s;
}
.archive-row:last-child { border-bottom: none; }
.archive-row:hover { background: rgba(0, 0, 0, 0.02); }
.archive-row .a-date { font-size: 15px; font-weight: 600; }
.archive-row .a-week { font-size: 13px; color: var(--text-3); }
.archive-row .a-right { display: flex; align-items: center; gap: 14px; }
.archive-row .a-count { font-size: 12px; color: var(--text-3); }
.archive-row .a-arrow { color: var(--accent); }

/* ── Footer ── */
.footer {
    margin-top: 56px; padding-top: 24px;
    border-top: 1px solid var(--hairline);
    display: flex; justify-content: space-between; flex-wrap: wrap; gap: 10px;
    font-size: 12.5px; color: var(--text-3);
}

/* ── Empty ── */
.empty { text-align: center; padding: 60px 20px; color: var(--text-3); font-size: 14px; }

/* ── Responsive ── */
@media (max-width: 700px) {
    .page { padding: 0 16px 60px; }
    .topbar-inner { padding: 12px 16px; }
    .hero { padding: 36px 0 8px; }
    .hero-date { font-size: 34px; }
    .briefs { grid-template-columns: 1fr; }
    .lead { padding: 22px 20px 20px; }
    .lead h3 { font-size: 22px; }
    .brief { padding: 20px 20px 18px; }
    .news-item { padding: 16px 20px; }
    .archive-row { padding: 14px 20px; }
}
</style>'''


# ───────────────────────── shared JS ─────────────────────────
PAGE_JS = '''<script>
// Section tabs: filter the news list by 资讯类型 (vanilla, always on).
(function () {
    const seg = document.getElementById("news-seg");
    if (!seg) return;
    const items = document.querySelectorAll("#news-list .news-item");
    const emptyEl = document.getElementById("news-empty");
    seg.addEventListener("click", (e) => {
        const btn = e.target.closest("button");
        if (!btn) return;
        seg.querySelectorAll("button").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        const sec = btn.dataset.sec;
        let shown = 0;
        items.forEach((it) => {
            const match = sec === "all" || it.dataset.section === sec;
            it.style.display = match ? "" : "none";
            if (match) shown++;
        });
        if (emptyEl) emptyEl.hidden = shown !== 0;
    });
})();
</script>'''


# ───────────────────────── HTML builders ─────────────────────────

def _item_parts(item: dict) -> dict:
    title = _esc(item.get("title", ""))
    summary = item.get("brief") or item.get("summary", "")
    summary = _esc(summary[:120] + ("..." if len(summary) > 120 else ""))
    return {
        "url": item.get("url", ""),
        "title": title,
        "summary": summary,
        "source": _esc(item.get("source_name", "")),
        "cat": _esc(item.get("category", "其他")),
        "cat_color": item.get("category_color", "#0071E3"),
        "pub": _esc(item.get("published_at", "")[:10]),
        "heat": item.get("sources_count", 1),
        "linked": _valid_url(item.get("url", "")),
    }


def _heat_html(p: dict) -> str:
    """Cross-platform attention badge: only shown when 2+ sources covered the story."""
    if p["heat"] > 1:
        return f'<span class="heat">◆ {p["heat"]} 家报道</span>'
    return ""


def _tag_html(p: dict) -> str:
    return f'<span class="tag" style="color:{p["cat_color"]};background:{p["cat_color"]}1a">{p["cat"]}</span>'


def _byline_html(p: dict, extra: str = "") -> str:
    return f'<div class="byline"><span>{p["source"]} · {p["pub"]}</span>{_heat_html(p)}{extra}</div>'


def _news_item_html(item: dict, idx: int) -> str:
    p = _item_parts(item)
    sec = section_of_category(item.get("category_id", ""))
    tag, attrs = ("a", f'href="{_esc(p["url"])}" target="_blank" rel="noopener"') if p["linked"] else ("article", "")
    more = '<span class="more">阅读原文 →</span>' if p["linked"] else ""
    return f'''
    <{tag} {attrs} class="news-item" data-section="{sec}">
        <div class="row"><span class="idx">{idx:02d}</span>{_tag_html(p)}</div>
        <h4>{p['title']}</h4>
        {f'<p>{p["summary"]}</p>' if p["summary"] else ""}
        <div class="meta"><span class="src">{p['source']} · {p['pub']}</span>{_heat_html(p)}{more}</div>
    </{tag}>'''


def _lead_html(item: dict) -> str:
    p = _item_parts(item)
    tag, attrs = ("a", f'href="{_esc(p["url"])}" target="_blank" rel="noopener"') if p["linked"] else ("article", "")
    return f'''
    <{tag} {attrs} class="lead card">
        <span class="kicker"><span class="dot" style="background:{p['cat_color']}"></span>头条 · {p['cat']}</span>
        <h3>{p['title']}</h3>
        {f'<p>{p["summary"]}</p>' if p["summary"] else ""}
        {_byline_html(p)}
    </{tag}>'''


def _brief_html(item: dict, num: int) -> str:
    p = _item_parts(item)
    tag, attrs = ("a", f'href="{_esc(p["url"])}" target="_blank" rel="noopener"') if p["linked"] else ("article", "")
    return f'''
    <{tag} {attrs} class="brief card">
        <span class="num">{num:02d}</span>
        <h4>{p['title']}</h4>
        {f'<p>{p["summary"]}</p>' if p["summary"] else ""}
        {_byline_html(p)}
    </{tag}>'''


def _highlights_section(highlights: list[dict]) -> str:
    if not highlights:
        return ""
    lead = _lead_html(highlights[0])
    briefs = "\n".join(_brief_html(it, i + 2) for i, it in enumerate(highlights[1:3]))
    briefs_html = f'<div class="briefs">{briefs}</div>' if briefs else ""
    return f'''
    <section class="section">
        <div class="section-head">
            <h2 class="section-title">今日看点</h2>
            <span class="section-note">Headlines</span>
        </div>
        {lead}
        {briefs_html}
    </section>'''


def _news_section(items: list[dict]) -> str:
    if not items:
        return ""
    counts = {}
    for it in items:
        sec = section_of_category(it.get("category_id", ""))
        counts[sec] = counts.get(sec, 0) + 1
    tabs = [f'<button class="active" data-sec="all">全部 · {len(items)}</button>']
    for sec_id, sec_name in SECTIONS:
        tabs.append(f'<button data-sec="{sec_id}">{sec_name} · {counts.get(sec_id, 0)}</button>')
    cards = "\n".join(_news_item_html(it, i + 1) for i, it in enumerate(items))
    return f'''
    <section class="section">
        <div class="section-head">
            <h2 class="section-title">全部资讯</h2>
            <span class="section-note">{len(items)} 条 · All Stories</span>
        </div>
        <div class="seg" id="news-seg">{''.join(tabs)}</div>
        <div class="card news-list" id="news-list">{cards}
        </div>
        <div class="tab-empty" id="news-empty" hidden>本栏目今日暂无资讯</div>
    </section>'''


def _archive_section(history: list[dict]) -> str:
    if not history:
        return ""
    rows = ""
    for b in history:
        rows += f'''
        <a href="./{b['slug']}/" class="archive-row">
            <span class="a-date">{_esc(b['date'][:10])}</span>
            <span class="a-week">{_esc(b['date_cn'].split(' ')[-1])}</span>
            <span class="a-right"><span class="a-count">{len(b.get('items', []))} 条</span><span class="a-arrow">→</span></span>
        </a>'''
    return f'''
    <section class="section">
        <div class="section-head">
            <h2 class="section-title">往期存档</h2>
            <span class="section-note">{len(history)} 期 · Archive</span>
        </div>
        <div class="card archive-list">{rows}
        </div>
    </section>'''


def _hero(date_cn: str, issue_no: str) -> str:
    date_str, _, weekday = date_cn.partition(" ")
    return f'''
    <section class="hero">
        <div class="eyebrow">Mitong AI Daily Briefing</div>
        <h1 class="hero-date">{date_str}</h1>
        <div class="hero-meta">
            <span>{weekday}</span>
            <span>{issue_no}</span>
            <span class="motto">每日精选 · 十秒速览</span>
        </div>
    </section>'''


def _page_shell(title: str, body: str, prefix: str = "./", home_href: str = "./", right_html: str = "") -> str:
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="{prefix}icon.jpg" type="image/jpeg">
    <title>{title}</title>
    {CSS}
</head>
<body>
    <header class="topbar">
        <div class="topbar-inner">
            <a href="{home_href}" class="brand">
                <img src="{prefix}icon.jpg" alt="米桶">
                <span class="brand-name">米桶 AI 早报</span>
            </a>
            <span class="topbar-right">{right_html}</span>
        </div>
    </header>

    <div class="page">
{body}
    </div>

    <footer class="footer">
        <span>米桶 AI 早报 · 仅供信息参考，不构成任何建议</span>
        <span>机器之心 / 量子位 / 36氪 / BBC / FT / 华尔街见闻</span>
    </footer>

{PAGE_JS}
</body>
</html>'''


def _detail_page_html(b: dict) -> str:
    """Archive page for one date, at website/cn/<slug>/index.html."""
    items = b.get("items", [])
    highlights = b.get("highlights") or items[:3]
    body = f'''
    {_hero(b["date_cn"], b["issue_no"])}
    {_highlights_section(highlights)}
    {_news_section(items)}
    {'' if items else '<div class="empty">当日暂无资讯记录</div>'}'''
    return _page_shell(f"{b['date'][:10]} · 米桶 AI 早报", body, prefix="../../",
                       home_href="../../", right_html='<a href="../../">← 返回首页</a>')


def _home_page_html(latest: dict, history: list[dict]) -> str:
    items = latest.get("items", [])
    highlights = latest.get("highlights") or items[:3]
    body = f'''
    {_hero(latest["date_cn"], latest["issue_no"])}
    {_highlights_section(highlights)}
    {_news_section(items)}
    {_archive_section(history)}
    {'' if items else '<div class="empty">暂无资讯，敬请期待</div>'}'''
    return _page_shell("米桶 AI 早报", body)


# ───────────────────────── entry point ─────────────────────────

def generate_website():
    briefings = get_all_briefings()
    if not briefings:
        print("No briefings found.")
        return

    WEB_DIR.mkdir(parents=True, exist_ok=True)

    # Detail (archive) pages
    for b in briefings:
        detail_dir = WEB_DIR / b["slug"]
        detail_dir.mkdir(exist_ok=True)
        (detail_dir / "index.html").write_text(_detail_page_html(b), encoding="utf-8")
        print(f"  Archive page: {detail_dir}/index.html")

    # Home page
    latest = briefings[0]
    (WEB_DIR / "index.html").write_text(
        _home_page_html(latest, briefings[1:]), encoding="utf-8")

    print(f"✅ Website generated: {WEB_DIR}/index.html")
    print(f"   Briefings: {len(briefings)} · Latest: {latest['date']} · Items: {len(latest.get('items', []))}")


if __name__ == "__main__":
    generate_website()
