"""AI 影片生成模組 - Veo 3.1 + Nano Banana"""

import logging
import time
from pathlib import Path

import requests
from google import genai

from config.settings import settings

logger = logging.getLogger(__name__)


class VeoGenerator:
    """Google Veo 3.1 影片生成。"""

    def __init__(self):
        self.client = genai.Client(api_key=settings.google_api_key)

    def generate(
        self,
        prompt: str,
        output_path: Path,
        duration: int = 8,
        aspect_ratio: str = "9:16",
    ) -> Path:
        """生成影片片段。

        Args:
            prompt: 英文畫面描述
            output_path: 輸出路徑
            duration: 時長（秒），支援 4/6/8
            aspect_ratio: 畫面比例

        Returns:
            生成的影片路徑
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 限制 duration 為 Veo 支援的值
        valid_durations = [4, 6, 8]
        duration = min(valid_durations, key=lambda x: abs(x - duration))

        logger.info("Veo 3.1 生成中: %.30s... (%ds)", prompt, duration)

        operation = self.client.models.generate_videos(
            model=settings.veo_model,
            prompt=prompt,
            config={
                "aspect_ratio": aspect_ratio,
                "resolution": "1080p",
                "duration_seconds": duration,
                "person_generation": "allow_all",
                "generate_audio": False,
            },
        )

        # 等待生成完成
        while not operation.done:
            time.sleep(5)
            operation = self.client.operations.get(operation)

        # 下載影片
        video = operation.result.generated_videos[0]
        video_data = self.client.files.download(file=video.video)
        output_path.write_bytes(video_data)

        logger.info("Veo 影片已生成: %s", output_path)
        return output_path


class NanoBananaGenerator:
    """Nano Banana 影片生成（備選方案）。"""

    BASE_URL = "https://api.nanobananavideo.com/v1"

    def __init__(self):
        self.api_key = settings.nano_banana_api_key

    def generate(
        self,
        prompt: str,
        output_path: Path,
        duration: int = 8,
        aspect_ratio: str = "9:16",
    ) -> Path:
        """生成影片片段。"""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "resolution": "1080p",
        }

        logger.info("Nano Banana 生成中: %.30s... (%ds)", prompt, duration)

        # 提交生成任務
        resp = requests.post(
            f"{self.BASE_URL}/generate",
            json=payload,
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        task_id = resp.json()["task_id"]

        # 輪詢等待完成
        while True:
            status_resp = requests.get(
                f"{self.BASE_URL}/tasks/{task_id}",
                headers=headers,
                timeout=30,
            )
            status_resp.raise_for_status()
            status = status_resp.json()

            if status["status"] == "completed":
                video_url = status["video_url"]
                break
            elif status["status"] == "failed":
                raise RuntimeError(f"Nano Banana 生成失敗: {status.get('error')}")

            time.sleep(5)

        # 下載影片
        video_resp = requests.get(video_url, timeout=120)
        video_resp.raise_for_status()
        output_path.write_bytes(video_resp.content)

        logger.info("Nano Banana 影片已生成: %s", output_path)
        return output_path


def generate_scene_videos(
    scenes: list[dict],
    output_dir: Path,
    provider: str = "veo",
) -> list[dict]:
    """為每個場景生成影片。

    Args:
        scenes: 場景列表，每項含 scene_id, prompt, duration
        output_dir: 輸出目錄
        provider: 使用的生成器 ("veo" 或 "nano_banana")

    Returns:
        包含 scene_id 和 video_path 的列表
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    if provider == "veo":
        generator = VeoGenerator()
    else:
        generator = NanoBananaGenerator()

    results = []
    for scene in scenes:
        scene_id = scene["scene_id"]
        output_path = output_dir / f"video_scene_{scene_id:02d}.mp4"

        generator.generate(
            prompt=scene["prompt"],
            output_path=output_path,
            duration=int(scene["duration"]),
        )
        results.append({
            "scene_id": scene_id,
            "video_path": output_path,
        })

    return results
