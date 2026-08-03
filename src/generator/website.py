"""Generate a static website to display daily briefings and history."""

import os
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
WEB_DIR = PROJECT_ROOT / "website"


def get_all_briefings() -> list[dict]:
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
    return list(reversed(briefings))  # Newest first


def generate_website():
    briefings = get_all_briefings()
    if not briefings:
        print("No briefings found.")
        return

    latest = briefings[0]
    history = briefings[1:]

    WEB_DIR.mkdir(exist_ok=True)

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>米桶 AI 早报</title>
    <style>
        :root {{
            --bg: #F5F7FA;
            --card: #FFFFFF;
            --text: #1D1D1F;
            --text-secondary: #86868B;
            --blue: #007AFF;
            --border: #E5E5EA;
            --shadow: 0 4px 24px rgba(0,0,0,0.08);
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding-bottom: 60px;
        }}
        
        /* Header */
        .header {{
            background: var(--card);
            border-bottom: 1px solid var(--border);
            padding: 20px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(20px);
        }}
        .header-brand {{
            font-size: 24px;
            font-weight: 600;
            color: var(--blue);
            text-decoration: none;
        }}
        .header-sub {{
            font-size: 14px;
            color: var(--text-secondary);
            margin-left: 8px;
        }}
        
        /* Hero Section */
        .hero {{
            max-width: 900px;
            margin: 40px auto;
            padding: 0 20px;
            text-align: center;
        }}
        .hero h1 {{
            font-size: 48px;
            font-weight: 700;
            margin-bottom: 8px;
        }}
        .hero .accent {{
            display: inline-block;
            width: 60px;
            height: 4px;
            background: var(--blue);
            border-radius: 2px;
            margin: 0 auto 16px;
        }}
        .hero p {{
            color: var(--text-secondary);
            font-size: 18px;
        }}
        .hero .date {{
            display: inline-block;
            background: var(--card);
            border: 1px solid var(--border);
            padding: 8px 20px;
            border-radius: 20px;
            margin-top: 16px;
            font-size: 16px;
            color: var(--text-secondary);
        }}
        
        /* Today's Cards */
        .today {{
            max-width: 900px;
            margin: 0 auto 60px;
            padding: 0 20px;
        }}
        .section-title {{
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .section-title::before {{
            content: "";
            width: 4px;
            height: 28px;
            background: var(--blue);
            border-radius: 2px;
        }}
        
        .image-card {{
            background: var(--card);
            border-radius: 24px;
            overflow: hidden;
            box-shadow: var(--shadow);
            margin-bottom: 24px;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .image-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        }}
        .image-card img {{
            width: 100%;
            display: block;
            cursor: zoom-in;
        }}
        .image-card .label {{
            padding: 16px 24px;
            font-size: 16px;
            color: var(--text-secondary);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .image-card .label span {{
            background: var(--bg);
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 14px;
        }}
        
        /* History Grid */
        .history {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        .history-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }}
        .history-item {{
            background: var(--card);
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            transition: transform 0.2s, box-shadow 0.2s;
            text-decoration: none;
            color: inherit;
        }}
        .history-item:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow);
        }}
        .history-item img {{
            width: 100%;
            height: 200px;
            object-fit: cover;
            display: block;
        }}
        .history-item .info {{
            padding: 16px 20px;
        }}
        .history-item .date {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 4px;
        }}
        .history-item .meta {{
            font-size: 14px;
            color: var(--text-secondary);
        }}
        
        /* Lightbox */
        .lightbox {{
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.9);
            z-index: 200;
            justify-content: center;
            align-items: center;
            padding: 40px;
        }}
        .lightbox.active {{
            display: flex;
        }}
        .lightbox img {{
            max-width: 100%;
            max-height: 90vh;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }}
        .lightbox .close {{
            position: absolute;
            top: 20px;
            right: 30px;
            font-size: 40px;
            color: white;
            cursor: pointer;
            opacity: 0.8;
        }}
        .lightbox .close:hover {{
            opacity: 1;
        }}
        
        /* Empty State */
        .empty {{
            text-align: center;
            padding: 80px 20px;
            color: var(--text-secondary);
        }}
        .empty-icon {{
            font-size: 64px;
            margin-bottom: 16px;
        }}
        
        /* Footer */
        .footer {{
            text-align: center;
            padding: 40px;
            color: var(--text-secondary);
            font-size: 14px;
            border-top: 1px solid var(--border);
            margin-top: 60px;
        }}
        
        @media (max-width: 768px) {{
            .hero h1 {{ font-size: 36px; }}
            .history-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <a href="/" class="header-brand">
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
            if thumb:
                html += f'''
            <a href="#" class="history-item" onclick="showDate('{b['date']}'); return false;">
                <img src="./{thumb}" alt="{b['date']}">
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
    else:
        html += '''
    <section class="history">
        <div class="empty">
            <div class="empty-icon">📭</div>
            <p>暂无历史记录</p>
        </div>
    </section>
    '''

    html += '''
    <footer class="footer">
        米桶 AI · 不构成任何建议，仅供信息参考<br>
        自动采集自机器之心、量子位、36氪等信源
    </footer>
    
    <!-- Lightbox -->
    <div class="lightbox" id="lightbox" onclick="closeLightbox(event)">
        <span class="close">&times;</span>
        <img src="" alt="大图" id="lightbox-img">
    </div>
    
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
        function showDate(date) {
            alert('点击查看 ' + date + ' 的详细内容\\n（完整历史页面开发中）');
        }
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                document.getElementById('lightbox').classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    </script>
</body>
</html>
'''

    index_path = WEB_DIR / "index.html"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Website generated: {index_path}")
    print(f"   Total briefings: {len(briefings)}")
    print(f"   Latest: {latest['date']}")
    print(f"   History: {len(history)} days")


if __name__ == "__main__":
    generate_website()
