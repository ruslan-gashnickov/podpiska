# run_bot.py

import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN
from bot.handlers import start, channels, tasks, distribute_points
from bot.middlewares.user_middleware import UserMiddleware

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
        tasks.router,
        distribute_points.router
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())