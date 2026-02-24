#!/usr/bin/env python3
"""
晨间简报Agent - 简化版 (使用requests代替aiohttp)
用于本地网络环境有限的情况
"""

import os
import sys
import requests
from pathlib import Path
from datetime import datetime
import json
import pytz

# 禁用SSL警告
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from config import *


def fetch_market_data_simple():
    """简化的市场数据获取"""
    print("  📊 获取市场数据...")

    # 使用requests，它有更好的SSL处理
    session = requests.Session()
    session.verify = False  # 跳过SSL验证

    # 获取恐慌贪婪指数
    try:
        resp = session.get("https://api.alternative.me/fng/", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            value = int(data.get("data", [{}])[0].get("value", 50))
            text = data.get("data", [{}])[0].get("value_classification", "Neutral")
            return {
                "fear_greed": {
                    "value": value,
                    "text": text,
                    "classification": "极度恐慌" if value < 20 else "恐慌" if value < 40 else "中性"
                }
            }
    except Exception as e:
        print(f"    获取恐慌贪婪失败: {e}")

    return {"fear_greed": {"value": 50, "text": "中性", "classification": "中性"}}


def fetch_dexscreener_simple(chain="solana", limit=20):
    """简化的DexScreener获取"""
    print(f"  🪙 获取{chain.upper()} Meme币...")

    session = requests.Session()
    session.verify = False

    url = f"https://api.dexscreener.com/latest/v2/pairs/{chain}"

    try:
        resp = session.get(url, params={"limit": limit}, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            pairs = data.get("pairs", [])

            result = []
            for pair in pairs[:limit]:
                base_token = pair.get("baseToken", {})
                quote_token = pair.get("quoteToken", {})

                # 只保留稳定币对
                if quote_token.get("symbol", "").upper() not in ["USDT", "USDC", "DAI"]:
                    continue

                symbol = base_token.get("symbol", "")
                price = pair.get("priceUsd", 0)
                if not price:
                    continue

                change_24h = pair.get("change_24h", 0) or 0
                change_1h = pair.get("change_1h", 0) or 0
                liquidity = pair.get("liquidity", {}).get("usd", 0) or 0
                volume_24h = pair.get("volume", {}).get("h24", 0) or 0

                # 检查AI关键词
                is_ai = any(kw.lower() in symbol.lower() for kw in AI_KEYWORDS)

                result.append({
                    "symbol": symbol,
                    "price": price,
                    "change_24h": change_24h,
                    "change_1h": change_1h,
                    "liquidity": liquidity,
                    "volume_24h": volume_24h,
                    "chain": chain,
                    "is_ai": is_ai,
                    "pair_link": pair.get("url", ""),
                })

            print(f"    获取到 {len(result)} 个交易对")
            return result

    except Exception as e:
        print(f"    获取失败: {e}")
        return []


def generate_briefing_simple():
    """生成简化版简报"""
    print("=" * 50)
    print("🚀 晨间简报Agent (简化版)启动")
    print("=" * 50)

    # 获取数据
    market = fetch_market_data_simple()
    solana_tokens = fetch_dexscreener_simple("solana", 50)
    bsc_tokens = fetch_dexscreener_simple("bsc", 30)

    # 生成简报
    now = datetime.now(pytz.timezone(TIMEZONE))
    date_str = now.strftime("%Y-%m-%d")

    briefing = f"""# 🌅 Jacky晨间简报 | {date_str}

> 由Agent自动生成 | 数据来源: DexScreener

---

## 📊 市场概况

**恐慌贪婪**: {market['fear_greed']['value']} ({market['fear_greed']['text']}) {market['fear_greed']['classification']}

---

## 🪙 Meme热点

### 🔥 Solana 新币 (24h)

"""

    # Solana新币
    solana_tokens = solana_tokens or []
    if solana_tokens:
        # 按交易量排序
        solana_tokens.sort(key=lambda x: x.get("volume_24h", 0), reverse=True)

        briefing += "| 币种 | 价格 | 24h | 1h | 流动性 | 交易量 | AI |\n"
        briefing += "|------|------|-----|----|--------|--------|-----|\n"

        for token in solana_tokens[:15]:
            ai_tag = "🤖" if token.get("is_ai") else ""
            briefing += f"| {token['symbol']} | ${token['price']:.10f} | {token['change_24h']:+.1f}% | {token['change_1h']:+.1f}% | ${token['liquidity']:,.0f} | ${token['volume_24h']:,.0f} | {ai_tag} |\n"

    # BSC新币
    if bsc_tokens:
        bsc_tokens.sort(key=lambda x: x.get("volume_24h", 0), reverse=True)
        briefing += "\n### 🔥 BSC 新币 (24h)\n\n"
        briefing += "| 币种 | 价格 | 24h | 流动性 | 交易量 |\n"
        briefing += "|------|------|-----|--------|--------|\n"

        for token in bsc_tokens[:10]:
            briefing += f"| {token['symbol']} | ${token['price']:.10f} | {token['change_24h']:+.1f}% | ${token['liquidity']:,.0f} | ${token['volume_24h']:,.0f} |\n"

    # AI相关币
    solana_tokens = solana_tokens or []
    bsc_tokens = bsc_tokens or []
    ai_tokens = [t for t in solana_tokens + bsc_tokens if t.get("is_ai", False)]
    if ai_tokens:
        briefing += "\n### 🤖 AI Agent Meme\n\n"
        for token in ai_tokens[:5]:
            briefing += f"- **{token['symbol']}**: {token['change_24h']:+.1f}% (${token['volume_24h']:,.0f})\n"

    briefing += f"""
---

## 📊 数据来源

- DexScreener API
- Alternative.me

---

📊 更新时间: {now.strftime('%H:%M')}
🤖 生成: Jacky's Agent (DexScreener版)
"""

    return briefing


if __name__ == "__main__":
    briefing = generate_briefing_simple()

    # 保存简报
    data_dir = Path(__file__).parent / "data" / "briefings"
    data_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(pytz.timezone(TIMEZONE))
    filename = now.strftime("briefing_%Y%m%d_%H%M.md")
    filepath = data_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(briefing)

    print(f"\n💾 简报已保存: {filepath}")
    print(f"\n📄 简报预览:\n")
    print(briefing[:1000])
    print("...")
