"""多角度腳本生成模組"""

import json
import logging
from pathlib import Path

import anthropic

from config.settings import settings, ROOT_DIR
from src.models.schema import CopyAngle, Script

logger = logging.getLogger(__name__)

PROMPTS_DIR = ROOT_DIR / "config" / "prompts"


def _load_prompt(angle: CopyAngle) -> str:
    """載入對應角度的 prompt template。"""
    prompt_file = PROMPTS_DIR / f"{angle.value}.txt"
    return prompt_file.read_text(encoding="utf-8")


def generate_script(summary: str, angle: CopyAngle) -> Script:
    """用 Claude API 生成指定角度的腳本。

    Args:
        summary: 影片摘要文字
        angle: 文案角度（fear/greed/trending）

    Returns:
        Script 物件
    """
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    prompt_template = _load_prompt(angle)
    prompt = prompt_template.replace("{summary}", summary)

    logger.info("生成 %s 角度腳本...", angle.value)

    message = client.messages.create(
        model=settings.claude_model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text

    # 從回應中提取 JSON
    json_str = _extract_json(response_text)
    script_data = json.loads(json_str)
    script_data["angle"] = angle.value

    script = Script(**script_data)
    logger.info(
        "腳本生成完成: %s, 場景數=%d, 總時長=%.1fs",
        script.title,
        len(script.scenes),
        script.total_duration,
    )
    return script


def generate_all_scripts(summary: str, angles: list[CopyAngle] | None = None) -> list[Script]:
    """生成所有角度的腳本。

    Args:
        summary: 影片摘要
        angles: 要生成的角度列表，預設全部

    Returns:
        Script 列表
    """
    if angles is None:
        angles = list(CopyAngle)

    scripts = []
    for angle in angles:
        script = generate_script(summary, angle)
        scripts.append(script)

    return scripts


def _extract_json(text: str) -> str:
    """從 LLM 回應中提取 JSON 字串。"""
    # 嘗試找 ```json ... ``` 區塊
    if "```json" in text:
        start = text.index("```json") + 7
        end = text.index("```", start)
        return text[start:end].strip()

    # 嘗試找 ``` ... ``` 區塊
    if "```" in text:
        start = text.index("```") + 3
        end = text.index("```", start)
        return text[start:end].strip()

    # 嘗試找第一個 { 和最後一個 }
    start = text.index("{")
    end = text.rindex("}") + 1
    return text[start:end]
