"""
Twitter/X数据采集器 - Twitter Fetcher
使用Jina Reader获取KOL推文内容
"""

import asyncio
import aiohttp
import ssl
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pytz
import re
from urllib.parse import quote


class TwitterFetcher:
    """Twitter数据采集器 (使用Jina Reader)"""

    def __init__(self, config: Dict):
        self.config = config
        self.my_kols = config.get("MY_KOLS", {})
        self.kol_monitor = config.get("KOL_MONITOR", {})
        self.api_endpoints = config.get("API_ENDPOINTS", {})
        self.tz = pytz.timezone(config.get("TIMEZONE", "Asia/Shanghai"))
        self.jina_base = "https://r.jina.ai/http://x.com/"

        # SSL context
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    async def fetch_user_tweets(self, username: str, limit: int = 10) -> List[Dict]:
        """
        获取指定用户的推文

        Args:
            username: Twitter用户名 (不带@)
            limit: 返回数量

        Returns:
            [
                {
                    "username": "user",
                    "text": "推文内容",
                    "url": "推文链接",
                    "time": "...",
                    "likes": 100,
                    "replies": 10,
                    "retweets": 5,
                },
                ...
            ]
        """
        url = f"{self.jina_base}{username}"

        try:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, timeout=20) as resp:
                    if resp.status == 200:
                        content = await resp.text()
                        return self._parse_tweets(content, username)
        except Exception as e:
            print(f"获取@{username}推文失败: {e}")

        return []

    def _parse_tweets(self, content: str, username: str) -> List[Dict]:
        """
        解析Jina Reader返回的推文内容

        Jina Reader返回的是纯文本，需要从中提取推文
        """
        tweets = []

        # 简单解析：按时间戳分割推文
        # 实际中Jina返回的格式可能变化，需要适配
        lines = content.split("\n")

        current_tweet = []
        current_time = None

        for line in lines:
            line = line.strip()

            # 检测时间戳 (推文通常以时间开头)
            if re.match(r"^\d{1,2}/\d{1,2}", line) or re.match(r"^\d+h$", line):
                if current_tweet:
                    text = " ".join(current_tweet).strip()
                    if text and len(text) > 10:
                        tweets.append({
                            "username": username,
                            "text": text,
                            "time": current_time or datetime.now(self.tz).strftime("%H:%M"),
                            "url": f"https://x.com/{username}",
                        })
                current_tweet = []
                current_time = line
            elif line and not line.startswith("@"):
                current_tweet.append(line)

        # 最后一条推文
        if current_tweet:
            text = " ".join(current_tweet).strip()
            if text and len(text) > 10:
                tweets.append({
                    "username": username,
                    "text": text,
                    "time": current_time or datetime.now(self.tz).strftime("%H:%M"),
                    "url": f"https://x.com/{username}",
                })

        return tweets[:10]  # 限制返回数量

    async def fetch_kol_tweets(self, level: str = "S") -> Dict[str, List[Dict]]:
        """
        获取指定优先级KOL的推文

        Args:
            level: KOL等级 (S/A/B/C)

        Returns:
            {
                "username1": [...],
                "username2": [...],
            }
        """
        kols = self.my_kols.get(f"{level}级", [])
        result = {}

        # 并行获取所有KOL的推文
        tasks = [self.fetch_user_tweets(kol) for kol in kols]
        tweet_lists = await asyncio.gather(*tasks, return_exceptions=True)

        for kol, tweets in zip(kols, tweet_lists):
            if isinstance(tweets, Exception):
                continue
            if tweets:
                result[kol] = tweets

        return result

    async def fetch_all_important_kols(self) -> Dict[str, List[Dict]]:
        """
        获取S级和A级KOL的推文

        Returns:
            {
                "S级": {"kol1": [...], ...},
                "A级": {"kol1": [...], ...},
            }
        """
        result = {}

        for level in ["S", "A"]:
            kols = self.my_kols.get(f"{level}级", [])

            tasks = [self.fetch_user_tweets(kol) for kol in kols]
            tweet_lists = await asyncio.gather(*tasks, return_exceptions=True)

            level_result = {}
            for kol, tweets in zip(kols, tweet_lists):
                if isinstance(tweets, Exception) or not tweets:
                    continue
                level_result[kol] = tweets

            if level_result:
                result[f"{level}级"] = level_result

        return result

    async def extract_token_addresses(self, tweets: Dict) -> List[Dict]:
        """
        从推文中提取合约地址

        Args:
            tweets: 推文数据

        Returns:
            [
                {
                    "token": "TOKEN",
                    "address": "合约地址",
                    "chain": "推测的链",
                    "source": "推文作者",
                },
                ...
            ]
        """
        addresses = []

        # Solana地址格式 (base58, 32-44字符)
        solana_pattern = r"[1-9A-HJ-NP-Za-km-z]{32,44}"
        # ETH/BSC地址格式 (0x开头, 42字符)
        evm_pattern = r"0x[a-fA-F0-9]{40}"

        for level, kols in tweets.items():
            for kol, tweet_list in kols.items():
                for tweet in tweet_list:
                    text = tweet.get("text", "")

                    # 查找Solana地址
                    sol_matches = re.findall(solana_pattern, text)
                    for addr in sol_matches:
                        if len(addr) >= 32:  # Solana地址
                            addresses.append({
                                "address": addr,
                                "chain": "solana",
                                "source": kol,
                                "text": text[:100],
                                "url": tweet.get("url", ""),
                            })

                    # 查找EVM地址
                    evm_matches = re.findall(evm_pattern, text)
                    for addr in evm_matches:
                        addresses.append({
                            "address": addr,
                            "chain": "evm",
                            "source": kol,
                            "text": text[:100],
                            "url": tweet.get("url", ""),
                        })

        return addresses

    async def get_tweet_summary(self) -> Dict:
        """
        获取推文摘要

        Returns:
            {
                "S级推文": {...},
                "A级推文": {...},
                "新币提及": [...],
                "重要资讯": [...],
                "timestamp": "..."
            }
        """
        tweets = await self.fetch_all_important_kols()

        # 提取合约地址
        token_mentions = await self.extract_token_addresses(tweets)

        # 提取重要资讯 (高互动或特定关键词)
        important_news = []
        for level, kols in tweets.items():
            for kol, tweet_list in kols.items():
                for tweet in tweet_list:
                    text = tweet.get("text", "")
                    # 简单的重要性判断
                    if self._is_important(text):
                        important_news.append({
                            "username": kol,
                            "text": text,
                            "level": level,
                            "url": tweet.get("url", ""),
                        })

        return {
            "tweets": tweets,
            "token_mentions": token_mentions,
            "important_news": important_news[:10],
            "timestamp": datetime.now(self.tz).strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _is_important(self, text: str) -> bool:
        """判断推文是否重要"""
        # 重要关键词
        important_keywords = [
            "突破", "暴跌", "暴涨", "新高", "新低",
            "上架", "下架", "binance", "币安",
            "融资", "投资", "ipo",
            "监管", "禁止",
            "alert", "break", "pump", "dump",
        ]

        text_lower = text.lower()
        return any(kw in text_lower or kw in text for kw in important_keywords)


# 测试代码
if __name__ == "__main__":
    import sys
    sys.path.append("..")
    from config import MY_KOLS, KOL_MONITOR, API_ENDPOINTS, TIMEZONE

    config = {
        "MY_KOLS": MY_KOLS,
        "KOL_MONITOR": KOL_MONITOR,
        "API_ENDPOINTS": API_ENDPOINTS,
        "TIMEZONE": TIMEZONE,
    }

    async def test():
        fetcher = TwitterFetcher(config)

        print("=== 测试获取KOL推文 ===")
        # 测试获取一个KOL的推文
        tweets = await fetcher.fetch_user_tweets("cz_binance", 5)

        print(f"获取到 {len(tweets)} 条推文")
        for tweet in tweets[:3]:
            print(f"\n{tweet['username']}: {tweet['text'][:100]}...")

    asyncio.run(test())
