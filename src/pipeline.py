"""主流程編排 - 串接所有模組"""

import logging
from pathlib import Path

from config.settings import settings
from src.models.schema import CopyAngle, ProjectAssets, SceneAssets, Script
from src.transcriber.downloader import download_audio
from src.transcriber.whisper import transcribe
from src.transcriber.summarizer import summarize
from src.copywriter.script_gen import generate_script, generate_all_scripts
from src.copywriter.scene_parser import validate_script_timing, get_visual_prompts
from src.assets.voice import synthesize_scenes
from src.assets.video_gen import generate_scene_videos
from src.assets.music import select_track, get_mood_for_angle
from src.composer.renderer import render_shorts

logger = logging.getLogger(__name__)


def run_full_pipeline(
    url: str | None = None,
    transcript_path: str | None = None,
    angles: list[str] | None = None,
    video_provider: str = "veo",
    voice_id: str | None = None,
    skip_video_gen: bool = False,
    skip_voice_gen: bool = False,
) -> list[Path]:
    """執行完整的 Shorts 生成流程。

    Args:
        url: 影片 URL
        transcript_path: 已有的文字稿路徑（與 url 二擇一）
        angles: 文案角度列表，如 ["fear", "greed"]
        video_provider: 影片生成服務 ("veo" 或 "nano_banana")
        voice_id: Inworld AI 語音 ID
        skip_video_gen: 跳過影片生成（用黑底替代）
        skip_voice_gen: 跳過語音生成

    Returns:
        生成的影片路徑列表
    """
    # 解析角度
    copy_angles = [CopyAngle(a) for a in (angles or ["fear"])]

    # Step 1: 取得文字稿
    if transcript_path:
        logger.info("使用提供的文字稿: %s", transcript_path)
        full_text = Path(transcript_path).read_text(encoding="utf-8")
    elif url:
        logger.info("Step 1: 下載影片並轉錄...")
        audio_path = download_audio(url)
        transcript = transcribe(audio_path)
        full_text = transcript.full_text
    else:
        raise ValueError("必須提供 url 或 transcript_path")

    # Step 2: 摘要
    logger.info("Step 2: 生成摘要...")
    summary = summarize(full_text)
    logger.info("摘要完成 (%d 字)", len(summary))

    # Step 3: 生成腳本
    logger.info("Step 3: 生成腳本 (%s)...", ", ".join(a.value for a in copy_angles))
    scripts = generate_all_scripts(summary, copy_angles)

    # Step 4-6: 為每個腳本生成素材和影片
    output_paths = []
    for script in scripts:
        script = validate_script_timing(script, settings.target_duration)
        output_path = _process_single_script(
            script, video_provider, voice_id,
            skip_video_gen, skip_voice_gen,
        )
        output_paths.append(output_path)

    logger.info("全部完成！共生成 %d 支影片", len(output_paths))
    return output_paths


def _process_single_script(
    script: Script,
    video_provider: str,
    voice_id: str | None,
    skip_video_gen: bool,
    skip_voice_gen: bool,
) -> Path:
    """處理單一腳本：素材生成 → 合成影片。"""
    work_dir = settings.temp_dir / script.angle.value
    work_dir.mkdir(parents=True, exist_ok=True)

    scene_assets = []

    # 生成語音
    if not skip_voice_gen:
        logger.info("Step 4: 生成語音 (%s)...", script.angle.value)
        voice_results = synthesize_scenes(
            [{"scene_id": s.scene_id, "narration": s.narration} for s in script.scenes],
            work_dir / "voice",
            voice_id,
        )
    else:
        voice_results = []

    # 生成影片素材
    if not skip_video_gen:
        logger.info("Step 5: 生成影片素材 (%s)...", script.angle.value)
        video_results = generate_scene_videos(
            get_visual_prompts(script),
            work_dir / "video",
            video_provider,
        )
    else:
        video_results = []

    # 組裝 SceneAssets
    for scene in script.scenes:
        voice_info = next(
            (v for v in voice_results if v["scene_id"] == scene.scene_id),
            None,
        )
        video_info = next(
            (v for v in video_results if v["scene_id"] == scene.scene_id),
            None,
        )
        scene_assets.append(SceneAssets(
            scene_id=scene.scene_id,
            voice_path=voice_info["voice_path"] if voice_info else None,
            video_path=video_info["video_path"] if video_info else None,
        ))

    # 選取背景音樂
    mood = get_mood_for_angle(script.angle.value)
    music_path = select_track(mood)

    # 組裝 ProjectAssets
    project = ProjectAssets(
        script=script,
        scene_assets=scene_assets,
        music_path=music_path,
    )

    # 合成最終影片
    logger.info("Step 6: 合成影片 (%s)...", script.angle.value)
    output_path = render_shorts(project)
    project.output_path = output_path

    return output_path


def preview_scripts(
    url: str | None = None,
    transcript_path: str | None = None,
    angles: list[str] | None = None,
) -> list[Script]:
    """預覽腳本（不生成影片）。"""
    copy_angles = [CopyAngle(a) for a in (angles or ["fear"])]

    if transcript_path:
        full_text = Path(transcript_path).read_text(encoding="utf-8")
    elif url:
        audio_path = download_audio(url)
        transcript = transcribe(audio_path)
        full_text = transcript.full_text
    else:
        raise ValueError("必須提供 url 或 transcript_path")

    summary = summarize(full_text)
    scripts = generate_all_scripts(summary, copy_angles)

    for script in scripts:
        script = validate_script_timing(script, settings.target_duration)

    return scripts
