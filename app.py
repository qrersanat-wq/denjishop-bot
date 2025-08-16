import asyncio
import sqlite3
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from db import init_db, get_order_by_amount, mark_order_paid
from handlers import start as h_start
from handlers import order as h_order
from handlers import admin as h_admin
from fastapi import FastAPI, Request
import uvicorn

# --- Telegram бот ---
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(h_start.router)
dp.include_router(h_order.router)
dp.include_router(h_admin.router)  # <- подключаем админку

# --- FastAPI ---
app = FastAPI()


async def notify_user_payment(tg_user_id: int, order_id: int):
    text = f"✅ Оплата за заказ #{order_id} получена!\nМы начинаем обработку вашего заказа."
    try:
        await bot.send_message(chat_id=tg_user_id, text=text)
    except Exception as e:
        print(f"Ошибка отправки сообщения пользователю: {e}")


@app.post("/api/kaspi/notify")
async def kaspi_notify(request: Request):
    data = await request.json()
    amount = int(data.get("amount", 0))

    order = get_order_by_amount(amount)
    if not order:
        return {"status": "error", "message": "Order not found"}

    mark_order_paid(order["id"])
    await notify_user_payment(order["tg_user_id"], order["id"])

    return {"status": "ok", "order_id": order["id"]}


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("Укажи токен в .env (BOT_TOKEN=...) или прямо в config.py")

    init_db()

    print("Telegram бот запущен. Нажми Ctrl+C для остановки.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Запускаем одновременно FastAPI и Telegram бота
    loop = asyncio.get_event_loop()

    # сервер API
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, loop="asyncio")
    server = uvicorn.Server(config)

    # запускаем FastAPI и бота параллельно
    loop.create_task(server.serve())
    loop.run_until_complete(main())
