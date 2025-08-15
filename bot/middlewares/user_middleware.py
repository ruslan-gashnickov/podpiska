# bot/middlewares/user_middleware.py

from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
import aiohttp
import logging
from bot.config import DJANGO_API_URL
logger = logging.getLogger(__name__)


class UserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        tg_user: User = data.get("event_from_user")
        if tg_user is not None:
            # Регистрируем пользователя через Django API
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                            f"{DJANGO_API_URL}register-user/",
                            json={
                                "telegram_id": tg_user.id,
                                "username": tg_user.username or f"user_{tg_user.id}"
                            }
                    ) as response:
                        if response.status == 200 or response.status == 201:
                            user_data = await response.json()
                            data["user"] = user_data
                        else:
                            logger.error(f"Failed to register user: {response.status}")
            except Exception as e:
                logger.error(f"Error registering user: {e}")

        return await handler(event, data)