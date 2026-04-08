"""Whisper 語音轉文字模組"""

import logging
from pathlib import Path

import whisper

from config.settings import settings
from src.models.schema import Transcript, TranscriptSegment

logger = logging.getLogger(__name__)

_model = None


def _get_model():
    """延遲載入 Whisper 模型。"""
    global _model
    if _model is None:
        logger.info("載入 Whisper 模型: %s", settings.whisper_model)
        _model = whisper.load_model(settings.whisper_model)
    return _model


def transcribe(audio_path: Path, language: str | None = None) -> Transcript:
    """將音頻檔案轉錄為文字。

    Args:
        audio_path: 音頻檔案路徑（MP3、WAV 等）
        language: 指定語言代碼（如 "zh", "en"），None 為自動偵測

    Returns:
        Transcript 物件，含完整文字和分段時間軸
    """
    model = _get_model()

    options = {}
    if language:
        options["language"] = language

    logger.info("開始轉錄: %s", audio_path)
    result = model.transcribe(str(audio_path), **options)

    segments = [
        TranscriptSegment(
            start=seg["start"],
            end=seg["end"],
            text=seg["text"].strip(),
        )
        for seg in result["segments"]
    ]

    transcript = Transcript(
        language=result.get("language", ""),
        full_text=result["text"].strip(),
        segments=segments,
    )

    logger.info(
        "轉錄完成: 語言=%s, 段落數=%d, 總字數=%d",
        transcript.language,
        len(transcript.segments),
        len(transcript.full_text),
    )
    return transcript
