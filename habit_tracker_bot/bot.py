import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from config import BOT_TOKEN
from database.db import init_db, get_or_create_user, add_habit, get_user_habits

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Главная клавиатура
def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="➕ Добавить привычку")
    builder.button(text="📋 Мои привычки")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await get_or_create_user(message.from_user.id, message.from_user.username)
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n"
        "Я помогу тебе следить за твоими привычками.",
        reply_markup=get_main_keyboard()
    )


@dp.message(F.text == "📋 Мои привычки")
async def show_habits(message: types.Message):
    habits = await get_user_habits(message.from_user.id)
    if not habits:
        await message.answer("У тебя пока нет сохраненных привычек! Добавь первую через /add <название>")
    else:
        text = "🎯 **Твои привычки:**\n\n"
        for idx, h in enumerate(habits, 1):
            text += f"{idx}. {h.title}\n"
        await message.answer(text, parse_mode="Markdown")


# Простая команда добавления: /add Выпить воду
@dp.message(Command("add"))
async def cmd_add(message: types.Message):
    habit_title = message.text.replace("/add", "").strip()
    if not habit_title:
        await message.answer("Пожалуйста, напиши название привычки после команды.\nПример: `/add Зарядка 15 мин`",
                             parse_mode="Markdown")
        return

    await add_habit(message.from_user.id, habit_title)
    await message.answer(f"✅ Привычка **«{habit_title}»** успешно добавлена!", parse_mode="Markdown")


async def main():
    await init_db()
    print("База данных подключена, бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())