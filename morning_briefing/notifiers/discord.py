"""
Discord通知器 - Discord Notifier
通过Discord Webhook发送简报
"""

import asyncio
import aiohttp
from typing import Dict, Optional


class DiscordNotifier:
    """Discord通知器"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def send_briefing(self, briefing: str) -> bool:
        """
        发送简报到Discord

        Args:
            briefing: Markdown格式的简报

        Returns:
            是否成功
        """
        if not self.webhook_url:
            print("Discord Webhook URL未配置")
            return False

        # Discord消息有长度限制，需要分段
        max_length = 2000

        # 提取标题作为第一段
        lines = briefing.split("\n")
        first_line = lines[0] if lines else "🌅 晨间简报"

        chunks = []
        current_chunk = ""
        current_length = 0

        for line in lines[1:]:
            line_length = len(line) + 1  # +1 for newline

            if current_length + line_length > max_length:
                chunks.append(current_chunk)
                current_chunk = line + "\n"
                current_length = line_length
            else:
                current_chunk += line + "\n"
                current_length += line_length

        if current_chunk:
            chunks.append(current_chunk)

        # 发送每个chunk
        try:
            async with aiohttp.ClientSession() as session:
                # 第一条消息带标题
                await self._send_message(session, first_line + "\n\n" + chunks[0])

                # 后续消息
                for chunk in chunks[1:]:
                    await self._send_message(session, "_(续)_ " + chunk)

            return True
        except Exception as e:
            print(f"发送Discord失败: {e}")
            return False

    async def _send_message(self, session: aiohttp.ClientSession, content: str) -> None:
        """发送单条消息"""
        payload = {
            "content": content,
            "username": "Jacky's Agent",
            "avatar_url": "https://i.imgur.com/xxxxx.png",  # 可以设置头像
        }

        async with session.post(self.webhook_url, json=payload) as resp:
            if resp.status != 200:
                print(f"Discord API错误: {resp.status}")

    async def send_alert(self, message: str, level: str = "info") -> bool:
        """
        发送紧急通知

        Args:
            message: 通知内容
            level: 级别 (info/warning/critical)

        Returns:
            是否成功
        """
        emojis = {
            "info": "ℹ️",
            "warning": "⚠️",
            "critical": "🚨",
        }

        emoji = emojis.get(level, "ℹ️")
        content = f"{emoji} **Agent通知**\n\n{message}"

        try:
            async with aiohttp.ClientSession() as session:
                await self._send_message(session, content)
            return True
        except Exception as e:
            print(f"发送通知失败: {e}")
            return False
