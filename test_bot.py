import pytest
from unittest.mock import AsyncMock
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from bot import send_welcome, handle_post, handle_date, handle_hashtags, make_prediction
from aioresponses import aioresponses

@pytest.mark.asyncio
async def test_start_command(mocker):
    # Мокаем объект message
    message = AsyncMock()
    message.answer = AsyncMock()

    # Создаем клавиатуру
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = KeyboardButton('/post')
    button2 = KeyboardButton('/date')
    button3 = KeyboardButton('/hashtags')
    keyboard.add(button1, button2, button3)

    # Тестируем команду /start
    await send_welcome(message)

    # Проверка, что метод answer был вызван
    message.answer.assert_awaited_with(
        "Привет! Я бот для предсказания лайков в ВК. Введите текст поста, дату публикации и хештеги.",
        reply_markup=keyboard
    )


@pytest.mark.asyncio
async def test_handle_post(mocker):
    # Мокаем объект message
    message = AsyncMock()
    message.from_user.id = 12345
    message.reply = AsyncMock()

    # Тестируем команду /post
    await handle_post(message)

    # Проверка, что метод reply был вызван
    message.reply.assert_awaited_with("Введите текст поста:")


@pytest.mark.asyncio
async def test_handle_date(mocker):
    # Мокаем объект message
    message = AsyncMock()
    message.from_user.id = 12345
    message.reply = AsyncMock()

    # Мокаем данные пользователя
    user_data = {12345: {'post_text': 'Текст поста', 'post_date': '', 'hashtags': ''}}

    # Тестируем команду /date
    await handle_date(message)

    # Проверка, что метод reply был вызван
    message.reply.assert_awaited_with("Введите дату публикации (в формате YYYY-MM-DD):")


@pytest.mark.asyncio
async def test_handle_hashtags(mocker):
    # Мокаем объект message
    message = AsyncMock()
    message.from_user.id = 12345
    message.reply = AsyncMock()

    # Мокаем данные пользователя
    user_data = {12345: {'post_text': 'Текст поста', 'post_date': '2024-12-20', 'hashtags': ''}}

    # Тестируем команду /hashtags
    await handle_hashtags(message)

    # Проверка, что метод reply был вызван
    message.reply.assert_awaited_with("Введите хештеги (разделенные пробелом):")


@pytest.mark.asyncio
async def test_full_flow(mocker):
    # Мокаем объекты сообщений
    message = AsyncMock()
    message.from_user.id = 12345
    message.reply = AsyncMock()

    # Мокаем user_data
    user_data = {12345: {'post_text': '', 'post_date': '', 'hashtags': ''}}

    # Мокаем make_prediction
    mocker.patch("bot.make_prediction", return_value=None)

    # Симулируем полный процесс ввода данных
    await handle_post(message)
    await handle_date(message)
    await handle_hashtags(message)

    # Проверка, что метод reply был вызван
    message.reply.assert_awaited_with("Введите хештеги (разделенные пробелом):")
