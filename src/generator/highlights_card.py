"""Apple-style highlights card image generator."""

from pathlib import Path
from PIL import Image, ImageDraw

from .fonts import get_font
from utils.logger import get_logger

logger = get_logger(__name__)

W, H = 1242, 1656


def _hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def _draw_gradient_bg(draw: ImageDraw.Draw, width: int, height: int):
    top = (255, 255, 255)
    bottom = (245, 247, 250)
    for y in range(height):
        ratio = y / height
        r = int(top[0] * (1 - ratio) + bottom[0] * ratio)
        g = int(top[1] * (1 - ratio) + bottom[1] * ratio)
        b = int(top[2] * (1 - ratio) + bottom[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def _draw_text_bold(draw: ImageDraw.Draw, xy, text, fill, font):
    x, y = xy
    draw.text((x - 1, y), text, fill=fill, font=font)
    draw.text((x + 1, y), text, fill=fill, font=font)
    draw.text((x, y - 1), text, fill=fill, font=font)
    draw.text((x, y + 1), text, fill=fill, font=font)
    draw.text((x, y), text, fill=fill, font=font)


def generate_highlights_image(news_list: list[dict], date_str: str) -> Image.Image:
    img = Image.new("RGB", (W, H), (245, 247, 250))
    draw = ImageDraw.Draw(img)
    _draw_gradient_bg(draw, W, H)

    font_small = get_font(20)
    font_title = get_font(80)
    font_date = get_font(28)
    font_cat = get_font(24)
    font_item_title = get_font(40)
    font_item_desc = get_font(22)
    font_footer = get_font(26)
    font_tiny = get_font(18)
    font_brand = get_font(30)

    draw.text((60, 40), "AI 早报", fill=(80, 80, 85), font=font_small)
    draw.text((W - 160, 40), "DAILY BRIEF", fill=(150, 150, 155), font=font_small)
    draw.line([(60, 73), (W - 60, 73)], fill=(230, 230, 235), width=1)

    _draw_text_bold(draw, (60, 95), "AI早报", fill=(0, 0, 0), font=font_title)
    draw.text((60, 185), date_str, fill=(110, 110, 115), font=font_date)
    draw.line([(60, 175), (200, 175)], fill=(0, 122, 255), width=3)

    tag_y = 215
    tags = ["10 秒速览", "Agent · 推理 · 算力"]
    tag_x = 60
    for tag in tags:
        tw = len(tag) * 14 + 40
        draw.rounded_rectangle(
            [(tag_x, tag_y), (tag_x + tw, tag_y + 36)],
            radius=18, fill=(235, 235, 240), outline=(220, 220, 225), width=1,
        )
        draw.text((tag_x + 18, tag_y + 7), tag, fill=(70, 70, 75), font=font_small)
        tag_x += tw + 12

    font_section = get_font(42)
    draw.text((60, 280), "今日看点", fill=(0, 0, 0), font=font_section)
    draw.line([(60, 335), (200, 335)], fill=(0, 122, 255), width=3)

    card_h = 290
    start_y = 360
    gap_y = 20

    for i, item in enumerate(news_list[:3]):
        y = start_y + i * (card_h + gap_y)

        draw.rounded_rectangle(
            [(52, y + 3), (W - 48, y + card_h)],
            radius=28, fill=(235, 237, 240),
        )
        draw.rounded_rectangle(
            [(50, y), (W - 50, y + card_h)],
            radius=28, fill=(255, 255, 255), outline=(230, 230, 235), width=1,
        )

        cx, cy = 85, y + 32
        draw.ellipse([(cx, cy), (cx + 52, cy + 52)], outline=(200, 200, 205), width=2)
        draw.text((cx + 12, cy + 10), f"{i + 1:02d}", fill=(110, 110, 115), font=get_font(20))

        cat_color = _hex_to_rgb(item.get("category_color", "#007AFF"))
        cat_x = 155
        draw.ellipse([(cat_x, cy + 14), (cat_x + 16, cy + 30)], fill=cat_color)
        draw.text((cat_x + 22, cy + 12), item.get("category", ""), fill=(70, 70, 75), font=font_cat)
        _draw_text_bold(draw, (cat_x, cy + 48), item.get("title", ""), fill=(10, 10, 12), font=font_item_title)
        draw.text((cat_x, cy + 92), item.get("brief", ""), fill=(110, 110, 115), font=font_item_desc)

    banner_y = H - 210
    draw.rounded_rectangle(
        [(50, banner_y), (W - 50, banner_y + 68)],
        radius=20, fill=(0, 122, 255),
    )
    draw.text(
        (W // 2 - 190, banner_y + 18),
        "16 条 AI 要闻 · 2 页速览 · 10 秒看完",
        fill=(255, 255, 255), font=font_footer,
    )
    draw.text(
        (W // 2 - 120, banner_y + 46),
        "不构成任何建议，仅供信息参考",
        fill=(180, 210, 255), font=font_tiny,
    )

    _draw_text_bold(draw, (W // 2 - 65, H - 95), "米桶 AI", fill=(0, 122, 255), font=font_brand)
    draw.text((W // 2 - 55, H - 58), "Daily Brief", fill=(140, 140, 145), font=font_small)

    return img


def save_highlights_image(news_list: list[dict], date_str: str) -> Path:
    """Generate and save the highlights image to output/YYYY-MM-DD/highlights.png."""
    date_part = date_str.split()[0].replace(".", "-")
    out_dir = Path("output") / date_part
    out_dir.mkdir(parents=True, exist_ok=True)
    img = generate_highlights_image(news_list, date_str)
    out_path = out_dir / "highlights.png"
    img.save(str(out_path), quality=95)
    logger.info("Saved highlights image to %s", out_path)
    return out_path
