"""9:16 直式影片版面配置"""

from config.settings import settings

# 畫面區域定義（以 1080x1920 為基準）
LAYOUT = {
    # 上方標題/字幕區
    "subtitle": {
        "y_ratio": 0.08,       # 起始 y 比例
        "height_ratio": 0.30,  # 佔畫面高度比例
    },
    # 中間主視覺區（AI 生成的影片）
    "visual": {
        "y_ratio": 0.15,
        "height_ratio": 0.55,
    },
    # 重點關鍵字區（大字衝擊）
    "highlight": {
        "y_ratio": 0.35,
        "height_ratio": 0.20,
    },
    # 底部免責聲明
    "disclaimer": {
        "y_ratio": 0.90,
        "height_ratio": 0.08,
    },
}


def get_canvas_size() -> tuple[int, int]:
    """取得畫布尺寸 (width, height)。"""
    return settings.video_width, settings.video_height


def get_region_bounds(region: str) -> tuple[int, int, int, int]:
    """取得指定區域的邊界 (x, y, width, height)。"""
    w, h = get_canvas_size()
    config = LAYOUT[region]
    y = int(h * config["y_ratio"])
    region_h = int(h * config["height_ratio"])
    return 0, y, w, region_h
