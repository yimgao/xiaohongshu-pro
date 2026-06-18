"""发布模块 — 发布图文笔记。"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from src.client import XHSBrowser

console = Console()


def publish(
    browser: XHSBrowser,
    title: str,
    content: str,
    images: list[str] | None = None,
    tags: list[str] | None = None,
    auto_publish: bool = False,
) -> bool:
    """发布图文笔记。

    Args:
        browser: 浏览器客户端
        title: 标题
        content: 正文
        images: 图片路径列表
        tags: 话题标签列表
        auto_publish: True 自动发布，False 停在发布按钮前

    Returns:
        是否发布成功
    """
    # 展示内容让用户确认
    console.print(Panel(
        f"[bold]📝 准备发布[/bold]\n\n"
        f"[bold]标题:[/bold] {title}\n\n"
        f"{content[:300]}...\n\n"
        f"[bold]标签:[/bold] {', '.join(tags) if tags else '无'}\n"
        f"[bold]图片:[/bold] {len(images) if images else 0}张",
        border_style="yellow",
    ))

    if not auto_publish:
        ok = Confirm.ask("确认发布到小红书？")
        if not ok:
            console.print("[yellow]已取消发布[/yellow]")
            return False

    # 打开创作者中心
    browser.safe_goto(
        "https://creator.xiaohongshu.com/publish/publish",
        wait_seconds=3,
    )

    # 上传图片
    if images:
        _upload_images(browser, images)

    # 填写标题
    browser.human_delay(1, 1)
    title_input = browser.page.query_selector('[data-testid="publish-title"]')
    if not title_input:
        title_input = browser.page.query_selector("input[placeholder*='标题']")
    if title_input:
        title_input.click()
        browser.human_delay(0.3, 0.3)
        for char in title:
            title_input.type(char, delay=30)
            time.sleep(0.03)
        console.print(f"[dim]📝 标题已填写: {title}[/dim]")

    # 填写正文
    browser.human_delay(0.5, 0.5)
    body_input = browser.page.query_selector('[data-testid="publish-content"]')
    if not body_input:
        body_input = browser.page.query_selector("[contenteditable]")
    if body_input:
        body_input.click()
        browser.human_delay(0.3, 0.5)
        for char in content:
            body_input.type(char, delay=20)
            time.sleep(0.02)
        console.print(f"[dim]📝 正文已填写 ({len(content)}字)[/dim]")

    # 添加标签
    if tags:
        browser.human_delay(0.5, 1)
        for tag in tags:
            _add_tag(browser, tag)

    if auto_publish:
        # 点击发布
        browser.human_delay(1, 2)
        publish_btn = browser.page.query_selector('[data-testid="publish-button"]')
        if publish_btn:
            publish_btn.click()
            time.sleep(3)
            console.print("[bold green]✅ 已发布！[/bold green]")
            return True
        console.print("[yellow]⚠️  未找到发布按钮，请手动发布[/yellow]")
        return False

    console.print("[green]✅ 内容已填写完毕！请检查后手动点击发布[/green]")
    return True


def _upload_images(browser: XHSBrowser, images: list[str]) -> None:
    """上传图片。"""
    upload_btn = browser.page.query_selector('[data-testid="upload-button"]')
    if not upload_btn:
        upload_btn = browser.page.query_selector("input[type='file']")
    if upload_btn:
        # 构建文件路径
        file_paths = []
        for img in images:
            p = Path(img)
            if p.exists():
                file_paths.append(str(p.absolute()))
        if file_paths:
            upload_btn.set_input_files(file_paths)
            console.print(f"[dim]📷 已选择 {len(file_paths)} 张图片[/dim]")
            time.sleep(3)


def _add_tag(browser: XHSBrowser, tag: str) -> None:
    """添加单个话题标签。"""
    tag_input = browser.page.query_selector('[data-testid="tag-input"]')
    if tag_input:
        tag_input.click()
        browser.human_delay(0.3, 0.3)
        tag_input.fill(tag)
        browser.human_delay(0.5, 0.5)
        # 选择第一个联想结果
        suggestion = browser.page.query_selector('[data-testid="tag-suggestion"]')
        if suggestion:
            suggestion.click()
        browser.human_delay(0.3, 0.3)
