"""AI 内容生成 — 调用 LLM 生成小红书爆款内容。"""

from __future__ import annotations

from typing import Any

from rich.console import Console

from src.config import settings

console = Console()

SYSTEM_PROMPT = """你是一个小红书爆款笔记写作专家。你的任务是为主题生成一篇完整的、符合小红书流量算法的小红书笔记。

## 标题要求
- 使用爆款公式：数字+结果 / 反问共鸣 / 对比惊喜 / 身份经历 / 痛点方案 / 悬念揭秘
- 长度 15-20 字
- 包含 1-2 个 emoji

## 正文要求
- 前 2 行必须有 hook（钩子），激发点击欲望
- 分段清晰，每段 2-3 行，用 emoji 点缀
- 字数 400-800 字
- 口语化、真诚、有个人经历感
- 结尾引导互动（"你们觉得呢？"、"评论区告诉我"）

## 话题标签
- 5-8 个标签：3 个大词 + 3 个长尾词 + 品牌词

## 输出格式
以 JSON 格式输出:
{
  "title": "标题",
  "body": "正文（含 emoji 和分段）",
  "tags": ["标签1", "标签2"],
  "image_suggestions": ["封面图建议", "内页图建议"],
  "post_time_suggestion": "最佳发布时间建议"
}
"""


def generate_content(topic: str, context: str = "") -> dict[str, Any]:
    """为主题生成小红书内容。

    Args:
        topic: 内容主题
        context: 额外上下文信息

    Returns:
        包含 title, body, tags, image_suggestions 的字典
    """
    if not settings.llm_available:
        console.print("[yellow]⚠️  未配置 LLM API Key，使用模板生成[/yellow]")
        return _template_fallback(topic)

    try:
        import httpx

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"为主题生成一篇小红书笔记。\n"
                    f"主题：{topic}\n"
                    f"额外信息：{context}\n"
                    f"要求：爆款标题 + 种草风正文 + emoji + 标签 + 配图建议"
                ),
            },
        ]

        resp = httpx.post(
            f"{settings.llm_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.llm_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.llm_model,
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 2048,
            },
            timeout=60,
        )
        resp.raise_for_status()
        result = resp.json()
        content = result["choices"][0]["message"]["content"]

        # 尝试从返回中解析 JSON
        import json, re

        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {"title": topic, "body": content, "tags": [], "image_suggestions": []}

    except Exception as e:
        console.print(f"[yellow]⚠️  LLM 调用失败 ({e})，使用模板生成[/yellow]")
        return _template_fallback(topic)


def _template_fallback(topic: str) -> dict[str, Any]:
    """无 LLM 时的模板生成。"""
    return {
        "title": f"关于{topic}，我有几个不得不说的事🤔",
        "body": (
            f"最近一直在研究{topic}这个话题\n\n"
            f"花了不少时间做了功课，发现了一些很有意思的点👇\n\n"
            f"1️⃣ 第一点...\n"
            f"2️⃣ 第二点...\n"
            f"3️⃣ 第三点...\n\n"
            f"你们觉得呢？评论区聊聊👇\n\n"
            f"💾 觉得有用的话先收藏起来"
        ),
        "tags": [topic, "经验分享", "干货", "推荐", "日常"],
        "image_suggestions": ["文字封面 + 相关配图"],
        "post_time_suggestion": "周六 20:00-21:00",
    }
