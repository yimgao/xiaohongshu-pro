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
    try:
        page.goto("https://creator.xiaohongshu.com/login?source=official", wait_until="commit", timeout=20000)
    except Exception:
        page.goto("https://creator.xiaohongshu.com/login?source=official", wait_until="domcontentloaded", timeout=30000)
    browser.human_delay(3, 2)

    # 截图保存以便调试
    page.screenshot(path=str(browser._cookie_path().parent / "login_debug.png"))
    console.print(f"[dim]📸 登录页截图已保存[/dim]")

    # 点击二维码登录按钮（左侧图片图标）
    qr_btn = page.query_selector("img[src*='login'], .login-qrcode, .qrcode-tab")
    if not qr_btn:
        # 尝试找所有可点击的图片元素
        images = page.query_selector_all("img")
        for img in images:
            src = img.get_attribute("src") or ""
            if "qr" in src.lower() or "wechat" in src.lower():
                qr_btn = img
                break
    if qr_btn:
        qr_btn.click()
        browser.human_delay(2, 1)
    else:
        # 备用：点击第一个非短信登录的可交互元素
        tabs = page.query_selector_all("[role='tab'], .tab, [class*='tab']")
        for tab in tabs:
            text = tab.inner_text()
            if "短信" not in text and text.strip():
                tab.click()
                browser.human_delay(2, 1)
                break

    # 保存二维码图片到本地（不管页面加载情况）
    browser.human_delay(1, 1)
    try:
        qr_img = page.query_selector_all("img")
        for img in qr_img:
            src = img.get_attribute("src") or ""
            if src.startswith("data:image/png") and img.bounding_box() and img.bounding_box()["width"] > 100:
                import base64
                b64_data = src.split(",")[1]
                qr_path = browser._cookie_path().parent / "qrcode.png"
                with open(str(qr_path), "wb") as f:
                    f.write(base64.b64decode(b64_data))
                console.print(f"[green]📱 二维码已保存: {qr_path}[/green]")
                console.print("[yellow]💡 如果浏览器没有弹出窗口，请打开此图片用小红书 App 扫码[/yellow]")
                break
    except Exception as e:
        console.print(f"[dim]二维码提取失败: {e}[/dim]")

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
