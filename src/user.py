"""用户模块 — 用户主页信息提取。"""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.table import Table

from src.client import XHSBrowser

console = Console()


def get_user(browser: XHSBrowser, user_id: str | None = None) -> dict[str, Any]:
    """获取用户主页信息。

    Args:
        browser: 浏览器客户端
        user_id: 用户 ID。None 表示当前登录用户

    Returns:
        用户信息
    """
    if user_id:
        url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
    else:
        url = "https://www.xiaohongshu.com/user/profile/self"

    browser.safe_goto(url, wait_seconds=3)
    # 滚动加载笔记
    for _ in range(2):
        browser.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        browser.human_delay(1, 1)

    state = browser.extract_initial_state()
    info = _extract_user_info(state)
    notes = _extract_user_notes(state)

    _display_user(info, notes)
    return {**info, "notes": notes}


def _extract_user_info(state: dict) -> dict[str, Any]:
    """提取用户信息。"""
    try:
        user_data = state.get("user", {}).get("userPageData", {})
        basic = user_data.get("basic_info", {})
        stats = user_data.get("stats_info", {})
        return {
            "user_id": user_data.get("user_id", ""),
            "nickname": basic.get("nickname", ""),
            "desc": basic.get("desc", ""),
            "followers": stats.get("follower_count", "0"),
            "following": stats.get("following_count", "0"),
            "notes_count": stats.get("note_count", "0"),
        }
    except Exception as e:
        console.print(f"[yellow]⚠️  提取用户信息异常: {e}[/yellow]")
        return {}


def _extract_user_notes(state: dict) -> list[dict]:
    """提取用户笔记列表。"""
    notes = []
    try:
        items = state.get("user", {}).get("notes", {}).get("notes", [])
        for item in items[:20]:
            display = item.get("note_card", item)
            notes.append({
                "id": display.get("id", ""),
                "title": display.get("display_title", ""),
                "liked_count": display.get("interact_info", {}).get("liked_count", "0"),
            })
    except Exception:
        pass
    return notes


def _display_user(info: dict, notes: list[dict]) -> None:
    """展示用户信息。"""
    console.print(f"\n[bold cyan]👤 {info.get('nickname', '')}[/bold cyan]")
    console.print(f"   {info.get('desc', '')[:200]}")
    console.print(f"   📊 {info.get('notes_count', '0')}篇笔记  "
                  f"👥 {info.get('followers', '0')}粉丝  "
                  f"➡️ {info.get('following', '0')}关注")

    if notes:
        table = Table(title="📝 最近笔记")
        table.add_column("标题", width=40)
        table.add_column("👍", justify="right")
        for n in notes[:10]:
            table.add_row(n["title"][:38], n["liked_count"])
        console.print(table)
