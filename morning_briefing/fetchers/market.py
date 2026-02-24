"""
市场数据采集器 - Market Data Fetcher
获取加密货币市场数据: 价格、涨跌幅、恐慌贪婪指数等
"""

import asyncio
import aiohttp
import ssl
from typing import Dict, List, Optional
from datetime import datetime
import pytz


class MarketFetcher:
    """市场数据采集器"""

    def __init__(self, config: Dict):
        self.config = config
        self.api_endpoints = config.get("API_ENDPOINTS", {})
        self.api_keys = config.get("API_KEYS", {})
        self.watchlist = config.get("WATCHED_COINS", {})
        self.tz = pytz.timezone(config.get("TIMEZONE", "Asia/Shanghai"))

        # 创建SSL context (macOS兼容性)
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    async def fetch_prices(self) -> Dict:
        """
        获取关注币种的价格和涨跌幅

        Returns:
            {
                "bitcoin": {"symbol": "BTC", "price": 98500, "change_24h": 2.3, ...},
                "ethereum": {"symbol": "ETH", "price": 3450, "change_24h": 1.8, ...},
                ...
            }
        """
        ids = ",".join(self.watchlist.keys())
        url = f"{self.api_endpoints['coingecko_price']}"

        params = {
            "ids": ids,
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_market_cap": "true",
            "include_24hr_vol": "true",
        }

        # 如果有API key
        if self.api_keys.get("coingecko"):
            headers = {"x-cg-demo-api-key": self.api_keys["coingecko"]}
        else:
            headers = {}

        try:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, params=params, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        result = {}
                        for coin_id, coin_data in data.items():
                            symbol = self.watchlist.get(coin_id, coin_id.upper())
                            result[coin_id] = {
                                "symbol": symbol,
                                "price": coin_data.get("usd", 0),
                                "change_24h": coin_data.get("usd_24h_change", 0),
                                "market_cap": coin_data.get("usd_market_cap", 0),
                                "volume_24h": coin_data.get("usd_24h_vol", 0),
                                "last_update": datetime.now(self.tz).strftime("%H:%M"),
                            }
                        return result
        except Exception as e:
            print(f"获取价格数据失败: {e}")

        return {}

    async def fetch_fear_greed(self) -> Dict:
        """
        获取恐慌贪婪指数

        Returns:
            {
                "value": 65,
                "text": "Greed",
                "change": 5,
                "timestamp": "..."
            }
        """
        url = self.api_endpoints["fear_greed"]

        try:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        value = int(data.get("data", [{}])[0].get("value", 50))
                        text = data.get("data", [{}])[0].get("value_classification", "Neutral")

                        # 简单的涨跌计算 (实际应该存储历史值)
                        return {
                            "value": value,
                            "text": self._translate_fg(text),
                            "classification": self._get_fg_level(value),
                            "timestamp": datetime.now(self.tz).strftime("%H:%M"),
                        }
        except Exception as e:
            print(f"获取恐慌贪婪指数失败: {e}")

        return {"value": 50, "text": "中性", "classification": "中性"}

    def _translate_fg(self, text: str) -> str:
        """翻译恐慌贪婪指数"""
        translations = {
            "Extreme Fear": "极度恐慌",
            "Fear": "恐慌",
            "Neutral": "中性",
            "Greed": "贪婪",
            "Extreme Greed": "极度贪婪",
        }
        return translations.get(text, text)

    def _get_fg_level(self, value: int) -> str:
        """获取恐慌贪婪等级"""
        if value <= 20:
            return "极度恐慌"
        elif value <= 40:
            return "恐慌"
        elif value <= 60:
            return "中性"
        elif value <= 80:
            return "贪婪"
        else:
            return "极度贪婪"

    async def fetch_top_gainers(self, limit: int = 20) -> List[Dict]:
        """
        获取涨跌幅榜

        Args:
            limit: 返回数量

        Returns:
            [
                {"symbol": "COIN", "price": 1.23, "change_24h": 50.5, ...},
                ...
            ]
        """
        url = self.api_endpoints["coingecko_markets"]

        params = {
            "vs_currency": "usd",
            "order": "percent_change_24h_desc",
            "per_page": limit,
            "page": 1,
            "sparkline": "false",
        }

        headers = {}
        if self.api_keys.get("coingecko"):
            headers["x-cg-demo-api-key"] = self.api_keys["coingecko"]

        try:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, params=params, headers=headers, timeout=15) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        result = []
                        for coin in data:
                            result.append({
                                "id": coin.get("id"),
                                "symbol": coin.get("symbol", "").upper(),
                                "name": coin.get("name"),
                                "price": coin.get("current_price", 0),
                                "change_24h": coin.get("price_change_percentage_24h", 0),
                                "volume_24h": coin.get("total_volume", 0),
                                "market_cap": coin.get("market_cap", 0),
                            })
                        return result
        except Exception as e:
            print(f"获取涨跌幅榜失败: {e}")

        return []

    async def fetch_market_overview(self) -> Dict:
        """
        获取市场概况 (整合所有市场数据)

        Returns:
            {
                "prices": {...},
                "fear_greed": {...},
                "top_gainers": [...],
                "timestamp": "..."
            }
        """
        prices, fear_greed, gainers = await asyncio.gather(
            self.fetch_prices(),
            self.fetch_fear_greed(),
            self.fetch_top_gainers(10)
        )

        return {
            "prices": prices,
            "fear_greed": fear_greed,
            "top_gainers": gainers,
            "timestamp": datetime.now(self.tz).strftime("%Y-%m-%d %H:%M:%S"),
        }


# 测试代码
if __name__ == "__main__":
    import sys
    sys.path.append("..")
    from config import API_ENDPOINTS, API_KEYS, WATCHED_COINS, TIMEZONE

    config = {
        "API_ENDPOINTS": API_ENDPOINTS,
        "API_KEYS": API_KEYS,
        "WATCHED_COINS": WATCHED_COINS,
        "TIMEZONE": TIMEZONE,
    }

    async def test():
        fetcher = MarketFetcher(config)
        overview = await fetcher.fetch_market_overview()

        print("=== 价格数据 ===")
        for coin, data in overview["prices"].items():
            print(f"{data['symbol']}: ${data['price']:,.2f} ({data['change_24h']:+.2f}%)")

        print("\n=== 恐慌贪婪指数 ===")
        fg = overview["fear_greed"]
        print(f"{fg['value']} - {fg['text']}")

        print("\n=== 涨幅榜 ===")
        for coin in overview["top_gainers"][:5]:
            print(f"{coin['symbol']}: {coin['change_24h']:+.2f}%")

    asyncio.run(test())
