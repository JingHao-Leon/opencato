<div align="center">

<img src="docs/images/banner.png" alt="OpenCATO - 一只住在企业微信里的 AI 提醒猫" width="100%">

# OpenCATO 🐱

**一只住在企业微信里的 AI 提醒猫 —— 看到「微信里的提醒猫」这类付费项目后，想开源学习一下它是怎么做的，于是有了这个从企业微信合规通道、定时提醒引擎到猫设 prompt 的完整独立实现**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

</div>

**English**: An open-source AI reminder cat living in WeCom (Enterprise WeChat) — schedule reminders, Pomodoro focus timer, daily check-ins and LLM companionship through the official WeCom API. Built for learning how "a cat living in your chat app" products actually work.

## 这是什么

<img src="docs/images/logo.png" alt="OpenCATO 吉祥物 喵小盯" align="right" width="130">

市面上出现了「住在微信里的小猫」一类的付费订阅产品（计划整理 + 定时督促 + 专注计时 + 打卡陪伴）。OpenCATO 是一个**学习性质的开源复刻**：把这类产品拆解为可自托管的最小实现，代码全部独立编写，MIT 协议，供想研究「AI 陪伴 + 消息提醒」产品形态的同学参考。

关键词：企业微信机器人 / WeCom bot / 微信提醒猫 / AI 伴侣 / LLM 应用 / 定时提醒 / 番茄钟 / 打卡 / FastAPI / SQLite

## 功能特性

- 💬 **AI 聊天陪伴**：LLM 驱动，猫设 prompt 见 [`prompts/cat.md`](prompts/cat.md)（本项目的灵魂，欢迎调教）
- ⏰ **自然语言定时提醒**：`提醒我 18:30 吃药` / `明天早上8点提醒我开会` / `30分钟后提醒我喝水`
- 🍅 **专注计时（番茄钟）**：`开始专注 25 分钟`，到点猫来叫你
- ✅ **每日打卡**：`打卡`，记录累计天数
- 📋 **计划查看**：`计划`，列出待触发的提醒
- 🔒 **合规通道**：只使用企业微信官方 API，主动推送走应用消息，不碰个人号协议

## 效果预览

<p align="center">
  <img src="docs/images/demo.png" alt="OpenCATO 对话演示：定时提醒、番茄钟、打卡" width="360">
</p>

## 为什么是企业微信（WeCom）

个人微信协议机器人会被封号且连坐收款账户。企业微信自建应用是官方合规通道，支持服务端**主动推送应用消息**——这是"猫主动来戳你"能合法实现的关键。本项目不含、也不支持任何个人微信外挂能力。

## 快速开始

### 1. 企业微信后台配置（约 15 分钟）

1. 注册企业微信（个人/个体户均可），完成认证
2. 「应用管理 → 自建 → 创建应用」，记下 **AgentId** 和 **Secret**
3. 在应用的「接收消息 → 设置 API 接收」中，记下 **Token** 和 **EncodingAESKey**（回调 URL 等服务起来后再填）
4. 「我的企业 → 企业信息」记下 **企业 ID（CorpId）**

### 2. 本地运行

```bash
git clone https://github.com/JingHao-Leon/opencato.git
cd opencato
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 填入企业微信配置 + LLM API Key
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

开发期用内网穿透暴露回调地址（`localhost.run` / `cpolar` / `花生壳` 任选），然后在企业微信后台把回调 URL 填为 `https://你的域名/wecom/callback` 并保存验证。

### 3. 生产部署

任何能跑 Python 3.10+ 的机器即可（轻量云服务器约 ¥50/月），建议 nginx 反代 + HTTPS。数据库是单个 SQLite 文件，备份即拷贝。

## 配置项

| 环境变量 | 说明 |
|---|---|
| `WECOM_CORP_ID` | 企业 ID |
| `WECOM_AGENT_ID` | 自建应用 AgentId |
| `WECOM_SECRET` | 自建应用 Secret |
| `WECOM_TOKEN` / `WECOM_ENCODING_AES_KEY` | 回调 Token / EncodingAESKey |
| `LLM_API_KEY` | LLM API Key |
| `LLM_BASE_URL` | OpenAI 兼容接口地址，默认 Moonshot |
| `LLM_MODEL` | 模型名，默认 `kimi-k2-0905-preview` |

## 常见问题（FAQ）

**Q：想自己部署一只，最少要配哪些东西？**

A：一台能跑 Python 3.10+ 的机器 + 一个企业微信自建应用。`cp .env.example .env` 后必填 6 项企业微信与 LLM 配置（`WECOM_CORP_ID` / `WECOM_AGENT_ID` / `WECOM_SECRET` / `WECOM_TOKEN` / `WECOM_ENCODING_AES_KEY` / `LLM_API_KEY`），`LLM_BASE_URL`、`LLM_MODEL`、`DATABASE_PATH` 不填走默认，然后 `uvicorn app.main:app --host 0.0.0.0 --port 8000` 即可。任何必填项缺失进程会直接启动失败——配置在应用加载时硬读取，属于故意的 fail-fast 设计。

**Q：企业微信回调 URL 怎么填？为什么一直验证不过？**

A：在自建应用的「接收消息 → 设置 API 接收」里，URL 填 `https://你的域名/wecom/callback`，Token 和 EncodingAESKey 必须与 `.env` 中 `WECOM_TOKEN` / `WECOM_ENCODING_AES_KEY` 完全一致。**要先启动服务再点「保存」**：验证请求由 `GET /wecom/callback` 处理，服务没起、签名不符都会导致验证失败。本地开发没有公网 HTTPS 时，用内网穿透（localhost.run / cpolar / 花生壳）暴露 8000 端口。

**Q：LLM 用的什么模型？能换 DeepSeek / 通义吗？**

A：能。代码只要求一个 OpenAI 兼容的 `/chat/completions` 接口（见 `app/llm.py`），默认指向 Moonshot（`https://api.moonshot.cn/v1` + `kimi-k2-0905-preview`）；换成 DeepSeek、通义等只需改 `LLM_BASE_URL` / `LLM_MODEL` 两个环境变量并填对应的 `LLM_API_KEY`。另外只有正则指令没接住的消息才会走 LLM——「打卡」「计划」等固定指令不消耗 token。

**Q：怎么和猫交互？支持哪些说法？**

A：直接发消息：`提醒我 18:30 吃药` / `明天早上8点提醒我开会` / `30分钟后提醒我喝水` / `开始专注 25 分钟` / `打卡` / `计划`。指令解析基于正则，只认有限的中文句式（详见下文局限）；没被识别的消息一律转给 LLM 闲聊，所以随口聊天也不会报错。

**Q：和市面上「微信里的提醒猫」付费产品是什么关系？**

A：没有关系。本项目是看到这类产品后出于学习目的的**独立实现**：未使用其任何素材、文案或品牌资源，也未逆向其协议，全部代码与猫设 prompt 从零编写，MIT 协议开源，仅供学习交流。

**Q：数据都存在哪？会丢吗？**

A：全部在单个 SQLite 文件里（环境变量 `DATABASE_PATH`，默认 `./meowminder.db`），只有 users / reminders / checkins 三张表，备份就是拷贝这个文件；数据库文件已被 `.gitignore` 排除，不会被误提交。

## 架构

<p align="center">
  <img src="docs/images/architecture.png" alt="OpenCATO 架构图：企业微信回调 → FastAPI → LLM / 定时引擎 → 主动推送" width="100%">
</p>

<details>
<summary>文字版架构（点开展开）</summary>

```
用户 ──► 企业微信 ──回调──► FastAPI (app/main.py)
                              ├─ 解密 (wecom_crypto) → 指令解析 (commands) ─┐
                              │                       └─ 闲聊 → LLM (llm)  │
                              ├─ 定时引擎 (scheduler) 每 20s 扫到期提醒 ─────┤
                              └─ 主动推送 (wecom_api) ◄─────────────────────┘
                              └─ SQLite (db)：用户 / 提醒 / 打卡
```

</details>

## 测试

```bash
pip install pytest httpx
python -m pytest tests -q
```

20 个测试用例：指令解析（含中文两种语序、时段推断、防误判）、回调加解密 round-trip、坏签名拦截、HTTP 端到端、调度器推送。

## 路线图

- [ ] 每周计划回顾（猫主动发起）
- [ ] 打卡 streak / 情侣互相督促
- [ ] 订阅会员状态（支付对接）
- [ ] 多猫设与皮肤
- [ ] Web 管理面板

## 局限与已知问题（Limitations）

- **单实例设计，不能水平扩展**：定时引擎是进程内后台线程每 20 秒轮询一次到期提醒（`app/scheduler.py`），SQLite 为单连接 + 进程内锁。起多个副本或多 worker 会导致同一条提醒被重复推送；提醒触发精度也受 20 秒轮询间隔限制。
- **LLM 没有跨轮记忆**：每次闲聊只发送猫设 system prompt + 当前这一条消息（`app/llm.py`），没有会话历史存储——猫设里「记住用户目标」目前只靠单轮上下文，代码层面并不记得上一轮聊了什么。
- **指令解析是正则，句式覆盖有限**：只支持「明天/后天 + 时段 + 时刻」两种语序和「N 分钟后」相对提醒，时刻必须带「点 / ： / 半」以防误判；不支持「每周三」「下周一」等日期表达，也没有循环 / 重复提醒。
- **只处理文本消息**：回调仅响应 `MsgType=text`（`app/main.py`），图片、语音、表情包不会得到回复；主动推送同样只有文本一种格式。
- **LLM 输出未接内容审核**：模型回复会原样推送给用户，部署者需按免责声明自行接入内容审核并遵守当地法律法规。
- **时间依赖服务器本地时区**：指令解析与调度全部使用 `datetime.now()`，若服务器时区不是 UTC+8，提醒时间会整体错位。

## 免责声明

本项目仅供学习交流，与任何同名或相似商业产品**无任何关联**；代码为独立实现，未使用任何第三方产品的素材、文案或品牌资源。AI 生成内容请在部署时自行接入内容审核并遵守当地法律法规。

## License

[MIT](LICENSE) — 随便用，注明出处即可。欢迎 Star ⭐ 和 PR！
