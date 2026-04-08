"""應用程式設定管理"""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
    )

    # Claude API
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-20250514"

    # Inworld AI TTS
    inworld_api_key: str = ""
    inworld_tts_model: str = "tts-1.5-mini"

    # Google Veo 3.1
    google_project_id: str = ""
    google_api_key: str = ""
    veo_model: str = "veo-3.1-generate-001"

    # Nano Banana
    nano_banana_api_key: str = ""

    # Whisper
    whisper_model: str = "base"  # tiny, base, small, medium, large

    # 影片輸出設定
    output_dir: Path = Field(default=ROOT_DIR / "output")
    temp_dir: Path = Field(default=ROOT_DIR / "tmp")
    video_width: int = 1080
    video_height: int = 1920
    video_fps: int = 30
    target_duration: int = 60  # 秒

    # 字型
    font_path: str = str(ROOT_DIR / "assets" / "fonts" / "NotoSansTC-Bold.ttf")


settings = Settings()
