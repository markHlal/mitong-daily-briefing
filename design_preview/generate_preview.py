#!/usr/bin/env python3
"""Generate design preview images for the news briefing system."""

import os
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = "/Users/huang/Documents/Kimi/Workspaces/ai新闻收集/design_preview"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Try to find a Chinese-capable font
FONT_CANDIDATES = [
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/PingFang SC.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]

FONT_PATH = None
for f in FONT_CANDIDATES:
    if os.path.exists(f):
        FONT_PATH = f
        print(f"Using font: {f}")
        break

if FONT_PATH is None:
    print("No Chinese font found! Using default.")
    FONT_PATH = None

# ---- Helpers ----

def get_font(size, bold=False):
    try:
        if FONT_PATH:
            return ImageFont.truetype(FONT_PATH, size)
    except Exception as e:
        pass
    return ImageFont.load_default()

# Sample news data (from reference image)
NEWS_LIST = [
    {"cat": "Agent", "cat_color": "#00e5ff", "title": "腾讯WorkBuddy上线人机双写", "desc": "AI可在原始文档中接力编辑内容", "detail": "办公智能体从旁路生成走向直接协作，文档编辑、审阅和知识流转会更快进入团队流程。", "source": "IT之家 · July 30"},
    {"cat": "Agent", "cat_color": "#00e5ff", "title": "微软确认开发Copilot AI超级应用", "desc": "整合聊天编程与智能代理", "detail": "微软正在把多入口AI能力收束成统一工作入口，企业软件竞争会继续向智能体平台迁移。", "source": "AIBase · July 30"},
    {"cat": "产业", "cat_color": "#00ff88", "title": "字节调整AI业务架构", "desc": "大模型ARR达到40亿美元", "detail": "飞书、豆包和火山引擎的协同被继续强化，国内大模型商业化开始进入组织整合阶段。", "source": "AIBase · July 30"},
    {"cat": "模型", "cat_color": "#b967ff", "title": "OpenAI部署GPT-5.6 Sol", "desc": "优化推理链路服务成本最多降低20%", "detail": "推理成本继续成为模型落地的关键变量，平台竞争正在从能力榜单延伸到单位任务经济性。", "source": "IT之家 · July 30"},
    {"cat": "模型", "cat_color": "#b967ff", "title": "马斯克预告Grok 4.6", "desc": "8月7日发布Grok 4.7达2.1万亿参数", "detail": "xAI继续用大参数和密集迭代拉开声量，但实际体验仍要看推理稳定性和工具生态。", "source": "IT之家 · July 30"},
    {"cat": "模型", "cat_color": "#b967ff", "title": "OpenAI启动科研人员计划", "desc": "最高10万人开放GPT-5.6与Codex工具", "detail": "前沿模型继续面向科研场景扩散，代码、文献和实验设计会成为高价值生产力入口。", "source": "机器之心 · July 30"},
    {"cat": "模型", "cat_color": "#b967ff", "title": "Kimi K3预训练拆解", "desc": "3T级工程注意力与并行提升效率", "detail": "国产模型开始更多披露训练工程细节，效率优化会影响后续开源模型的成本和可复制性。", "source": "华尔街见闻 · July 30"},
    {"cat": "安全/监管", "cat_color": "#ff6b6b", "title": "普华永道报告被指高概率AI生成", "desc": "并含捏造信息引发争议", "detail": "企业报告和咨询交付正在接受AI事实校验压力，审核流程会成为大模型应用的底线能力。", "source": "IT之家 · July 30"},
]

HIGHLIGHTS = [
    {"cat": "Agent办公", "cat_color": "#00e5ff", "title": "WorkBuddy上线人机双写", "desc": "AI直接接力编辑原始文档。"},
    {"cat": "推理降本", "cat_color": "#b967ff", "title": "GPT-5.6 Sol成本降20%", "desc": "模型竞争转向任务经济性。"},
    {"cat": "算力能源", "cat_color": "#00ff88", "title": "千亿美元项目转向AI算力", "desc": "数据中心扩张绑定电力资产。"},
]

# ---- Image 1: Detail Version ----

def draw_gradient_bg(draw, width, height, top_color, bottom_color):
    """Draw a vertical gradient background."""
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

def generate_detail_image():
    W, H = 1242, 2208
    img = Image.new('RGB', (W, H), (10, 22, 40))
    draw = ImageDraw.Draw(img)
    
    # Gradient background
    draw_gradient_bg(draw, W, H, (10, 22, 40), (26, 39, 68))
    
    # Header area
    font_title = get_font(72)
    font_sub = get_font(28)
    font_date = get_font(24)
    font_tiny = get_font(20)
    
    # "AI早报" title
    draw.text((60, 50), "AI早报", fill=(255, 255, 255), font=font_title)
    draw.text((60, 140), "10秒速览AI天下事!", fill=(0, 229, 255), font=font_sub)
    draw.text((60, 185), "2026.07.31  星期五 · BEIJING", fill=(150, 170, 200), font=font_date)
    draw.text((60, 225), "Codex AIGC By AI-芯视界, 不构成任何建议!", fill=(100, 120, 150), font=font_tiny)
    
    # Top right corner
    font_top = get_font(56)
    font_top2 = get_font(24)
    draw.text((850, 50), "Top16", fill=(255, 255, 255), font=font_top)
    draw.text((850, 120), "NEWS", fill=(0, 229, 255), font=font_top2)
    draw.text((850, 155), "第1页/共2页", fill=(120, 140, 170), font=font_tiny)
    draw.text((850, 195), "DAILY AI BRIEF", fill=(100, 120, 150), font=font_tiny)
    
    # Decorative circle icon in top right
    draw.ellipse([(1080, 50), (1180, 150)], outline=(0, 229, 255), width=2)
    draw.ellipse([(1110, 80), (1150, 120)], outline=(0, 229, 255), width=1)
    
    # News cards - 2 columns, 4 rows
    card_w, card_h = 560, 440
    start_y = 280
    gap_x, gap_y = 40, 20
    
    font_card_title = get_font(30)
    font_card_desc = get_font(22)
    font_card_detail = get_font(18)
    font_card_src = get_font(16)
    font_num = get_font(20)
    
    for i, news in enumerate(NEWS_LIST[:8]):
        col = i % 2
        row = i // 2
        x = 30 + col * (card_w + gap_x)
        y = start_y + row * (card_h + gap_y)
        
        # Card background with slight transparency effect
        draw.rounded_rectangle([(x, y), (x + card_w, y + card_h)], radius=16, 
                               fill=(20, 35, 60), outline=(40, 60, 90), width=1)
        
        # Number circle
        circle_x, circle_y = x + 30, y + 20
        draw.ellipse([(circle_x, circle_y), (circle_x + 36, circle_y + 36)], 
                     outline=(80, 100, 130), width=2)
        num_text = f"{i+1:02d}"
        draw.text((circle_x + 8, circle_y + 6), num_text, fill=(150, 170, 200), font=font_num)
        
        # Category label
        cat_x = circle_x + 46
        cat_color = news["cat_color"]
        # Convert hex to RGB
        cat_rgb = tuple(int(cat_color[i:i+2], 16) for i in (1, 3, 5))
        draw.text((cat_x, circle_y + 6), news["cat"], fill=cat_rgb, font=font_num)
        
        # Title
        title_y = y + 70
        draw.text((x + 20, title_y), news["title"], fill=(255, 255, 255), font=font_card_title)
        
        # Description line
        desc_y = title_y + 45
        draw.text((x + 20, desc_y), news["desc"], fill=(200, 210, 230), font=font_card_desc)
        
        # Detail text (wrapped roughly)
        detail_y = desc_y + 40
        detail_text = f"解读 {news['detail']}"
        draw.text((x + 20, detail_y), detail_text, fill=(130, 150, 180), font=font_card_detail)
        
        # Source
        src_y = y + card_h - 30
        draw.text((x + 20, src_y), news["source"], fill=(100, 120, 150), font=font_card_src)
    
    # Bottom area
    draw.rectangle([(0, H-80), (W, H)], fill=(15, 28, 50))
    draw.text((W - 250, H - 50), "公众号 · SeeAlx", fill=(150, 170, 200), font=font_tiny)
    
    img.save(os.path.join(OUTPUT_DIR, "preview_detail.png"), quality=95)
    print("Generated: preview_detail.png")


# ---- Image 2: Highlights Version ----

def generate_highlights_image():
    W, H = 1242, 1656
    img = Image.new('RGB', (W, H), (10, 22, 40))
    draw = ImageDraw.Draw(img)
    
    # Gradient background
    draw_gradient_bg(draw, W, H, (10, 22, 40), (26, 39, 68))
    
    font_small = get_font(22)
    font_title = get_font(80)
    font_top16 = get_font(64)
    font_date = get_font(48)
    font_cat = get_font(26)
    font_item_title = get_font(38)
    font_item_desc = get_font(24)
    font_footer = get_font(28)
    font_tiny = get_font(20)
    font_brand = get_font(30)
    
    # Top bar
    draw.text((50, 40), "Codex AIGC By AI-芯视界", fill=(150, 170, 200), font=font_small)
    draw.text((850, 40), "DAILY AI BRIEF", fill=(0, 229, 255), font=font_small)
    
    # Main title "AI早报"
    draw.text((50, 110), "AI早报", fill=(255, 255, 255), font=font_title)
    
    # Top16
    draw.text((750, 130), "Top16", fill=(255, 255, 255), font=font_top16)
    draw.text((750, 210), "NEWS", fill=(0, 229, 255), font=font_small)
    
    # Tag pills
    draw.rounded_rectangle([(50, 260), (300, 300)], radius=15, fill=(20, 50, 80), outline=(0, 229, 255), width=1)
    draw.text((70, 265), "10秒速览AI天下事", fill=(0, 229, 255), font=font_small)
    
    draw.rounded_rectangle([(320, 260), (620, 300)], radius=15, fill=(20, 50, 80), outline=(0, 229, 255), width=1)
    draw.text((340, 265), "Agent / 推理 / 算力", fill=(0, 229, 255), font=font_small)
    
    draw.text((750, 265), "公众号@SeeAlx", fill=(150, 170, 200), font=font_small)
    
    # Date line
    draw.text((50, 340), "20260731 · 今日看点", fill=(255, 255, 255), font=font_date)
    draw.line([(50, 410), (W-50, 410)], fill=(0, 229, 255), width=3)
    
    # Highlight cards
    card_h = 280
    start_y = 450
    gap_y = 30
    
    for i, item in enumerate(HIGHLIGHTS):
        y = start_y + i * (card_h + gap_y)
        
        # Card background
        draw.rounded_rectangle([(50, y), (W-50, y + card_h)], radius=20,
                               fill=(20, 35, 60), outline=(40, 60, 90), width=1)
        
        # Number circle
        cx, cy = 90, y + 50
        draw.ellipse([(cx, cy), (cx + 56, cy + 56)], outline=(0, 229, 255), width=2)
        draw.text((cx + 14, cy + 12), f"{i+1:02d}", fill=(0, 229, 255), font=get_font(24))
        
        # Category
        cat_color = tuple(int(item["cat_color"][j:j+2], 16) for j in (1, 3, 5))
        draw.text((170, cy + 8), item["cat"], fill=cat_color, font=font_cat)
        
        # Title
        draw.text((170, cy + 50), item["title"], fill=(255, 255, 255), font=font_item_title)
        
        # Description
        draw.text((170, cy + 100), item["desc"], fill=(180, 195, 220), font=font_item_desc)
    
    # Bottom banner
    banner_y = H - 250
    draw.rounded_rectangle([(50, banner_y), (W-50, banner_y + 80)], radius=15,
                           fill=(0, 229, 255))
    draw.text((200, banner_y + 20), "16条AI要闻 · 2页速览 · 10秒看完", fill=(10, 22, 40), font=font_footer)
    draw.text((350, banner_y + 55), "不构成任何建议，仅供信息参考", fill=(40, 60, 90), font=font_tiny)
    
    # Brand
    draw.text((500, H - 120), "AI-芯视界", fill=(0, 229, 255), font=font_brand)
    draw.text((500, H - 80), "Codex AIGC", fill=(150, 170, 200), font=font_small)
    
    draw.text((W - 200, H - 80), "公众号 · SeeAlx", fill=(150, 170, 200), font=font_small)
    
    img.save(os.path.join(OUTPUT_DIR, "preview_highlights.png"), quality=95)
    print("Generated: preview_highlights.png")


if __name__ == "__main__":
    generate_detail_image()
    generate_highlights_image()
    print("Done! Files saved to:", OUTPUT_DIR)
PYEOF