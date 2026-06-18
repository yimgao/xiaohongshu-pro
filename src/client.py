"""浏览器客户端 — Playwright 封装，带自适应反检测。"""

from __future__ import annotations

import json
import random
import time
from pathlib import Path
from typing import Any

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
)
from rich.console import Console

from src.config import settings

console = Console()


class CaptchaError(Exception):
    """检测到小红书安全验证时抛出。"""


class RateLimitError(Exception):
    """检测到频率限制时抛出。"""


class XHSBrowser:
    """小红书浏览器客户端。

    特性：
    - 自适应频率控制（根据操作历史动态调整延迟）
    - 真人化行为模拟（随机延迟、鼠标轨迹）
    - Cookie 自动持久化
    - 验证码 / 频率限制检测
    """

    def __init__(self) -> None:
        self._pw: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None
        self._action_count: int = 0
        self._last_action_time: float = 0.0

    # ── Lifecycle ──────────────────────────────────────────────

    def start(self) -> Page:
        """启动浏览器并返回页面对象。"""
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(
            headless=settings.headless,
            slow_mo=settings.slow_mo,
        )
        self._context = self._browser.new_context(
            viewport={
                "width": settings.viewport_width,
                "height": settings.viewport_height,
            },
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
        )

        # 恢复 Cookie
        self._restore_cookies()

        self._page = self._context.new_page()
        self._page.add_init_script(self._ANTI_DETECT_JS)
        return self._page

    def stop(self) -> None:
        """关闭浏览器并保存 Cookie。"""
        self._save_cookies()
        if self._browser:
            self._browser.close()
        if self._pw:
            self._pw.stop()

    @property
    def page(self) -> Page:
        assert self._page is not None, "Call start() first"
        return self._page

    # ── Cookie 管理 ──────────────────────────────────────────

    def _cookie_path(self) -> Path:
        assert settings.cookie_file is not None
        return settings.cookie_file

    def _save_cookies(self) -> None:
        if self._context is None:
            return
        path = self._cookie_path()
        cookies = self._context.cookies()
        path.write_text(json.dumps(cookies, ensure_ascii=False, indent=2))
        console.print(f"[dim]💾 Cookie saved ({len(cookies)} items)[/dim]")

    def _restore_cookies(self) -> None:
        path = self._cookie_path()
        if self._context and path.exists():
            cookies = json.loads(path.read_text())
            self._context.add_cookies(cookies)
            console.print(f"[dim]🔑 Cookie restored ({len(cookies)} items)[/dim]")

    def clear_cookies(self) -> None:
        """清除已保存的 Cookie（用于重新登录）。"""
        path = self._cookie_path()
        if path.exists():
            path.unlink()
            console.print("[yellow]🗑️  Cookie cleared[/yellow]")

    def is_logged_in(self) -> bool:
        """通过访问个人页判断是否登录。"""
        self.page.goto("https://www.xiaohongshu.com", wait_until="domcontentloaded")
        time.sleep(2)
        has_login = self.page.query_selector('[data-testid="user-profile"]')
        return has_login is not None

    # ── 反检测 ────────────────────────────────────────────────

    _ANTI_DETECT_JS = """
    // 覆盖 webdriver 检测
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN','zh'] });
    // 覆盖 Chrome 检测
    window.chrome = { runtime: {} };
    """

    def human_delay(self, base: float = 1.0, variance: float = 0.5) -> None:
        """模拟人类操作的随机延迟。"""
        delay = base + random.uniform(0, variance)
        time.sleep(delay)

    def cool_down(self) -> None:
        """每 N 次操作后的冷却期。"""
        self._action_count += 1
        if self._action_count % 5 == 0:
            cool = random.uniform(8, 15)
            console.print(f"[dim]😴 Cooling down {cool:.0f}s (action #{self._action_count})[/dim]")
            time.sleep(cool)

    def check_captcha(self) -> None:
        """检查是否触发了安全验证。"""
        if "sec_verify" in self.page.url or "captcha" in self.page.url.lower():
            console.print("[red]🚨 触发了安全验证！需要手动过验证[/red]")
            raise CaptchaError("Security verification triggered")

    def check_rate_limit(self) -> None:
        """检查频率限制 toast 提示。"""
        toast = self.page.query_selector('text=频繁')
        if toast:
            console.print("[yellow]⚠️  操作频繁，暂停 30s[/yellow]")
            time.sleep(30)
            raise RateLimitError("Rate limited")

    # ── 安全导航 ──────────────────────────────────────────────

    def safe_goto(self, url: str, *, wait_seconds: float = 3.0) -> None:
        """带反爬检测的导航。"""
        self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
        self.human_delay(wait_seconds, 2.0)
        self.check_captcha()
        self.cool_down()

    def safe_click(self, selector: str, *, pre_delay: float = 1.0) -> None:
        """带延迟的点击。"""
        self.human_delay(pre_delay, 1.5)
        el = self.page.query_selector(selector)
        if el:
            el.click()
            self.human_delay(0.5, 1.0)
            self.check_captcha()
            self.cool_down()

    def safe_type(self, selector: str, text: str, *, char_delay: tuple = (0.02, 0.06)) -> None:
        """逐字输入模拟真人打字。"""
        self.human_delay(0.5, 1.0)
        el = self.page.query_selector(selector)
        if el:
            el.click()
            self.human_delay(0.3, 0.5)
            for char in text:
                el.type(char, delay=int(random.uniform(*char_delay) * 1000))
            self.cool_down()

    # ── 数据提取 ──────────────────────────────────────────────

    def extract_initial_state(self) -> dict[str, Any]:
        """从页面提取 __INITIAL_STATE__。"""
        return self.page.evaluate("window.__INITIAL_STATE__")
