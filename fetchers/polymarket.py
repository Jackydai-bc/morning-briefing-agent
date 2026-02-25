"""
Polymarket数据采集器 - Polymarket Fetcher
获取预测市场数据、套利机会、OpenClaw策略状态
"""

import asyncio
import aiohttp
import ssl
from typing import Dict, List, Optional
from datetime import datetime
import pytz
import re


class PolymarketFetcher:
    """Polymarket数据采集器"""

    def __init__(self, config: Dict):
        self.config = config
        self.api_endpoints = config.get("API_ENDPOINTS", {})
        self.poly_config = config.get("POLY_CONFIG", {})
        self.tz = pytz.timezone(config.get("TIMEZONE", "Asia/Shanghai"))

        # SSL context
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    async def fetch_markets(self, limit: int = 100) -> List[Dict]:
        """
        获取Polymarket市场列表

        Args:
            limit: 返回数量

        Returns:
            [
                {
                    "id": "...",
                    "question": "问题",
                    "yes_price": 0.65,
                    "no_price": 0.38,
                    "volume": 50000,
                    "liquidity": 10000,
                    "end_date": "...",
                    "category": "sports",
                },
                ...
            ]
        """
        url = self.api_endpoints["polymarket_markets"]

        try:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, params={"limit": limit}, timeout=15) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._parse_markets(data)
        except Exception as e:
            print(f"获取Polymarket市场失败: {e}")

        return []

    def _parse_markets(self, data: List) -> List[Dict]:
        """解析市场数据"""
        markets = []

        for market in data:
            try:
                # 获取价格
                yes_price = market.get("bestAsk", 0) / 100 if market.get("bestAsk") else 0
                no_price = 1 - yes_price

                markets.append({
                    "id": market.get("id", ""),
                    "question": market.get("question", ""),
                    "description": market.get("description", ""),
                    "yes_price": yes_price,
                    "no_price": no_price,
                    "volume": market.get("volume", 0),
                    "liquidity": market.get("liquidity", 0),
                    "end_date": market.get("endDate", ""),
                    "category": self._get_category(market),
                    "tags": market.get("tags", []),
                })
            except:
                continue

        return markets

    def _get_category(self, market: Dict) -> str:
        """获取市场类别"""
        tags = market.get("tags", [])
        description = market.get("description", "").lower()
        question = market.get("question", "").lower()

        # 体育类别
        sports_keywords = ["football", "basketball", "soccer", "nba", "nfl", "世界杯", "比赛"]
        if any(kw in str(tags).lower() or kw in description or kw in question for kw in sports_keywords):
            return "sports"

        # 加密货币
        crypto_keywords = ["bitcoin", "btc", "eth", "crypto", "price"]
        if any(kw in description or kw in question for kw in crypto_keywords):
            return "crypto"

        # 政治
        politics_keywords = ["election", "president", "trump", "biden"]
        if any(kw in description or kw in question for kw in politics_keywords):
            return "politics"

        return "other"

    async def fetch_new_markets(self, max_age_hours: int = 24) -> List[Dict]:
        """
        获取新市场

        Args:
            max_age_hours: 最大市场年龄(小时)

        Returns:
            新市场列表
        """
        markets = await self.fetch_markets(200)

        # 过滤新市场
        cutoff_time = datetime.now(self.tz) - timedelta(hours=max_age_hours)
        new_markets = []

        for market in markets:
            try:
                end_date = market.get("end_date", "")
                if end_date:
                    # 简单判断: 如果end_date在未来不久
                    new_markets.append(market)
            except:
                new_markets.append(market)

        return new_markets[:20]

    def find_arbitrage_opportunities(self, markets: List[Dict]) -> List[Dict]:
        """
        寻找套利机会

        Args:
            markets: 市场列表

        Returns:
            [
                {
                    "market_id": "...",
                    "question": "...",
                    "type": "stable",  # stable/high
                    "profit": 0.02,
                    "action": "买是 卖否",
                },
                ...
            ]
        """
        opportunities = []

        for market in markets:
            yes_price = market.get("yes_price", 0)
            no_price = market.get("no_price", 0)

            # 计算套利空间
            total = yes_price + no_price
            profit = 1 - total

            # 稳定套利: 1-3%
            min_profit = self.poly_config.get("arbitrage", {}).get("min_profit", 0.01)
            max_profit = self.poly_config.get("arbitrage", {}).get("max_profit", 0.03)

            if min_profit <= profit <= max_profit:
                opportunities.append({
                    **market,
                    "type": "stable",
                    "profit": profit,
                    "action": f"买是({yes_price:.2f}) 卖否({no_price:.2f})",
                })
            # 高盈利套利: >3%
            elif profit > max_profit and profit < 0.1:  # 排除异常值
                opportunities.append({
                    **market,
                    "type": "high",
                    "profit": profit,
                    "action": f"买是({yes_price:.2f}) 卖否({no_price:.2f})",
                })

        # 按收益排序
        opportunities.sort(key=lambda x: x.get("profit", 0), reverse=True)

        return opportunities[:10]

    async def fetch_sports_markets(self) -> List[Dict]:
        """
        获取体育类市场

        Returns:
            体育市场列表
        """
        all_markets = await self.fetch_markets(200)

        sports = [m for m in all_markets if m.get("category") == "sports"]

        return sports[:20]

    async def get_openclaw_signal(self) -> Dict:
        """
        获取OpenClaw策略信号

        Returns:
            {
                "strategy": "Bitcoin 5m UP/DOWN",
                "signal": "UP",
                "confidence": 0.55,
                "status": "running",
                "last_update": "...",
            }
        """
        # 这里需要从OpenClaw webhook获取实际信号
        # 暂时返回模拟数据
        return {
            "strategy": "Bitcoin 5m UP/DOWN",
            "signal": "UP",
            "confidence": 0.55,
            "status": "running",
            "last_update": datetime.now(self.tz).strftime("%H:%M"),
        }

    async def get_polymarket_summary(self) -> Dict:
        """
        获取Polymarket摘要

        Returns:
            {
                "new_markets": [...],
                "arbitrage": [...],
                "sports": [...],
                "openclaw_signal": {...},
                "timestamp": "..."
            }
        """
        markets, new_markets, sports = await asyncio.gather(
            self.fetch_markets(200),
            self.fetch_new_markets(24),
            self.fetch_sports_markets(),
            return_exceptions=True
        )

        if isinstance(markets, Exception):
            markets = []
        if isinstance(new_markets, Exception):
            new_markets = []
        if isinstance(sports, Exception):
            sports = []

        arbitrage = self.find_arbitrage_opportunities(markets)
        openclaw_signal = await self.get_openclaw_signal()

        return {
            "new_markets": new_markets[:10],
            "arbitrage": arbitrage[:5],
            "sports_markets": sports[:10],
            "openclaw_signal": openclaw_signal,
            "timestamp": datetime.now(self.tz).strftime("%Y-%m-%d %H:%M:%S"),
        }


# 测试代码
if __name__ == "__main__":
    import sys
    from datetime import timedelta
    sys.path.append("..")
    from config import API_ENDPOINTS, POLY_CONFIG, TIMEZONE

    config = {
        "API_ENDPOINTS": API_ENDPOINTS,
        "POLY_CONFIG": POLY_CONFIG,
        "TIMEZONE": TIMEZONE,
    }

    async def test():
        fetcher = PolymarketFetcher(config)

        print("=== 测试获取Polymarket数据 ===")
        summary = await fetcher.get_polymarket_summary()

        print(f"\n=== 新市场 ({len(summary['new_markets'])}) ===")
        for market in summary["new_markets"][:5]:
            print(f"- {market['question'][:50]}...")

        print(f"\n=== 套利机会 ({len(summary['arbitrage'])}) ===")
        for opp in summary["arbitrage"][:3]:
            print(f"- {opp['profit']*100:.1f}%: {opp['action']}")

    asyncio.run(test())
