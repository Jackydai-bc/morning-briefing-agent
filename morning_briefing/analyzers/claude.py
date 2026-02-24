"""
Claude AI分析器 - Claude Analyzer
使用Claude API分析数据并生成洞察
"""

import asyncio
import aiohttp
import ssl
import json
from typing import Dict, List, Optional
from datetime import datetime
import pytz


class ClaudeAnalyzer:
    """Claude AI分析器"""

    def __init__(self, config: Dict):
        self.config = config
        self.api_key = config.get("API_KEYS", {}).get("claude", "")
        self.tz = pytz.timezone(config.get("TIMEZONE", "Asia/Shanghai"))
        self.api_url = "https://api.anthropic.com/v1/messages"

        # SSL context
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    async def analyze_market_sentiment(self, market_data: Dict) -> str:
        """
        分析市场情绪

        Args:
            market_data: 市场数据

        Returns:
            情绪分析文本
        """
        prompt = self._build_sentiment_prompt(market_data)
        return await self._call_claude(prompt, max_tokens=500)

    def _build_sentiment_prompt(self, data: Dict) -> str:
        """构建市场情绪分析prompt"""
        prices = data.get("prices", {})
        fear_greed = data.get("fear_greed", {})
        gainers = data.get("top_gainers", [])

        prompt = f"""分析以下加密货币市场数据，给出简短的市场情绪判断 (100字以内):

价格数据:
- BTC: ${prices.get('bitcoin', {}).get('price', 0):,.0f} ({prices.get('bitcoin', {}).get('change_24h', 0):+.1f}%)
- ETH: ${prices.get('ethereum', {}).get('price', 0):,.0f} ({prices.get('ethereum', {}).get('change_24h', 0):+.1f}%)
- SOL: ${prices.get('solana', {}).get('price', 0):,.0f} ({prices.get('solana', {}).get('change_24h', 0):+.1f}%)

恐慌贪婪指数: {fear_greed.get('value', 50)} ({fear_greed.get('text', '中性')})

涨幅榜前3:
{chr(10).join([f"- {g['symbol']}: {g['change_24h']:+.1f}%" for g in gainers[:3]])}

请给出:
1. 市场整体情绪 (一句话)
2. 主导叙事 (一个词)
3. 资金流向 (一个词)

格式:
市场情绪: [情绪判断]
主导叙事: [叙事]
资金流向: [流向]
"""
        return prompt

    async def select_must_read_news(self, news_data: Dict, limit: int = 3) -> List[Dict]:
        """
        选择必读新闻

        Args:
            news_data: 新闻数据
            limit: 返回数量

        Returns:
            必读新闻列表
        """
        all_news = []
        for source, articles in news_data.get("all_news", {}).items():
            for article in articles:
                all_news.append({
                    **article,
                    "source": source,
                })

        if not all_news:
            return []

        # 构建prompt让Claude选择
        news_text = "\n".join([
            f"{i+1}. [{n['source']}] {n['title']}"
            for i, n in enumerate(all_news[:30])
        ])

        prompt = f"""从以下加密货币新闻中选择{limit}条最重要的必读新闻。

新闻列表:
{news_text}

选择标准:
1. 重大监管政策变化
2. 黑天鹅事件(被黑/破产/战争)
3. 美联储重大决策
4. BTC/ETH单日涨跌>10%
5. 知名项目重大公告
6. 大额鲸鱼操作

只返回{limit}条的编号，用逗号分隔，如: 1,5,12
"""

        response = await self._call_claude(prompt, max_tokens=100)

        # 解析返回的编号
        try:
            indices = [int(x.strip()) for x in response.split(",") if x.strip().isdigit()]
            selected = []
            for idx in indices[:limit]:
                if 0 <= idx - 1 < len(all_news):
                    selected.append(all_news[idx - 1])
            return selected
        except:
            # 解析失败，返回前3条
            return all_news[:limit]

    async def analyze_meme_token(self, token: Dict) -> Dict:
        """
        分析单个meme币

        Args:
            token: 代币数据

        Returns:
            分析结果
        """
        prompt = f"""分析以下meme币的投资价值 (100字以内):

币种: {token.get('symbol', 'N/A')}
链: {token.get('chain', 'N/A')}
价格: ${token.get('price', 0):.10f}
24h涨幅: {token.get('change_24h', 0):+.1f}%
1h涨幅: {token.get('change_1h', 0):+.1f}%
流动性: ${token.get('liquidity', 0):,.0f}
交易量24h: ${token.get('volume_24h', 0):,.0f}
持有者: {token.get('holders', 0)}
LP锁定: {token.get('lp_lock_pct', 0)}%

请给出:
1. 风险评级 (S/A/B/C/D)
2. 一句话风险评估

格式:
评级: [S/A/B/C/D]
风险: [一句话]
"""

        response = await self._call_claude(prompt, max_tokens=200)

        # 解析响应
        result = {"symbol": token.get("symbol"), "analysis": response}

        # 尝试提取评级
        if "评级:" in response or "Grade:" in response:
            for line in response.split("\n"):
                if "评级:" in line or "Grade:" in line:
                    grade = line.split(":")[-1].strip().upper()
                    if grade in ["S", "A", "B", "C", "D"]:
                        result["grade"] = grade
                        break

        return result

    async def select_high_potential_memes(self, tokens: List[Dict], limit: int = 10) -> List[Dict]:
        """
        选择高潜力meme币

        Args:
            tokens: 代币列表
            limit: 返回数量

        Returns:
            高潜力代币列表
        """
        # 先按基本指标筛选
        filtered = []
        for token in tokens:
            # 基础过滤
            if token.get("liquidity", 0) < 10000:
                continue
            if token.get("holders", 0) < 50:
                continue

            # 有明显上涨
            if token.get("change_1h", 0) > 10 or token.get("change_5m", 0) > 5:
                filtered.append(token)
                continue

            # AI相关
            if token.get("is_ai", False):
                filtered.append(token)
                continue

        # 如果筛选结果太多，取前limit个
        if len(filtered) > limit:
            # 按综合评分排序
            filtered.sort(key=lambda x: (
                x.get("change_1h", 0) * 2 +
                x.get("change_5m", 0) +
                (100 if x.get("is_ai") else 0)
            ), reverse=True)
            filtered = filtered[:limit]

        return filtered

    async def generate_daily_commentary(self, all_data: Dict) -> str:
        """
        生成每日评论

        Args:
            all_data: 所有数据

        Returns:
            评论文本
        """
        prompt = f"""根据以下数据生成一段简短的加密货币市场评论 (150字以内):

市场概况: {all_data.get('market', {})}
Meme热点: {len(all_data.get('meme', {}).get('ai_tokens', []))}个AI相关新币
Polymarket: {len(all_data.get('polymarket', {}).get('arbitrage', []))}个套利机会

评论风格: 简洁、专业、有洞察
"""

        return await self._call_claude(prompt, max_tokens=300)

    async def _call_claude(self, prompt: str, max_tokens: int = 500) -> str:
        """
        调用Claude API

        Args:
            prompt: 提示词
            max_tokens: 最大token数

        Returns:
            Claude响应
        """
        if not self.api_key:
            # 没有API key时返回空
            return ""

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        data = {
            "model": "claude-3-5-haiku-20241022",
            "max_tokens": max_tokens,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        try:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(self.api_url, headers=headers, json=data, timeout=30) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result.get("content", [{}])[0].get("text", "")
                    else:
                        error_text = await resp.text()
                        print(f"Claude API错误: {resp.status} - {error_text[:300]}")
                        return ""
        except Exception as e:
            print(f"调用Claude失败: {e}")
            return ""

    async def analyze_all(self, all_data: Dict) -> Dict:
        """
        分析所有数据

        Args:
            all_data: 所有采集的数据

        Returns:
            分析结果
        """
        # 并行执行各种分析
        must_read_news, commentary, high_potential = await asyncio.gather(
            self.select_must_read_news(all_data.get("news", {}), 3),
            self.generate_daily_commentary(all_data),
            self.select_high_potential_memes(
                all_data.get("meme", {}).get("high_potential", []),
                10
            ),
            return_exceptions=True
        )

        return {
            "must_read_news": must_read_news if not isinstance(must_read_news, Exception) else [],
            "commentary": commentary if not isinstance(commentary, Exception) else "",
            "high_potential_memes": high_potential if not isinstance(high_potential, Exception) else [],
            "market_sentiment": await self.analyze_market_sentiment(all_data.get("market", {})),
            "timestamp": datetime.now(self.tz).strftime("%Y-%m-%d %H:%M:%S"),
        }
