# MeowMinder · 喵小盯

一只住在企业微信里的提醒猫 🐱 —— 计划整理、定时督促、专注计时、每日打卡。

**为什么是企业微信**：个人微信协议机器人会被封号且连坐收款账户；企业微信自建应用是官方合规通道，支持服务端**主动推送应用消息**，这是"猫主动来戳你"能合法实现的关键。

## 功能

- 💬 **聊天陪伴**：LLM 驱动，猫设 prompt 见 `prompts/cat.md`（本项目的灵魂，欢迎调教）
- ⏰ **定时提醒**：`提醒我 18:30 吃药` / `明天早上8点提醒我开会` / `30分钟后提醒我喝水`
- 🍅 **专注计时**：`开始专注 25 分钟`，到点猫来叫你
- ✅ **每日打卡**：`打卡`，记录连续天数
- 📋 **计划查看**：`计划`，列出待触发的提醒

## 快速开始

### 1. 企业微信后台配置（约 15 分钟）

1. 注册企业微信（个人/个体户均可），完成认证
2. 「应用管理 → 自建 → 创建应用」，记下 **AgentId** 和 **Secret**
3. 在应用的「接收消息 → 设置 API 接收」中，记下 **Token** 和 **EncodingAESKey**（回调 URL 先随便填，服务起来后再回来验证）
4. 「我的企业 → 企业信息」记下 **企业 ID（CorpId）**

### 2. 本地运行

```bash
pip install -r requirements.txt
cp .env.example .env   # 填入上一步的配置 + LLM API Key
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

开发期用内网穿透暴露回调地址（任选其一）：`localhost.run`、`cpolar`、`花生壳`。
穿透成功后回企业微信后台把回调 URL 填为 `https://你的域名/wecom/callback` 并保存验证。

### 3. 生产部署

任何能跑 Python 的机器都行（轻量云服务器约 ¥50/月）。建议配 nginx 反代 + HTTPS。
数据库是单个 SQLite 文件，备份即拷贝。

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

## 架构

```
用户 ──► 企业微信 ──回调──► FastAPI(app/main.py)
                              ├─ 解密(wecom_crypto) → 指令解析(commands) ─┐
                              │                    └─ 闲聊 → LLM(llm)    │
                              ├─ 定时器(scheduler) 每分钟扫到期提醒 ───────┤
                              └─ 主动发消息(wecom_api) ◄───────────────────┘
                              └─ SQLite(db): 用户 / 提醒 / 打卡
```

## 路线图

- [ ] 每周计划回顾（猫主动发起）
- [ ] 打卡 streak 排行榜 / 情侣互相督促
- [ ] 订阅会员状态（支付对接）
- [ ] 多猫设与皮肤
- [ ] Web 管理面板

## 合规说明

本项目仅使用企业微信官方 API，不包含、也不支持任何个人微信协议/外挂能力。
AI 生成内容请在部署时自行接入内容审核并遵守当地法规。

## License

MIT — 随便用，注明出处即可。欢迎 PR！
