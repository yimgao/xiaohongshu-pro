"""帖子详情模块 — 查看单篇笔记详情和评论。"""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from src.client import XHSBrowser

console = Console()


def get_feed(
    browser: XHSBrowser,
    feed_id: str,
    xsec_token: str,
    load_comments: bool = False,
    max_comments: int = 20,
) -> dict[str, Any]:
    """获取帖子详情。

    Args:
        browser: 浏览器客户端
        feed_id: 帖子 ID
        xsec_token: 安全令牌（从搜索结果获取）
        load_comments: 是否加载评论
        max_comments: 最多加载的评论数

    Returns:
        帖子详情数据
    """
    url = f"https://www.xiaohongshu.com/explore/{feed_id}?xsec_token={xsec_token}"
    browser.safe_goto(url, wait_seconds=3)

    state = browser.extract_initial_state()
    detail = _extract_detail(state, feed_id)

    if detail:
        _display_detail(detail)

    if load_comments and detail:
        comments = _extract_comments(state, feed_id, max_comments)
        detail["comments"] = comments
        _display_comments(comments)

    return detail


def _extract_detail(state: dict, feed_id: str) -> dict[str, Any]:
    """从 __INITIAL_STATE__ 提取帖子详情。"""
    try:
        note_map = state.get("note", {}).get("noteDetailMap", {})
        note_data = note_map.get(feed_id, {}).get("note", {})
        return {
            "id": feed_id,
            "title": note_data.get("title", ""),
            "desc": note_data.get("desc", ""),
            "user": note_data.get("user", {}).get("nickname", ""),
            "liked_count": note_data.get("interact_info", {}).get("liked_count", "0"),
            "collected_count": note_data.get("interact_info", {}).get("collected_count", "0"),
            "comment_count": note_data.get("interact_info", {}).get("comment_count", "0"),
            "image_count": len(note_data.get("image_list", [])),
            "tag_list": [t.get("name", "") for t in note_data.get("tag_list", [])],
        }
    except Exception as e:
        console.print(f"[yellow]⚠️  提取详情异常: {e}[/yellow]")
        return {}


def _extract_comments(state: dict, feed_id: str, max_count: int) -> list[dict]:
    """提取评论列表。"""
    comments = []
    try:
        comment_data = (
            state.get("note", {})
            .get("noteDetailMap", {})
            .get(feed_id, {})
            .get("comment", {})
            .get("comments", [])
        )
        for c in comment_data[:max_count]:
            comments.append({
                "user": c.get("user_info", {}).get("nickname", ""),
                "content": c.get("content", ""),
                "likes": c.get("like_count", 0),
                "time": c.get("create_time", ""),
            })
    except Exception:
        pass
    return comments


def _display_detail(detail: dict) -> None:
    """展示帖子详情。"""
    text = Text()
    text.append(f"👤 {detail.get('user', '')}\n", style="bold cyan")
    text.append(f"📝 {detail.get('title', '')}\n\n", style="bold")
    text.append(f"{detail.get('desc', '')[:500]}\n\n")
    text.append(f"👍 {detail['liked_count']}  ⭐ {detail['collected_count']}  💬 {detail['comment_count']}")
    if detail.get("tag_list"):
        text.append(f"\n🏷️  {'  '.join(detail['tag_list'])}")
    text.append(f"\n📷 {detail.get('image_count', 0)}张图片")

    console.print(Panel(text, title="📄 帖子详情", border_style="blue"))


def _display_comments(comments: list[dict]) -> None:
    """展示评论。"""
    if not comments:
        console.print("[dim]💬 暂无评论[/dim]")
        return
    console.print(f"\n[bold]💬 评论 ({len(comments)}条)[/bold]")
    for i, c in enumerate(comments, 1):
        console.print(f"  {i}. {c['user']}: {c['content'][:100]}")
