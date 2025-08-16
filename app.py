import os
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from db import init_db, get_order_by_amount, mark_order_paid
from handlers import start as h_start
from handlers import order as h_order
from handlers import admin as h_admin
from fastapi import FastAPI, Request

# --- Telegram бот ---
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher(storage=MemoryStorage())

# Подключаем роутеры
dp.include_router(h_start.router)
dp.include_router(h_order.router)
dp.include_router(h_admin.router)

# --- FastAPI ---
app = FastAPI()

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

# Уведомление пользователю об оплате
async def notify_user_payment(tg_user_id: int, order_id: int):
    text = f"✅ Оплата за заказ #{order_id} получена!\nМы начинаем обработку вашего заказа."
    try:
        await bot.send_message(chat_id=tg_user_id, text=text)
    except Exception as e:
        print(f"Ошибка отправки сообщения пользователю: {e}")

# Kaspi callback
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

# --- Webhook Telegram ---
@app.on_event("startup")
async def on_startup():
    if not BOT_TOKEN:
        raise RuntimeError("Укажи токен в .env (BOT_TOKEN=...) или прямо в config.py")

    init_db()

    render_url = os.getenv("RENDER_EXTERNAL_URL")
    if render_url:
        webhook_url = f"{render_url}/webhook"
        await bot.set_webhook(webhook_url)
        print(f"Webhook установлен: {webhook_url}")
    else:
        print("⚠️ Нет переменной RENDER_EXTERNAL_URL — Render сам её подставит")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return {"ok": True}
