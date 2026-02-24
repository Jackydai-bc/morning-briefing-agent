#!/usr/bin/env python3
"""
晨间简报Agent - 主程序
Morning Briefing Agent - Main Script

每天7:00自动生成并发送加密货币晨间简报
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import pytz

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from config import *
from fetchers import MarketFetcher, MemeFetcher, TwitterFetcher, NewsFetcher, PolymarketFetcher
from analyzers import ClaudeAnalyzer, MemeQualityAnalyzer
from generators import BriefingGenerator
from notifiers import DiscordNotifier, TelegramNotifier


class MorningBriefingAgent:
    """晨间简报Agent"""

    def __init__(self):
        # 加载环境变量
        load_dotenv()

        # 配置
        self.config = {
            "MY_TWITTER": MY_TWITTER,
            "MY_KOLS": MY_KOLS,
            "KOL_MONITOR": KOL_MONITOR,
            "AI_KEYWORDS": AI_KEYWORDS,
            "AI_MEME_COINS": AI_MEME_COINS,
            "CHAIN_PRIORITY": CHAIN_PRIORITY,
            "CHAIN_CONFIG": CHAIN_CONFIG,
            "WATCHED_COINS": WATCHED_COINS,
            "MEME_QUALITY_CHECK": MEME_QUALITY_CHECK,
            "NEW_TOKEN_FILTERS": NEW_TOKEN_FILTERS,
            "POLY_CONFIG": POLY_CONFIG,
            "API_ENDPOINTS": API_ENDPOINTS,
            "API_KEYS": {
                "coingecko": os.getenv("COINGECKO_API_KEY"),
                "birdeye": os.getenv("BIRDEYE_API_KEY"),
                "gmgn": os.getenv("GMGN_API_KEY"),
                "claude": os.getenv("CLAUDE_API_KEY"),
                "openclaw": os.getenv("OPENCLAW_WEBHOOK_URL"),
            },
            "NOTIFICATION_CONFIG": {
                "discord_webhook": os.getenv("DISCORD_WEBHOOK_URL"),
                "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN"),
                "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID"),
            },
            "TIMEZONE": TIMEZONE,
        }

        # 初始化各模块
        self.market_fetcher = MarketFetcher(self.config)
        self.meme_fetcher = MemeFetcher(self.config)
        self.twitter_fetcher = TwitterFetcher(self.config)
        self.news_fetcher = NewsFetcher(self.config)
        self.polymarket_fetcher = PolymarketFetcher(self.config)

        self.claude_analyzer = ClaudeAnalyzer(self.config)
        self.meme_quality_analyzer = MemeQualityAnalyzer(self.config)

        self.briefing_generator = BriefingGenerator(self.config)

        # 初始化通知器
        discord_webhook = self.config["NOTIFICATION_CONFIG"]["discord_webhook"]
        self.discord_notifier = DiscordNotifier(discord_webhook) if discord_webhook else None

        telegram_token = self.config["NOTIFICATION_CONFIG"]["telegram_bot_token"]
        telegram_chat_id = self.config["NOTIFICATION_CONFIG"]["telegram_chat_id"]
        self.telegram_notifier = TelegramNotifier(telegram_token, telegram_chat_id) if telegram_token else None

    async def fetch_all_data(self) -> dict:
        """采集所有数据"""
        print("=" * 50)
        print("📡 开始采集数据...")
        print("=" * 50)

        # 并行采集所有数据
        tasks = {
            "market": self.market_fetcher.fetch_market_overview(),
            "meme": self.meme_fetcher.get_meme_summary(),
            "tweets": self.twitter_fetcher.get_tweet_summary(),
            "news": self.news_fetcher.get_news_summary(),
            "polymarket": self.polymarket_fetcher.get_polymarket_summary(),
        }

        results = {}
        for name, task in tasks.items():
            try:
                print(f"  ⏳ 采集 {name}...")
                results[name] = await task
                print(f"  ✅ {name} 采集完成")
            except Exception as e:
                print(f"  ❌ {name} 采集失败: {e}")
                results[name] = {}

        print("\n✅ 数据采集完成")
        return results

    async def analyze_data(self, all_data: dict) -> dict:
        """分析所有数据"""
        print("\n" + "=" * 50)
        print("🤖 开始分析数据...")
        print("=" * 50)

        analysis = await self.claude_analyzer.analyze_all(all_data)

        print("✅ 数据分析完成")
        return analysis

    def save_briefing(self, briefing: str) -> str:
        """保存简报到文件"""
        # 创建data目录
        data_dir = Path(__file__).parent / "data" / "briefings"
        data_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        now = datetime.now(pytz.timezone(TIMEZONE))
        filename = now.strftime("briefing_%Y%m%d_%H%M.md")
        filepath = data_dir / filename

        # 保存
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(briefing)

        print(f"\n💾 简报已保存: {filepath}")
        return str(filepath)

    async def send_notifications(self, briefing: str) -> None:
        """发送通知"""
        print("\n" + "=" * 50)
        print("📤 发送通知...")
        print("=" * 50)

        # Discord
        if self.discord_notifier:
            print("  ⏳ 发送到 Discord...")
            success = await self.discord_notifier.send_briefing(briefing)
            if success:
                print("  ✅ Discord 发送成功")
            else:
                print("  ❌ Discord 发送失败")

        # Telegram
        if self.telegram_notifier:
            print("  ⏳ 发送到 Telegram...")
            success = await self.telegram_notifier.send_briefing(briefing)
            if success:
                print("  ✅ Telegram 发送成功")
            else:
                print("  ❌ Telegram 发送失败")

    async def run(self) -> str:
        """运行完整流程"""
        start_time = datetime.now()

        print(f"\n🚀 晨间简报Agent启动 - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # 1. 采集数据
        all_data = await self.fetch_all_data()

        # 2. 分析数据
        analysis = await self.analyze_data(all_data)

        # 3. 生成简报
        print("\n" + "=" * 50)
        print("📝 生成简报...")
        print("=" * 50)

        briefing = self.briefing_generator.generate(all_data, analysis)

        # 4. 保存简报
        filepath = self.save_briefing(briefing)

        # 5. 发送通知
        await self.send_notifications(briefing)

        # 完成
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print("\n" + "=" * 50)
        print(f"✅ 晨间简报生成完成 - 耗时 {duration:.1f}秒")
        print("=" * 50)

        return briefing


async def main():
    """主函数"""
    agent = MorningBriefingAgent()

    try:
        briefing = await agent.run()

        # 打印预览
        print("\n" + "=" * 50)
        print("📄 简报预览 (前500字符)")
        print("=" * 50)
        print(briefing[:500] + "...")

    except KeyboardInterrupt:
        print("\n⏸️ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
