"""yt-dlp 影片下載模組"""

import logging
from pathlib import Path

import yt_dlp

from config.settings import settings

logger = logging.getLogger(__name__)


def download_audio(url: str, output_dir: Path | None = None) -> Path:
    """從影片 URL 下載音頻檔案（MP3）。

    Args:
        url: 影片 URL（支援 YouTube、各大平台）
        output_dir: 輸出目錄，預設使用 temp_dir

    Returns:
        下載後的音頻檔案路徑
    """
    output_dir = output_dir or settings.temp_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    output_template = str(output_dir / "%(id)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info["id"]
        audio_path = output_dir / f"{video_id}.mp3"
        logger.info("音頻已下載: %s", audio_path)
        return audio_path


def download_video(url: str, output_dir: Path | None = None) -> Path:
    """從 URL 下載完整影片。

    Args:
        url: 影片 URL
        output_dir: 輸出目錄

    Returns:
        下載後的影片檔案路徑
    """
    output_dir = output_dir or settings.temp_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    output_template = str(output_dir / "%(id)s.%(ext)s")

    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": "mp4",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info["id"]
        video_path = output_dir / f"{video_id}.mp4"
        logger.info("影片已下載: %s", video_path)
        return video_path


def get_video_info(url: str) -> dict:
    """取得影片資訊（不下載）。"""
    ydl_opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)
