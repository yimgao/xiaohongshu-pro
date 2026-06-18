"""搜索模块 — 小红书关键词搜索。"""

from __future__ import annotations

import json
from typing import Any

from rich.console import Console
from rich.table import Table

from src.client import XHSBrowser

console = Console()


def search(
    browser: XHSBrowser,
    keyword: str,
    sort: str = "general",
    note_type: str = "general",
    limit: int = 10,
) -> list[dict[str, Any]]:
    """搜索小红书笔记。

    Args:
        browser: 浏览器客户端
        keyword: 搜索关键词
        sort: general(综合) / latest(最新)
        note_type: general(不限) / video(视频)
        limit: 返回结果数

    Returns:
        搜索结果的笔记列表
    """
    url = (
        f"https://www.xiaohongshu.com/search_result"
        f"?keyword={keyword}&sort={sort}&type={note_type}"
    )
    browser.safe_goto(url, wait_seconds=3)

    # 滚动加载更多
    for _ in range(min(limit // 6 + 1, 3)):
        browser.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        browser.human_delay(1.5, 1.0)

    # 提取数据
    state = browser.extract_initial_state()
    feeds = _extract_feeds(state, limit)

    _display_results(keyword, feeds)
    return feeds


def _extract_feeds(state: dict, limit: int) -> list[dict[str, Any]]:
    """从 __INITIAL_STATE__ 提取搜索结果。"""
    results: list[dict[str, Any]] = []
    try:
        items = state.get("search", {}).get("feeds", [])
        for item in items[:limit]:
            note = item.get("note", item)
            results.append({
                "id": note.get("id", ""),
                "xsec_token": note.get("xsec_token", ""),
                "title": note.get("display_title", ""),
                "type": note.get("type", ""),
                "user": note.get("user", {}).get("nickname", ""),
                "user_id": note.get("user", {}).get("user_id", ""),
                "liked_count": note.get("interact_info", {}).get("liked_count", "0"),
                "collected_count": note.get("interact_info", {}).get("collected_count", "0"),
                "comment_count": note.get("interact_info", {}).get("comment_count", "0"),
            })
    except Exception as e:
        console.print(f"[yellow]⚠️  提取搜索结果异常: {e}[/yellow]")
    return results


def _display_results(keyword: str, feeds: list[dict]) -> None:
    """在终端展示搜索结果。"""
    table = Table(title=f"🔍 搜索结果: {keyword} ({len(feeds)}条)")
    table.add_column("#", style="dim")
    table.add_column("标题", width=30)
    table.add_column("作者")
    table.add_column("👍", justify="right")
    table.add_column("⭐", justify="right")
    table.add_column("💬", justify="right")

    for i, feed in enumerate(feeds, 1):
        table.add_row(
            str(i),
            feed["title"][:28],
            feed["user"],
            feed["liked_count"],
            feed["collected_count"],
            feed["comment_count"],
        )
    console.print(table)
