"""Generate a static website with GSAP animations and polished Apple-style design."""

from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
WEB_DIR = PROJECT_ROOT / "website"

def get_all_briefings() -> list[dict]:
    """Scan output directory, merge same-day detail+highlights, return sorted briefings."""
    from collections import defaultdict
    merged = defaultdict(lambda: {"detail": False, "highlights": False,
                                   "detail_path": None, "highlights_path": None})

    for date_dir in sorted(OUTPUT_DIR.iterdir()):
        if not date_dir.is_dir():
            continue
        date_key = date_dir.name.split()[0]
        detail = date_dir / "detail.png"
        highlights = date_dir / "highlights.png"
        if detail.exists():
            merged[date_key]["detail"] = True
            merged[date_key]["detail_path"] = str(detail.relative_to(PROJECT_ROOT))
        if highlights.exists():
            merged[date_key]["highlights"] = True
            merged[date_key]["highlights_path"] = str(highlights.relative_to(PROJECT_ROOT))

    briefings = []
    for date_key in sorted(merged.keys(), reverse=True):
        b = merged[date_key]
        briefings.append({"date": date_key, **b})
    return briefings

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
    --radius-sm: 16px;
    --radius: 24px;
    --radius-lg: 32px;
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
    max-width: 860px;
    margin: 0 auto;
    padding: 140px 24px 60px;
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
    margin-bottom: 32px;
    box-shadow: var(--shadow-sm);
}
.hero-badge .dot {
    width: 8px; height: 8px;
    background: #34C759;
    border-radius: 50%;
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}
.hero h1 {
    font-size: 56px;
    font-weight: 700;
    letter-spacing: -1.5px;
    line-height: 1.1;
    margin-bottom: 16px;
    background: linear-gradient(135deg, #1D1D1F 0%, #434344 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 21px;
    color: var(--text-secondary);
    font-weight: 400;
    margin-bottom: 8px;
}
.hero-date {
    font-size: 15px;
    color: var(--text-tertiary);
    font-weight: 500;
}

/* Section */
.section {
    max-width: 860px;
    margin: 0 auto 64px;
    padding: 0 24px;
}
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

/* Image Card */
.image-card {
    background: var(--surface);
    border-radius: var(--radius-lg);
    overflow: hidden;
    box-shadow: var(--shadow);
    margin-bottom: 28px;
    transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.4s ease;
    will-change: transform;
    cursor: pointer;
}
.image-card:hover {
    transform: translateY(-6px) scale(1.005);
    box-shadow: var(--shadow-lg);
}
.image-card img {
    width: 100%;
    display: block;
    opacity: 1;
}
.image-card.animate-in img {
    opacity: 0;
    animation: imgFadeIn 0.8s ease forwards;
}
@keyframes imgFadeIn {
    to { opacity: 1; }
}
    width: 100%;
    display: block;
    opacity: 0;
    transition: opacity 0.6s ease;
}
.image-card .label {
    padding: 18px 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.label-text { font-size: 15px; color: var(--text-secondary); font-weight: 500; }
.label-tag {
    font-size: 12px;
    font-weight: 600;
    padding: 5px 14px;
    border-radius: 100px;
    background: var(--blue-light);
    color: var(--blue);
    letter-spacing: 0.3px;
}

/* History */
.history-section { max-width: 1200px; margin: 0 auto 80px; padding: 0 24px; }
.history-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 24px;
}
.history-card {
    background: var(--surface);
    border-radius: var(--radius);
    overflow: hidden;
    box-shadow: var(--shadow-sm);
    transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.4s ease;
    text-decoration: none;
    color: inherit;
    will-change: transform;
    opacity: 0;
    transform: translateY(30px);
}
.history-card.visible {
    opacity: 1;
    transform: translateY(0);
}
.history-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}
.history-card .thumb-wrap {
    position: relative;
    overflow: hidden;
    aspect-ratio: 16/10;
}
.history-card .thumb-wrap img {
    width: 100%; height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
.history-card:hover .thumb-wrap img { transform: scale(1.05); }
.history-card .overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.5) 0%, transparent 50%);
    opacity: 0;
    transition: opacity 0.3s;
}
.history-card:hover .overlay { opacity: 1; }
.history-card .info {
    padding: 20px 22px;
}
.history-card .date {
    font-size: 17px;
    font-weight: 600;
    margin-bottom: 6px;
    letter-spacing: -0.3px;
}
.history-card .meta {
    font-size: 13px;
    color: var(--text-tertiary);
    display: flex;
    align-items: center;
    gap: 6px;
}

/* Empty */
.empty {
    text-align: center;
    padding: 100px 20px;
    color: var(--text-tertiary);
}
.empty-icon { font-size: 56px; margin-bottom: 16px; opacity: 0.6; }
.empty p { font-size: 16px; }

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
    transform: scale(0.9);
    transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.lightbox.active img { transform: scale(1); }
.lightbox .close {
    position: absolute;
    top: 20px;
    right: 28px;
    font-size: 36px;
    color: rgba(255,255,255,0.8);
    cursor: pointer;
    width: 44px; height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: rgba(255,255,255,0.1);
    transition: background 0.2s, color 0.2s;
    z-index: 10;
}
.lightbox .close:hover { background: rgba(255,255,255,0.2); color: white; }

/* Footer */
.footer {
    text-align: center;
    padding: 48px 20px;
    color: var(--text-tertiary);
    font-size: 13px;
    border-top: 1px solid var(--border);
    margin-top: 40px;
    line-height: 1.8;
}

/* Responsive */
@media (max-width: 768px) {
    .header { padding: 12px 20px; }
    .hero { padding: 110px 20px 40px; }
    .hero h1 { font-size: 38px; }
    .hero-sub { font-size: 18px; }
    .section { padding: 0 20px; margin-bottom: 48px; }
    .history-section { padding: 0 20px; }
    .history-grid { grid-template-columns: 1fr; gap: 16px; }
    .image-card { border-radius: var(--radius); }
    .image-card .label { padding: 14px 20px; }
}
</style>'''

# ── Shared JS ──
def _js(is_detail: bool = False) -> str:
    return f'''<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script>
gsap.registerPlugin(ScrollTrigger);

// Hero entrance
const heroTl = gsap.timeline({{defaults: {{ease: "power3.out", duration: 0.8}}}});
heroTl
    .from(".hero-badge", {{y: 20, opacity: 0, duration: 0.6}})
    .from(".hero h1", {{y: 40, opacity: 0, duration: 1}}, "-=0.3")
    .from(".hero-sub", {{y: 20, opacity: 0}}, "-=0.6")
    .from(".hero-date", {{y: 15, opacity: 0}}, "-=0.5")
    .from(".section-title", {{y: 20, opacity: 0}}, "-=0.4");

// Today's cards stagger
gsap.from(".image-card", {{
    y: 60,
    opacity: 0,
    duration: 0.9,
    stagger: 0.15,
    ease: "power3.out",
    delay: 0.4
}});

// History cards scroll trigger
{'' if is_detail else '''gsap.utils.toArray(".history-card").forEach((card, i) => {{
    gsap.to(card, {{
        scrollTrigger: {{
            trigger: card,
            start: "top 88%",
            toggleActions: "play none none none",
        }},
        y: 0,
        opacity: 1,
        duration: 0.7,
        delay: i * 0.08,
        ease: "power3.out",
        onComplete: () => card.classList.add("visible")
    }});
}});'''}


// Lightbox
const lightbox = document.getElementById("lightbox");
const lightboxImg = document.getElementById("lightbox-img");

function openLightbox(src) {{
    lightboxImg.src = src;
    lightbox.classList.add("show");
    document.body.style.overflow = "hidden";
    requestAnimationFrame(() => lightbox.classList.add("active"));
}}
function closeLightbox(e) {{
    if (e.target === e.currentTarget || e.target.classList.contains("close")) {{
        lightbox.classList.remove("active");
        setTimeout(() => {{
            lightbox.classList.remove("show");
            lightboxImg.src = "";
            document.body.style.overflow = "";
        }}, 300);
    }}
}}
document.addEventListener("keydown", (e) => {{
    if (e.key === "Escape" && lightbox.classList.contains("show")) {{
        lightbox.classList.remove("active");
        setTimeout(() => {{
            lightbox.classList.remove("show");
            lightboxImg.src = "";
            document.body.style.overflow = "";
        }}, 300);
    }}
}});

// Header blur on scroll
window.addEventListener("scroll", () => {{
    const header = document.querySelector(".header");
    if (window.scrollY > 10) {{
        header.style.background = "rgba(255,255,255,0.92)";
    }} else {{
        header.style.background = "rgba(255,255,255,0.72)";
    }}
}});
</script>'''

# ── Detail page for a specific date ──
def _detail_page_html(b: dict) -> str:
    date = b["date"]
    cards = ""
    if b.get("detail_path"):
        cards += f'''
        <div class="image-card" onclick="openLightbox('./{b['detail_path']}')">
            <img src="./{b['detail_path']}" alt="详细版">
            <div class="label">
                <span class="label-text">详细版 · 8 条精选资讯</span>
                <span class="label-tag">📱 手机全屏</span>
            </div>
        </div>'''
    if b.get("highlights_path"):
        cards += f'''
        <div class="image-card" onclick="openLightbox('./{b['highlights_path']}')">
            <img src="./{b['highlights_path']}" alt="今日看点">
            <div class="label">
                <span class="label-text">今日看点 · 3 条重点</span>
                <span class="label-tag">🎯 精选推荐</span>
            </div>
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

    <section class="section">
        <div class="section-header">
            <h2 class="section-title">{date} 早报</h2>
        </div>
        {cards}
    </section>

    <footer class="footer">
        米桶 AI · 不构成任何建议，仅供信息参考<br>
        自动采集自机器之心、量子位、36氪等信源
    </footer>

    <div class="lightbox" id="lightbox" onclick="closeLightbox(event)">
        <span class="close">&times;</span>
        <img src="" alt="大图" id="lightbox-img">
    </div>

{_js(is_detail=True)}
</body>
</html>'''

# ── Home page ──
def _home_page_html(latest: dict, history: list[dict]) -> str:
    today_cards = ""
    if latest.get("detail_path"):
        today_cards += f'''
        <div class="image-card" onclick="openLightbox('./{latest['detail_path']}')">
            <img src="./{latest['detail_path']}" alt="详细版">
            <div class="label">
                <span class="label-text">详细版 · 8 条精选资讯</span>
                <span class="label-tag">📱 手机全屏</span>
            </div>
        </div>'''
    if latest.get("highlights_path"):
        today_cards += f'''
        <div class="image-card" onclick="openLightbox('./{latest['highlights_path']}')">
            <img src="./{latest['highlights_path']}" alt="今日看点">
            <div class="label">
                <span class="label-text">今日看点 · 3 条重点</span>
                <span class="label-tag">🎯 精选推荐</span>
            </div>
        </div>'''

    history_html = ""
    if history:
        history_html += '''
    <section class="history-section">
        <div class="section-header">
            <h2 class="section-title">历史记录</h2>
            <span class="section-count">''' + str(len(history)) + ''' 期</span>
        </div>
        <div class="history-grid">
'''
        for b in history:
            thumb = b.get("highlights_path") or b.get("detail_path")
            date_slug = b["date"].replace(" ", "_").replace(".", "-")
            meta_parts = []
            if b['detail']:
                meta_parts.append("详细版")
            if b['highlights']:
                meta_parts.append("今日看点")
            meta = " · ".join(meta_parts)
            if thumb:
                history_html += f'''
            <a href="./{date_slug}/" class="history-card">
                <div class="thumb-wrap">
                    <img src="./{thumb}" alt="{b['date']}" loading="lazy">
                    <div class="overlay"></div>
                </div>
                <div class="info">
                    <div class="date">{b['date']}</div>
                    <div class="meta">📄 {meta}</div>
                </div>
            </a>
'''
        history_html += '''
        </div>
    </section>
'''
    else:
        history_html = '''
    <section class="history-section">
        <div class="empty">
            <div class="empty-icon">📭</div>
            <p>暂无历史记录</p>
        </div>
    </section>
'''

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
        <p class="hero-date">📅 {latest['date']}</p>
    </section>

    <section class="section">
        <div class="section-header">
            <h2 class="section-title">今日早报</h2>
        </div>
        {today_cards}
    </section>

    {history_html}

    <footer class="footer">
        米桶 AI · 不构成任何建议，仅供信息参考<br>
        自动采集自机器之心、量子位、36氪等信源
    </footer>

    <div class="lightbox" id="lightbox" onclick="closeLightbox(event)">
        <span class="close">&times;</span>
        <img src="" alt="大图" id="lightbox-img">
    </div>

{_js(is_detail=False)}
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

    # ── Generate detail pages ──
    for b in briefings:
        date_slug = b["date"].replace(" ", "_").replace(".", "-")
        detail_dir = WEB_DIR / date_slug
        detail_dir.mkdir(exist_ok=True)
        (detail_dir / "index.html").write_text(_detail_page_html(b), encoding="utf-8")
        print(f"  Detail page: {detail_dir}/index.html")

    # ── Generate home page ──
    home_html = _home_page_html(latest, history)
    (WEB_DIR / "index.html").write_text(home_html, encoding="utf-8")

    print(f"✅ Website generated: {WEB_DIR}/index.html")
    print(f"   Total briefings: {len(briefings)}")
    print(f"   Detail pages: {len(briefings)}")
    print(f"   Latest: {latest['date']}")
    print(f"   History: {len(history)} days")

if __name__ == "__main__":
    generate_website()
