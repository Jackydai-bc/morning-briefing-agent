"""
晨间简报Agent - 配置文件
Morning Briefing Agent Configuration
"""

import os
from dataclasses import dataclass
from typing import List, Dict

# ==================== 项目配置 ====================
PROJECT_NAME = "jacky-morning-briefing"
VERSION = "1.0.0"
TIMEZONE = "Asia/Shanghai"

# ==================== 你的账号 ====================
MY_TWITTER = "jingouwang888"

# ==================== KOL列表 (Jacky专属) ====================
MY_KOLS = {
    "S级": ["cz_binance", "heyibinance"],  # 必读
    "A级": ["Bitwux", "PhyrexNi", "ai_9684xtpa", "bitfish"],  # 重要
    "B级": ["0xSunNFT", "BroLeon", "wolfyxbt", "Michael_Liu93"],  # 关注
    "C级": [
        "kiki520_eth", "xiaomucrypto", "jason_chen998",
        "dotyyds1234", "BTCdayu", "GCsheng", "brc20niubi",
        "thecryptoskanda", "hexiecs", "_FORAB"
    ],  # 参考
}

# KOL监控分类
KOL_MONITOR = {
    "新币喊单": ["Bitwux", "0xSunNFT", "wolfyxbt"],
    "市场分析": ["PhyrexNi", "BroLeon", "Michael_Liu93"],
    "行业资讯": ["thecryptoskanda", "jason_chen998"],
    "AI/技术": ["ai_9684xtpa", "hexiecs"],
}

# ==================== AI Agent监控关键词 ====================
AI_KEYWORDS = [
    "AI Agent", "ai16z", "eliza", "framework",
    "openclaw", "agent payment", "autonomous agent",
    "virtuals", "game",
]

# AI相关币种
AI_MEME_COINS = {
    "solana": ["AI16Z", "FARTCOIN", "GAME"],
    "base": ["VIRTUAL"],
    "bsc": [],
}

# ==================== 链配置 ====================
CHAIN_PRIORITY = ["solana", "bsc", "base"]

CHAIN_CONFIG = {
    "solana": {
        "name": "Solana",
        "dexscreener_id": "solana",
        "gmgn_id": "sol",
        "native_token": "SOL",
    },
    "bsc": {
        "name": "BSC",
        "dexscreener_id": "bsc",
        "gmgn_id": "bsc",
        "native_token": "BNB",
    },
    "base": {
        "name": "Base",
        "dexscreener_id": "base",
        "gmgn_id": "base",
        "native_token": "ETH",
    },
}

# ==================== API配置 ====================
API_KEYS = {
    "coingecko": os.getenv("COINGECKO_API_KEY", ""),
    "birdeye": os.getenv("BIRDEYE_API_KEY", ""),
    "gmgn": os.getenv("GMGN_API_KEY", ""),
    "claude": os.getenv("CLAUDE_API_KEY", ""),
    "openclaw": os.getenv("OPENCLAW_WEBHOOK_URL", ""),
}

# ==================== API端点 ====================
API_ENDPOINTS = {
    # CoinGecko
    "coingecko_price": "https://api.coingecko.com/api/v3/simple/price",
    "coingecko_markets": "https://api.coingecko.com/api/v3/coins/markets",
    "coingecko_global": "https://api.coingecko.com/api/v3/global",

    # DexScreener
    "dexscreener_tokens": "https://api.dexscreener.com/latest/v2/tokens/",
    "dexscreener_search": "https://api.dexscreener.com/latest/v2/search/",
    "dexscreener_new_pairs": "https://api.dexscreener.com/latest/v2/pairs",

    # GMGN
    "gmgn_sol_new": "https://api.gmgn.ai/v2/sol/pairs/v2/new_pairs",
    "gmgn_bsc_new": "https://api.gmgn.ai/v2/bsc/pairs/v2/new_pairs",
    "gmgn_base_new": "https://api.gmgn.ai/v2/base/pairs/v2/new_pairs",
    "gmgn_sol_hot": "https://api.gmgn.ai/v2/sol/pairs/v2/hot_pairs",

    # Birdeye
    "birdeye_token_list": "https://public-api.birdeye.so/defi/v2/token_list",
    "birdeye_price": "https://public-api.birdeye.so/defi/price",

    # 恐慌贪婪指数
    "fear_greed": "https://api.alternative.me/fng/",

    # Polymarket
    "polymarket_markets": "https://gamma-api.polymarket.com/markets",

    # Jina Reader (Twitter)
    "jina_twitter": "https://r.jina.ai/http://x.com/",

    # RSS
    "coindesk_rss": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "theblock_rss": "https://www.theblockcrypto.com/rss.xml",
    "panews_rss": "https://www.panewslab.com/rss",
}

# ==================== 监控的币种 ====================
WATCHED_COINS = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
}

# ==================== Meme币质检标准 ====================
MEME_QUALITY_CHECK = {
    "最小交易量": 50000,  # 24h > $50k
    "最小持有者": 100,
    "最大Top10持仓": 50,  # %
    "最小LP锁定": 80,  # %
    "最小流动性": 10000,
}

# ==================== 新币筛选条件 ====================
NEW_TOKEN_FILTERS = {
    "最大年龄小时": 24,
    "最小交易量": 50000,
    "最小持有者": 100,
    "最小流动性": 10000,
}

# ==================== Polymarket配置 ====================
POLY_CONFIG = {
    "focus": ["sports", "crypto"],
    "arbitrage": {
        "min_profit": 0.01,  # 1%
        "max_profit": 0.03,  # 3% 稳定套利
        "min_liquidity": 10000,  # 最小流动性
    },
    "sports": {
        "football": True,
        "basketball": True,
        "other": True,
    },
}

# ==================== 简报输出配置 ====================
BRIEFING_CONFIG = {
    "输出格式": "markdown",
    "时区": "Asia/Shanghai",
    "最大条目": {
        "必读": 3,
        "新币": 10,
        "大涨": 5,
        "X精选": 5,
        "新闻": 3,
    },
}

# ==================== 通知配置 ====================
NOTIFICATION_CONFIG = {
    "discord_webhook": os.getenv("DISCORD_WEBHOOK_URL", ""),
    "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
    "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
    "enabled_channels": ["discord"],  # 可选: discord, telegram
}

# ==================== 数据存储 ====================
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")

# ==================== 监控频率 ====================
FETCH_INTERVALS = {
    "价格": 900,  # 15分钟
    "新币": 300,  # 5分钟
    "KOL推文": 600,  # 10分钟
    "Polymarket": 300,  # 5分钟
}

# ==================== 必读事件优先级 ====================
EVENT_PRIORITY = {
    "S级": [
        "美联储", "加息", "降息", "利率决议",
        "监管", "禁止", "合法化",
        "交易所被黑", "FTX", "破产",
        "BTC", "ETH", "突破", "暴跌", "暴涨",  # 涨跌>10%
    ],
    "A级": [
        "融资", "投资", "IPO",
        "上线", "下架", "Binance",
        "鲸鱼", "清算",
    ],
}

# ==================== 热门叙事关键词 ====================
NARRATIVE_KEYWORDS = {
    "AI Agent": ["ai", "agent", "eliza", "ai16z"],
    "RWA": ["rwa", "real world", "tokenized"],
    "GameFi": ["game", "gaming", "play to earn"],
    "DePIN": ["depin", "physical infrastructure"],
    "Meme": ["meme", "doge", "pepe", "shib"],
}

# ==================== 辅助函数 ====================
def get_all_kols() -> List[str]:
    """获取所有KOL用户名"""
    all_kols = []
    for kols in MY_KOLS.values():
        all_kols.extend(kols)
    return list(set(all_kols))


def get_priority_kols(level: str = "S") -> List[str]:
    """获取指定优先级的KOL"""
    return MY_KOLS.get(f"{level}级", [])


def get_chain_config(chain: str) -> Dict:
    """获取链配置"""
    return CHAIN_CONFIG.get(chain.lower(), {})


def get_gmgn_endpoint(chain: str) -> str:
    """获取GMGN新币端点"""
    chain_id = get_chain_config(chain).get("gmgn_id", chain)
    return f"https://api.gmgn.ai/v2/{chain_id}/pairs/v2/new_pairs"


def is_ai_keyword(text: str) -> bool:
    """检查文本是否包含AI关键词"""
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in AI_KEYWORDS)
