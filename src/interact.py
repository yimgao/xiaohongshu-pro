"""互动模块 — 点赞、收藏、评论。"""

from __future__ import annotations

import re
from typing import Any

from rich.console import Console
from rich.prompt import Confirm

from src.client import XHSBrowser

console = Console()


def like(browser: XHSBrowser, feed_id: str, xsec_token: str) -> bool:
    """点赞帖子。"""
    url = f"https://www.xiaohongshu.com/explore/{feed_id}?xsec_token={xsec_token}"
    browser.safe_goto(url, wait_seconds=2)

    # 尝试点击点赞按钮
    btn = browser.page.query_selector('[data-testid="like-button"]')
    if not btn:
        btn = browser.page.query_selector("svg[aria-label*='赞']")
    if btn:
        browser.human_delay(0.5, 0.5)
        btn.click()
        browser.human_delay(1, 1)
        console.print("[green]✅ 点赞成功[/green]")
        return True
    console.print("[yellow]⚠️  未找到点赞按钮[/yellow]")
    return False


def collect(browser: XHSBrowser, feed_id: str, xsec_token: str) -> bool:
    """收藏帖子。"""
    url = f"https://www.xiaohongshu.com/explore/{feed_id}?xsec_token={xsec_token}"
    browser.safe_goto(url, wait_seconds=2)

    btn = browser.page.query_selector('[data-testid="collect-button"]')
    if btn:
        browser.human_delay(0.5, 0.5)
        btn.click()
        browser.human_delay(1, 1)
        console.print("[green]✅ 收藏成功[/green]")
        return True
    console.print("[yellow]⚠️  未找到收藏按钮[/yellow]")
    return False


def comment(
    browser: XHSBrowser,
    feed_id: str,
    xsec_token: str,
    content: str,
) -> bool:
    """评论帖子。"""
    url = f"https://www.xiaohongshu.com/explore/{feed_id}?xsec_token={xsec_token}"
    browser.safe_goto(url, wait_seconds=2)

    # 定位评论输入框
    input_el = browser.page.query_selector('[data-testid="comment-input"]')
    if not input_el:
        input_el = browser.page.query_selector("textarea, [contenteditable]")
    if not input_el:
        console.print("[yellow]⚠️  未找到评论输入框[/yellow]")
        return False

    browser.human_delay(0.5, 1)
    input_el.click()
    browser.human_delay(0.3, 0.5)
    input_el.fill(content)
    browser.human_delay(0.5, 1)

    # 点击发送
    send_btn = browser.page.query_selector('[data-testid="comment-submit"]')
    if not send_btn:
        send_btn = browser.page.query_selector("button:has-text('发布')")
    if send_btn:
        send_btn.click()
        browser.human_delay(2, 2)
        console.print(f"[green]✅ 评论已发送: {content[:50]}[/green]")
        return True

    console.print("[yellow]⚠️  未找到发送按钮[/yellow]")
    return False
