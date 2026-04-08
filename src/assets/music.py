"""背景音樂選取模組"""

import logging
import random
from pathlib import Path

from config.settings import settings, ROOT_DIR

logger = logging.getLogger(__name__)

MUSIC_DIR = ROOT_DIR / "assets" / "music"


def get_available_tracks() -> list[Path]:
    """取得所有可用的背景音樂檔案。"""
    if not MUSIC_DIR.exists():
        return []
    return sorted(MUSIC_DIR.glob("*.mp3")) + sorted(MUSIC_DIR.glob("*.wav"))


def select_track(mood: str = "neutral") -> Path | None:
    """根據情緒選取背景音樂。

    Args:
        mood: 情緒類型（"tense", "upbeat", "neutral"）

    Returns:
        音樂檔案路徑，無可用音樂時返回 None
    """
    tracks = get_available_tracks()
    if not tracks:
        logger.warning("沒有可用的背景音樂")
        return None

    # 嘗試匹配情緒關鍵字
    mood_tracks = [t for t in tracks if mood in t.stem.lower()]
    if mood_tracks:
        selected = random.choice(mood_tracks)
    else:
        selected = random.choice(tracks)

    logger.info("選取背景音樂: %s", selected.name)
    return selected


def get_mood_for_angle(angle: str) -> str:
    """根據文案角度決定音樂情緒。"""
    mood_map = {
        "fear": "tense",
        "greed": "upbeat",
        "trending": "neutral",
    }
    return mood_map.get(angle, "neutral")
