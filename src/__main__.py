"""小红书 Pro CLI 入口。"""

from __future__ import annotations

import sys

import click
from rich.console import Console

from src.client import XHSBrowser
from src.login import check_login, qrcode_login
from src.search import search
from src.feed import get_feed
from src.user import get_user
from src.interact import like, collect, comment
from src.publish import publish
from src.content import generate_content
from src.templates import generate_template

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="xiaohongshu")
def cli():
    """小红书 Pro — AI-powered 小红书浏览器自动化工具。"""


@cli.command()
@click.option("--headless", is_flag=True, help="无头模式")
def login(headless: bool):
    """扫码登录小红书。"""
    browser = XHSBrowser()
    try:
        browser.start()
        if qrcode_login(browser):
            console.print("[green]✅ 登录成功！[/green]")
        else:
            console.print("[red]❌ 登录失败[/red]")
            sys.exit(1)
    finally:
        browser.stop()


@cli.command()
def check():
    """检查登录状态。"""
    browser = XHSBrowser()
    browser.start()
    check_login(browser)
    browser.stop()


@cli.command()
def logout():
    """清除登录 Cookie。"""
    browser = XHSBrowser()
    browser.clear_cookies()
    console.print("[green]✅ 已登出[/green]")


@cli.command()
@click.argument("keyword")
@click.option("--sort", default="general", type=click.Choice(["general", "latest"]))
@click.option("--type", "note_type", default="general")
@click.option("--limit", default=10, type=int)
def search_cmd(keyword: str, sort: str, note_type: str, limit: int):
    """搜索小红书笔记。"""
    browser = XHSBrowser()
    browser.start()
    try:
        search(browser, keyword, sort, note_type, limit)
    finally:
        browser.stop()


@cli.command()
@click.argument("feed_id")
@click.argument("xsec_token")
@click.option("--comments", is_flag=True, help="加载评论")
def feed(feed_id: str, xsec_token: str, comments: bool):
    """查看帖子详情。"""
    browser = XHSBrowser()
    browser.start()
    try:
        get_feed(browser, feed_id, xsec_token, load_comments=comments)
    finally:
        browser.stop()


@cli.command()
@click.argument("user_id", required=False)
def profile(user_id: str | None):
    """查看用户主页。"""
    browser = XHSBrowser()
    browser.start()
    try:
        get_user(browser, user_id)
    finally:
        browser.stop()


@cli.command()
@click.option("--title", prompt="标题", help="笔记标题")
@click.option("--content", prompt="正文", help="笔记正文")
@click.option("--images", default="", help="图片路径，逗号分隔")
@click.option("--tags", default="", help="话题标签，逗号分隔")
@click.option("--auto", is_flag=True, help="自动发布")
def publish_cmd(title: str, content: str, images: str, tags: str, auto: bool):
    """发布图文笔记。"""
    img_list = [i.strip() for i in images.split(",") if i.strip()] if images else None
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None

    browser = XHSBrowser()
    browser.start()
    try:
        publish(browser, title, content, img_list, tag_list, auto_publish=auto)
    finally:
        browser.stop()


@cli.command()
@click.option("--topic", prompt="主题", help="内容主题")
@click.option("--context", default="", help="额外上下文")
@click.option("--publish", "do_publish", is_flag=True, help="生成后直接发布")
def publish_ai(topic: str, context: str, do_publish: bool):
    """AI 生成内容并发布。"""
    console.print(f"[bold]🤖 AI 正在为「{topic}」生成内容...[/bold]")
    result = generate_content(topic, context)

    console.print(f"\n[bold cyan]📝 标题:[/bold cyan] {result.get('title', '')}")
    console.print(f"\n[bold cyan]📄 正文:[/bold cyan]\n{result.get('body', '')[:500]}")
    console.print(f"\n[bold cyan]🏷️ 标签:[/bold cyan] {', '.join(result.get('tags', []))}")

    if do_publish:
        click.confirm("\n确认发布？", default=True)
        browser = XHSBrowser()
        browser.start()
        try:
            publish(
                browser,
                result.get("title", topic),
                result.get("body", ""),
                tags=result.get("tags"),
                auto_publish=True,
            )
        finally:
            browser.stop()
    else:
        console.print("\n[green]✅ 内容已生成！复制上面的内容去小红书发布吧[/green]")


@cli.command()
@click.argument("feed_id")
@click.argument("xsec_token")
def like_cmd(feed_id: str, xsec_token: str):
    """点赞帖子。"""
    browser = XHSBrowser()
    browser.start()
    try:
        like(browser, feed_id, xsec_token)
    finally:
        browser.stop()


@cli.command()
@click.argument("feed_id")
@click.argument("xsec_token")
def collect_cmd(feed_id: str, xsec_token: str):
    """收藏帖子。"""
    browser = XHSBrowser()
    browser.start()
    try:
        collect(browser, feed_id, xsec_token)
    finally:
        browser.stop()


@cli.command()
@click.argument("feed_id")
@click.argument("xsec_token")
@click.option("--content", prompt="评论内容", help="评论文字")
def comment_cmd(feed_id: str, xsec_token: str, content: str):
    """评论帖子。"""
    browser = XHSBrowser()
    browser.start()
    try:
        comment(browser, feed_id, xsec_token, content)
    finally:
        browser.stop()


@cli.command()
@click.argument("topic")
@click.option("--type", "template_type", default="经验分享", help="模板类型")
def template(topic: str, template_type: str):
    """生成写作模板。"""
    result = generate_template(topic, template_type)
    console.print(f"[bold]📝 模板类型:[/bold] {result['type']}")
    console.print(f"[bold]🎨 风格:[/bold] {result['style']}")
    console.print(f"[bold]🏗️  结构:[/bold] {result['structure']}")
    console.print(f"[bold]💡 示例标题:[/bold] {result['title']}")
    console.print(f"[bold]🏷️  推荐标签:[/bold] {', '.join(result['tags'])}")


if __name__ == "__main__":
    cli()
