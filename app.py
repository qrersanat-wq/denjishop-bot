import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from db import init_db
from handlers import start as h_start
from handlers import order as h_order


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("Укажи токен в .env (BOT_TOKEN=...) или прямо в config.py")

    init_db()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(h_start.router)
    dp.include_router(h_order.router)

    print("Telegram бот запущен. Нажми Ctrl+C для остановки.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
