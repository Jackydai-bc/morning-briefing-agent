"""
新闻数据采集器 - News Fetcher
从CoinDesk、The Block等加密媒体获取新闻
"""

import asyncio
import aiohttp
import ssl
from typing import Dict, List, Optional
from datetime import datetime
import pytz
import feedparser
import re


class NewsFetcher:
    """新闻数据采集器"""

    def __init__(self, config: Dict):
        self.config = config
        self.api_endpoints = config.get("API_ENDPOINTS", {})
        self.tz = pytz.timezone(config.get("TIMEZONE", "Asia/Shanghai"))

        # SSL context
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

        # RSS源
        self.rss_sources = {
            "CoinDesk": self.api_endpoints.get("coindesk_rss"),
            "The Block": self.api_endpoints.get("theblock_rss"),
            "PANews": self.api_endpoints.get("panews_rss"),
        }

    async def fetch_rss_feed(self, source: str, url: str, limit: int = 10) -> List[Dict]:
        """
        获取RSS新闻

        Args:
            source: 来源名称
            url: RSS链接
            limit: 返回数量

        Returns:
            [
                {
                    "title": "标题",
                    "url": "链接",
                    "summary": "摘要",
                    "published": "时间",
                    "source": "来源",
                },
                ...
            ]
        """
        try:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, timeout=15) as resp:
                    if resp.status == 200:
                        content = await resp.text()
                        feed = feedparser.parse(content)

                        articles = []
                        for entry in feed.entries[:limit]:
                            # 解析发布时间
                            published = entry.get("published", "")
                            if hasattr(entry, "published_parsed") and entry.published_parsed:
                                published = datetime(*entry.published_parsed[:6]).strftime("%m-%d %H:%M")

                            articles.append({
                                "title": entry.get("title", ""),
                                "url": entry.get("link", ""),
                                "summary": self._clean_summary(entry.get("summary", entry.get("description", ""))),
                                "published": published,
                                "source": source,
                            })

                        return articles
        except Exception as e:
            print(f"获取{source}新闻失败: {e}")

        return []

    def _clean_summary(self, summary: str) -> str:
        """清理HTML标签"""
        # 移除HTML标签
        summary = re.sub(r"<[^>]+>", "", summary)
        # 移除多余空格
        summary = re.sub(r"\s+", " ", summary).strip()
        # 限制长度
        return summary[:200]

    async def fetch_all_news(self, limit_per_source: int = 10) -> Dict[str, List[Dict]]:
        """
        获取所有源的新闻

        Args:
            limit_per_source: 每个源返回数量

        Returns:
            {
                "CoinDesk": [...],
                "The Block": [...],
                "PANews": [...],
            }
        """
        all_news = {}

        tasks = []
        for source, url in self.rss_sources.items():
            if url:
                tasks.append(self.fetch_rss_feed(source, url, limit_per_source))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                continue
            source = list(self.rss_sources.keys())[i]
            all_news[source] = result

        return all_news

    async def filter_important_news(self, news: Dict) -> List[Dict]:
        """
        筛选重要新闻

        Args:
            news: 所有新闻

        Returns:
            重要的新闻列表
        """
        important = []
        important_keywords = [
            # 监管/政策
            "sec", "cftc", "regulation", "ban", "approve", "etf",
            "监管", "批准", "禁止",
            # 重大事件
            "hack", "exploit", "bankruptcy", "collapse",
            "被黑", "破产", "倒闭",
            # 大额/重要
            "binance", "coinbase", "blackrock", "fidelity",
            "investment", "funding", "raise", "ipo",
            "融资", "投资",
            # 市场重要
            "bitcoin", "btc", "ethereum", "eth", "all-time high", "ath",
            "突破", "新高", "历史",
        ]

        for source, articles in news.items():
            for article in articles:
                title_lower = article.get("title", "").lower()
                summary_lower = article.get("summary", "").lower()

                if any(kw in title_lower or kw in summary_lower for kw in important_keywords):
                    important.append({
                        **article,
                        "priority": self._get_news_priority(title_lower),
                    })

        # 按优先级排序
        important.sort(key=lambda x: x.get("priority", 0), reverse=True)

        return important[:20]

    def _get_news_priority(self, title: str) -> int:
        """获取新闻优先级"""
        score = 0

        # S级关键词
        if any(kw in title for kw in ["sec", "etf approve", "regulation", "监管", "etf批准"]):
            score += 10
        # A级关键词
        elif any(kw in title for kw in ["hack", "exploit", "被黑", "binance", "coinbase"]):
            score += 5
        # B级关键词
        elif any(kw in title for kw in ["funding", "investment", "融资"]):
            score += 3

        return score

    async def get_news_summary(self) -> Dict:
        """
        获取新闻摘要

        Returns:
            {
                "all_news": {...},
                "important": [...],
                "by_source": {...},
                "timestamp": "..."
        }
        """
        all_news = await self.fetch_all_news(15)
        important = await self.filter_important_news(all_news)

        # 按来源分类
        by_source = {}
        for source, articles in all_news.items():
            if articles:
                by_source[source] = articles[:5]

        return {
            "all_news": all_news,
            "important": important[:10],
            "by_source": by_source,
            "timestamp": datetime.now(self.tz).strftime("%Y-%m-%d %H:%M:%S"),
        }


# 测试代码
if __name__ == "__main__":
    import sys
    sys.path.append("..")
    from config import API_ENDPOINTS, TIMEZONE

    config = {
        "API_ENDPOINTS": API_ENDPOINTS,
        "TIMEZONE": TIMEZONE,
    }

    async def test():
        fetcher = NewsFetcher(config)

        print("=== 测试获取新闻 ===")
        summary = await fetcher.get_news_summary()

        print(f"\n=== 重要新闻 ===")
        for news in summary["important"][:5]:
            print(f"[{news['source']}] {news['title']}")

    asyncio.run(test())
