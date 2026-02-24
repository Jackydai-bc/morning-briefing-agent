#!/usr/bin/env python3
"""
测试API连接性
"""
import asyncio
import aiohttp
import ssl

async def test_apis():
    """测试各个API的连接性"""

    # SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    apis = {
        "CoinGecko": "https://api.coingecko.com/api/v3/ping",
        "DexScreener": "https://api.dexscreener.com/latest/v2/pairs/solana?limit=1",
        "Alternative.me": "https://api.alternative.me/fng/",
        "Polymarket": "https://gamma-api.polymarket.com/markets?limit=1",
    }

    connector = aiohttp.TCPConnector(ssl=ssl_context)

    async with aiohttp.ClientSession(connector=connector) as session:
        for name, url in apis.items():
            try:
                print(f"测试 {name}...")
                async with session.get(url, timeout=10) as resp:
                    print(f"  {name}: {resp.status} - {'✅' if resp.status == 200 else '❌'}")
            except Exception as e:
                print(f"  {name}: ❌ {e}")

if __name__ == "__main__":
    asyncio.run(test_apis())
