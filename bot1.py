from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import datetime
import aiohttp
import nest_asyncio
import logging
from aiogram.utils import executor

nest_asyncio.apply()

BOT_TOKEN = '8098648164:AAEyUCEgdJhB18cuhVWgRyc_AaSN4pts_80'
MODEL_API_URL = 'http://127.0.0.1:5000/predict'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

user_data = {}

async def make_prediction(user_id):
    """Отправляет данные на сервер для предсказания лайков."""
    if user_id not in user_data:
        return

    data = {
        'post_text': user_data[user_id]['post_text'],
        'post_date': user_data[user_id]['post_date'],
        'hashtags': user_data[user_id]['hashtags']
    }
    print(f"Отправка данных на сервер: {data}")

    async with aiohttp.ClientSession() as session:
        async with session.post(MODEL_API_URL, json=data) as response:
            if response.status == 200:
                prediction = await response.json()
                await bot.send_message(user_id, f"Предполагаемое количество лайков: {prediction['prediction']}")
            else:
                await bot.send_message(user_id, f"Произошла ошибка при получении предсказания. Код ошибки: {response.status}")


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    try:
        # Создание клавиатуры с тремя кнопками
        keyboard = ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True
        )

        # Создание кнопок
        button1 = KeyboardButton('/post')
        button2 = KeyboardButton('/date')
        button3 = KeyboardButton('/hashtags')

        # Добавление кнопок на клавиатуру
        keyboard.add(button1, button2, button3)

        # Отправка приветственного сообщения с клавиатурой
        await message.answer(
            "Привет! Я бот для предсказания лайков в ВК. Введите текст поста, дату публикации и хештеги.",
            reply_markup=keyboard
        )
    except Exception as e:
        logging.error(f"Ошибка при обработке команды /start: {e}")
        await message.answer("Произошла ошибка при обработке команды /start.")


@dp.message_handler(commands=['post'])
async def handle_post(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {'post_text': '', 'post_date': '', 'hashtags': ''}
    await message.reply("Введите текст поста:")

@dp.message_handler(commands=['date'])
async def handle_date(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await message.reply("Сначала введите текст поста с помощью команды /post.")
        return
    await message.reply("Введите дату публикации (в формате YYYY-MM-DD):")

@dp.message_handler(commands=['hashtags'])
async def handle_hashtags(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await message.reply("Сначала введите текст поста с помощью команды /post.")
        return
    await message.reply("Введите хештеги (разделенные пробелом):")

@dp.message_handler()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    if user_id in user_data:
        if not user_data[user_id]['post_text']:
            user_data[user_id]['post_text'] = text
            await message.reply(f"Текст поста: {text}\nТеперь введите дату публикации с помощью команды /date.")
        elif not user_data[user_id]['post_date']:
            try:
                datetime.datetime.strptime(text, '%Y-%m-%d')
                user_data[user_id]['post_date'] = text
                await message.reply(f"Дата публикации: {text}\nТеперь введите хештеги с помощью команды /hashtags.")
            except ValueError:
                await message.reply("Неверный формат даты. Пожалуйста, используйте формат YYYY-MM-DD.")
        elif not user_data[user_id]['hashtags']:
            user_data[user_id]['hashtags'] = text.split()
            await message.reply(f"Хештеги: {', '.join(text.split())}\nВсе данные введены. Спасибо!")

            # Отправляем данные на сервер для получения предсказания
            await make_prediction(user_id)

        else:
            await message.reply("Все данные уже введены. Используйте команды /post, /date или /hashtags для ввода новых данных.")
    else:
        await message.reply("Используйте команды /post, /date или /hashtags для ввода данных.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
