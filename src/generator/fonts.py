"""Font loader with cross-platform Chinese font support."""

import os
from PIL import ImageFont

FONT_CANDIDATES = [
    # macOS
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/PingFang SC.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    # Linux - Noto CJK
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    # Linux - WenQuanYi
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    # Linux - DejaVu (fallback, no CJK)
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    # Windows
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/simsun.ttc",
]

_FONT_PATH = None


def _find_font() -> str | None:
    """Find the first usable Chinese font."""
    global _FONT_PATH
    if _FONT_PATH is not None:
        return _FONT_PATH

    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                # Test load the font
                ImageFont.truetype(path, 20)
                _FONT_PATH = path
                print(f"[fonts] Using font: {path}")
                return path
            except Exception as e:
                print(f"[fonts] Found but failed to load: {path} ({e})")
                continue

    # Last resort: search with fc-list on Linux
    try:
        import subprocess
        result = subprocess.run(
            ["fc-list", ":lang=zh", "file"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout:
            for line in result.stdout.strip().split("\n"):
                path = line.split(":")[0].strip()
                if os.path.exists(path):
                    try:
                        ImageFont.truetype(path, 20)
                        _FONT_PATH = path
                        print(f"[fonts] Using fc-list font: {path}")
                        return path
                    except Exception:
                        continue
    except Exception:
        pass

    _FONT_PATH = ""
    print("[fonts] WARNING: No Chinese font found! Text will be garbled.")
    return None


def get_font(size: int):
    """Get a font at the given size. Falls back to default if no CJK font found."""
    path = _find_font()
    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception as e:
            print(f"[fonts] Error loading font at size {size}: {e}")
    return ImageFont.load_default()
