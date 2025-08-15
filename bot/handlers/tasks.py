# bot/handlers/tasks.py

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from bot.keyboards.inline import main_menu
from bot.utils.api_client import DjangoAPIClient
from bot.utils.telegram_api import TelegramAPIClient

router = Router()


@router.callback_query(F.data == "get_task")
async def get_task(callback: CallbackQuery, user):
    api_client = DjangoAPIClient()

    try:
        task_data = await api_client.get_subscription_task(user['telegram_id'])

        if 'message' in task_data :
            await callback.message.edit_text(
                "📭 Нет заданий\nПопробуйте позже",
                reply_markup=main_menu()
            )
        else:
            channel_title = task_data.get('channel_title', 'Канал')
            channel_username = task_data.get('channel_username', '')
            channel_id = task_data.get('channel', '')  # ID канала для проверки

            text = (
                f"🎯 Задание!\n\n"
                f"Подпишитесь на:\n"
                f"📢 {channel_title}\n"
                f"{'@' + channel_username if channel_username else ''}\n\n"
                f"После подписки нажмите проверить"
            )

            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Проверить", callback_data=f"check_sub:{task_data['id']}:{channel_id}")],
                [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
            ])

            await callback.message.edit_text(text, reply_markup=keyboard)

    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка: {str(e)[:100]}",
            reply_markup=main_menu()
        )

    await callback.answer()


@router.callback_query(F.data.startswith("check_sub:"))
async def check_subscription(callback: CallbackQuery, user=None):
    # Проверяем, что user существует
    if user is None:
        await callback.message.edit_text(
            "❌ Ошибка: не удалось получить данные пользователя.\nПопробуйте позже.",
            reply_markup=main_menu()
        )
        await callback.answer()
        return

    # Разбираем callback data
    parts = callback.data.split(":")
    task_id = parts[1]
    channel_id = parts[2] if len(parts) > 2 else None

    print(f"Проверка подписки: user={user['telegram_id']}, task={task_id}, channel={channel_id}")  # Отладка

    telegram_client = TelegramAPIClient()

    try:
        # Проверяем подписку через Telegram API
        if channel_id:
            member_info = await telegram_client.get_chat_member(channel_id, user['telegram_id'])

            if member_info and member_info.get('result'):
                status = member_info['result'].get('status')
                print(f"Статус пользователя: {status}")  # Для отладки

                # Проверяем, что пользователь подписан (member, administrator, creator)
                if status in ['member', 'administrator', 'creator']:
                    # Подписка подтверждена, начисляем баллы через Django API
                    api_client = DjangoAPIClient()
                    result = await api_client.confirm_subscription(user['telegram_id'], task_id)

                    print(f"Результат подтверждения: {result}")  # Отладка

                    if result and 'error' not in result:
                        new_balance = result.get('new_balance', user['balance'] + 1)
                        points = result.get('points', 1)
                        await callback.message.edit_text(
                            f"✅ +{points} балл!\n"
                            f"Баланс: {new_balance}",
                            reply_markup=main_menu()
                        )
                    elif result and 'error' in result:
                        error_msg = result['error']
                        if 'already completed' in error_msg:
                            await callback.message.edit_text(
                                "❌ Эта задача уже выполнена!\nПолучите новое задание.",
                                reply_markup=main_menu()
                            )
                        elif 'not found' in error_msg:
                            await callback.message.edit_text(
                                "❌ Задание не найдено!\nПолучите новое задание.",
                                reply_markup=main_menu()
                            )
                        else:
                            await callback.message.edit_text(
                                f"❌ Ошибка: {error_msg}",
                                reply_markup=main_menu()
                            )
                    else:
                        await callback.message.edit_text(
                            "✅ Подписка подтверждена!\nБаллы начислены.",
                            reply_markup=main_menu()
                        )
                else:
                    # Пользователь не подписан
                    status_text = {
                        'left': 'вы вышли из канала',
                        'kicked': 'вы были исключены из канала',
                        'restricted': 'у вас ограничены права в канале'
                    }.get(status, 'вы не подписаны на канал')

                    await callback.message.edit_text(
                        f"❌ Проверка показала, что {status_text}!\n"
                        f"Подпишитесь и попробуйте снова.",
                        reply_markup=main_menu()
                    )
            else:
                # Ошибка получения информации о пользователе
                await callback.message.edit_text(
                    "❌ Не удалось проверить подписку. Возможно, канал приватный или бот не имеет доступа.\n"
                    "Попробуйте позже или обратитесь к администратору.",
                    reply_markup=main_menu()
                )
        else:
            # Если нет channel_id, показываем ошибку
            await callback.message.edit_text(
                "❌ Ошибка: не удалось получить информацию о канале.\n"
                "Попробуйте получить новое задание.",
                reply_markup=main_menu()
            )

    except Exception as e:
        import traceback
        print(f"Ошибка проверки подписки: {traceback.format_exc()}")  # Для отладки
        await callback.message.edit_text(
            f"❌ Ошибка проверки подписки: {str(e)[:100]}",
            reply_markup=main_menu()
        )

    await callback.answer()


@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery, user):
    text = (
        f"👤 Профиль\n\n"
        f"ID: {user['telegram_id']}\n"
        f"Username: @{user['username']}\n"
        f"Баланс: {user['balance']} баллов"
    )

    await callback.message.edit_text(text, reply_markup=main_menu())
    await callback.answer()