# bot/keyboards/inline.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Канал", callback_data="add_channel")],
        [InlineKeyboardButton(text="🎯 Задание", callback_data="get_task")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="💰 Баллы", callback_data="distribute_points")]
    ])
    return keyboard


def cancel_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="main_menu")]
    ])
    return keyboard