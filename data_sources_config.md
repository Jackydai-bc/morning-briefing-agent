# 晨间简报Agent - 数据源配置

> 具体的API配置、KOL列表、媒体源

---

## 👥 KOL追踪列表 (Jacky专属)

### 你的账号
- **@jingouwang888** - 你自己的X账号

### 核心关注KOL

```yaml
Alpha/资讯:
  - @Bitwux: 资讯
  - @PhyrexNi: 分析
  - @ai_9684xtpa: AI/数据
  - @0xSunNFT: NFT
  - @hexiecs: 分析

交易/策略:
  - @bitfish: 交易
  - @BroLeon: 策略
  - @_FORAB: 分析
  - @wolfyxbt: 交易
  - @Michael_Liu93: 分析

生态/KOL:
  - @kiki520_eth: ETH
  - @xiaomucrypto: 加密
  - @jason_chen998: 资讯
  - @dotyyds1234: DOT
  - @BTCdayu: BTC
  - @GCsheng: 分析
  - @brc20niubi: BRC20

行业/媒体:
  - @thecryptoskanda: 资讯
  - @cz_binance: Binance创始人
  - @heyibinance: Binance
```

### 监控策略

```python
# 按优先级分组
KOL_PRIORITY = {
    "S级": ["@cz_binance", "@heyibinance"],  # 必读
    "A级": ["@Bitwux", "@PhyrexNi", "@ai_9684xtpa", "@bitfish"],  # 重要
    "B级": ["@0xSunNFT", "@BroLeon", "@wolfyxbt", "@Michael_Liu93"],  # 关注
    "C级": ["@kiki520_eth", "@xiaomucrypto", "@jason_chen998"],  # 参考
}

# 监控内容类型
KOL_MONITOR = {
    "新币喊单": ["@Bitwux", "@0xSunNFT", "@wolfyxbt"],
    "市场分析": ["@PhyrexNi", "@BroLeon", "@Michael_Liu93"],
    "行业资讯": ["@thecryptoskanda", "@jason_chen998"],
    "AI/技术": ["@ai_9684xtpa", "@hexiecs"],
}
```

---

## 🪙 Meme币监控配置

### 链的优先级 (固定)
```
Solana 🔥 > BSC > Base
```

### 链上数据源 (新增)

```yaml
GMGN:
  网址: https://gmgn.ai
  功能:
    - 新币监控: https://gmgn.ai/sol/new_pairs
    - 热门榜: https://gmgn.ai/sol/trending
    - 聪明钱追踪: https://gmgn.ai/smart_money
  API: https://api.gmgn.ai (需注册)
  特色: 实时、精准、聪明钱标签
  优先级: ⭐⭐⭐⭐⭐

DeBank:
  网址: https://debank.com
  功能:
    - 钱包追踪
    - 聪明钱地址监控
  API: https://api.debank.com (有限)
  特色: 地址标签、持仓分析

DexScreener:
  网址: https://dexscreener.com
  功能:
    - 新币: /solana/new-pairs
    - 热门: /solana/hot
  API: https://api.dexscreener.com
  特色: 全面、免费

Birdeye:
  网址: https://birdeye.so
  功能: 链上数据、价格、交易量
  API: https://public-api.birdeye.so
```

### 新币发现策略

```python
新币发现渠道 = {
    "实时监控": [
        "GMGN 新币对列表",
        "DexScreener 新币",
        "DeBank 聪明钱钱包新买入",
    ],
    "KOL追踪": [
        "监控@Bitwux等KOL的新币推文",
        "提取合约地址",
        "快速质检",
    ],
    "聪明钱追踪": [
        "追踪已知聪明钱地址",
        "复制他们的新买入",
        "分析持仓变化",
    ],
}

早期发现信号 = {
    "信号1": "聪明钱地址买入 < 1小时",
    "信号2": "多个聪明钱同时买入",
    "信号3": "KOL喊单 + 交易量激增",
    "信号4": "GMGM热度上升",
}
```

---

## 🤖 AI Agent Meme专项监控

### 监控关键词 (扩展)

```yaml
核心关键词:
  - AI Agent
  - ai16z
  - eliza
  - framework

新增关键词:
  - openclaw
  - agent支付
  - agent payment
  - autonomous agent
  - virtuals
  - game
  - ai16z/eliza
```

### 相关币追踪

```yaml
Solana AI生态:
  - $AI16Z: ai16z核心
  - $FARTCOIN: AI社区
  - $GAME: 游戏AI
  - $ZENTAI: (自动发现新币)

Base AI生态:
  - $VIRTUAL: Virtuals协议
  - $AI: (自动发现新币)

BSC AI生态:
  - (监控中)

新币发现:
  - 自动扫描新币名字包含 "AI"/"AGENT"/"ELIZA"
  - 检查社交媒体提及
  - 分析合约安全性
```

### 早期发现机制

```python
def 发现新AI_Meme():
    监控渠道 = [
        "GMGN 新币中含AI关键词",
        "DexScreener 搜索AI相关",
        "Twitter监控 @shawwashere 等AI KOL",
        "GitHub监控 ai16z/eliza 等项目更新",
    ]

    早期信号 = [
        "合约部署 < 6小时",
        "持有者 < 500但快速增长",
        "交易量突然激增",
        "AI KOL开始提及",
    ]

    if 满足(早期信号, 至少2个):
        推送到简报("🚨 AI Meme早期机会: [币名]")
```

---

## 🎯 Polymarket配置

### 关注方向

```yaml
体育类市场:
  - 足球比赛结果
  - 篮球比赛结果
  - 其他体育赛事
  特点: 流动性好，数据源多

稳定套利:
  - 同一事件不同市场价差
  - 1-3%稳定收益
  - 高流动性市场

Bot自动交易:
  - OpenClaw Bitcoin 5m UP/DOWN
  - 策略状态实时显示
  - 胜率监控
```

### OpenClaw策略集成

```yaml
当前运行策略:
  Bitcoin 5m UP/DOWN:
    状态: 监控中
    胜率目标: >55%
    信号来源: OpenClaw Webhook

体育套利Bot:
    状态: (待开发)
    类型: 稳定套利
    目标收益: 1-3%/次
```

### 市场监控重点

```python
Polymarket监控 = {
    "体育类": {
        "优先级": "高",
        "原因": "流动性好，数据多",
        "套利机会": "频繁",
    },
    "加密货币": {
        "优先级": "中",
        "市场": "BTC价格预测",
    },
    "重大事件": {
        "优先级": "中",
        "类型": ["选举", "战争", "经济数据"],
    },
}

套利扫描器逻辑:
    if 市场A.是概率 + 市场B.否概率 < 100% - 手续费:
        return "套利机会"

稳定盈利策略:
    - 寻找 1-3% 价差
    - 高流动性市场
    - 短期市场(< 7天)
```

---

## 📡 API配置清单

### 市场数据API

```yaml
CoinGecko:
  BaseURL: https://api.coingecko.com/api/v3
  免费额度: 100次/分

GMGN (新增 - 重点):
  BaseURL: https://api.gmgn.ai
  文档: https://docs.gmgn.ai
  注册: https://gmgn.ai
  优先级: ⭐⭐⭐⭐⭐
  功能: 新币、聪明钱、热度

DexScreener:
  BaseURL: https://api.dexscreener.com
  免费: 是
  功能: 新币、价格、交易量

Birdeye:
  BaseURL: https://public-api.birdeye.so
  免费: 有限
```

### 社交媒体

```yaml
Twitter/X:
  方案1: Jina Reader (推荐)
    用法: GET https://r.jina.ai/http://x.com/username
    返回: 纯文本
    免费: 是

  方案2: Twitter API
    需要: API Key
    限制: 付费

监控的KOL列表:
  S级: @cz_binance, @heyibinance
  A级: @Bitwux, @PhyrexNi, @ai_9684xtpa, @bitfish
  B级: @0xSunNFT, @BroLeon, @wolfyxbt, @Michael_Liu93
  其他: 见完整列表
```

---

## 🔧 技术实现

### Python配置

```python
# config.py

# KOL列表 (Jacky专属)
MY_KOLS = {
    "S级": ["cz_binance", "heyibinance"],
    "A级": ["Bitwux", "PhyrexNi", "ai_9684xtpa", "bitfish"],
    "B级": ["0xSunNFT", "BroLeon", "wolfyxbt", "Michael_Liu93"],
    "C级": ["kiki520_eth", "xiaomucrypto", "jason_chen998",
            "dotyyds1234", "BTCdayu", "GCsheng", "brc20niubi",
            "thecryptoskanda", "hexiecs"],
}

# AI Agent监控关键词
AI_KEYWORDS = [
    "AI Agent", "ai16z", "eliza", "framework",
    "openclaw", "agent payment", "autonomous agent",
    "virtuals", "game",
]

# 链优先级
CHAIN_PRIORITY = ["solana", "bsc", "base"]

# 链上数据源
ONCHAIN_TOOLS = {
    "gmgn": {
        "url": "https://api.gmgn.ai",
        "priority": 1,
    },
    "dexscreener": {
        "url": "https://api.dexscreener.com",
        "priority": 2,
    },
    "birdeye": {
        "url": "https://public-api.birdeye.so",
        "priority": 3,
    },
}

# Polymarket配置
POLY_CONFIG = {
    "focus": ["sports", "crypto"],
    "arbitrage": {
        "min_profit": 0.01,  # 1%
        "max_profit": 0.03,  # 3% 稳定套利
    },
    "openclaw_webhook": os.getenv("OPENCLAW_WEBHOOK_URL"),
}
```

---

## 📊 监控频率

| 数据源 | 频率 | 优先级 |
|--------|------|--------|
| GMGN新币 | 实时 | 🔴 |
| KOL推文 | 每10分钟 | 🔴 |
| DexScreener | 每5分钟 | 🔴 |
| Polymarket套利 | 每5分钟 | 🔴 |
| CoinGecko价格 | 每15分钟 | 🟡 |
| OpenClaw信号 | 实时 | 🔴 |

---

## 🚀 下一步

配置已更新，包含：
- ✅ 你的专属KOL列表 (20+账号)
- ✅ 链优先级: Solana > BSC > Base
- ✅ AI Agent关键词 (含openclaw、agent支付)
- ✅ 链上工具: GMGN、Debot等
- ✅ Polymarket体育类 + 稳定套利

**确认无误后开始写代码？**
