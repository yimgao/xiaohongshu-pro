# 小红书 Pro — AI-Powered 小红书 Toolkit

Python + Playwright 浏览器自动化，AI 驱动的内容生成。

## 升级版 vs 原版

| 特性 | 原版 (DeliciousBuding) | 升级版 |
|------|----------------------|--------|
| 内容生成 | 固定模板 | **AI 驱动** — 调用 LLM 生成爆款内容 |
| 架构 | 函数式 | **OOP + 类型提示** |
| 配置 | 环境变量 | **Pydantic 配置管理** |
| 日志 | print | **Rich 控制台输出** |
| 错误处理 | 基础 try/except | **分层异常 + 自动重试** |
| 会话管理 | 手动 | **自动 Cookie 持久化 + 健康检查** |
| 反检测 | 固定延迟 | **自适应频率控制 + 行为模拟** |

## 安装

```bash
pip install -e .
playwright install chromium
```

## 快速开始

```bash
# 1. 登录
xiaohongshu login

# 2. 搜索
xiaohongshu search "美食" --sort latest --limit 10

# 3. AI 生成 + 发布
xiaohongshu publish-ai --topic="美国拉面探店"
```

## 功能

- `xiaohongshu login` — 扫码登录
- `xiaohongshu search <keyword>` — 搜索笔记
- `xiaohongshu feed <id> <token>` — 帖子详情
- `xiaohongshu publish <title> <content>` — 发布图文
- `xiaohongshu publish-ai --topic` — AI 生成并发布
- `xiaohongshu like/comment/collect` — 互动
- `xiaohongshu me` — 我的主页
- `xiaohongshu explore` — 推荐流
