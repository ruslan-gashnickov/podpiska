# bot/handlers/channels.py

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.keyboards.inline import cancel_keyboard, main_menu
from bot.utils.api_client import DjangoAPIClient
from bot.utils.telegram_api import TelegramAPIClient
import re

router = Router()


class ChannelStates(StatesGroup):
    waiting_for_channel = State()
    waiting_for_category = State()


@router.callback_query(F.data == "add_channel")
async def add_channel_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📢 Добавьте бота в администраторы канала!\n\n"
    "⚠️ Бот необходимо назначить администратором канала для проверки подписок.\n\n"
    "1️⃣ Сначала добавьте бота в администраторы канала:\n"
    "• Вручную через настройки канала\n"
    "• Или по ссылке: [Добавить бота](https://t.me/Channel_Ninja_Bot?startchannel&admin=invite_users+delete_messages)\n\n"
    "2️⃣ После этого отправьте в чат @username вашего канала\n"
    "Бот будет проверять, подписались ли на вас люди",
    parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(ChannelStates.waiting_for_channel)
    await callback.answer()


@router.message(ChannelStates.waiting_for_channel)
async def channel_received(message: Message, state: FSMContext, user):
    channel_info = message.text

    # Проверяем формат username
    username_match = re.search(r'@([a-zA-Z0-9_]{5,32})', channel_info)
    if username_match:
        username = username_match.group(1)
        await state.update_data(username=username)
    else:
        await message.answer("❌ Неверный формат. Отправьте @username")
        return

    # Проверяем, является ли пользователь администратором канала
    telegram_client = TelegramAPIClient()
    try:
        # Получаем информацию о канале
        chat_info = await telegram_client.get_chat(f"@{username}")
        if not chat_info or not chat_info.get('result'):
            await message.answer("❌ Не удалось найти канал. Проверьте username.")
            return

        chat_result = chat_info['result']
        chat_id = chat_result.get('id')

        if not chat_id:
            await message.answer("❌ Не удалось получить ID канала.")
            return

        await state.update_data(chat_id=chat_id, title=chat_result.get('title', f'@{username}'))

        # Проверяем администраторов канала
        admins_info = await telegram_client.get_chat_administrators(chat_id)
        if not admins_info or not admins_info.get('result'):
            await message.answer(
                "❌ Не удалось получить список администраторов канала.\n"
                "Убедитесь, что канал публичный и бот имеет доступ."
            )
            return

        # Проверяем, является ли пользователь администратором
        user_id = user['telegram_id']
        admins = admins_info['result']

        is_user_admin = any(
            admin.get('user', {}).get('id') == user_id
            for admin in admins
        )

        if not is_user_admin:
            await message.answer(
                "❌ Вы не являетесь администратором этого канала!\n"
                "Только администраторы могут добавлять каналы в систему."
            )
            await state.clear()
            return

        # Если пользователь админ, продолжаем

    except Exception as e:
        await message.answer(f"❌ Ошибка при проверке канала: {str(e)[:100]}")
        await state.clear()
        return

    # Отправляем выбор категории
    categories = [
        ("📱 Технологии", "tech"),
        ("📚 Образование", "edu"),
        ("🎮 Развлечения", "ent"),
        ("📰 Новости", "news"),
        ("Другое", "other")
    ]

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = []
    for name, code in categories:
        buttons.append([InlineKeyboardButton(text=name, callback_data=f"category:{code}")])
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer("Выберите категорию:", reply_markup=keyboard)
    await state.set_state(ChannelStates.waiting_for_category)


@router.callback_query(F.data.startswith("category:"))
async def category_selected(callback: CallbackQuery, state: FSMContext, user):
    category = callback.data.split(":")[1]
    data = await state.get_data()

    username = data.get('username')
    chat_id = data.get('chat_id')
    title = data.get('title', f'@{username}')

    # Отправляем в Django API
    api_client = DjangoAPIClient()
    try:
        result = await api_client.add_channel(
            owner_id=user['telegram_id'],
            channel_id=chat_id,  # Теперь реальный ID
            title=title,
            username=username,
            category=category
        )
        await callback.message.edit_text(
            f"✅ Канал @{username} добавлен!\n"
            f"Категория: {category}"
        )
    except Exception as e:
        error_msg = str(e)[:100] + "..." if len(str(e)) > 100 else str(e)
        await callback.message.edit_text(f"❌ Ошибка: {error_msg}")

    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_operation(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Отменено", reply_markup=main_menu())
    await callback.answer()