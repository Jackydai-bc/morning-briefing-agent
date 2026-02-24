"""
Meme币数据采集器 - Meme Coin Fetcher
使用DexScreener作为主要数据源，支持Solana、BSC、Base链
"""

import asyncio
import aiohttp
import ssl
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pytz
import re


class MemeFetcher:
    """Meme币数据采集器 (使用DexScreener)"""

    def __init__(self, config: Dict):
        self.config = config
        self.api_endpoints = config.get("API_ENDPOINTS", {})
        self.api_keys = config.get("API_KEYS", {})
        self.chain_priority = config.get("CHAIN_PRIORITY", ["solana", "bsc", "base"])
        self.chain_config = config.get("CHAIN_CONFIG", {})
        self.new_token_filters = config.get("NEW_TOKEN_FILTERS", {})
        self.ai_keywords = config.get("AI_KEYWORDS", [])
        self.tz = pytz.timezone(config.get("TIMEZONE", "Asia/Shanghai"))

        # SSL context
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

        # DexScreener配置
        self.dexscreener_base = "https://api.dexscreener.com/latest/v2"

    async def fetch_dexscreener_pairs(self, chain: str = "solana", sort_by: str = "age", limit: int = 50) -> List[Dict]:
        """
        从DexScreener获取交易对

        Args:
            chain: 链名称 (solana/bsc/base)
            sort_by: 排序方式 (age=最新, volume=交易量)
            limit: 返回数量

        Returns:
            [
                {
                    "address": "...",
                    "symbol": "TOKEN",
                    "name": "Token Name",
                    "chain": "solana",
                    "created_time": "...",
                    "liquidity": 100000,
                    "volume_24h": 500000,
                    "price": 0.0001,
                    "change_24h": 50.5,
                    "change_1h": 10.2,
                    "holders": 1000,
                    "lp_locked": True,
                    "is_ai": False,
                },
                ...
            ]
        """
        # DexScreener使用chain id
        chain_ids = {
            "solana": "solana",
            "bsc": "bsc",
            "base": "base",
        }

        chain_id = chain_ids.get(chain, chain)
        url = f"{self.dexscreener_base}/pairs/{chain_id}"

        params = {
            "limit": limit,
            "order": "key",  # 按地址排序可以获取较新的
        }

        try:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, params=params, timeout=30) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._parse_dexscreener_pairs(data, chain)
                    else:
                        print(f"DexScreener请求失败: {resp.status}")
                        return []
        except Exception as e:
            print(f"从DexScreener获取{chain}交易对失败: {e}")
            return []

    def _parse_dexscreener_pairs(self, data: Dict, chain: str) -> List[Dict]:
        """解析DexScreener返回的数据"""
        result = []

        pairs = data.get("pairs", [])

        for pair in pairs:
            try:
                # 获取基本信息
                base_token = pair.get("baseToken", {})
                quote_token = pair.get("quoteToken", {})
                pair_address = pair.get("pairAddress", "")

                # 跳过非稳定币对
                if not self._is_valid_pair(pair):
                    continue

                # 计算年龄
                pair_created_at = pair.get("pairCreatedAt", 0)
                if pair_created_at:
                    created_time = datetime.fromtimestamp(pair_created_at / 1000, tz=self.tz)
                    age_hours = (datetime.now(self.tz) - created_time).total_seconds() / 3600
                else:
                    created_time = None
                    age_hours = 999

                # 获取价格数据
                price_usd = pair.get("priceUsd", 0)
                if price_usd is None or price_usd == 0:
                    continue

                # 获取涨幅
                change_24h = pair.get("change_24h", 0) or 0
                change_1h = pair.get("change_1h", 0) or 0
                change_5m = pair.get("change_5m", 0) or 0

                # 获取流动性
                liquidity = pair.get("liquidity", {}).get("usd", 0) or 0
                if liquidity is None:
                    liquidity = 0

                # 获取交易量
                volume_24h = pair.get("volume", {}).get("h24", 0) or 0

                # 获取FDV (完全稀释估值)
                fdv = pair.get("fdv", 0) or 0

                # 检查是否是AI相关
                symbol = base_token.get("symbol", "")
                name = base_token.get("name", "")
                is_ai = self._is_ai_token(symbol, name)

                result.append({
                    "address": pair_address,
                    "symbol": symbol,
                    "name": name,
                    "chain": chain,
                    "dex": pair.get("dexId", "unknown"),
                    "created_time": created_time.strftime("%H:%M") if created_time else "",
                    "age_hours": age_hours,
                    "liquidity": liquidity,
                    "volume_24h": volume_24h,
                    "fdv": fdv,
                    "price": price_usd,
                    "change_24h": change_24h,
                    "change_1h": change_1h,
                    "change_5m": change_5m,
                    "holders": 0,  # DexScreener不提供
                    "lp_locked": None,  # DexScreener不提供
                    "lp_lock_pct": 0,
                    "market_cap": fdv,
                    "is_ai": is_ai,
                    "source": "dexscreener",
                    "txns": pair.get("txns", {}),
                    "pair_link": pair.get("url", ""),
                })
            except Exception as e:
                continue

        return result

    def _is_valid_pair(self, pair: Dict) -> bool:
        """检查是否是有效的交易对"""
        # 获取quote token
        quote_token = pair.get("quoteToken", {})
        quote_symbol = quote_token.get("symbol", "").upper()

        # 只接受稳定币对 (USDT, USDC, DAI, etc.)
        stablecoins = ["USDT", "USDC", "DAI", "USDC.E", "FDUSD", "PYUSD"]

        if quote_symbol not in stablecoins:
            return False

        # 检查是否有基础数据
        if not pair.get("baseToken"):
            return False

        return True

    async def fetch_dexscreener_hot(self, chain: str = "solana", limit: int = 30) -> List[Dict]:
        """
        获取热门交易对 (按交易量排序)

        Args:
            chain: 链名称
            limit: 返回数量

        Returns:
            热门交易对列表
        """
        # 先获取更多数据，然后按交易量排序
        pairs = await self.fetch_dexscreener_pairs(chain, sort_by="age", limit=200)

        # 过滤并排序
        filtered = []
        for pair in pairs:
            # 过滤条件
            if pair.get("liquidity", 0) < 1000:
                continue
            if pair.get("volume_24h", 0) < 100:
                continue

            filtered.append(pair)

        # 按交易量排序
        filtered.sort(key=lambda x: x.get("volume_24h", 0), reverse=True)

        return filtered[:limit]

    async def fetch_dexscreener_new(self, chain: str = "solana", max_age_hours: int = 24, limit: int = 50) -> List[Dict]:
        """
        获取新交易对

        Args:
            chain: 链名称
            max_age_hours: 最大币龄(小时)
            limit: 返回数量

        Returns:
            新交易对列表
        """
        pairs = await self.fetch_dexscreener_pairs(chain, sort_by="age", limit=200)

        # 过滤新币
        new_pairs = []
        for pair in pairs:
            age = pair.get("age_hours", 999)
            if age <= max_age_hours:
                new_pairs.append(pair)

        # 按币龄排序，最新的在前
        new_pairs.sort(key=lambda x: x.get("age_hours", 999))

        return new_pairs[:limit]

    async def fetch_dexscreener_gainers(self, chain: str = "solana", limit: int = 20) -> List[Dict]:
        """
        获取涨幅榜

        Args:
            chain: 链名称
            limit: 返回数量

        Returns:
            涨幅榜列表
        """
        pairs = await self.fetch_dexscreener_pairs(chain, sort_by="age", limit=200)

        # 过滤并排序
        filtered = []
        for pair in pairs:
            if pair.get("liquidity", 0) < 1000:
                continue
            if pair.get("volume_24h", 0) < 100:
                continue
            filtered.append(pair)

        # 按24h涨幅排序
        filtered.sort(key=lambda x: x.get("change_24h", 0), reverse=True)

        return filtered[:limit]

    async def fetch_dexscreener_by_token(self, token_address: str, chain: str = "solana") -> List[Dict]:
        """
        根据token地址获取信息

        Args:
            token_address: token合约地址
            chain: 链名称

        Returns:
            token信息
        """
        url = f"{self.dexscreener_base}/tokens/{token_address}"

        try:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, timeout=15) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._parse_dexscreener_pairs(data, chain)
        except Exception as e:
            print(f"获取token {token_address} 失败: {e}")

        return []

    async def fetch_all_new_pairs(self, max_age_hours: int = 24) -> Dict[str, List[Dict]]:
        """
        获取所有链的新币

        Args:
            max_age_hours: 最大币龄(小时)

        Returns:
            {
                "solana": [...],
                "bsc": [...],
                "base": [...],
                "ai_tokens": [...],
                "high_potential": [...],
            }
        """
        all_pairs = {"solana": [], "bsc": [], "base": [], "ai_tokens": [], "high_potential": []}

        # 并行获取所有链的数据
        tasks = []
        for chain in self.chain_priority:
            tasks.append(self.fetch_dexscreener_new(chain, max_age_hours, 100))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                continue
            chain = self.chain_priority[i]
            all_pairs[chain] = result

            # 筛选AI相关币
            ai_tokens = [t for t in result if t.get("is_ai", False)]
            all_pairs["ai_tokens"].extend(ai_tokens)

            # 筛选高潜力币
            high_potential = [t for t in result if self._is_high_potential(t)]
            all_pairs["high_potential"].extend(high_potential)

        return all_pairs

    async def fetch_all_hot_pairs(self) -> Dict[str, List[Dict]]:
        """
        获取所有链的热门币

        Returns:
            {
                "solana": [...],
                "bsc": [...],
                "base": [...],
            }
        """
        all_hot = {}

        tasks = []
        for chain in self.chain_priority:
            tasks.append(self.fetch_dexscreener_hot(chain, 50))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                continue
            chain = self.chain_priority[i]
            all_hot[chain] = result

        return all_hot

    async def fetch_all_gainers(self) -> Dict[str, List[Dict]]:
        """
        获取所有链的涨幅榜

        Returns:
            按链分类的涨幅榜
        """
        all_gainers = {}

        tasks = []
        for chain in self.chain_priority:
            tasks.append(self.fetch_dexscreener_gainers(chain, 30))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                continue
            chain = self.chain_priority[i]
            all_gainers[chain] = result

        return all_gainers

    def _is_ai_token(self, symbol: str, name: str) -> bool:
        """检查是否是AI相关代币"""
        text = f"{symbol} {name}".lower()
        return any(keyword.lower() in text for keyword in self.ai_keywords)

    def _is_high_potential(self, token: Dict) -> bool:
        """检查是否是高潜力币"""
        # 基础质检
        if token.get("liquidity", 0) < 5000:
            return False
        if token.get("volume_24h", 0) < 500:
            return False

        # 涨幅检查 (1h或5min有明显上涨)
        change_1h = token.get("change_1h", 0)
        change_5m = token.get("change_5m", 0)
        if change_1h > 20 or change_5m > 10:
            return True

        # 交易量活跃
        volume_24h = token.get("volume_24h", 0)
        liquidity = token.get("liquidity", 1)
        if liquidity > 0 and volume_24h / liquidity > 2:  # 交易量是流动性的2倍
            return True

        # AI相关自动标记为高潜力
        if token.get("is_ai", False):
            return True

        return False

    async def get_meme_summary(self) -> Dict:
        """
        获取Meme币市场摘要

        Returns:
            {
                "new_pairs": {...},
                "hot_pairs": {...},
                "gainers": {...},
                "ai_tokens": [...],
                "high_potential": [...],
                "narratives": {...},
                "timestamp": "..."
            }
        """
        new_pairs, hot_pairs, gainers = await asyncio.gather(
            self.fetch_all_new_pairs(24),
            self.fetch_all_hot_pairs(),
            self.fetch_all_gainers(),
            return_exceptions=True
        )

        if isinstance(new_pairs, Exception):
            new_pairs = {}
        if isinstance(hot_pairs, Exception):
            hot_pairs = {}
        if isinstance(gainers, Exception):
            gainers = {}

        # 分析叙事
        narratives = self._analyze_narratives(new_pairs)

        return {
            "new_pairs": new_pairs,
            "hot_pairs": hot_pairs,
            "gainers": gainers,
            "ai_tokens": new_pairs.get("ai_tokens", [])[:20],
            "high_potential": new_pairs.get("high_potential", [])[:20],
            "narratives": narratives,
            "timestamp": datetime.now(self.tz).strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _analyze_narratives(self, pairs: Dict) -> Dict:
        """分析当前热门叙事"""
        narratives = {
            "AI Agent": {"tokens": [], "count": 0},
            "Meme": {"tokens": [], "count": 0},
            "RWA": {"tokens": [], "count": 0},
            "GameFi": {"tokens": [], "count": 0},
        }

        # 统计各叙事的币数量
        all_tokens = []
        for chain_tokens in pairs.values():
            if isinstance(chain_tokens, list):
                all_tokens.extend(chain_tokens)

        for token in all_tokens[:50]:  # 只分析前50个
            symbol = token.get("symbol", "").lower()
            name = token.get("name", "").lower()

            if any(kw in symbol or kw in name for kw in ["ai", "agent", "eliza", "ai16z"]):
                narratives["AI Agent"]["tokens"].append(token.get("symbol"))
                narratives["AI Agent"]["count"] += 1
            elif any(kw in symbol or kw in name for kw in ["rwa", "real world"]):
                narratives["RWA"]["tokens"].append(token.get("symbol"))
                narratives["RWA"]["count"] += 1
            elif any(kw in symbol or kw in name for kw in ["game", "gaming"]):
                narratives["GameFi"]["tokens"].append(token.get("symbol"))
                narratives["GameFi"]["count"] += 1
            else:
                narratives["Meme"]["tokens"].append(token.get("symbol"))
                narratives["Meme"]["count"] += 1

        # 排序并只保留有币的叙事
        return {k: v for k, v in sorted(narratives.items(), key=lambda x: x[1]["count"], reverse=True) if v["count"] > 0}


# 测试代码
if __name__ == "__main__":
    import sys
    sys.path.append("..")
    from config import (
        API_ENDPOINTS, API_KEYS, CHAIN_PRIORITY,
        CHAIN_CONFIG, NEW_TOKEN_FILTERS, AI_KEYWORDS, TIMEZONE
    )

    config = {
        "API_ENDPOINTS": API_ENDPOINTS,
        "API_KEYS": API_KEYS,
        "CHAIN_PRIORITY": CHAIN_PRIORITY,
        "CHAIN_CONFIG": CHAIN_CONFIG,
        "NEW_TOKEN_FILTERS": NEW_TOKEN_FILTERS,
        "AI_KEYWORDS": AI_KEYWORDS,
        "TIMEZONE": TIMEZONE,
    }

    async def test():
        fetcher = MemeFetcher(config)

        print("=== 测试获取Solana新币 ===")
        new_pairs = await fetcher.fetch_dexscreener_new("solana", 24, 20)

        print(f"获取到 {len(new_pairs)} 个新币")
        for pair in new_pairs[:5]:
            ai_tag = "🤖" if pair.get("is_ai") else ""
            print(f"{pair['symbol']}: {pair['change_24h']:+.1f}% (${pair['volume_24h']:,.0f}) {ai_tag}")

    asyncio.run(test())
