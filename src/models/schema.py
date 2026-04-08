"""核心資料模型"""

from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field


class CopyAngle(str, Enum):
    """文案角度"""
    FEAR = "fear"
    GREED = "greed"
    TRENDING = "trending"


class TranscriptSegment(BaseModel):
    """轉錄片段"""
    start: float
    end: float
    text: str


class Transcript(BaseModel):
    """完整轉錄結果"""
    language: str = ""
    full_text: str = ""
    segments: list[TranscriptSegment] = []


class Scene(BaseModel):
    """單一場景分鏡"""
    scene_id: int
    narration: str = Field(description="旁白文字（中文）")
    visual_prompt: str = Field(description="畫面描述（英文，用於 AI 影片生成）")
    subtitle_highlight: str = Field(description="字幕重點文字（會以醒目樣式顯示）")
    duration: float = Field(description="場景時長（秒）")


class Script(BaseModel):
    """完整腳本"""
    title: str = Field(description="Shorts 標題")
    angle: CopyAngle
    hook: str = Field(description="開頭 hook（前 3 秒）")
    scenes: list[Scene]
    disclaimer: str = Field(
        default="免責聲明：以上內容僅供教育參考，不構成投資建議。投資涉及風險，如有需要請諮詢持牌投資顧問。"
    )
    total_duration: float = 0.0

    def model_post_init(self, __context):
        if not self.total_duration:
            self.total_duration = sum(s.duration for s in self.scenes)


class SceneAssets(BaseModel):
    """單一場景的已生成素材"""
    scene_id: int
    voice_path: Path | None = None
    video_path: Path | None = None
    voice_duration: float = 0.0


class ProjectAssets(BaseModel):
    """整個專案的素材集合"""
    script: Script
    scene_assets: list[SceneAssets] = []
    music_path: Path | None = None
    output_path: Path | None = None
