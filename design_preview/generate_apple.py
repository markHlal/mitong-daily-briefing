#!/usr/bin/env python3
"""Generate Apple-style design preview images."""

import os
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = "/Users/huang/Documents/Kimi/Workspaces/ai新闻收集/design_preview"
os.makedirs(OUTPUT_DIR, exist_ok=True)

FONT_PATH = "/Library/Fonts/Arial Unicode.ttf"

def get_font(size):
    try:
        if FONT_PATH and os.path.exists(FONT_PATH):
            return ImageFont.truetype(FONT_PATH, size)
    except:
        pass
    return ImageFont.load_default()

NEWS_LIST = [
    {"cat": "Agent", "cat_color": (0, 122, 255), "title": "腾讯 WorkBuddy 上线人机双写", "desc": "AI 可在原始文档中接力编辑内容", "detail": "办公智能体从旁路生成走向直接协作，文档编辑、审阅和知识流转会更快进入团队流程。", "source": "IT之家 · July 30"},
    {"cat": "Agent", "cat_color": (0, 122, 255), "title": "微软确认开发 Copilot AI 超级应用", "desc": "整合聊天编程与智能代理", "detail": "微软正在把多入口 AI 能力收束成统一工作入口，企业软件竞争会继续向智能体平台迁移。", "source": "AIBase · July 30"},
    {"cat": "产业", "cat_color": (48, 209, 88), "title": "字节调整 AI 业务架构", "desc": "大模型 ARR 达到 40 亿美元", "detail": "飞书、豆包和火山引擎的协同被继续强化，国内大模型商业化开始进入组织整合阶段。", "source": "AIBase · July 30"},
    {"cat": "模型", "cat_color": (175, 82, 222), "title": "OpenAI 部署 GPT-5.6 Sol", "desc": "优化推理链路服务成本最多降低 20%", "detail": "推理成本继续成为模型落地的关键变量，平台竞争正在从能力榜单延伸到单位任务经济性。", "source": "IT之家 · July 30"},
    {"cat": "模型", "cat_color": (175, 82, 222), "title": "马斯克预告 Grok 4.6", "desc": "8 月 7 日发布 Grok 4.7 达 2.1 万亿参数", "detail": "xAI 继续用大参数和密集迭代拉开声量，但实际体验仍要看推理稳定性和工具生态。", "source": "IT之家 · July 30"},
    {"cat": "模型", "cat_color": (175, 82, 222), "title": "OpenAI 启动科研人员计划", "desc": "最高 10 万人开放 GPT-5.6 与 Codex 工具", "detail": "前沿模型继续面向科研场景扩散，代码、文献和实验设计会成为高价值生产力入口。", "source": "机器之心 · July 30"},
    {"cat": "模型", "cat_color": (175, 82, 222), "title": "Kimi K3 预训练拆解", "desc": "3T 级工程注意力与并行提升效率", "detail": "国产模型开始更多披露训练工程细节，效率优化会影响后续开源模型的成本和可复制性。", "source": "华尔街见闻 · July 30"},
    {"cat": "安全", "cat_color": (255, 59, 48), "title": "普华永道报告被指高概率 AI 生成", "desc": "并含捏造信息引发争议", "detail": "企业报告和咨询交付正在接受 AI 事实校验压力，审核流程会成为大模型应用的底线能力。", "source": "IT之家 · July 30"},
]

HIGHLIGHTS = [
    {"cat": "Agent 办公", "cat_color": (0, 122, 255), "title": "WorkBuddy 上线人机双写", "desc": "AI 直接接力编辑原始文档。"},
    {"cat": "推理降本", "cat_color": (175, 82, 222), "title": "GPT-5.6 Sol 成本降 20%", "desc": "模型竞争转向任务经济性。"},
    {"cat": "算力能源", "cat_color": (48, 209, 88), "title": "千亿美元项目转向 AI 算力", "desc": "数据中心扩张绑定电力资产。"},
]


def draw_soft_shadow(draw, xy, radius=20, color=(0,0,0,18)):
    """Draw a soft shadow under a rectangle (simplified)."""
    x1, y1, x2, y2 = xy
    for i in range(radius, 0, -1):
        alpha = int(18 * (1 - i/radius))
        c = (200, 200, 200, alpha)
        draw.rounded_rectangle(
            [(x1 + i//3, y1 + i//2), (x2 + i//3, y2 + i//2)],
            radius=24, fill=None, outline=(230, 230, 230), width=1
        )


def generate_apple_detail():
    W, H = 1242, 2208
    # Apple-style: clean white with subtle gray background
    img = Image.new('RGB', (W, H), (245, 247, 250))
    draw = ImageDraw.Draw(img)
    
    # Subtle top gradient
    for y in range(300):
        ratio = y / 300
        r = int(245 + (255-245) * (1-ratio))
        g = int(247 + (255-247) * (1-ratio))
        b = int(250 + (255-250) * (1-ratio))
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    
    # Fonts - Apple style: large display, clean hierarchy
    font_brand = get_font(20)
    font_title = get_font(56)
    font_subtitle = get_font(24)
    font_date = get_font(20)
    font_card_title = get_font(24)
    font_card_desc = get_font(18)
    font_card_detail = get_font(16)
    font_card_src = get_font(14)
    font_num = get_font(16)
    font_badge = get_font(14)
    font_page = get_font(18)
    
    # Top bar - minimal
    draw.text((60, 50), "AI 早报", fill=(0, 0, 0), font=font_brand)
    draw.text((W-180, 50), "DAILY BRIEF", fill=(150, 150, 155), font=font_brand)
    draw.line([(60, 85), (W-60, 85)], fill=(230, 230, 235), width=1)
    
    # Main title area
    draw.text((60, 120), "AI早报", fill=(0, 0, 0), font=font_title)
    draw.text((60, 200), "每日精选 · 10 秒速览", fill=(120, 120, 125), font=font_subtitle)
    draw.text((60, 240), "2026.07.31  星期五", fill=(150, 150, 155), font=font_date)
    
    # Page indicator - subtle pill
    pill_x = W - 180
    draw.rounded_rectangle([(pill_x, 130), (pill_x + 120, 165)], radius=20, fill=(240, 240, 245), outline=(220, 220, 225), width=1)
    draw.text((pill_x + 25, 136), "Top 16", fill=(80, 80, 85), font=font_page)
    
    # News cards - 2 columns, Apple-style cards with large radius
    card_w, card_h = 540, 420
    start_y = 300
    gap_x, gap_y = 30, 24
    
    for i, news in enumerate(NEWS_LIST[:8]):
        col = i % 2
        row = i // 2
        x = 50 + col * (card_w + gap_x)
        y = start_y + row * (card_h + gap_y)
        
        # Card background - pure white with soft shadow effect (simulated)
        draw.rounded_rectangle([(x, y), (x + card_w, y + card_h)], radius=24, 
                               fill=(255, 255, 255), outline=(235, 235, 240), width=1)
        
        # Category dot + label
        dot_x, dot_y = x + 24, y + 20
        draw.ellipse([(dot_x, dot_y), (dot_x + 10, dot_y + 10)], fill=news["cat_color"])
        draw.text((dot_x + 18, dot_y - 2), news["cat"], fill=(100, 100, 105), font=font_badge)
        
        # Number - top right
        draw.text((x + card_w - 40, y + 16), f"{i+1:02d}", fill=(200, 200, 205), font=font_num)
        
        # Title
        title_y = y + 55
        draw.text((x + 24, title_y), news["title"], fill=(20, 20, 25), font=font_card_title)
        
        # Desc line
        desc_y = title_y + 38
        draw.text((x + 24, desc_y), news["desc"], fill=(80, 80, 85), font=font_card_desc)
        
        # Detail - lighter gray, wrapped
        detail_y = desc_y + 35
        draw.text((x + 24, detail_y), news["detail"], fill=(140, 140, 145), font=font_card_detail)
        
        # Separator line
        draw.line([(x + 24, y + card_h - 40), (x + card_w - 24, y + card_h - 40)], fill=(240, 240, 245), width=1)
        
        # Source
        draw.text((x + 24, y + card_h - 30), news["source"], fill=(170, 170, 175), font=font_card_src)
    
    # Bottom
    draw.text((W//2 - 120, H - 60), "米桶 AI  ·  不构成任何建议", fill=(180, 180, 185), font=font_date)
    
    img.save(os.path.join(OUTPUT_DIR, "apple_detail.png"), quality=95)
    print("Generated: apple_detail.png")


def generate_apple_highlights():
    W, H = 1242, 1656
    img = Image.new('RGB', (W, H), (245, 247, 250))
    draw = ImageDraw.Draw(img)
    
    # Subtle top
    for y in range(250):
        ratio = y / 250
        r = int(245 + (255-245) * (1-ratio))
        g = int(247 + (255-247) * (1-ratio))
        b = int(250 + (255-250) * (1-ratio))
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    
    font_small = get_font(18)
    font_title = get_font(64)
    font_date = get_font(40)
    font_cat = get_font(22)
    font_item_title = get_font(34)
    font_item_desc = get_font(20)
    font_footer = get_font(24)
    font_tiny = get_font(16)
    font_brand = get_font(26)
    
    # Top bar
    draw.text((60, 45), "AI 早报", fill=(80, 80, 85), font=font_small)
    draw.text((W - 160, 45), "DAILY BRIEF", fill=(150, 150, 155), font=font_small)
    draw.line([(60, 78), (W-60, 78)], fill=(230, 230, 235), width=1)
    
    # Big title
    draw.text((60, 110), "AI早报", fill=(0, 0, 0), font=font_title)
    
    # Date
    draw.text((60, 200), "2026.07.31", fill=(120, 120, 125), font=get_font(28))
    
    # Tags - Apple-style pills
    tag_y = 250
    tags = ["10 秒速览", "Agent · 推理 · 算力"]
    tag_x = 60
    for tag in tags:
        tw = len(tag) * 14 + 40
        draw.rounded_rectangle([(tag_x, tag_y), (tag_x + tw, tag_y + 36)], radius=18,
                               fill=(235, 235, 240), outline=(220, 220, 225), width=1)
        draw.text((tag_x + 18, tag_y + 7), tag, fill=(80, 80, 85), font=font_small)
        tag_x += tw + 12
    
    # Section title
    draw.text((60, 320), "今日看点", fill=(0, 0, 0), font=font_date)
    draw.line([(60, 380), (200, 380)], fill=(0, 122, 255), width=3)
    
    # Highlight cards - large, clean, vertical
    card_h = 300
    start_y = 420
    gap_y = 24
    
    for i, item in enumerate(HIGHLIGHTS):
        y = start_y + i * (card_h + gap_y)
        
        # White card
        draw.rounded_rectangle([(50, y), (W-50, y + card_h)], radius=28,
                               fill=(255, 255, 255), outline=(235, 235, 240), width=1)
        
        # Large number circle
        cx, cy = 90, y + 40
        draw.ellipse([(cx, cy), (cx + 56, cy + 56)], outline=(200, 200, 205), width=2)
        draw.text((cx + 14, cy + 12), f"{i+1:02d}", fill=(120, 120, 125), font=get_font(22))
        
        # Category with dot
        cat_x = 170
        draw.ellipse([(cat_x, cy + 16), (cat_x + 10, cy + 26)], fill=item["cat_color"])
        draw.text((cat_x + 18, cy + 10), item["cat"], fill=(80, 80, 85), font=font_cat)
        
        # Title
        draw.text((170, cy + 55), item["title"], fill=(20, 20, 25), font=font_item_title)
        
        # Desc
        draw.text((170, cy + 105), item["desc"], fill=(120, 120, 125), font=font_item_desc)
    
    # Bottom banner - Apple blue pill
    banner_y = H - 220
    draw.rounded_rectangle([(50, banner_y), (W-50, banner_y + 70)], radius=20,
                           fill=(0, 122, 255))
    draw.text((W//2 - 180, banner_y + 20), "16 条 AI 要闻 · 2 页速览 · 10 秒看完", fill=(255, 255, 255), font=font_footer)
    draw.text((W//2 - 120, banner_y + 48), "不构成任何建议，仅供信息参考", fill=(180, 210, 255), font=font_tiny)
    
    # Brand
    draw.text((W//2 - 60, H - 100), "米桶 AI", fill=(0, 122, 255), font=font_brand)
    draw.text((W//2 - 50, H - 65), "Daily Brief", fill=(150, 150, 155), font=font_small)
    
    img.save(os.path.join(OUTPUT_DIR, "apple_highlights.png"), quality=95)
    print("Generated: apple_highlights.png")


if __name__ == "__main__":
    generate_apple_detail()
    generate_apple_highlights()
    print("Done!")
