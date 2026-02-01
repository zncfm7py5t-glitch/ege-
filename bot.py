import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    LabeledPrice,
    FSInputFile
)
from aiogram.filters import Command

# ================== НАСТРОЙКИ ==================

BOT_TOKEN = "8230183079:AAFN0nDNmutEN9KvAnq-WfplhZCIhILxigs"
PAYMENT_TOKEN = "381764678:TEST:158589"

PRICE_SINGLE = 10000     # 100 ₽
PRICE_FULL = 90000       # 900 ₽

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# ================== КЛАВИАТУРЫ ==================

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📘 Купить конспекты")],
        [KeyboardButton(text="💼 Купить весь курс")]
    ],
    resize_keyboard=True
)

tasks_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Задание 1"), KeyboardButton(text="Задание 2")],
        [KeyboardButton(text="Задание 3")],
        [KeyboardButton(text="Задания 4–5")],
        [KeyboardButton(text="Задания 6–7")],
        [KeyboardButton(text="Задание 8")],
        [KeyboardButton(text="Задание 9")],
        [KeyboardButton(text="Задание 10")],
        [KeyboardButton(text="Задание 11")],
        [KeyboardButton(text="Задание 12")],
        [KeyboardButton(text="⬅ Назад")]
    ],
    resize_keyboard=True
)

# ================== START ==================

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Привет! 👋\n"
        "Это бот для подготовки к ЕГЭ по профильной математике.\n\n"
        "Здесь ты можешь купить конспекты по заданиям первой части.",
        reply_markup=main_keyboard
    )

# ================== МЕНЮ ==================

@dp.message(F.text == "📘 Купить конспекты")
async def buy(message: Message):
    await message.answer(
        "Выбери нужный конспект:",
        reply_markup=tasks_keyboard
    )

@dp.message(F.text == "⬅ Назад")
async def back(message: Message):
    await message.answer(
        "Главное меню:",
        reply_markup=main_keyboard
    )

# ================== КАРТА ЗАДАНИЙ ==================

TASK_MAP = {
    "Задание 1": ("task_1", "task1.pdf", "Задание 1"),
    "Задание 2": ("task_2", "task2.pdf", "Задание 2"),
    "Задание 3": ("task_3", "task3.pdf", "Задание 3"),
    "Задания 4–5": ("task_4_5", "task4_5.pdf", "Задания 4–5"),
    "Задания 6–7": ("task_6_7", "task6_7.pdf", "Задания 6–7"),
    "Задание 8": ("task_8", "task8.pdf", "Задание 8"),
    "Задание 9": ("task_9", "task9.pdf", "Задание 9"),
    "Задание 10": ("task_10", "task10.pdf", "Задание 10"),
    "Задание 11": ("task_11", "task11.pdf", "Задание 11"),
    "Задание 12": ("task_12", "task12.pdf", "Задание 12"),
}

# ================== ПОКУПКА ОДНОГО КОНСПЕКТА ==================

@dp.message(F.text.in_(TASK_MAP.keys()))
async def invoice_single(message: Message):
    payload, _, title = TASK_MAP[message.text]

    await bot.send_invoice(
        chat_id=message.chat.id,
        title=f"Конспект — {title}",
        description="Теория, формулы, примеры и подробные разборы",
        payload=payload,
        provider_token=PAYMENT_TOKEN,
        currency="RUB",
        prices=[LabeledPrice(label=title, amount=PRICE_SINGLE)]
    )

# ================== ПОКУПКА ВСЕГО КУРСА ==================

@dp.message(F.text == "💼 Купить весь курс")
async def invoice_full(message: Message):
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Полный курс ЕГЭ по профмату",
        description=(
            "Все конспекты первой части ЕГЭ.\n\n"
            "Задания 1–3\n"
            "Задания 4–5\n"
            "Задания 6–7\n"
            "Задания 8–12\n\n"
            "Всего 10 PDF-конспектов."
        ),
        payload="full_course",
        provider_token=PAYMENT_TOKEN,
        currency="RUB",
        prices=[LabeledPrice(label="Полный курс", amount=PRICE_FULL)]
    )

# ================== ПЛАТЁЖ ==================

@dp.pre_checkout_query()
async def checkout(pre):
    await pre.answer(ok=True)

@dp.message(F.successful_payment)
async def success(message: Message):
    payload = message.successful_payment.invoice_payload

    if payload == "full_course":
        await message.answer("⏳ Отправляю все конспекты курса…")

        files = [
            "task1.pdf",
            "task2.pdf",
            "task3.pdf",
            "task4_5.pdf",
            "task6_7.pdf",
            "task8.pdf",
            "task9.pdf",
            "task10.pdf",
            "task11.pdf",
            "task12.pdf",
        ]

        for filename in files:
            await message.answer_document(
                FSInputFile(f"materials/{filename}"),
                request_timeout=60
            )

        await message.answer("✅ Полный курс успешно получен!")
        return

    file_map = {v[0]: f"materials/{v[1]}" for v in TASK_MAP.values()}
    file_path = file_map[payload]

    await message.answer("⏳ Отправляю конспект…")
    await message.answer_document(
        FSInputFile(file_path),
        caption="📘 Ваш конспект",
        request_timeout=60
    )

# ================== ЗАПУСК ==================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
