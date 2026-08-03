"""Apple-style detail card image generator."""

from pathlib import Path
from PIL import Image, ImageDraw

from .fonts import get_font
from utils.logger import get_logger

logger = get_logger(__name__)

W, H = 1242, 2208
CARD_W, CARD_H = 540, 410
GAP_X, GAP_Y = 24, 20
COLS = 2


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


def generate_detail_image(news_list: list[dict], date_str: str) -> Image.Image:
    img = Image.new("RGB", (W, H), (245, 247, 250))
    draw = ImageDraw.Draw(img)
    _draw_gradient_bg(draw, W, H)

    font_brand = get_font(22)
    font_title = get_font(72)
    font_subtitle = get_font(28)
    font_date = get_font(22)
    font_card_title = get_font(28)
    font_card_desc = get_font(20)
    font_card_brief = get_font(18)
    font_card_src = get_font(14)
    font_num = get_font(16)
    font_badge = get_font(16)
    font_page = get_font(20)

    draw.text((60, 45), "AI 早报", fill=(0, 0, 0), font=font_brand)
    draw.text((W - 180, 45), "DAILY BRIEF", fill=(150, 150, 155), font=font_brand)
    draw.line([(60, 78), (W - 60, 78)], fill=(230, 230, 235), width=1)

    _draw_text_bold(draw, (60, 105), "AI早报", fill=(0, 0, 0), font=font_title)
    draw.text((60, 190), "每日精选 · 10 秒速览", fill=(110, 110, 115), font=font_subtitle)
    draw.text((60, 228), date_str, fill=(150, 150, 155), font=font_date)
    draw.line([(60, 175), (260, 175)], fill=(0, 122, 255), width=3)

    pill_x = W - 170
    draw.rounded_rectangle(
        [(pill_x, 115), (pill_x + 110, 150)],
        radius=20, fill=(240, 240, 245), outline=(220, 220, 225), width=1,
    )
    draw.text((pill_x + 22, 121), "Top 16", fill=(80, 80, 85), font=font_page)

    start_y = 275
    for i, news in enumerate(news_list[:8]):
        col = i % COLS
        row = i // COLS
        x = 50 + col * (CARD_W + GAP_X)
        y = start_y + row * (CARD_H + GAP_Y)

        draw.rounded_rectangle(
            [(x + 2, y + 3), (x + CARD_W, y + CARD_H)],
            radius=24, fill=(235, 237, 240),
        )
        draw.rounded_rectangle(
            [(x, y), (x + CARD_W, y + CARD_H)],
            radius=24, fill=(255, 255, 255), outline=(230, 230, 235), width=1,
        )

        cat_color = _hex_to_rgb(news.get("category_color", "#007AFF"))
        dot_x, dot_y = x + 22, y + 18
        draw.ellipse([(dot_x, dot_y), (dot_x + 14, dot_y + 14)], fill=cat_color)
        draw.text((dot_x + 20, dot_y + 1), news.get("category", ""), fill=(80, 80, 85), font=font_badge)
        draw.text((x + CARD_W - 32, y + 16), f"{i + 1:02d}", fill=(200, 200, 205), font=font_num)

        title_y = y + 52
        _draw_text_bold(draw, (x + 22, title_y), news.get("title", ""), fill=(10, 10, 12), font=font_card_title)

        desc_y = title_y + 38
        desc_text = news.get("summary", "")[:70]
        draw.text((x + 22, desc_y), desc_text, fill=(70, 70, 75), font=font_card_desc)

        brief_y = desc_y + 30
        brief = news.get("brief", "")
        if len(brief) > 85:
            brief = brief[:82] + "..."
        draw.text((x + 22, brief_y), brief, fill=(130, 130, 135), font=font_card_brief)

        draw.line(
            [(x + 22, y + CARD_H - 34), (x + CARD_W - 22, y + CARD_H - 34)],
            fill=(240, 240, 245), width=1,
        )
        draw.text((x + 22, y + CARD_H - 28), news.get("source_name", ""), fill=(160, 160, 165), font=font_card_src)

    font_footer = get_font(18)
    draw.text((W // 2 - 110, H - 55), "米桶 AI  ·  不构成任何建议", fill=(170, 170, 175), font=font_footer)

    return img


def save_detail_image(news_list: list[dict], date_str: str) -> Path:
    """Generate and save the detail image to output/YYYY-MM-DD/detail.png."""
    date_part = date_str.split()[0].replace(".", "-")
    out_dir = Path("output") / date_part
    out_dir.mkdir(parents=True, exist_ok=True)
    img = generate_detail_image(news_list, date_str)
    out_path = out_dir / "detail.png"
    img.save(str(out_path), quality=95)
    logger.info("Saved detail image to %s", out_path)
    return out_path
