# Task 4+5: Apple 风格图片生成引擎

**项目**: 米桶 AI 每日资讯早报系统  
**工作目录**: `/Users/huang/Documents/Kimi/Workspaces/ai新闻收集`

实现两张 Apple 风格的信息图生成：
- 图片 1（详细版）: 1242×2208px, 8 条资讯, 2×4 网格
- 图片 2（今日看点）: 1242×1656px, 3 条重点资讯, 垂直卡片

## 前置依赖

Task 1-3 已完成。
- `from utils.logger import get_logger` → logging.Logger

## 输入数据格式

```python
{
    "title": str,
    "summary": str,
    "brief": str,
    "source_name": str,
    "category": str,        # e.g. "Agent"
    "category_color": str,  # e.g. "#007AFF"
    "score": int,
}
```

## 需要创建的文件

1. `src/generator/fonts.py` — 字体加载工具
2. `src/generator/detail_card.py` — 详细版图片生成
3. `src/generator/highlights_card.py` — 今日看点图片生成
4. `tests/test_generator.py` — 图片生成测试

## 设计规范

### 通用风格（Apple 风格）
- 背景色: `#F5F7FA`（浅灰白）
- 卡片: 纯白 `#FFFFFF`, 圆角 24-28px, 边框 `#EBEBF0`
- 分类圆点: 6-10px, 使用 category_color
- 标题字体: 黑色 `#141415`
- 描述字体: 灰色 `#505055`
- 底部品牌: "米桶 AI", 蓝色 `#007AFF`

### 详细版（1242×2208）
- 顶部栏: "AI 早报" + "DAILY BRIEF" + 分隔线
- 标题区: "AI早报" 大号 + "每日精选 · 10 秒速览" + 日期
- 右上角: 灰色药丸 "Top 16"
- 内容: 2 列 × 4 行 卡片网格
- 每张卡片: 彩色圆点 + 分类名 + 序号 + 标题 + 描述 + 简读 + 来源
- 底部: "米桶 AI · 不构成任何建议"

### 今日看点版（1242×1656）
- 顶部栏: 同上
- 标题区: "AI早报" 大号 + 日期 + 标签药丸
- 分区标题: "今日看点" + Apple Blue 下划线
- 内容: 3 条全宽垂直卡片
- 每张卡片: 大号序号圆圈(56px) + 彩色圆点 + 分类名 + 标题(34px) + 描述
- 底部横幅: Apple Blue 药丸 "16 条 AI 要闻 · 2 页速览 · 10 秒看完"
- 底部品牌: "米桶 AI" + "Daily Brief"

## 代码要求

### fonts.py

```python
import os
from PIL import ImageFont

FONT_CANDIDATES = [
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/PingFang SC.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]

FONT_PATH = None
for f in FONT_CANDIDATES:
    if os.path.exists(f):
        FONT_PATH = f
        break


def get_font(size: int):
    if FONT_PATH:
        try:
            return ImageFont.truetype(FONT_PATH, size)
        except Exception:
            pass
    return ImageFont.load_default()
```

### detail_card.py

核心函数：
- `generate_detail_image(news_list: list[dict], date_str: str) -> Image.Image`
- `save_detail_image(news_list: list[dict], date_str: str) -> Path`

实现要点：
- 使用 `PIL.Image.new('RGB', (1242, 2208), (245, 247, 250))`
- 顶部渐变：从纯白到 `#F5F7FA`
- 卡片用 `draw.rounded_rectangle()` 绘制
- 保存到 `output/YYYY-MM-DD/detail.png`

### highlights_card.py

核心函数：
- `generate_highlights_image(news_list: list[dict], date_str: str) -> Image.Image`
- `save_highlights_image(news_list: list[dict], date_str: str) -> Path`

实现要点：
- 使用 `PIL.Image.new('RGB', (1242, 1656), (245, 247, 250))`
- 底部横幅用 Apple Blue `#007AFF` 填充
- 保存到 `output/YYYY-MM-DD/highlights.png`

### 测试

```python
# tests/test_generator.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from generator.detail_card import generate_detail_image
from generator.highlights_card import generate_highlights_image


def test_generate_detail_image():
    news = [
        {
            "title": "Test News",
            "summary": "This is a test summary",
            "brief": "Brief text",
            "source_name": "Test Source",
            "category": "Agent",
            "category_color": "#007AFF",
        }
        for _ in range(8)
    ]
    img = generate_detail_image(news, "2026.07.31  星期五")
    assert img.size == (1242, 2208)
    assert img.mode == "RGB"


def test_generate_highlights_image():
    news = [
        {
            "title": "Highlight 1",
            "brief": "Brief 1",
            "category": "Agent",
            "category_color": "#007AFF",
        }
        for _ in range(3)
    ]
    img = generate_highlights_image(news, "2026.07.31")
    assert img.size == (1242, 1656)
```

## 执行步骤

1. 创建 `src/generator/fonts.py`
2. 创建 `src/generator/detail_card.py`
3. 创建 `src/generator/highlights_card.py`
4. 创建 `tests/test_generator.py`
5. 运行测试: `pytest tests/test_generator.py -v`
6. 提交: `git add -A && git commit -m "feat: Apple-style image generators (detail + highlights)"`

## 全局约束

- Python >= 3.10, Pillow >= 10.0
- 中文字体必须显式包含在字体栈中
- 图片输出目录: `output/YYYY-MM-DD/`
- 禁止硬编码密钥

---
**注意**: 严格按照上述规范实现。测试必须全部通过。可以参考已有的预览图代码（`design_preview/generate_apple.py`）获取绘制逻辑，但需适配到模块化结构中。
