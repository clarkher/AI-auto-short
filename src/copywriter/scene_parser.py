"""腳本場景解析工具"""

from src.models.schema import Script, Scene


def validate_script_timing(script: Script, target_duration: int = 60) -> Script:
    """驗證並調整腳本時長。

    如果總時長偏離目標太多，按比例調整每個場景的時長。

    Args:
        script: 原始腳本
        target_duration: 目標總時長（秒）

    Returns:
        調整後的腳本
    """
    total = script.total_duration
    tolerance = 10  # 允許 ±10 秒

    if abs(total - target_duration) <= tolerance:
        return script

    # 按比例調整
    ratio = target_duration / total
    for scene in script.scenes:
        scene.duration = round(scene.duration * ratio, 1)

    script.total_duration = sum(s.duration for s in script.scenes)
    return script


def get_all_narrations(script: Script) -> str:
    """取得完整旁白文字（用於 TTS）。"""
    return " ".join(scene.narration for scene in script.scenes)


def get_visual_prompts(script: Script) -> list[dict]:
    """取得所有場景的畫面描述（用於 AI 影片生成）。"""
    return [
        {
            "scene_id": scene.scene_id,
            "prompt": scene.visual_prompt,
            "duration": scene.duration,
        }
        for scene in script.scenes
    ]
