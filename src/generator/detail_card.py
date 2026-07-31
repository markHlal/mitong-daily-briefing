"""Apple-style detail card image generator."""

import os
from pathlib import Path
from PIL import Image, ImageDraw

from .fonts import get_font
from utils.logger import get_logger

logger = get_logger(__name__)


def _hex_to_rgb(hex_color: str) -> tuple:
    """Convert #RRGGBB to (R, G, B) tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def generate_detail_image(news_list: list[dict], date_str: str) -> Image.Image:
    """Generate Apple-style detail image (1242×2208) with 8 news cards in 2×4 grid."""
    W, H = 1242, 2208
    img = Image.new("RGB", (W, H), (245, 247, 250))
    draw = ImageDraw.Draw(img)

    # Subtle top gradient: white → #F5F7FA
    for y in range(300):
        ratio = y / 300
        r = int(245 + (255 - 245) * (1 - ratio))
        g = int(247 + (255 - 247) * (1 - ratio))
        b = int(250 + (255 - 250) * (1 - ratio))
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Fonts
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

    # Top bar
    draw.text((60, 50), "AI 早报", fill=(0, 0, 0), font=font_brand)
    draw.text((W - 180, 50), "DAILY BRIEF", fill=(150, 150, 155), font=font_brand)
    draw.line([(60, 85), (W - 60, 85)], fill=(230, 230, 235), width=1)

    # Main title area
    draw.text((60, 120), "AI早报", fill=(0, 0, 0), font=font_title)
    draw.text((60, 200), "每日精选 · 10 秒速览", fill=(120, 120, 125), font=font_subtitle)
    draw.text((60, 240), date_str, fill=(150, 150, 155), font=font_date)

    # Page indicator pill
    pill_x = W - 180
    draw.rounded_rectangle(
        [(pill_x, 130), (pill_x + 120, 165)],
        radius=20,
        fill=(240, 240, 245),
        outline=(220, 220, 225),
        width=1,
    )
    draw.text((pill_x + 25, 136), "Top 16", fill=(80, 80, 85), font=font_page)

    # News cards — 2 columns × 4 rows
    card_w, card_h = 540, 420
    start_y = 300
    gap_x, gap_y = 30, 24

    for i, news in enumerate(news_list[:8]):
        col = i % 2
        row = i // 2
        x = 50 + col * (card_w + gap_x)
        y = start_y + row * (card_h + gap_y)

        # Card background
        draw.rounded_rectangle(
            [(x, y), (x + card_w, y + card_h)],
            radius=24,
            fill=(255, 255, 255),
            outline=(235, 235, 240),
            width=1,
        )

        # Category dot + label — enlarged dot for visibility
        cat_color = _hex_to_rgb(news.get("category_color", "#007AFF"))
        dot_x, dot_y = x + 24, y + 20
        draw.ellipse([(dot_x, dot_y), (dot_x + 16, dot_y + 16)], fill=cat_color)
        draw.text((dot_x + 22, dot_y + 1), news.get("category", ""), fill=(80, 80, 85), font=font_badge)
        cat_color = _hex_to_rgb(news.get("category_color", "#007AFF"))
        dot_x, dot_y = x + 24, y + 20
        draw.ellipse([(dot_x, dot_y), (dot_x + 10, dot_y + 10)], fill=cat_color)
        draw.text((dot_x + 18, dot_y - 2), news.get("category", ""), fill=(100, 100, 105), font=font_badge)

        # Number — top right
        draw.text((x + card_w - 40, y + 16), f"{i + 1:02d}", fill=(200, 200, 205), font=font_num)

        # Title
        title_y = y + 55
        draw.text((x + 24, title_y), news.get("title", ""), fill=(20, 20, 25), font=font_card_title)

        # Desc line (summary)
        desc_y = title_y + 38
        draw.text((x + 24, desc_y), news.get("summary", ""), fill=(80, 80, 85), font=font_card_desc)

        # Detail (brief)
        detail_y = desc_y + 35
        draw.text((x + 24, detail_y), news.get("brief", ""), fill=(140, 140, 145), font=font_card_detail)

        # Separator line
        draw.line(
            [(x + 24, y + card_h - 40), (x + card_w - 24, y + card_h - 40)],
            fill=(240, 240, 245),
            width=1,
        )

        # Source
        draw.text((x + 24, y + card_h - 30), news.get("source_name", ""), fill=(170, 170, 175), font=font_card_src)

    # Bottom brand text
    draw.text((W // 2 - 120, H - 60), "米桶 AI  ·  不构成任何建议", fill=(180, 180, 185), font=font_date)

    return img


def save_detail_image(news_list: list[dict], date_str: str) -> Path:
    """Generate and save the detail image to output/YYYY-MM-DD/detail.png.

    date_str is expected in the form "YYYY.MM.DD  星期X".
    """
    # Extract YYYY-MM-DD from date_str like "2026.07.31  星期五"
    date_part = date_str.split()[0].replace(".", "-")
    out_dir = Path("output") / date_part
    out_dir.mkdir(parents=True, exist_ok=True)
    img = generate_detail_image(news_list, date_str)
    out_path = out_dir / "detail.png"
    img.save(str(out_path), quality=95)
    logger.info("Saved detail image to %s", out_path)
    return out_path
