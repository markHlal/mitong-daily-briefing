"""Apple-style highlights card image generator."""

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


def generate_highlights_image(news_list: list[dict], date_str: str) -> Image.Image:
    """Generate Apple-style highlights image (1242×1656) with 3 full-width cards."""
    W, H = 1242, 1656
    img = Image.new("RGB", (W, H), (245, 247, 250))
    draw = ImageDraw.Draw(img)

    # Subtle top gradient: white → #F5F7FA
    for y in range(250):
        ratio = y / 250
        r = int(245 + (255 - 245) * (1 - ratio))
        g = int(247 + (255 - 247) * (1 - ratio))
        b = int(250 + (255 - 250) * (1 - ratio))
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Fonts
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
    draw.line([(60, 78), (W - 60, 78)], fill=(230, 230, 235), width=1)

    # Big title
    draw.text((60, 110), "AI早报", fill=(0, 0, 0), font=font_title)

    # Date
    draw.text((60, 200), date_str, fill=(120, 120, 125), font=get_font(28))

    # Tags — Apple-style pills
    tag_y = 250
    tags = ["10 秒速览", "Agent · 推理 · 算力"]
    tag_x = 60
    for tag in tags:
        tw = len(tag) * 14 + 40
        draw.rounded_rectangle(
            [(tag_x, tag_y), (tag_x + tw, tag_y + 36)],
            radius=18,
            fill=(235, 235, 240),
            outline=(220, 220, 225),
            width=1,
        )
        draw.text((tag_x + 18, tag_y + 7), tag, fill=(80, 80, 85), font=font_small)
        tag_x += tw + 12

    # Section title
    draw.text((60, 320), "今日看点", fill=(0, 0, 0), font=font_date)
    draw.line([(60, 380), (200, 380)], fill=(0, 122, 255), width=3)

    # Highlight cards — large, clean, vertical
    card_h = 300
    start_y = 420
    gap_y = 24

    for i, item in enumerate(news_list[:3]):
        y = start_y + i * (card_h + gap_y)

        # White card
        draw.rounded_rectangle(
            [(50, y), (W - 50, y + card_h)],
            radius=28,
            fill=(255, 255, 255),
            outline=(235, 235, 240),
            width=1,
        )

        # Large number circle (56px)
        cx, cy = 90, y + 40
        draw.ellipse([(cx, cy), (cx + 56, cy + 56)], outline=(200, 200, 205), width=2)
        draw.text((cx + 14, cy + 12), f"{i + 1:02d}", fill=(120, 120, 125), font=get_font(22))

        # Category with dot — enlarged for visibility
        cat_color = _hex_to_rgb(item.get("category_color", "#007AFF"))
        cat_x = 170
        draw.ellipse([(cat_x, cy + 14), (cat_x + 16, cy + 30)], fill=cat_color)
        draw.text((cat_x + 22, cy + 12), item.get("category", ""), fill=(80, 80, 85), font=font_cat)
        cat_color = _hex_to_rgb(item.get("category_color", "#007AFF"))
        cat_x = 170
        draw.ellipse([(cat_x, cy + 16), (cat_x + 10, cy + 26)], fill=cat_color)
        draw.text((cat_x + 18, cy + 10), item.get("category", ""), fill=(80, 80, 85), font=font_cat)

        # Title
        draw.text((170, cy + 55), item.get("title", ""), fill=(20, 20, 25), font=font_item_title)

        # Desc
        draw.text((170, cy + 105), item.get("brief", ""), fill=(120, 120, 125), font=font_item_desc)

    # Bottom banner — Apple blue pill
    banner_y = H - 220
    draw.rounded_rectangle(
        [(50, banner_y), (W - 50, banner_y + 70)],
        radius=20,
        fill=(0, 122, 255),
    )
    draw.text(
        (W // 2 - 180, banner_y + 20),
        "16 条 AI 要闻 · 2 页速览 · 10 秒看完",
        fill=(255, 255, 255),
        font=font_footer,
    )
    draw.text(
        (W // 2 - 120, banner_y + 48),
        "不构成任何建议，仅供信息参考",
        fill=(180, 210, 255),
        font=font_tiny,
    )

    # Brand
    draw.text((W // 2 - 60, H - 100), "米桶 AI", fill=(0, 122, 255), font=font_brand)
    draw.text((W // 2 - 50, H - 65), "Daily Brief", fill=(150, 150, 155), font=font_small)

    return img


def save_highlights_image(news_list: list[dict], date_str: str) -> Path:
    """Generate and save the highlights image to output/YYYY-MM-DD/highlights.png.

    date_str is expected in the form "YYYY.MM.DD".
    """
    date_part = date_str.replace(".", "-")
    out_dir = Path("output") / date_part
    out_dir.mkdir(parents=True, exist_ok=True)
    img = generate_highlights_image(news_list, date_str)
    out_path = out_dir / "highlights.png"
    img.save(str(out_path), quality=95)
    logger.info("Saved highlights image to %s", out_path)
    return out_path
