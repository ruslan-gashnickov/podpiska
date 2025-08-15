# bot/handlers/start.py

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from bot.keyboards.inline import main_menu

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    text = (
        "👋 Добро пожаловать в бот взаимных подписок!\n\n"
        "Как работает наш бот:\n"
        "• Добавить свой канал в бота\n"
        "• Выполняй задания на подписку \n"
        "• Зарабатывай баллы\n"
        "• Трать баллы на продвижение своих каналов\n"
        "• 1 балл = 1 подписчик\n"
    )
    await message.answer(text, reply_markup=main_menu())


@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите действие:",
        reply_markup=main_menu()
    )
    await callback.answer()