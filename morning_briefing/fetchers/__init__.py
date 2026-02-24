"""
数据采集模块 - Data Fetchers
负责从各个数据源采集原始数据
"""

from .market import MarketFetcher
from .meme import MemeFetcher
from .twitter import TwitterFetcher
from .news import NewsFetcher
from .polymarket import PolymarketFetcher

__all__ = [
    "MarketFetcher",
    "MemeFetcher",
    "TwitterFetcher",
    "NewsFetcher",
    "PolymarketFetcher",
]
