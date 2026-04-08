"""MoviePy 影片合成引擎"""

import logging
from pathlib import Path

import numpy as np
from moviepy import (
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    VideoFileClip,
    concatenate_videoclips,
)

from config.settings import settings
from src.composer.layout import get_canvas_size
from src.composer.text_effects import (
    create_disclaimer_frame,
    create_highlight_frame,
    create_subtitle_frame,
)
from src.models.schema import ProjectAssets, Scene

logger = logging.getLogger(__name__)


def render_shorts(project: ProjectAssets, output_path: Path | None = None) -> Path:
    """合成最終 Shorts 影片。

    Args:
        project: 包含腳本和所有素材的 ProjectAssets
        output_path: 輸出路徑，預設自動生成

    Returns:
        輸出的影片路徑
    """
    if output_path is None:
        output_dir = settings.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{project.script.angle.value}_{project.script.title[:10]}.mp4"

    width, height = get_canvas_size()
    fps = settings.video_fps

    scene_clips = []

    for i, scene in enumerate(project.script.scenes):
        scene_asset = next(
            (a for a in project.scene_assets if a.scene_id == scene.scene_id),
            None,
        )

        clip = _build_scene_clip(scene, scene_asset, width, height, fps)
        scene_clips.append(clip)

    # 串接所有場景
    main_video = concatenate_videoclips(scene_clips, method="compose")

    # 加上免責聲明（全程顯示）
    disclaimer_frame = create_disclaimer_frame(width, height)
    disclaimer_clip = (
        ImageClip(disclaimer_frame, is_mask=False)
        .with_duration(main_video.duration)
    )

    # 合成最終影片
    final = CompositeVideoClip(
        [main_video, disclaimer_clip],
        size=(width, height),
    )

    # 加入背景音樂
    audio_clips = []

    # 場景語音
    for scene_asset in project.scene_assets:
        if scene_asset.voice_path and scene_asset.voice_path.exists():
            voice_clip = AudioFileClip(str(scene_asset.voice_path))
            # 計算此場景的起始時間
            start_time = sum(
                s.duration
                for s in project.script.scenes
                if s.scene_id < scene_asset.scene_id
            )
            audio_clips.append(voice_clip.with_start(start_time))

    # 背景音樂
    if project.music_path and project.music_path.exists():
        music = (
            AudioFileClip(str(project.music_path))
            .subclipped(0, min(final.duration, AudioFileClip(str(project.music_path)).duration))
            .with_volume_scaled(0.15)  # 背景音樂音量較低
        )
        audio_clips.append(music)

    if audio_clips:
        final_audio = CompositeAudioClip(audio_clips)
        final = final.with_audio(final_audio)

    # 輸出
    logger.info("輸出影片: %s", output_path)
    final.write_videofile(
        str(output_path),
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4,
    )

    # 清理
    final.close()
    for clip in scene_clips:
        clip.close()

    logger.info("影片完成: %s (%.1f秒)", output_path, final.duration)
    return output_path


def _build_scene_clip(
    scene: Scene,
    scene_asset,
    width: int,
    height: int,
    fps: int,
) -> CompositeVideoClip:
    """建構單一場景的合成片段。"""
    duration = scene.duration

    # 底層：AI 生成的影片或黑底
    if scene_asset and scene_asset.video_path and scene_asset.video_path.exists():
        bg = (
            VideoFileClip(str(scene_asset.video_path))
            .resized((width, height))
            .subclipped(0, min(duration, VideoFileClip(str(scene_asset.video_path)).duration))
        )
        # 如果影片比場景短，循環播放
        if bg.duration < duration:
            loops = int(duration / bg.duration) + 1
            bg = concatenate_videoclips([bg] * loops).subclipped(0, duration)
    else:
        # 黑底 fallback
        bg = ImageClip(
            np.zeros((height, width, 3), dtype=np.uint8),
            is_mask=False,
        ).with_duration(duration)

    # 字幕層（帶動畫）
    def make_subtitle_frame(t):
        progress = min(1.0, t / 0.5)  # 0.5 秒內完成進場動畫
        return create_subtitle_frame(
            scene.narration, scene.subtitle_highlight,
            width, height, progress,
        )

    subtitle_clip = (
        ImageClip(make_subtitle_frame(0), is_mask=False)
        .with_duration(duration)
        .with_effects([lambda clip: clip.with_make_frame(
            lambda t: create_subtitle_frame(
                scene.narration, scene.subtitle_highlight,
                width, height, min(1.0, t / 0.5),
            )
        )])
    )

    # 重點關鍵字（場景中段 1 秒顯示）
    highlight_start = duration * 0.3
    highlight_duration = min(2.0, duration * 0.4)

    def make_highlight_frame(t):
        progress = min(1.0, t / 0.3)
        return create_highlight_frame(
            scene.subtitle_highlight, width, height, progress,
        )

    highlight_clip = (
        ImageClip(make_highlight_frame(0), is_mask=False)
        .with_duration(highlight_duration)
        .with_start(highlight_start)
    )

    return CompositeVideoClip(
        [bg, subtitle_clip, highlight_clip],
        size=(width, height),
    ).with_duration(duration)
