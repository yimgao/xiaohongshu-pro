"""登录管理 — 二维码扫码登录。"""

from __future__ import annotations

import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from src.client import XHSBrowser

console = Console()


def qrcode_login(browser: XHSBrowser, timeout: int = 120) -> bool:
    """通过二维码扫码登录小红书。

    Args:
        browser: 浏览器客户端实例
        timeout: 等待扫码的超时秒数

    Returns:
        True 登录成功, False 超时
    """
    page = browser.page
    page.goto("https://www.xiaohongshu.com/login", wait_until="domcontentloaded")
    browser.human_delay(2, 2)

    # 切换到二维码 tab
    qr_tab = page.query_selector('[data-testid="qrcode-login"]')
    if qr_tab:
        qr_tab.click()
        browser.human_delay(1, 1)

    console.print(Panel.fit(
        "[bold yellow]📱 请用微信或小红书 App 扫码登录[/bold yellow]\n\n"
        "等待扫码中...（最多 120 秒）",
        border_style="yellow",
    ))

    # 等待成功 — 检测 URL 跳转或登录状态变化
    start = time.time()
    while time.time() - start < timeout:
        time.sleep(2)

        # 检查是否跳转到了首页
        if "login" not in page.url:
            console.print("[bold green]✅ 登录成功！[/bold green]")
            browser.human_delay(2, 2)
            # 保存 Cookie
            browser._save_cookies()
            return True

        # 检查是否有登录成功 toast
        success = page.query_selector("text=登录成功")
        if success:
            console.print("[bold green]✅ 登录成功！[/bold green]")
            browser._save_cookies()
            return True

        remaining = timeout - int(time.time() - start)
        if remaining % 10 == 0:
            console.print(f"[dim]⏳ 等待扫码... 还剩 {remaining}s[/dim]")

    console.print("[red]❌ 登录超时[/red]")
    return False


def check_login(browser: XHSBrowser) -> bool:
    """检查当前登录状态。

    Returns:
        True 已登录, False 未登录
    """
    try:
        browser.safe_goto("https://www.xiaohongshu.com", wait_seconds=2)
        page = browser.page

        # 检测登录态：看有没有"我的"相关元素
        is_logged = page.query_selector('[data-testid="user-profile"]')
        if is_logged:
            console.print("[bold green]✅ 已登录[/bold green]")
            return True

        # 备选：看 URL 是否仍为登录页
        if "login" in page.url:
            console.print("[yellow]❌ 未登录或 Cookie 已过期[/yellow]")
            return False

        console.print("[yellow]⚠️  登录状态不明，建议重新登录[/yellow]")
        return False
    except Exception as e:
        console.print(f"[red]检查登录状态失败: {e}[/red]")
        return False
