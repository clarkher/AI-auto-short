"""Chief PaPa 風格文字動態效果模組

效果規格：
1. 主標題：粗體白字 + 黑色描邊，置中上方 1/3
2. 重點關鍵字：黃色粗體 + 紅底框，強調效果
3. 動態進場：文字由小放大（zoom in）
4. 免責聲明：底部小字灰色，固定顯示
"""

import textwrap
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from config.settings import settings


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """載入字型，fallback 到系統預設。"""
    font_path = settings.font_path
    try:
        return ImageFont.truetype(font_path, size)
    except OSError:
        # Fallback: 嘗試系統字型
        fallbacks = [
            "C:/Windows/Fonts/msjhbd.ttc",  # 微軟正黑體粗體
            "C:/Windows/Fonts/msjh.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        ]
        for fb in fallbacks:
            try:
                return ImageFont.truetype(fb, size)
            except OSError:
                continue
        return ImageFont.load_default()


def create_subtitle_frame(
    text: str,
    highlight: str,
    width: int,
    height: int,
    progress: float = 1.0,
) -> np.ndarray:
    """建立單幀字幕圖片（透明背景）。

    Args:
        text: 完整字幕文字
        highlight: 要強調的關鍵字
        width: 畫面寬度
        height: 畫面高度
        progress: 動畫進度 0.0~1.0（用於縮放動畫）

    Returns:
        RGBA numpy array
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_size = int(72 * max(0.5, progress))
    font = _load_font(font_size)
    small_font = _load_font(36)

    # 文字自動換行
    max_chars = max(1, int(width / font_size * 1.5))
    lines = textwrap.wrap(text, width=max_chars)

    # 計算文字總高度
    line_height = font_size + 12
    total_text_height = line_height * len(lines)

    # 字幕位置：上方 1/3
    y_start = int(height * 0.15) - total_text_height // 2

    for i, line in enumerate(lines):
        y = y_start + i * line_height

        # 計算置中 x
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2

        if highlight and highlight in line:
            # 分段繪製：普通部分 + 高亮部分
            _draw_line_with_highlight(draw, x, y, line, highlight, font, width)
        else:
            # 白字 + 黑色描邊
            _draw_outlined_text(draw, x, y, line, font, fill="white", stroke="black")

    return np.array(img)


def create_highlight_frame(
    text: str,
    width: int,
    height: int,
    progress: float = 1.0,
) -> np.ndarray:
    """建立重點關鍵字大字幕（Chief PaPa 風格的衝擊性文字）。

    Args:
        text: 重點文字（2-6 字）
        width: 畫面寬度
        height: 畫面高度
        progress: 動畫進度

    Returns:
        RGBA numpy array
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 大字尺寸，帶縮放動畫
    base_size = 120
    scale = 0.3 + 0.7 * min(1.0, progress * 1.5)  # 快速放大效果
    font_size = int(base_size * scale)
    font = _load_font(font_size)

    # 計算位置（畫面中央偏上）
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = int(height * 0.4) - text_height // 2

    # 紅底黃字框
    padding = 20
    bg_rect = [
        x - padding,
        y - padding,
        x + text_width + padding,
        y + text_height + padding,
    ]

    # 透明度隨進度
    alpha = int(220 * min(1.0, progress * 2))
    draw.rectangle(bg_rect, fill=(200, 30, 30, alpha))

    # 黃色大字
    _draw_outlined_text(
        draw, x, y, text, font,
        fill=(255, 255, 0, 255),
        stroke=(0, 0, 0, 255),
        stroke_width=4,
    )

    return np.array(img)


def create_disclaimer_frame(width: int, height: int) -> np.ndarray:
    """建立免責聲明（底部灰色小字）。"""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font = _load_font(24)
    disclaimer = "免責聲明：以上內容僅供教育參考，不構成投資建議。\n投資涉及風險，如有需要請諮詢持牌投資顧問。"

    lines = disclaimer.split("\n")
    y = height - 100

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y), line, font=font, fill=(180, 180, 180, 200))
        y += 30

    return np.array(img)


def _draw_outlined_text(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill="white",
    stroke="black",
    stroke_width: int = 3,
):
    """繪製帶描邊的文字。"""
    draw.text(
        (x, y), text, font=font, fill=fill,
        stroke_width=stroke_width, stroke_fill=stroke,
    )


def _draw_line_with_highlight(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    line: str,
    highlight: str,
    font: ImageFont.FreeTypeFont,
    canvas_width: int,
):
    """繪製含高亮關鍵字的一行文字。"""
    idx = line.find(highlight)
    if idx == -1:
        _draw_outlined_text(draw, x, y, line, font)
        return

    before = line[:idx]
    after = line[idx + len(highlight):]

    # 繪製前段（白字）
    cursor_x = x
    if before:
        _draw_outlined_text(draw, cursor_x, y, before, font)
        bbox = draw.textbbox((0, 0), before, font=font)
        cursor_x += bbox[2] - bbox[0]

    # 繪製高亮字（黃字 + 底框）
    hl_bbox = draw.textbbox((0, 0), highlight, font=font)
    hl_w = hl_bbox[2] - hl_bbox[0]
    hl_h = hl_bbox[3] - hl_bbox[1]
    padding = 6
    draw.rectangle(
        [cursor_x - padding, y - padding, cursor_x + hl_w + padding, y + hl_h + padding],
        fill=(200, 30, 30, 200),
    )
    _draw_outlined_text(draw, cursor_x, y, highlight, font, fill=(255, 255, 0, 255))
    cursor_x += hl_w

    # 繪製後段（白字）
    if after:
        _draw_outlined_text(draw, cursor_x, y, after, font)
