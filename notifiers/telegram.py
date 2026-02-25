"""
Telegram通知器 - Telegram Notifier
通过Telegram Bot发送简报
"""

import asyncio
import aiohttp
from typing import Optional


class TelegramNotifier:
    """Telegram通知器"""

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/"

    async def send_briefing(self, briefing: str) -> bool:
        """
        发送简报到Telegram

        Args:
            briefing: Markdown格式的简报

        Returns:
            是否成功
        """
        if not self.bot_token or not self.chat_id:
            print("Telegram配置未完成")
            return False

        # Telegram消息长度限制
        max_length = 4096

        if len(briefing) <= max_length:
            return await self._send_message(briefing)
        else:
            # 分段发送
            chunks = [briefing[i:i+max_length] for i in range(0, len(briefing), max_length)]
            for i, chunk in enumerate(chunks):
                prefix = f"({i+1}/{len(chunks)})" if len(chunks) > 1 else ""
                await self._send_message(prefix + "\n" + chunk)
            return True

    async def _send_message(self, content: str) -> bool:
        """发送单条消息"""
        url = f"{self.api_url}sendMessage"

        payload = {
            "chat_id": self.chat_id,
            "text": content,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        return True
                    else:
                        print(f"Telegram API错误: {resp.status}")
                        return False
        except Exception as e:
            print(f"发送Telegram失败: {e}")
            return False

    async def send_alert(self, message: str, level: str = "info") -> bool:
        """
        发送紧急通知

        Args:
            message: 通知内容
            level: 级别

        Returns:
            是否成功
        """
        emojis = {
            "info": "ℹ️",
            "warning": "⚠️",
            "critical": "🚨",
        }

        emoji = emojis.get(level, "ℹ️")
        content = f"{emoji} *Agent通知*\n\n{message}"

        return await self._send_message(content)
