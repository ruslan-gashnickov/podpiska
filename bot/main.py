# bot/main.py

import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN
from bot.handlers import start, channels, tasks
from bot.middlewares.user_middleware import UserMiddleware
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Подключаем мидлвари
    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())

    # Подключаем роутеры
    dp.include_routers(
        start.router,
        channels.router,
        tasks.router
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())