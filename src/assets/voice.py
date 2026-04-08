"""Inworld AI TTS 語音合成模組"""

import logging
from pathlib import Path

import requests

from config.settings import settings

logger = logging.getLogger(__name__)

INWORLD_TTS_URL = "https://voice.inworld.ai/v1/tts"


def synthesize_speech(
    text: str,
    output_path: Path,
    voice_id: str | None = None,
) -> Path:
    """用 Inworld AI TTS 將文字合成語音。

    Args:
        text: 要合成的文字
        output_path: 輸出音頻檔案路徑
        voice_id: 語音 ID（使用已訓練的語音模型）

    Returns:
        生成的音頻檔案路徑
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.inworld_api_key}",
    }

    payload = {
        "text": text,
        "model": settings.inworld_tts_model,
        "output_format": "mp3",
    }
    if voice_id:
        payload["voice_id"] = voice_id

    logger.info("TTS 合成中: %d 字...", len(text))
    response = requests.post(INWORLD_TTS_URL, json=payload, headers=headers, timeout=120)
    response.raise_for_status()

    output_path.write_bytes(response.content)
    logger.info("語音已生成: %s", output_path)
    return output_path


def synthesize_scenes(
    scenes: list[dict],
    output_dir: Path,
    voice_id: str | None = None,
) -> list[dict]:
    """為每個場景生成語音。

    Args:
        scenes: 場景列表，每項需含 scene_id 和 narration
        output_dir: 輸出目錄
        voice_id: 語音 ID

    Returns:
        包含 scene_id 和 voice_path 的列表
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []

    for scene in scenes:
        scene_id = scene["scene_id"]
        narration = scene["narration"]
        output_path = output_dir / f"voice_scene_{scene_id:02d}.mp3"

        synthesize_speech(narration, output_path, voice_id)
        results.append({
            "scene_id": scene_id,
            "voice_path": output_path,
        })

    return results
