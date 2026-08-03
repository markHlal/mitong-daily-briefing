"""Generate a responsive website with card-based news layout and GSAP animations."""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
WEB_DIR = PROJECT_ROOT / "website"

# ── Category gradient backgrounds (when no image available) ──
CAT_GRADIENTS = {
    "Agent": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    "模型": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
    "产业": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
    "算力": "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
    "安全": "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
    "其他": "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",
}

CAT_ICONS = {
    "Agent": "🤖",
    "模型": "🧠",
    "产业": "💼",
    "算力": "⚡",
    "安全": "🔒",
    "其他": "📰",
}


def get_all_briefings() -> list[dict]:
    """Scan output directory and return all briefings sorted by date."""
    briefings = []
    for date_dir in sorted(OUTPUT_DIR.iterdir()):
        if not date_dir.is_dir():
            continue
        data_file = date_dir / "data.json"
        detail_img = date_dir / "detail.png"
        highlights_img = date_dir / "highlights.png"
        if data_file.exists() or detail_img.exists():
            data = {}
            if data_file.exists():
                try:
                    with open(data_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    pass
            briefings.append({
                "date": date_dir.name,
                "date_key": data.get("date_key", date_dir.name),
                "items": data.get("items", []),
                "highlights": data.get("highlights", []),
                "detail_image": str(detail_img.relative_to(PROJECT_ROOT)) if detail_img.exists() else None,
                "highlights_image": str(highlights_img.relative_to(PROJECT_ROOT)) if highlights_img.exists() else None,
            })
    return list(reversed(briefings))


# ── Shared CSS ──
CSS = '''<style>
:root {
    --bg: #F5F7FA;
    --surface: #FFFFFF;
    --text: #1D1D1F;
    --text-secondary: #6E6E73;
    --text-tertiary: #86868B;
    --blue: #0071E3;
    --blue-light: #E8F4FD;
    --border: rgba(0,0,0,0.06);
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.02);
    --shadow: 0 4px 24px rgba(0,0,0,0.06);
    --shadow-lg: 0 12px 40px rgba(0,0,0,0.1);
    --radius-sm: 12px;
    --radius: 20px;
    --radius-lg: 28px;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "PingFang SC", "Microsoft YaHei", sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Header */
.header {
    position: fixed; top: 0; left: 0; right: 0;
    background: rgba(255,255,255,0.72);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    border-bottom: 1px solid var(--border);
    padding: 14px 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 100;
    transition: background 0.3s;
}
.header-brand {
    font-size: 20px;
    font-weight: 600;
    color: var(--blue);
    text-decoration: none;
    letter-spacing: -0.3px;
}
.header-sub { font-size: 12px; color: var(--text-tertiary); margin-left: 4px; font-weight: 400; }
.header-back {
    color: var(--blue);
    text-decoration: none;
    font-size: 15px;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 100px;
    transition: background 0.2s;
}
.header-back:hover { background: var(--blue-light); }

/* Hero */
.hero {
    max-width: 1100px;
    margin: 0 auto;
    padding: 130px 24px 40px;
    text-align: center;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--surface);
    border: 1px solid var(--border);
    padding: 8px 20px;
    border-radius: 100px;
    font-size: 14px;
    color: var(--text-secondary);
    margin-bottom: 28px;
    box-shadow: var(--shadow-sm);
}
.hero-badge .dot {
    width: 8px; height: 8px;
    background: #34C759;
    border-radius: 50%;
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
.hero h1 {
    font-size: 48px;
    font-weight: 700;
    letter-spacing: -1.2px;
    line-height: 1.1;
    margin-bottom: 14px;
    background: linear-gradient(135deg, #1D1D1F 0%, #434344 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub { font-size: 20px; color: var(--text-secondary); font-weight: 400; margin-bottom: 8px; }
.hero-date { font-size: 15px; color: var(--text-tertiary); font-weight: 500; }

/* Section */
.section { max-width: 1100px; margin: 0 auto 64px; padding: 0 24px; }
.section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 28px;
}
.section-title {
    font-size: 24px;
    font-weight: 600;
    letter-spacing: -0.5px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.section-title::before {
    content: "";
    width: 4px; height: 24px;
    background: var(--blue);
    border-radius: 2px;
}
.section-count {
    font-size: 13px;
    color: var(--text-tertiary);
    background: var(--surface);
    padding: 4px 12px;
    border-radius: 100px;
    border: 1px solid var(--border);
}

/* ── News Cards Grid ── */
.news-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
}
@media (max-width: 1024px) {
    .news-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 640px) {
    .news-grid { grid-template-columns: 1fr; gap: 16px; }
    .header { padding: 12px 20px; }
    .hero { padding: 110px 20px 32px; }
    .hero h1 { font-size: 36px; }
    .hero-sub { font-size: 18px; }
    .section { padding: 0 16px; margin-bottom: 48px; }
}

/* News Card */
.news-card {
    background: var(--surface);
    border-radius: var(--radius);
    overflow: hidden;
    box-shadow: var(--shadow-sm);
    transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.35s ease;
    text-decoration: none;
    color: inherit;
    display: flex;
    flex-direction: column;
    height: 100%;
    will-change: transform;
}
.news-card:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-lg);
}
.card-image {
    position: relative;
    width: 100%;
    aspect-ratio: 16/10;
    overflow: hidden;
    background: #E8E8ED;
}
.card-image img {
    width: 100%; height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
.news-card:hover .card-image img { transform: scale(1.06); }
.card-image .placeholder {
    width: 100%; height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 48px;
}
.card-category {
    position: absolute;
    top: 12px; left: 12px;
    font-size: 11px;
    font-weight: 600;
    padding: 5px 12px;
    border-radius: 100px;
    background: rgba(255,255,255,0.92);
    backdrop-filter: blur(10px);
    color: var(--text);
    letter-spacing: 0.3px;
    text-transform: uppercase;
}
.card-body {
    padding: 18px 20px 20px;
    display: flex;
    flex-direction: column;
    flex: 1;
}
.card-title {
    font-size: 16px;
    font-weight: 600;
    line-height: 1.45;
    margin-bottom: 8px;
    letter-spacing: -0.2px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.card-summary {
    font-size: 13.5px;
    color: var(--text-secondary);
    line-height: 1.6;
    margin-bottom: 14px;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    flex: 1;
}
.card-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: auto;
    padding-top: 12px;
    border-top: 1px solid var(--border);
}
.card-source {
    font-size: 12px;
    color: var(--text-tertiary);
    font-weight: 500;
}
.card-time {
    font-size: 12px;
    color: var(--text-tertiary);
}

/* ── Highlights Section (top 3) ── */
.highlights-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
}
@media (max-width: 1024px) {
    .highlights-grid { grid-template-columns: 1fr; }
}
.highlight-card {
    background: var(--surface);
    border-radius: var(--radius-lg);
    overflow: hidden;
    box-shadow: var(--shadow);
    transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.35s ease;
    text-decoration: none;
    color: inherit;
    display: flex;
    flex-direction: column;
    cursor: pointer;
}
.highlight-card:hover {
    transform: translateY(-6px);
    box-shadow: var(--shadow-lg);
}
.highlight-card .card-image { aspect-ratio: 16/9; }
.highlight-card .card-body { padding: 22px 24px 24px; }
.highlight-card .card-title { font-size: 18px; }
.highlight-card .card-summary { font-size: 14px; -webkit-line-clamp: 4; }

/* ── Old Image Cards (for legacy images) ── */
.image-card-lg {
    background: var(--surface);
    border-radius: var(--radius-lg);
    overflow: hidden;
    box-shadow: var(--shadow);
    margin-bottom: 28px;
    transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.35s ease;
    cursor: pointer;
    max-width: 500px;
    margin-left: auto;
    margin-right: auto;
}
.image-card-lg:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-lg);
}
.image-card-lg img {
    width: 100%;
    display: block;
    max-height: 70vh;
    object-fit: contain;
    background: #f0f0f2;
}
.image-card-lg .label {
    padding: 16px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* ── History Section ── */
.history-section { max-width: 1100px; margin: 0 auto 80px; padding: 0 24px; }
.history-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
}
@media (max-width: 1024px) {
    .history-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 768px) {
    .history-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 480px) {
    .history-grid { grid-template-columns: 1fr; }
}
.history-item {
    background: var(--surface);
    border-radius: var(--radius);
    overflow: hidden;
    box-shadow: var(--shadow-sm);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    text-decoration: none;
    color: inherit;
}
.history-item:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow);
}
.history-item img {
    width: 100%;
    aspect-ratio: 16/10;
    object-fit: cover;
    display: block;
}
.history-item .info { padding: 14px 16px; }
.history-item .date { font-size: 15px; font-weight: 600; margin-bottom: 4px; }
.history-item .meta { font-size: 12px; color: var(--text-tertiary); }

/* Empty */
.empty {
    text-align: center;
    padding: 80px 20px;
    color: var(--text-tertiary);
}
.empty-icon { font-size: 48px; margin-bottom: 12px; opacity: 0.5; }

/* Lightbox */
.lightbox {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.94);
    z-index: 200;
    justify-content: center;
    align-items: center;
    padding: 20px;
    opacity: 0;
    transition: opacity 0.3s ease;
}
.lightbox.show { display: flex; }
.lightbox.active { opacity: 1; }
.lightbox img {
    max-width: 100%;
    max-height: 90vh;
    border-radius: 16px;
    box-shadow: 0 24px 80px rgba(0,0,0,0.5);
    transform: scale(0.92);
    transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.lightbox.active img { transform: scale(1); }
.lightbox .close {
    position: absolute;
    top: 20px; right: 28px;
    font-size: 32px;
    color: rgba(255,255,255,0.8);
    cursor: pointer;
    width: 44px; height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: rgba(255,255,255,0.1);
    transition: all 0.2s;
    z-index: 10;
}
.lightbox .close:hover { background: rgba(255,255,255,0.25); color: white; }

/* Footer */
.footer {
    text-align: center;
    padding: 48px 20px;
    color: var(--text-tertiary);
    font-size: 13px;
    border-top: 1px solid var(--border);
    line-height: 1.8;
}
</style>'''


# ── Shared JS ──
LIGHTBOX_JS = '''<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script>
gsap.registerPlugin(ScrollTrigger);

// Hero entrance
const heroTl = gsap.timeline({defaults: {ease: "power3.out", duration: 0.8}});
heroTl
    .from(".hero-badge", {y: 20, opacity: 0, duration: 0.6})
    .from(".hero h1", {y: 40, opacity: 0, duration: 1}, "-=0.3")
    .from(".hero-sub", {y: 20, opacity: 0}, "-=0.6")
    .from(".hero-date", {y: 15, opacity: 0}, "-=0.5")
    .from(".section-title", {y: 20, opacity: 0}, "-=0.4");

// Cards stagger entrance
gsap.from(".news-card, .highlight-card", {
    y: 50,
    opacity: 0,
    duration: 0.8,
    stagger: 0.08,
    ease: "power3.out",
    delay: 0.3
});

// History items scroll trigger
gsap.utils.toArray(".history-item").forEach((item, i) => {
    gsap.from(item, {
        scrollTrigger: {
            trigger: item,
            start: "top 90%",
            toggleActions: "play none none none",
        },
        y: 30,
        opacity: 0,
        duration: 0.6,
        delay: i * 0.05,
        ease: "power3.out"
    });
});

// Image lazy load
document.querySelectorAll("img[data-src]").forEach(img => {
    const src = img.dataset.src;
    if (!src) return;
    const temp = new Image();
    temp.onload = () => { img.src = src; img.classList.add("loaded"); };
    temp.onerror = () => { img.style.display = "none"; };
    temp.src = src;
});

// Lightbox
const lb = document.getElementById("lightbox");
const lbImg = document.getElementById("lightbox-img");
function openLightbox(src) {
    lbImg.src = src;
    lb.classList.add("show");
    document.body.style.overflow = "hidden";
    requestAnimationFrame(() => lb.classList.add("active"));
}
function closeLightbox(e) {
    if (e.target === e.currentTarget || e.target.classList.contains("close")) {
        lb.classList.remove("active");
        setTimeout(() => { lb.classList.remove("show"); lbImg.src = ""; document.body.style.overflow = ""; }, 300);
    }
}
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && lb.classList.contains("show")) {
        lb.classList.remove("active");
        setTimeout(() => { lb.classList.remove("show"); lbImg.src = ""; document.body.style.overflow = ""; }, 300);
    }
});

// Header blur on scroll
window.addEventListener("scroll", () => {
    const h = document.querySelector(".header");
    h.style.background = window.scrollY > 10 ? "rgba(255,255,255,0.92)" : "rgba(255,255,255,0.72)";
});
</script>'''


def _card_html(item: dict, is_highlight: bool = False) -> str:
    """Generate a single news card HTML."""
    url = item.get("url", "#")
    title = item.get("title", "")
    summary = item.get("brief") or item.get("summary", "")[:120]
    if len(summary) > 120:
        summary = summary[:117] + "..."
    source = item.get("source_name", "")
    cat = item.get("category", "其他")
    cat_color = item.get("category_color", "#8E8E93")
    image_url = item.get("image_url", "")
    pub = item.get("published_at", "")[:10]

    card_class = "highlight-card" if is_highlight else "news-card"

    # Image section
    if image_url:
        img_html = f'<div class="card-image"><img src="{image_url}" alt="{title}" loading="lazy" onerror="this.style.display=\'none\';this.parentElement.querySelector(\'.placeholder\').style.display=\'flex\'"><div class="placeholder" style="display:none;background:{CAT_GRADIENTS.get(cat, CAT_GRADIENTS['其他'])};position:absolute;inset:0;align-items:center;justify-content:center;font-size:48px;">{CAT_ICONS.get(cat, "📰")}</div><span class="card-category" style="color:{cat_color}">{cat}</span></div>'
    else:
        icon = CAT_ICONS.get(cat, "📰")
        gradient = CAT_GRADIENTS.get(cat, CAT_GRADIENTS["其他"])
        img_html = f'<div class="card-image"><div class="placeholder" style="background:{gradient}">{icon}</div><span class="card-category" style="color:{cat_color}">{cat}</span></div>'

    return f'''
    <a href="{url}" target="_blank" rel="noopener" class="{card_class}">
        {img_html}
        <div class="card-body">
            <h3 class="card-title">{title}</h3>
            <p class="card-summary">{summary}</p>
            <div class="card-footer">
                <span class="card-source">{source}</span>
                <span class="card-time">{pub}</span>
            </div>
        </div>
    </a>'''


def _detail_page_html(b: dict) -> str:
    """Generate detail page for a specific date."""
    date = b["date"]
    items = b.get("items", [])
    highlights = b.get("highlights", items[:3]) if items else []

    # Highlights cards
    hl_cards = ""
    if highlights:
        hl_cards = '\n'.join(_card_html(item, is_highlight=True) for item in highlights)

    # All items cards
    all_cards = ""
    if items:
        all_cards = '\n'.join(_card_html(item) for item in items)

    # Legacy images
    legacy = ""
    if b.get("detail_image"):
        legacy += f'''
        <div class="image-card-lg" onclick="openLightbox('./{b['detail_image']}')">
            <img src="./{b['detail_image']}" alt="详细版">
            <div class="label"><span class="label-text">详细版海报</span></div>
        </div>'''

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{date} · 米桶 AI 早报</title>
    {CSS}
</head>
<body>
    <header class="header">
        <a href="./" class="header-brand">米桶 AI <span class="header-sub">Daily Brief</span></a>
        <a href="./" class="header-back">← 返回首页</a>
    </header>

    <section class="hero">
        <div class="hero-badge"><span class="dot"></span>每日更新</div>
        <h1>AI 早报</h1>
        <p class="hero-sub">每日精选 · 10 秒速览</p>
        <p class="hero-date">📅 {date}</p>
    </section>

    {f'<section class="section"><div class="section-header"><h2 class="section-title">今日看点</h2></div><div class="highlights-grid">{hl_cards}</div></section>' if hl_cards else ''}

    {f'<section class="section"><div class="section-header"><h2 class="section-title">全部资讯</h2><span class="section-count">{len(items)} 条</span></div><div class="news-grid">{all_cards}</div></section>' if all_cards else ''}

    {f'<section class="section"><div class="section-header"><h2 class="section-title">历史海报</h2></div>{legacy}</section>' if legacy else ''}

    <footer class="footer">
        米桶 AI · 不构成任何建议，仅供信息参考<br>
        自动采集自机器之心、量子位、36氪等信源
    </footer>

    <div class="lightbox" id="lightbox" onclick="closeLightbox(event)">
        <span class="close">&times;</span>
        <img src="" alt="大图" id="lightbox-img">
    </div>

{LIGHTBOX_JS}
</body>
</html>'''


def _home_page_html(latest: dict, history: list[dict]) -> str:
    """Generate home page with latest news and history."""
    date = latest["date"]
    items = latest.get("items", [])
    highlights = latest.get("highlights", items[:3]) if items else []

    # Highlights
    hl_section = ""
    if highlights:
        hl_cards = '\n'.join(_card_html(item, is_highlight=True) for item in highlights)
        hl_section = f'''
    <section class="section">
        <div class="section-header">
            <h2 class="section-title">今日看点</h2>
        </div>
        <div class="highlights-grid">
            {hl_cards}
        </div>
    </section>'''

    # All items
    all_section = ""
    if items:
        all_cards = '\n'.join(_card_html(item) for item in items)
        all_section = f'''
    <section class="section">
        <div class="section-header">
            <h2 class="section-title">全部资讯</h2>
            <span class="section-count">{len(items)} 条</span>
        </div>
        <div class="news-grid">
            {all_cards}
        </div>
    </section>'''

    # Legacy images
    legacy_section = ""
    if latest.get("detail_image") or latest.get("highlights_image"):
        legacy_cards = ""
        if latest.get("detail_image"):
            legacy_cards += f'''
        <div class="image-card-lg" onclick="openLightbox('./{latest['detail_image']}')">
            <img src="./{latest['detail_image']}" alt="详细版">
            <div class="label"><span class="label-text">📱 详细版海报</span></div>
        </div>'''
        if latest.get("highlights_image"):
            legacy_cards += f'''
        <div class="image-card-lg" onclick="openLightbox('./{latest['highlights_image']}')">
            <img src="./{latest['highlights_image']}" alt="今日看点">
            <div class="label"><span class="label-text">🎯 今日看点海报</span></div>
        </div>'''
        legacy_section = f'''
    <section class="section">
        <div class="section-header">
            <h2 class="section-title">每日海报</h2>
        </div>
        {legacy_cards}
    </section>'''

    # History
    hist_section = ""
    if history:
        hist_items = ""
        for b in history:
            thumb = None
            if b.get("highlights_image"):
                thumb = b["highlights_image"]
            elif b.get("detail_image"):
                thumb = b["detail_image"]
            elif b.get("items") and b["items"][0].get("image_url"):
                thumb = b["items"][0]["image_url"]

            date_slug = b["date"].replace(" ", "_").replace(".", "-")
            img_tag = f'<img src="./{thumb}" alt="{b['date']}" loading="lazy">' if thumb else f'<div style="width:100%;aspect-ratio:16/10;background:linear-gradient(135deg,#667eea,#764ba2);display:flex;align-items:center;justify-content:center;font-size:32px;">📰</div>'
            hist_items += f'''
            <a href="./{date_slug}/" class="history-item">
                {img_tag}
                <div class="info">
                    <div class="date">{b['date']}</div>
                    <div class="meta">{len(b.get('items', []))} 条资讯</div>
                </div>
            </a>'''
        hist_section = f'''
    <section class="history-section">
        <div class="section-header">
            <h2 class="section-title">历史记录</h2>
            <span class="section-count">{len(history)} 期</span>
        </div>
        <div class="history-grid">
            {hist_items}
        </div>
    </section>'''

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>米桶 AI 早报</title>
    {CSS}
</head>
<body>
    <header class="header">
        <a href="./" class="header-brand">米桶 AI <span class="header-sub">Daily Brief</span></a>
        <span style="color: var(--text-tertiary); font-size: 14px; font-weight: 500;">每日资讯早报</span>
    </header>

    <section class="hero">
        <div class="hero-badge"><span class="dot"></span>每日更新</div>
        <h1>AI 早报</h1>
        <p class="hero-sub">每日精选 · 10 秒速览</p>
        <p class="hero-date">📅 {date}</p>
    </section>

    {hl_section}
    {all_section}
    {legacy_section}
    {hist_section}

    <footer class="footer">
        米桶 AI · 不构成任何建议，仅供信息参考<br>
        自动采集自机器之心、量子位、36氪等信源
    </footer>

    <div class="lightbox" id="lightbox" onclick="closeLightbox(event)">
        <span class="close">&times;</span>
        <img src="" alt="大图" id="lightbox-img">
    </div>

{LIGHTBOX_JS}
</body>
</html>'''


def generate_website():
    briefings = get_all_briefings()
    if not briefings:
        print("No briefings found.")
        return

    WEB_DIR.mkdir(exist_ok=True)
    latest = briefings[0]
    history = briefings[1:]

    # Generate detail pages
    for b in briefings:
        date_slug = b["date"].replace(" ", "_").replace(".", "-")
        detail_dir = WEB_DIR / date_slug
        detail_dir.mkdir(exist_ok=True)
        (detail_dir / "index.html").write_text(_detail_page_html(b), encoding="utf-8")
        print(f"  Detail page: {detail_dir}/index.html")

    # Generate home page
    home_html = _home_page_html(latest, history)
    (WEB_DIR / "index.html").write_text(home_html, encoding="utf-8")

    print(f"✅ Website generated: {WEB_DIR}/index.html")
    print(f"   Total briefings: {len(briefings)}")
    print(f"   Detail pages: {len(briefings)}")
    print(f"   Latest: {latest['date']}")
    print(f"   Items: {len(latest.get('items', []))}")
    print(f"   History: {len(history)} days")


if __name__ == "__main__":
    generate_website()
