"""CLI 命令列介面"""

import json
import logging
import sys
from typing import Optional

import typer

from src.pipeline import run_full_pipeline, preview_scripts

app = typer.Typer(
    name="ai-short",
    help="AI Auto Shorts - 自動化生成 YouTube Shorts 短影片",
)


def _setup_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


@app.command()
def generate(
    url: Optional[str] = typer.Argument(None, help="影片 URL"),
    transcript: Optional[str] = typer.Option(None, "--transcript", "-t", help="文字稿檔案路徑"),
    angles: str = typer.Option("fear", "--angles", "-a", help="文案角度，逗號分隔 (fear,greed,trending)"),
    provider: str = typer.Option("veo", "--provider", "-p", help="影片生成服務 (veo/nano_banana)"),
    voice_id: Optional[str] = typer.Option(None, "--voice-id", help="Inworld AI 語音 ID"),
    skip_video: bool = typer.Option(False, "--skip-video", help="跳過 AI 影片生成（用黑底）"),
    skip_voice: bool = typer.Option(False, "--skip-voice", help="跳過 AI 語音生成"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="詳細輸出"),
):
    """從影片 URL 或文字稿生成 Shorts 短影片。"""
    _setup_logging(verbose)

    if not url and not transcript:
        typer.echo("錯誤：必須提供影片 URL 或 --transcript 文字稿路徑", err=True)
        raise typer.Exit(1)

    angle_list = [a.strip() for a in angles.split(",")]

    typer.echo(f"🎬 AI Auto Shorts 開始生成...")
    typer.echo(f"   角度: {', '.join(angle_list)}")
    typer.echo(f"   影片生成: {'跳過' if skip_video else provider}")
    typer.echo(f"   語音生成: {'跳過' if skip_voice else 'Inworld AI'}")
    typer.echo()

    output_paths = run_full_pipeline(
        url=url,
        transcript_path=transcript,
        angles=angle_list,
        video_provider=provider,
        voice_id=voice_id,
        skip_video_gen=skip_video,
        skip_voice_gen=skip_voice,
    )

    typer.echo()
    typer.echo("✅ 生成完成！")
    for path in output_paths:
        typer.echo(f"   📹 {path}")


@app.command()
def preview(
    url: Optional[str] = typer.Argument(None, help="影片 URL"),
    transcript: Optional[str] = typer.Option(None, "--transcript", "-t", help="文字稿檔案路徑"),
    angles: str = typer.Option("fear", "--angles", "-a", help="文案角度，逗號分隔"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="詳細輸出"),
):
    """預覽生成的腳本（不生成影片）。"""
    _setup_logging(verbose)

    if not url and not transcript:
        typer.echo("錯誤：必須提供影片 URL 或 --transcript 文字稿路徑", err=True)
        raise typer.Exit(1)

    angle_list = [a.strip() for a in angles.split(",")]

    typer.echo("📝 預覽腳本生成中...")
    scripts = preview_scripts(
        url=url,
        transcript_path=transcript,
        angles=angle_list,
    )

    for script in scripts:
        typer.echo(f"\n{'='*60}")
        typer.echo(f"📌 角度: {script.angle.value}")
        typer.echo(f"📌 標題: {script.title}")
        typer.echo(f"📌 Hook: {script.hook}")
        typer.echo(f"📌 總時長: {script.total_duration:.1f}s")
        typer.echo(f"📌 場景數: {len(script.scenes)}")
        typer.echo(f"{'='*60}")

        for scene in script.scenes:
            typer.echo(f"\n  場景 {scene.scene_id} ({scene.duration}s):")
            typer.echo(f"  旁白: {scene.narration}")
            typer.echo(f"  重點: {scene.subtitle_highlight}")
            typer.echo(f"  畫面: {scene.visual_prompt[:80]}...")

        # 也輸出 JSON
        typer.echo(f"\n--- JSON ---")
        typer.echo(script.model_dump_json(indent=2))


if __name__ == "__main__":
    app()
