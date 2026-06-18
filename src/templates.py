"""写作模板 — 多种小红书笔记类型模板。"""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.table import Table

console = Console()

TEMPLATES: dict[str, dict[str, Any]] = {
    "探店测评": {
        "style": "种草风",
        "word_count": "600-800字",
        "structure": ["位置→环境→菜品→价格→总结"],
        "title_formula": [
            "藏在{location}的宝藏{type}，我不允许你不知道",
            "{location}这家{type}，连吃三天了😋",
            "为了这口{type}，我愿意来{location}一万次",
        ],
        "tags": ["探店", "美食", "{location}", "{type}", "周末去哪儿"],
    },
    "攻略教程": {
        "style": "干货风",
        "word_count": "800-1000字",
        "structure": ["痛点→方法→步骤→效果"],
        "title_formula": [
            "做到这{N}点，我终于搞定了{topic}",
            "{topic}全攻略｜从入门到精通一篇就够了",
            "新手必看｜{topic}避坑指南🚫",
        ],
        "tags": ["攻略", "教程", "{topic}", "新手必看", "干货"],
    },
    "产品推荐": {
        "style": "种草风",
        "word_count": "500-700字",
        "structure": ["为什么买→使用感受→亮点→建议"],
        "title_formula": [
            "这个{product}真的绝了！后悔没早买😭",
            "无限回购的{product}，第{N}次安利",
            "冷门但好用的{product}｜不允许还有人不知道",
        ],
        "tags": ["好物推荐", "{product}", "种草", "值得买", "测评"],
    },
    "经验分享": {
        "style": "真诚风",
        "word_count": "700-900字",
        "structure": ["背景→过程→收获→建议"],
        "title_formula": [
            "关于{topic}，我的{N}条真心话",
            "做了{N}个月{topic}后，我想说...",
            "普通人是如何通过{topic}逆袭的？",
        ],
        "tags": ["经验分享", "{topic}", "个人成长", "真实经历", "心得"],
    },
}


def list_templates() -> None:
    """列出所有可用模板。"""
    table = Table(title="📝 写作模板")
    table.add_column("类型")
    table.add_column("风格")
    table.add_column("字数")
    table.add_column("结构")
    for name, t in TEMPLATES.items():
        table.add_row(name, t["style"], t["word_count"], t["structure"][0])
    console.print(table)


def generate_template(
    topic: str,
    template_type: str = "经验分享",
    location: str = "",
    product: str = "",
) -> dict[str, Any]:
    """根据模板类型生成内容框架。"""
    t = TEMPLATES.get(template_type, TEMPLATES["经验分享"])
    import random

    title = random.choice(t["title_formula"])
    title = (
        title.replace("{location}", location or "这里")
        .replace("{type}", topic)
        .replace("{topic}", topic)
        .replace("{product}", product or topic)
        .replace("{N}", str(random.randint(3, 7)))
    )

    return {
        "type": template_type,
        "style": t["style"],
        "title": title,
        "structure": t["structure"][0],
        "tags": [tag.replace("{topic}", topic).replace("{location}", location or topic)
                 for tag in t["tags"]],
    }
