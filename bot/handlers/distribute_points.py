# bot/handlers/distribute_points.py

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.keyboards.inline import main_menu, cancel_keyboard
import aiohttp
import logging
import json

logger = logging.getLogger(__name__)

router = Router()


class DistributePointsStates(StatesGroup):
    choosing_channel = State()
    entering_points = State()


@router.callback_query(F.data == "distribute_points")
async def distribute_points_start(callback: CallbackQuery, user):
    print(f"Пользователь: {user}")  # Отладка

    # Получаем список каналов пользователя через Django API
    try:
        async with aiohttp.ClientSession() as session:
            url = f"http://127.0.0.1:8000/api/user-channels/{user['telegram_id']}/"
            print(f"Запрос к: {url}")  # Отладка

            async with session.get(url) as response:
                print(f"Статус ответа: {response.status}")  # Отладка

                if response.status == 200:
                    # Читаем текст ответа
                    response_text = await response.text()
                    print(f"Текст ответа: {response_text}")  # Отладка

                    # Парсим JSON
                    try:
                        channels_data = json.loads(response_text)
                        print(f"Распарсенные данные: {channels_data}")  # Отладка
                    except json.JSONDecodeError as e:
                        print(f"Ошибка парсинга JSON: {e}")
                        await callback.message.edit_text(
                            "❌ Ошибка обработки данных",
                            reply_markup=main_menu()
                        )
                        return

                    if isinstance(channels_data, list) and len(channels_data) > 0:
                        # Создаем клавиатуру с каналами пользователя
                        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

                        buttons = []
                        for channel in channels_data:
                            # Убедимся, что у канала есть необходимые поля
                            if 'title' in channel and 'id' in channel:
                                button_text = f"{channel['title'][:20]}..." if len(channel['title']) > 20 else channel[
                                    'title']
                                buttons.append([
                                    InlineKeyboardButton(
                                        text=button_text,
                                        callback_data=f"select_channel:{channel['id']}"
                                    )
                                ])

                        if buttons:  # Если есть кнопки
                            buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="main_menu")])
                            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

                            await callback.message.edit_text(
                                f"💰 Распределение баллов\n\n"
                                f"Ваш баланс: {user['balance']} баллов\n\n"
                                f"Выберите канал для пополнения:",
                                reply_markup=keyboard
                            )
                        else:
                            await callback.message.edit_text(
                                "❌ У вас нет подходящих каналов для пополнения.",
                                reply_markup=main_menu()
                            )
                    else:
                        await callback.message.edit_text(
                            "❌ У вас нет добавленных каналов.\n"
                            "Сначала добавьте канал через меню 'Добавить канал'.",
                            reply_markup=main_menu()
                        )
                else:
                    error_text = await response.text()
                    print(f"Ошибка API: {error_text}")  # Отладка
                    await callback.message.edit_text(
                        f"❌ Ошибка получения каналов: HTTP {response.status}",
                        reply_markup=main_menu()
                    )
    except Exception as e:
        import traceback
        print(f"Полная ошибка: {traceback.format_exc()}")  # Для отладки
        logger.error(f"Error in distribute_points_start: {e}")
        await callback.message.edit_text(
            f"❌ Ошибка: {str(e)[:100]}",
            reply_markup=main_menu()
        )

    await callback.answer()


@router.callback_query(F.data.startswith("select_channel:"))
async def select_channel(callback: CallbackQuery, state: FSMContext, user):
    channel_id = callback.data.split(":")[1]
    await state.update_data(selected_channel_id=channel_id)

    await callback.message.edit_text(
        f"Введите количество баллов для перевода:\n"
        f"Ваш баланс: {user['balance']} баллов",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(DistributePointsStates.entering_points)
    await callback.answer()


@router.message(DistributePointsStates.entering_points)
async def enter_points(message: Message, state: FSMContext, user):
    try:
        points = int(message.text)

        if points <= 0:
            await message.answer("❌ Введите положительное число")
            return

        if points > user['balance']:
            await message.answer(f"❌ Недостаточно баллов. Ваш баланс: {user['balance']}")
            return

        data = await state.get_data()
        channel_id = data.get('selected_channel_id')

        # Отправляем запрос на перевод баллов через Django API
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        "http://127.0.0.1:8000/api/distribute-points/",
                        json={
                            "user_id": user['telegram_id'],
                            "channel_id": channel_id,
                            "points": points
                        }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        await message.answer(
                            f"✅ Успешно переведено {points} баллов!\n"
                            f"Новый баланс канала: {result.get('channel_balance', 0)}\n"
                            f"Ваш баланс: {result.get('user_balance', 0)}",
                            reply_markup=main_menu()
                        )
                    else:
                        error_text = await response.text()
                        await message.answer(
                            f"❌ Ошибка перевода: HTTP {response.status}",
                            reply_markup=main_menu()
                        )
        except Exception as e:
            logger.error(f"Error distributing points: {e}")
            await message.answer(
                f"❌ Ошибка перевода: {str(e)[:100]}",
                reply_markup=main_menu()
            )

        await state.clear()

    except ValueError:
        await message.answer("❌ Введите корректное число")
    except Exception as e:
        logger.error(f"Error in enter_points: {e}")
        await message.answer(f"❌ Ошибка: {str(e)[:100]}")
        await state.clear()


@router.callback_query(F.data == "cancel_distribute")
async def cancel_distribute(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Операция отменена", reply_markup=main_menu())
    await callback.answer()