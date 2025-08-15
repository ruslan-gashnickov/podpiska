# bot/utils/telegram_api.py

import aiohttp
from bot.config import BOT_TOKEN
import logging

logger = logging.getLogger(__name__)

class TelegramAPIClient:
    def __init__(self):
        self.base_url = f"https://api.telegram.org/bot{BOT_TOKEN}"

    async def get_chat(self, chat_id):
        """Получить информацию о чате"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/getChat",
                params={"chat_id": chat_id}
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None

    async def get_chat_administrators(self, chat_id):
        """Получить список администраторов чата"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/getChatAdministrators",
                    params={"chat_id": chat_id}
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    logger.error(f"get_chat_administrators error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"get_chat_administrators exception: {e}")
            return None

    async def get_me(self):
        """Получить информацию о боте"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/getMe") as response:
                if response.status == 200:
                    return await response.json()
                return None

    async def get_chat_member(self, chat_id, user_id):
        """Проверить, является ли пользователь участником чата"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{self.base_url}/getChatMember",
                    params={
                        "chat_id": chat_id,
                        "user_id": user_id
                    }
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None