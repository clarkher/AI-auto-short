"""Claude API 文字摘要模組"""

import logging

import anthropic

from config.settings import settings

logger = logging.getLogger(__name__)


def summarize(text: str, max_length: int = 2000) -> str:
    """用 Claude API 摘要長文本。

    Args:
        text: 要摘要的長文本（轉錄稿）
        max_length: 摘要目標字數上限

    Returns:
        摘要後的文字
    """
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    prompt = f"""你是一位專業的財經內容分析師。請將以下長影片轉錄稿摘要為精華重點。

要求：
1. 保留所有關鍵數據、論點和結論
2. 標記出最有衝擊力的觀點（適合做成短影片的素材）
3. 摘要控制在 {max_length} 字以內
4. 使用繁體中文
5. 分段整理，每段標注主題

轉錄稿內容：
{text}"""

    message = client.messages.create(
        model=settings.claude_model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    summary = message.content[0].text
    logger.info("摘要完成: 原文 %d 字 → 摘要 %d 字", len(text), len(summary))
    return summary
