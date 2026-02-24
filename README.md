# 晨间简报Agent | Morning Briefing Agent

> 每天7:00自动生成并发送加密货币晨间简报

---

## 📋 功能

- 🔥 **必读**: 筛选3条最重要新闻
- 📊 **市场概况**: BTC/ETH/SOL价格 + 恐慌贪婪指数
- 🪙 **Meme热点**: Solana/BSC/Base新币、AI Agent专项
- 🎯 **Polymarket**: 套利机会 + OpenClaw策略状态
- 📰 **核心资讯**: X KOL精选 + 媒体头条
- 💡 **创新雷达**: 新项目、新趋势

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd morning_briefing
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑.env文件，填入你的API密钥
```

### 3. 运行

```bash
python main.py
```

---

## ⚙️ 配置说明

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `COINGECKO_API_KEY` | CoinGecko API密钥 | 否 |
| `GMGN_API_KEY` | GMGN API密钥 | 推荐 |
| `CLAUDE_API_KEY` | Claude API密钥 | 推荐 |
| `DISCORD_WEBHOOK_URL` | Discord Webhook | 推荐 |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | 可选 |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID | 可选 |
| `OPENCLAW_WEBHOOK_URL` | OpenClaw Webhook | 可选 |

---

## 📁 项目结构

```
morning_briefing/
├── config.py          # 配置文件
├── main.py            # 主程序
├── fetchers/          # 数据采集模块
│   ├── market.py      # 市场数据
│   ├── meme.py        # Meme币数据
│   ├── twitter.py     # Twitter/X数据
│   ├── news.py        # 新闻数据
│   └── polymarket.py  # Polymarket数据
├── analyzers/         # 分析模块
│   ├── claude.py      # Claude AI分析
│   └── meme_quality.py # Meme质检
├── generators/        # 生成模块
│   └── briefing.py    # 简报生成
├── notifiers/         # 通知模块
│   ├── discord.py     # Discord通知
│   └── telegram.py    # Telegram通知
└── data/              # 数据目录
    └── briefings/     # 简报存档
```

---

## 🤖 GitHub Actions自动化

1. Fork此仓库

2. 在GitHub仓库设置中添加Secrets:
   - `COINGECKO_API_KEY`
   - `GMGN_API_KEY`
   - `CLAUDE_API_KEY`
   - `DISCORD_WEBHOOK_URL`
   - 其他需要的环境变量

3. 启用Actions

4. 每天早上7:00自动运行

---

## 📊 数据源

| 数据类型 | 数据源 | 免费额度 |
|----------|--------|----------|
| 价格 | CoinGecko | 100次/分 |
| Meme新币 | GMGN | 有限 |
| Twitter | Jina Reader | 免费 |
| 新闻 | RSS | 免费 |
| Polymarket | 官方API | 免费 |

---

## 🔧 自定义配置

### 修改KOL列表

编辑 `config.py`:

```python
MY_KOLS = {
    "S级": ["your_favorite_kol1", "kol2"],
    "A级": ["more_kols"],
}
```

### 添加AI关键词

```python
AI_KEYWORDS = [
    "your_keyword1",
    "your_keyword2",
]
```

### 修改链优先级

```python
CHAIN_PRIORITY = ["solana", "bsc", "base"]
```

---

## 📝 输出示例

```markdown
# 🌅 Jacky晨间简报 | 2026-02-24

## 🔥 今日必读 (3条)
...

## 📊 市场概况
...
```

---

## 🐛 故障排除

### 问题: Discord通知发送失败
**解决**: 检查 `DISCORD_WEBHOOK_URL` 是否正确

### 问题: GMGN数据获取失败
**解决**: GMGM需要API key，注册 https://gmgn.ai

### 问题: Claude分析失败
**解决**: 检查 `CLAUDE_API_KEY` 是否有效

---

## 📄 License

MIT

---

## 🤝 贡献

欢迎提交Issue和Pull Request!

---

**@jingouwang888** | Powered by Claude Code
