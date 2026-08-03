"""Generate a static website with daily detail pages and history grid."""

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
        # Normalize date key: "2026-08-03 Mon" -> "2026-08-03"
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
        briefings.append({
            "date": date_key,
            **b,
        })
    return briefings
    """Scan output directory and return all briefings sorted by date."""
    briefings = []
    for date_dir in sorted(OUTPUT_DIR.iterdir()):
        if not date_dir.is_dir():
            continue
        detail = date_dir / "detail.png"
        highlights = date_dir / "highlights.png"
        if detail.exists() or highlights.exists():
            briefings.append({
                "date": date_dir.name,
                "detail": detail.exists(),
                "highlights": highlights.exists(),
                "detail_path": str(detail.relative_to(PROJECT_ROOT)) if detail.exists() else None,
                "highlights_path": str(highlights.relative_to(PROJECT_ROOT)) if highlights.exists() else None,
            })
    return list(reversed(briefings))


CSS = '''
    <style>
        :root {
            --bg: #F5F7FA;
            --card: #FFFFFF;
            --text: #1D1D1F;
            --text-secondary: #86868B;
            --blue: #007AFF;
            --border: #E5E5EA;
            --shadow: 0 4px 24px rgba(0,0,0,0.08);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding-bottom: 60px;
        }
        .header {
            background: rgba(255,255,255,0.85);
            border-bottom: 1px solid var(--border);
            padding: 16px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
        }
        .header-brand {
            font-size: 22px;
            font-weight: 600;
            color: var(--blue);
            text-decoration: none;
        }
        .header-sub { font-size: 13px; color: var(--text-secondary); margin-left: 6px; }
        .header-back {
            color: var(--blue);
            text-decoration: none;
            font-size: 15px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .header-back:hover { opacity: 0.7; }

        .hero {
            max-width: 900px;
            margin: 40px auto;
            padding: 0 20px;
            text-align: center;
        }
        .hero h1 { font-size: 44px; font-weight: 700; margin-bottom: 8px; }
        .hero .accent {
            display: inline-block;
            width: 60px;
            height: 4px;
            background: var(--blue);
            border-radius: 2px;
            margin: 0 auto 16px;
        }
        .hero p { color: var(--text-secondary); font-size: 18px; }
        .hero .date {
            display: inline-block;
            background: var(--card);
            border: 1px solid var(--border);
            padding: 8px 20px;
            border-radius: 20px;
            margin-top: 16px;
            font-size: 16px;
            color: var(--text-secondary);
        }

        .today {
            max-width: 900px;
            margin: 0 auto 60px;
            padding: 0 20px;
        }
        .section-title {
            font-size: 26px;
            font-weight: 600;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .section-title::before {
            content: "";
            width: 4px;
            height: 26px;
            background: var(--blue);
            border-radius: 2px;
        }

        .image-card {
            background: var(--card);
            border-radius: 24px;
            overflow: hidden;
            box-shadow: var(--shadow);
            margin-bottom: 24px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .image-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        }
        .image-card img {
            width: 100%;
            display: block;
            cursor: zoom-in;
        }
        .image-card .label {
            padding: 16px 24px;
            font-size: 16px;
            color: var(--text-secondary);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .image-card .label span {
            background: var(--bg);
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 14px;
        }

        .history {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        .history-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }
        .history-item {
            background: var(--card);
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            transition: transform 0.2s, box-shadow 0.2s;
            text-decoration: none;
            color: inherit;
        }
        .history-item:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow);
        }
        .history-item img {
            width: 100%;
            height: 200px;
            object-fit: cover;
            display: block;
        }
        .history-item .info {
            padding: 16px 20px;
        }
        .history-item .date { font-size: 17px; font-weight: 600; margin-bottom: 4px; }
        .history-item .meta { font-size: 14px; color: var(--text-secondary); }

        .lightbox {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.92);
            z-index: 200;
            justify-content: center;
            align-items: center;
            padding: 40px;
        }
        .lightbox.active { display: flex; }
        .lightbox img {
            max-width: 100%;
            max-height: 90vh;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }
        .lightbox .close {
            position: absolute;
            top: 20px;
            right: 30px;
            font-size: 40px;
            color: white;
            cursor: pointer;
            opacity: 0.8;
        }
        .lightbox .close:hover { opacity: 1; }

        .empty {
            text-align: center;
            padding: 80px 20px;
            color: var(--text-secondary);
        }
        .empty-icon { font-size: 64px; margin-bottom: 16px; }

        .footer {
            text-align: center;
            padding: 40px;
            color: var(--text-secondary);
            font-size: 14px;
            border-top: 1px solid var(--border);
            margin-top: 60px;
        }

        @media (max-width: 768px) {
            .hero h1 { font-size: 32px; }
            .history-grid { grid-template-columns: 1fr; }
            .header { padding: 12px 20px; }
        }
    </style>
'''

LIGHTBOX_JS = '''
    <script>
        function openLightbox(src) {
            document.getElementById('lightbox-img').src = src;
            document.getElementById('lightbox').classList.add('active');
            document.body.style.overflow = 'hidden';
        }
        function closeLightbox(e) {
            if (e.target === e.currentTarget || e.target.classList.contains('close')) {
                document.getElementById('lightbox').classList.remove('active');
                document.body.style.overflow = '';
            }
        }
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                document.getElementById('lightbox').classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    </script>
'''


def _generate_detail_page(b: dict, is_home: bool = False) -> str:
    """Generate a detail page for a specific date's briefing."""
    date = b["date"]
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{date} · 米桶 AI 早报</title>
    {CSS}
</head>
<body>
    <header class="header">
        <a href="./" class="header-brand">
            米桶 AI <span class="header-sub">Daily Brief</span>
        </a>
        <a href="./" class="header-back">← 返回首页</a>
    </header>

    <section class="hero">
        <h1>AI 早报</h1>
        <div class="accent"></div>
        <p>每日精选 · 10 秒速览</p>
        <div class="date">📅 {date}</div>
    </section>

    <section class="today">
        <h2 class="section-title">{date} 早报</h2>
'''

    if b.get("detail_path"):
        html += f'''
        <div class="image-card">
            <img src="./{b['detail_path']}" alt="详细版" onclick="openLightbox(this.src)">
            <div class="label">
                详细版 · 8 条精选资讯
                <span>📱 手机全屏</span>
            </div>
        </div>
        '''

    if b.get("highlights_path"):
        html += f'''
        <div class="image-card">
            <img src="./{b['highlights_path']}" alt="今日看点" onclick="openLightbox(this.src)">
            <div class="label">
                今日看点 · 3 条重点
                <span>🎯 精选推荐</span>
            </div>
        </div>
        '''

    html += '''
    </section>

    <footer class="footer">
        米桶 AI · 不构成任何建议，仅供信息参考<br>
        自动采集自机器之心、量子位、36氪等信源
    </footer>

    <div class="lightbox" id="lightbox" onclick="closeLightbox(event)">
        <span class="close">&times;</span>
        <img src="" alt="大图" id="lightbox-img">
    </div>

''' + LIGHTBOX_JS + '''
</body>
</html>
'''
    return html


def generate_website():
    briefings = get_all_briefings()
    if not briefings:
        print("No briefings found.")
        return

    WEB_DIR.mkdir(exist_ok=True)
    latest = briefings[0]
    history = briefings[1:]

    # ── Generate detail pages for each date ──
    for b in briefings:
        date_slug = b["date"].replace(" ", "_").replace(".", "-")
        detail_dir = WEB_DIR / date_slug
        detail_dir.mkdir(exist_ok=True)
        page_html = _generate_detail_page(b)
        (detail_dir / "index.html").write_text(page_html, encoding="utf-8")
        print(f"  Detail page: {detail_dir}/index.html")

    # ── Generate home page ──
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>米桶 AI 早报</title>
    {CSS}
</head>
<body>
    <header class="header">
        <a href="./" class="header-brand">
            米桶 AI <span class="header-sub">Daily Brief</span>
        </a>
        <span style="color: var(--text-secondary); font-size: 14px;">每日资讯早报</span>
    </header>

    <section class="hero">
        <h1>AI 早报</h1>
        <div class="accent"></div>
        <p>每日精选 · 10 秒速览</p>
        <div class="date">📅 {latest['date']}</div>
    </section>

    <section class="today">
        <h2 class="section-title">今日早报</h2>
'''

    if latest.get("detail_path"):
        html += f'''
        <div class="image-card">
            <img src="./{latest['detail_path']}" alt="详细版" onclick="openLightbox(this.src)">
            <div class="label">
                详细版 · 8 条精选资讯
                <span>📱 手机全屏</span>
            </div>
        </div>
        '''

    if latest.get("highlights_path"):
        html += f'''
        <div class="image-card">
            <img src="./{latest['highlights_path']}" alt="今日看点" onclick="openLightbox(this.src)">
            <div class="label">
                今日看点 · 3 条重点
                <span>🎯 精选推荐</span>
            </div>
        </div>
        '''

    html += '''
    </section>
'''

    if history:
        html += '''
    <section class="history">
        <h2 class="section-title">历史记录</h2>
        <div class="history-grid">
'''
        for b in history:
            thumb = b.get("highlights_path") or b.get("detail_path")
            date_slug = b["date"].replace(" ", "_").replace(".", "-")
            if thumb:
                html += f'''
            <a href="./{date_slug}/" class="history-item">
                <img src="./{thumb}" alt="{b['date']}" loading="lazy">
                <div class="info">
                    <div class="date">{b['date']}</div>
                    <div class="meta">📄 {'详细版' if b['detail'] else ''} {'·' if b['detail'] and b['highlights'] else ''} {'今日看点' if b['highlights'] else ''}</div>
                </div>
            </a>
'''
        html += '''
        </div>
    </section>
'''

    html += '''
    <footer class="footer">
        米桶 AI · 不构成任何建议，仅供信息参考<br>
        自动采集自机器之心、量子位、36氪等信源
    </footer>

    <div class="lightbox" id="lightbox" onclick="closeLightbox(event)">
        <span class="close">&times;</span>
        <img src="" alt="大图" id="lightbox-img">
    </div>

''' + LIGHTBOX_JS + '''
</body>
</html>
'''

    index_path = WEB_DIR / "index.html"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Website generated: {index_path}")
    print(f"   Total briefings: {len(briefings)}")
    print(f"   Detail pages: {len(briefings)}")
    print(f"   Latest: {latest['date']}")
    print(f"   History: {len(history)} days")


if __name__ == "__main__":
    generate_website()
