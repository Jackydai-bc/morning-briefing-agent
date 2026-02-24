"""
晨间简报生成器 - Briefing Generator
将所有数据整合成最终的晨间简报
"""

from typing import Dict, List, Optional
from datetime import datetime
import pytz


class BriefingGenerator:
    """晨间简报生成器"""

    def __init__(self, config: Dict):
        self.config = config
        self.tz = pytz.timezone(config.get("TIMEZONE", "Asia/Shanghai"))
        self.my_twitter = config.get("MY_TWITTER", "jingouwang888")

    def generate(self, all_data: Dict, analysis: Dict) -> str:
        """
        生成完整的晨间简报

        Args:
            all_data: 所有采集的数据
            analysis: 分析结果

        Returns:
            Markdown格式的简报
        """
        now = datetime.now(self.tz)
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")

        sections = []

        # 标题
        sections.append(self._generate_header(date_str, time_str))

        # 必读
        must_read = analysis.get("must_read_news", [])
        if must_read:
            sections.append(self._generate_must_read(must_read))

        # 市场概况
        market = all_data.get("market", {})
        if market:
            sections.append(self._generate_market_overview(market, analysis))

        # Meme热点
        meme = all_data.get("meme", {})
        if meme:
            sections.append(self._generate_meme_section(meme, analysis))

        # Polymarket
        polymarket = all_data.get("polymarket", {})
        if polymarket:
            sections.append(self._generate_polymarket_section(polymarket))

        # 核心资讯
        news = all_data.get("news", {})
        tweets = all_data.get("tweets", {})
        if news or tweets:
            sections.append(self._generate_news_section(news, tweets))

        # 创新雷达
        innovations = self._generate_innovations_section(all_data)
        if innovations:
            sections.append(innovations)

        # 今日关注
        sections.append(self._generate_action_items(all_data))

        # 页脚
        sections.append(self._generate_footer())

        return "\n\n---\n\n".join(sections)

    def _generate_header(self, date_str: str, time_str: str) -> str:
        """生成标题"""
        return f"""# 🌅 Jacky晨间简报 | {date_str}

> 由Agent自动生成 | 阅读时长: 3分钟"""

    def _generate_must_read(self, news: List[Dict]) -> str:
        """生成必读部分"""
        section = "## 🔥 今日必读 (3条)\n\n"

        for i, item in enumerate(news[:3], 1):
            priority = item.get("priority", 0)
            level = "S级" if priority >= 10 else ("A级" if priority >= 5 else "B级")

            section += f"### {i}. [{level}] {item.get('title', '未知')}\n"
            section += f"- **来源**: {item.get('source', 'N/A')}\n"
            section += f"- **链接**: {item.get('url', '')}\n"
            section += f"- **时间**: {item.get('published', '')}\n\n"

        return section

    def _generate_market_overview(self, market: Dict, analysis: Dict) -> str:
        """生成市场概况"""
        prices = market.get("prices", {})
        fear_greed = market.get("fear_greed", {})
        sentiment = analysis.get("market_sentiment", "")

        section = "## 📊 市场概况\n\n"

        # 价格表格
        section += "| 币种 | 价格 | 24h | 关键点位 |\n"
        section += "|------|------|-----|----------|\n"

        for coin_id, data in prices.items():
            symbol = data.get("symbol", coin_id.upper())
            price = data.get("price", 0)
            change = data.get("change_24h", 0)
            section += f"| {symbol} | ${price:,.0f} | {change:+.1f}% | - |\n"

        # 恐慌贪婪
        fg_value = fear_greed.get("value", 50)
        fg_text = fear_greed.get("text", "中性")
        fg_level = fear_greed.get("classification", "中性")
        fg_emoji = "🟢" if fg_value > 60 else ("🟡" if fg_value > 40 else "🔴")

        section += f"\n**{fg_emoji} 恐慌贪婪**: {fg_value} ({fg_text}) {fg_level}\n"

        # 情绪分析
        if sentiment:
            section += f"\n{sentiment}\n"

        return section

    def _generate_meme_section(self, meme: Dict, analysis: Dict) -> str:
        """生成Meme热点部分"""
        section = "## 🪙 Meme热点\n\n"

        # 叙事
        narratives = meme.get("narratives", {})
        if narratives:
            section += "### 📢 热门叙事\n\n"
            for narrative, data in list(narratives.items())[:4]:
                if data.get("count", 0) > 0:
                    tokens = ", ".join(data.get("tokens", [])[:5])
                    section += f"- **{narrative}**: {tokens}\n"
            section += "\n"

        # AI专项
        ai_tokens = meme.get("ai_tokens", [])
        if ai_tokens:
            section += "### 🤖 AI Agent Meme\n\n"
            section += "| 币种 | 链 | 1h | 24h | 流动性 |\n"
            section += "|------|----|----|----|--------|\n"

            for token in ai_tokens[:5]:
                symbol = token.get("symbol", "N/A")
                chain = token.get("chain", "").upper()
                change_1h = token.get("change_1h", 0)
                change_24h = token.get("change_24h", 0)
                liquidity = token.get("liquidity", 0)
                section += f"| {symbol} | {chain} | {change_1h:+.1f}% | {change_24h:+.1f}% | ${liquidity:,.0f} |\n"

            section += "\n"

        # 新币速递
        new_pairs = meme.get("new_pairs", {})
        all_new = []
        for chain, tokens in new_pairs.items():
            if isinstance(tokens, list):
                all_new.extend(tokens)

        # 按交易量排序
        all_new.sort(key=lambda x: x.get("volume_24h", 0), reverse=True)

        if all_new:
            section += "### 🆕 新币速递 (24h)\n\n"
            section += "| 币种 | 链 | 1h | 24h | 流动性 | 质检 |\n"
            section += "|------|----|----|----|--------|------|\n"

            for token in all_new[:10]:
                symbol = token.get("symbol", "N/A")
                chain = token.get("chain", "").upper()
                change_1h = token.get("change_1h", 0)
                change_24h = token.get("change_24h", 0)
                liquidity = token.get("liquidity", 0)

                # 简单质检
                is_ai = token.get("is_ai", False)
                high_potential = token.get("high_potential", False)
                quality = "🤖" if is_ai else ("⚠️" if liquidity < 50000 else "✅")

                section += f"| {symbol} | {chain} | {change_1h:+.1f}% | {change_24h:+.1f}% | ${liquidity:,.0f} | {quality} |\n"

            section += "\n"

        # 大涨榜
        hot_pairs = meme.get("hot_pairs", {})
        all_hot = []
        for chain, tokens in hot_pairs.items():
            if isinstance(tokens, list):
                all_hot.extend(tokens)

        all_hot.sort(key=lambda x: x.get("change_24h", 0), reverse=True)

        if all_hot:
            section += "### 🚀 大涨榜 (24h)\n\n"
            for token in all_hot[:5]:
                symbol = token.get("symbol", "N/A")
                chain = token.get("chain", "").upper()
                change = token.get("change_24h", 0)
                reason = token.get("reason", "热钱涌入")

                section += f"- **{symbol}** ({chain}): {change:+.1f}% - {reason}\n"

            section += "\n"

        return section

    def _generate_polymarket_section(self, polymarket: Dict) -> str:
        """生成Polymarket部分"""
        section = "## 🎯 Polymarket\n\n"

        # 新市场
        new_markets = polymarket.get("new_markets", [])
        if new_markets:
            section += "### 🆕 新市场 (24h)\n\n"
            section += "| 市场 | 是 | 否 | 交易量 |\n"
            section += "|------|----|----|--------|\n"

            for market in new_markets[:5]:
                question = market.get("question", "")[:40]
                yes_price = market.get("yes_price", 0) * 100
                no_price = market.get("no_price", 0) * 100
                volume = market.get("volume", 0)

                section += f"| {question}... | {yes_price:.0f}% | {no_price:.0f}% | ${volume:,.0f} |\n"

            section += "\n"

        # 套利机会
        arbitrage = polymarket.get("arbitrage", [])
        if arbitrage:
            section += "### 💰 套利机会\n\n"

            for opp in arbitrage[:3]:
                question = opp.get("question", "")[:50]
                profit = opp.get("profit", 0) * 100
                opp_type = "稳定" if opp.get("type") == "stable" else "高收益"

                section += f"- **{opp_type}套利**: {profit:.2f}%\n"
                section += f"  - 市场: {question}...\n"
                section += f"  - 操作: {opp.get('action', '')}\n\n"

        # OpenClaw策略
        openclaw = polymarket.get("openclaw_signal", {})
        if openclaw:
            section += "### 📊 OpenClaw策略状态\n\n"
            section += f"- **策略**: {openclaw.get('strategy', 'N/A')}\n"
            section += f"- **信号**: {openclaw.get('signal', 'N/A')}\n"
            section += f"- **胜率**: {openclaw.get('confidence', 0):.1%}\n"
            section += f"- **状态**: {'✅ 运行中' if openclaw.get('status') == 'running' else '⏸️ 暂停'}\n"

        return section

    def _generate_news_section(self, news: Dict, tweets: Dict) -> str:
        """生成资讯部分"""
        section = "## 📰 核心资讯\n\n"

        # X精选
        important_tweets = tweets.get("important_news", [])
        if important_tweets:
            section += "### 🐦 X精选\n\n"

            for tweet in important_tweets[:5]:
                username = tweet.get("username", "")
                text = tweet.get("text", "")[:100]
                url = tweet.get("url", "")
                level = tweet.get("level", "")

                section += f"- **@{username}** ({level}): {text}...\n"

            section += "\n"

        # 媒体头条
        important = news.get("important", [])
        if important:
            section += "### 📰 媒体头条\n\n"

            for item in important[:5]:
                source = item.get("source", "N/A")
                title = item.get("title", "")
                url = item.get("url", "")

                section += f"- **{source}**: {title}\n"
                section += f"  {url}\n"

            section += "\n"

        return section

    def _generate_innovations_section(self, all_data: Dict) -> str:
        """生成创新雷达部分"""
        section = "## 💡 创新雷达\n\n"

        # AI相关新币
        meme = all_data.get("meme", {})
        ai_tokens = meme.get("ai_tokens", [])

        if ai_tokens:
            section += "### 🆕 AI Agent新项目\n\n"
            for token in ai_tokens[:5]:
                symbol = token.get("symbol", "N/A")
                chain = token.get("chain", "").upper()
                change_1h = token.get("change_1h", 0)
                section += f"- **{symbol}** ({chain}): {change_1h:+.1f}% - 新AI项目\n"

            section += "\n"

        # 新趋势 (从叙事中提取)
        narratives = meme.get("narratives", {})
        if narratives:
            section += "### 🔥 新趋势\n\n"
            for narrative, data in list(narratives.items())[:3]:
                if data.get("count", 0) > 3:
                    section += f"- **{narrative}**: {data.get('count', 0)}个相关币\n"

            section += "\n"

        return section

    def _generate_action_items(self, all_data: Dict) -> str:
        """生成今日关注"""
        section = "## ⚡ 今日关注\n\n"

        # 市场概况
        market = all_data.get("market", {})
        prices = market.get("prices", {})
        btc_change = prices.get("bitcoin", {}).get("change_24h", 0)

        if btc_change > 5:
            section += f"- [ ] BTC大涨 {btc_change:.1f}%，注意回调风险\n"
        elif btc_change < -5:
            section += f"- [ ] BTC大跌 {btc_change:.1f}%，关注抄底机会\n"
        else:
            section += f"- [ ] BTC横盘整理，耐心等待方向\n"

        # Meme机会
        meme = all_data.get("meme", {})
        ai_tokens = meme.get("ai_tokens", [])

        if ai_tokens:
            section += f"- [ ] {len(ai_tokens)}个新AI Meme，关注 {ai_tokens[0].get('symbol', '')}\n"

        # Polymarket套利
        polymarket = all_data.get("polymarket", {})
        arbitrage = polymarket.get("arbitrage", [])

        if arbitrage:
            section += f"- [ ] Polymarket有 {len(arbitrage)}个套利机会\n"

        return section

    def _generate_footer(self) -> str:
        """生成页脚"""
        now = datetime.now(self.tz)

        return f"""---

📊 数据更新时间: {now.strftime('%H:%M')}
⏱️ 阅读时长: 3分钟
🤖 生成: Jacky's Agent

> 订阅: @{self.my_twitter} | 反馈请私信"""
